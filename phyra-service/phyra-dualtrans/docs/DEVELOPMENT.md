# Development guide

## Relationship to Phyra (sibling project)

`phyra-dualtrans` is a **standalone, sibling project** to
[Phyra](https://github.com/OrientoNubo/Phyra) — not a Phyra plugin, not a
submodule, not a subdirectory. They are meant to live side by side:

```
phyra-proj/
├── Phyra/            # the Claude Code research plugin (skills/commands/agents)
└── phyra-dualtrans/  # this repo — the standalone translation WebUI service
```

### What came from Phyra, and how it's decoupled

This project was extracted from Phyra's `paper-translate` skill. The
coupling to Phyra was only **two small pure utilities**, which were
**vendored** (copied in, not referenced):

| In this repo | Origin in Phyra | Status |
|---|---|---|
| `phyra_dualtrans/vendor/_retry.py` | `skills/paper-read/scripts/_retry.py` | copied **verbatim** |
| `phyra_dualtrans/vendor/resolve_input.py` | `skills/paper-read/scripts/resolve_input.py` | copied, **decoupled** (CLI `main()` removed; callers must pass an explicit out dir; no `.phyra/papers` fallback) |
| `phyra_dualtrans/pipeline/slice_pdf.py` | `skills/paper-translate/scripts/slice_pdf.py` | ported (pure PyMuPDF) |
| `phyra_dualtrans/pipeline/build_dual.py` | `skills/paper-translate/scripts/build_dual.py` | ported (pure PyMuPDF) |
| `phyra_dualtrans/pipeline/prompts.py` | `translate_with_claude.py` (SYSTEM_PROMPTS / system_prompt_for / _clean) | extracted **verbatim** |
| `phyra_dualtrans/pipeline/babeldoc_translator.py` | `translate_with_claude.py` (`ClaudeHeadlessTranslator`) | refactored — one `BaseTranslator` + injected `LLMClient`; retry loop & placeholder regexes kept byte-identical |

**Runtime independence is verified:** the package has zero imports that
escape it, no hard-coded Phyra paths, and no `${CLAUDE_PLUGIN_ROOT}`
dependency. You can move this repo anywhere without Phyra present.

> Why the docstrings still say "vendored from Phyra paper-read": that is
> deliberate provenance, not a runtime link. If Phyra fixes a bug in
> `_retry.py` / `resolve_input.py` you can re-sync by copying the file
> again and re-applying the `resolve_input` decoupling (drop `main()`,
> require `override_out_dir`).

What was **intentionally NOT** carried over (Phyra-only, not needed for a
service): the `soul` / `typography` skills, the `paper-translator`
subagent, the command/skill markdown, and the `${CLAUDE_PLUGIN_ROOT}`
preflight check.

## Project layout

```
phyra_dualtrans/
├── config.py           # AppSettings (env) + UserDefaults (config.json) + resolve_backend()
├── models.py           # request/response pydantic models
├── backends/           # base.py (LLMClient Protocol + BackendConfig + errors)
│                        # openai_compatible.py / ollama.py / claude_cli.py + registry
├── pipeline/           # slice_pdf · babeldoc_translator · translate_runner (child)
│                        # build_dual · compress · preflight · prompts
├── vendor/             # _retry.py (verbatim) · resolve_input.py (decoupled)
└── web/                # app.py (factory) · jobs.py (supervisor) · sse.py
                         # routes_* · static/ (index.html · app.js · styles.css)
```

## Setup & run

Requires `uv`, Python ≥ 3.12, Ghostscript (`gs`, for lossy compression).

```bash
uv sync                       # create .venv + install (commit uv.lock)
scripts/warmup.sh             # one-time: BabelDOC models + CJK fonts (~340MB)
scripts/serve.sh              # → http://localhost:8000   (PORT=9000 to change)
# or: uv run uvicorn phyra_dualtrans.web.app:app --host 0.0.0.0 --port 8000
uv run pytest -q              # 25 tests, no network / no LLM needed
```

## Architecture: the os._exit isolation boundary

BabelDOC 0.5.24 leaves non-daemon executor threads alive after finishing,
stalling asyncio teardown ~20 min. The upstream CLI works around this with
`os._exit()` once the PDF is on disk — correct for a one-shot CLI, **fatal
in a long-lived server**.

So the rule is absolute: **the server process never imports BabelDOC.**
Each job spawns a child:

```
python -m phyra_dualtrans.pipeline.translate_runner <sliced.pdf> <workdir> \
        --lang-in en --lang-out zh-TW --qps 2 [--compat]
```

- The `BackendConfig` (incl. the real `api_key`) is fed on the child's
  **stdin** as one JSON line — never argv, so it never shows in `ps`.
- The child writes **NDJSON** events to **stdout** (one JSON object per
  line); all logging goes to **stderr** (captured to `<workdir>/child.log`).
- Only the child calls `os._exit` — it kills only itself.
- Cancel = `proc.kill()`, clean because of the process boundary.

Invariant test you can run anytime:

```bash
uv run python -c "import sys, phyra_dualtrans.web.app; \
  assert 'babeldoc' not in sys.modules; print('isolation OK')"
```

### NDJSON event types (child → supervisor → SSE)

`backend` · `started` · `progress` (`stage`, `stage_pct`, `overall_pct`) ·
`stage_end` · `rate_limit` (`attempt`, `max_attempts`, `wait_sec`) ·
`chunk_fallback` · `finish` (`dual_pdf`) · `error`. The supervisor
(`web/jobs.py`) re-broadcasts these to every SSE subscriber of the job and
keeps a snapshot for late-joining browser tabs.

## SSE heartbeat must not cancel the event generator

A second isolation rule, learned from an end-to-end run: the 15 s SSE
heartbeat in `web/sse.py` must **never** cancel the in-flight
`it.__anext__()`. The naive `asyncio.wait_for(it.__anext__(), timeout=
HEARTBEAT_SEC)` does exactly that on every timeout — and since that
coroutine is suspended inside `JobManager.subscribe()`'s `await
queue.get()`, the `CancelledError` unwinds that generator (running its
`finally`, dropping the subscriber) and closes it. The next `__anext__()`
raises `StopAsyncIteration`, so the stream ends — i.e. the live progress
bar dies on the **first >15 s quiet gap**, which every real LLM-paced
translation has (it was observed dying mid-`Translate Paragraphs`).

The fix keeps a single in-flight `__anext__()` task alive **across**
heartbeat timeouts (`asyncio.wait({nxt}, timeout=…)`; on timeout emit a
ping and keep the same task); only a real client disconnect cancels it.
Locked by `tests/test_sse.py` (`test_heartbeat_does_not_kill_stream`,
`test_client_disconnect_cancels_pending_anext`).

## Pipeline extensions

**References slicing (page-granular, content-safe).** `slice_pdf`
finds the `References` header page (`find_ref_start_page_from_pdf`,
last match) and the next `Supplementary`/`Appendix` heading
(`find_supp_start_page_from_pdf`) → references region
`[ref_header .. ref_end]`. Within that region a page is skipped **only
if `_page_is_pure_references()` says it is nothing but a bibliography**;
any mixed page is translated. Slicing is page-granular, so dropping a
page that still holds body text loses content — the reported bug was the
References-header page (refs start mid-page, body above). The classifier
is deterministic on that boundary (a page still bearing the `References`
heading is never "pure") and, for later pages, counts enumerated entry
markers (`[12]` / `12.`) + venue/year hints rather than a line ratio, so
it survives two-column PDFs whose entries wrap over many fragment lines.
Conservative: unsure → not pure → translate. `build_dual` walks every
page 1..N (`ref_pages` → placeholder, else → next translated page), so a
non-contiguous kept set is fine as long as the sliced PDF holds the kept
pages ascending. Locked by `tests/test_slice_pdf.py`
(`test_refs_header_page_is_kept`, supplementary cases).

**Ollama native no-think client.** `OllamaClient` does *not* reuse the
OpenAI `/v1` path — it POSTs the native `<host>/api/chat` with
`"think": false`. qwen3 keeps a hidden chain-of-thought on `/v1` that no
flag there disables (~9× tokens, several × slower). It still subclasses
`OpenAICompatibleClient` only to keep the registry / isinstance contract;
`complete()` is fully overridden. `clean()` also strips any leaked
`<think>…</think>` so a reasoning model can't corrupt the PDF. Numbers
and the why: `docs/SPEED.md`.

**Context distillation (opt-in pre-pass).** When a job sets `distill`,
the child (`pipeline/distill.py`, before `init()`/`async_translate`)
extracts the refs-stripped PDF text (capped by
`PHYRA_DUALTRANS_DISTILL_MAX_CHARS`, default 24 000), makes ONE
`llm.complete()` call for a compact guide (domain / glossary /
keep-in-English / style), and passes it to `BabelDocTranslator`, which
appends it to the per-segment system prompt and folds a hash of it into
the BabelDOC cache id (so a different guide never reuses another guide's
cached segments). It must never fail the job: any error → `None` →
translate as before. Emits `distill` NDJSON events
(`start`/`done`/`skipped`).

**Batch ordering.** `POST /api/translate/batch` reads the multipart
form in field order (Starlette preserves it across keys; an `arxiv`
textarea is expanded per line) and creates jobs chained via
`Job._after`/`_done_evt`: job N awaits the predecessor's terminal event
*before* contending for the concurrency semaphore, so a batch runs in
strict submission order regardless of `asyncio.Semaphore` fairness.
Single-job posts are unaffected (`after=None`).

**Restart rehydration.** Every terminal job writes `workdir/job.json`
(`_persist`, best-effort). On startup `JobManager.rehydrate()` (called
from the lifespan) scans `jobs_dir`: a job.json is restored as-is
(non-terminal status → `failed` "interrupted by a server restart");
a dir with no job.json but a `*_bilingual.*.dual.pdf` is synthesized as
`succeeded`; anything else is skipped. Live registry entries are never
clobbered. Stage-E cleanup keeps `job.json` (and `slice_meta.json`).

## Adding a new LLM backend

1. Implement a class with `name: str` and
   `complete(self, system: str, prompt: str) -> str` (synchronous — it
   runs in BabelDOC's thread pool). Raise `RateLimitSignal(matched)` for
   rate limits, `HardCallError(...)` for non-retryable failures. See
   `backends/openai_compatible.py` as the reference.
2. Register it in `backends/__init__.py` (`BACKEND_REGISTRY` + add an
   entry to `BACKEND_INFO`).
3. Add per-backend checks in `pipeline/preflight.py::_check_backend`.
4. Extend `config.py::resolve_backend` if it needs new credential/url
   precedence, and surface any new field in `web/static/` (index.html +
   app.js `collect()`).

The retry loop, prompts, placeholder regexes and source-text fallback live
once in `pipeline/babeldoc_translator.py` — do **not** duplicate them per
backend (the placeholder tuples must stay byte-identical or BabelDOC's
reassembly silently corrupts).

## Config & secrets

Precedence (resolved per request in `resolve_backend`):
`per-request override > config.json > env/.env > built-in default`.

- `~/.config/phyra-dualtrans/config.json` (chmod 0600) — written by
  `PUT /api/settings`. **Outside the repo**, so moving the repo does not
  lose settings.
- API keys are never committed, never logged, never on argv; `.gitignore`
  excludes `.env` and `config.json`; `GET /api/settings` returns `***`.

### Workdir cleanup (pipeline stage E)

A finished job's intermediates (`*.no_refs*` sliced + BabelDOC dual,
`child.log`) dwarf the output (~90 MB vs ~2 MB). Stage E in
`JobManager._run` deletes them — but **only on success**: a failed job
keeps everything because that is exactly what you debug with. The match
is substring-based (`".no_refs" in name`), not glob, so stems full of
shell/regex metachars (e.g. `2605_VGGT-$_Omega$`) are safe. Final
dual/mono and `slice_meta.json` are never touched; the original pdf is
kept unless `PHYRA_DUALTRANS_DROP_ORIGINAL`. `PHYRA_DUALTRANS_KEEP_
INTERMEDIATES=1` skips the stage entirely. Cleanup never raises (it must
not fail a translation that already produced its output). Locked by
`tests/test_cleanup.py`. Note: `job_ttl_hours` exists in config but is
**not implemented** — there is no age-based sweeper yet.

### claude_cli password gate + arXiv LFI guard (env-only, on purpose)

Only `claude_cli` is gateable — it spends the host's Claude auth.
`gate_password_for(kind)` returns `PHYRA_DUALTRANS_CLAUDE_CLI_PASSWORD`
for `claude_cli`, else `None` (`ollama` = local GPU and `openai` =
caller's key are deliberately NOT gated). The plumbing is generic
(`gate_password_for` / `backend_gated` / `check_backend_password`,
`hmac.compare_digest`) so another backend could be gated later, but
today only claude_cli is. Enforced in `routes_translate._resolve`
(single + `/batch`) before the upload is read; advertised per backend
via `needs_password` on `/api/backends`.

The password is read **only** from env/.env — never `config.json` / the
API, which are unauthenticated and could otherwise be read/overwritten
to defeat the gate (also why there is no server-side settings file at
all). Locked by `tests/test_admin_gate.py`.

**arXiv LFI guard.** `resolve_input()` treats a non-arXiv string as a
**local filesystem path** (a CLI affordance from its Phyra origin). On
this unauthenticated service that is an arbitrary-file read, so the
`arxiv` input is validated with `detect_arxiv_id()` at the web boundary
(`routes_translate.py`, single → 400, batch → skip) **and** again in
`JobManager._run` (defense-in-depth) before `resolve_input` is called.

## Moving the project directory

The repo is self-contained, but the **`.venv` is not relocatable** (uv
hard-codes absolute paths). It's gitignored, so after moving:

```bash
cd <new-location>/phyra-dualtrans
rm -rf .venv && uv sync          # cheap — wheels are cached
```

`jobs/` (runtime workdirs) and `~/.config|~/.local` data are unaffected.

## Resuming the Claude Code conversation after moving Phyra

Claude Code keys session history by the **launch directory path**. This
build's conversation ran in `/home/nubo/workspace/Phyra`, stored at
`~/.claude/projects/-home-nubo-workspace-Phyra/`. After you move it to
`/home/nubo/workspace/phyra-proj/Phyra` the auto-derived slug becomes
`-home-nubo-workspace-phyra-proj-Phyra`, so `claude --resume` won't find
the old session — and it can **only** be resumed from the (moved) *Phyra*
project, never from inside *phyra-dualtrans* (different project).

Options (pick one):

```bash
# A. Before moving — relaunch in place, then move while it stays open:
cd /home/nubo/workspace/Phyra && claude --continue

# B. After moving — rename the stored project folder to the new slug
#    (preserves ALL sessions, including this one):
mv ~/.claude/projects/-home-nubo-workspace-Phyra \
   ~/.claude/projects/-home-nubo-workspace-phyra-proj-Phyra
cd /home/nubo/workspace/phyra-proj/Phyra && claude --resume   # pick this session

# C. Most robust — export this conversation to a durable file first:
#    (inside the running session)  /export phyra-dualtrans-build.md
```

Everything needed to continue without the chat history is already
captured: this committed repo, the plan file at
`~/.claude/plans/phyra-translate-dreamy-nova.md`, and this guide.
