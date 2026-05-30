# phyra-dualtrans

A local **WebUI service** that turns an academic-paper PDF (or arXiv link)
into a **side-by-side bilingual PDF** — original on the left, translation on
the right — using [BabelDOC](https://github.com/funstory-ai/BabelDOC) for
layout-faithful reconstruction and a **pluggable LLM backend** for the
actual translation.

Extracted from the [Phyra](https://github.com/OrientoNubo/Phyra)
`paper-translate` skill, rebuilt as a standalone FastAPI app so you can use
your own API keys / local models from a browser.

## Features

- **Bilingual dual PDF** (same page count as the source). A
  per-paragraph policy keeps the **References** section, **figure/table
  content**, formulas and running headers **verbatim in the original**
  (visible, not a grey placeholder) while **captions and all body text
  are translated** — robust to references mixed onto a body page.
- **Figures never break**: BabelDOC's page rebuild can corrupt the
  translated side's images; the original figure regions are stamped back
  so they look exactly like the source (captions still translated).
- Optional **translation-only (mono) PDF**.
- **Three LLM backends**, chosen per job in the UI:

  | Backend | Needs | Covers |
  |---|---|---|
  | `openai` | `base_url` + `api_key` | OpenAI, DeepSeek, Together, Groq, OpenRouter, vLLM, LM Studio — any OpenAI-compatible endpoint |
  | `ollama` | Ollama running locally | Local models; auto-lists installed models |
  | `claude_cli` | `claude` CLI on host (no API key) | Your existing Claude Code auth |

- **Input**: drag-drop a PDF *or* paste an arXiv URL / id. A **Batch**
  tab takes many PDFs / arXiv links and runs them strictly in the order
  added (one after another).
- **Context distillation** (opt-in): a one-shot pre-pass builds a
  compact translation guide (domain, term glossary, proper nouns to keep
  in English, style) that is injected into every segment — document-wide
  term consistency without feeding the whole paper into each call, so it
  fits small-context local models. See `docs/DEVELOPMENT.md`.
- **Managed, fast local Ollama**: the WebUI owns a dedicated Ollama
  (starts/stops with the service, its own port — never touches a system
  or manual instance) and a tuned `qwen3:14b` model created on first
  run. The `ollama` backend calls the native `/api/chat` with thinking
  disabled — ~9× fewer tokens / several × faster than the `/v1` shim for
  reasoning models like qwen3. Leave the UI Base URL blank. See
  `docs/ollama.md` / `docs/SPEED.md`.
- **Runtime status** under Settings → Options: a live badge
  (`/api/runtime`) showing whether an NVIDIA GPU + driver are visible
  (`nvidia-smi`) and whether the Ollama model is resident in VRAM or has
  fallen back to **CPU** — catches the silent slow-down where a crashed
  GPU driver pushes inference onto the CPU (~10× slower, no error).
  Hover for per-GPU memory/utilisation; re-probes every 30 s and on the ↻
  button.
- **Live progress** over Server-Sent Events. Finished jobs survive a
  restart (the list is rebuilt from the jobs dir).
- **PDF compression** on output: `lossy` (Ghostscript, choose DPI/preset),
  `lossless` (re-deflate), or `off`. Intermediates are auto-cleaned on
  success.
- Light / dark / system **theme** (matches the `paper-base` visual style).

## Quick start

```bash
scripts/start.sh                 # ← that's it
```

One command, nothing else: it repairs the venv if needed (e.g. after
moving the folder), downloads the BabelDOC models + CJK fonts the first
time (~340 MB, once), starts the server, and opens your browser when it's
ready. `Ctrl+C` stops it. `PORT=9000 scripts/start.sh` to change the port,
`NO_BROWSER=1` to skip auto-opening the browser.

Then pick a backend, drop a PDF, watch it translate, download the dual
(and mono) PDF.

<details><summary>Manual / advanced (what <code>start.sh</code> automates)</summary>

```bash
# one-time: download BabelDOC models + CJK fonts (~340 MB)
scripts/warmup.sh

# run (foreground, no venv-repair, no browser)
scripts/serve.sh                 # → http://localhost:8000
# or
uv run uvicorn phyra_dualtrans.web.app:app --host 0.0.0.0 --port 8000
```
</details>

## Configuration

Settings can be set in the WebUI ("Save as defaults" → writes
`~/.config/phyra-dualtrans/config.json`, chmod `0600`) or via env / `.env`
(see `.env.example`). Precedence:

```
per-request override  >  config.json  >  env / .env  >  built-in default
```

API keys are **never** committed, never logged, never passed on the command
line — they reach the translation subprocess only over its stdin.

## Docker

```bash
docker build -t phyra-dualtrans .
docker run --rm -p 8000:8000 \
  -v "$HOME/.cache/babeldoc:/root/.cache/babeldoc" \   # reuse warmed models/fonts
  -e OPENAI_API_KEY=sk-... \
  phyra-dualtrans
```

The `claude_cli` backend is host-only (needs the `claude` binary + your
`~/.claude` auth); inside the container use `openai` or `ollama`.

## Why each translation runs in a subprocess

BabelDOC 0.5.24 leaves non-daemon executor threads alive after it finishes,
which stalls asyncio teardown for ~20 minutes. The upstream Phyra CLI works
around this with `os._exit()` once the PDF is on disk — correct for a
one-shot CLI, **fatal for a long-lived server** (it would kill uvicorn and
every other in-flight job).

So this service **never imports BabelDOC**. Each job spawns
`python -m phyra_dualtrans.pipeline.translate_runner` as a child process;
that child is the only thing allowed to `os._exit`. Progress streams back
parent←child as line-delimited JSON. This also gives clean hard-cancel and
full memory isolation.

## Relationship to Phyra

`phyra-dualtrans` is a **standalone sibling project** of
[Phyra](https://github.com/OrientoNubo/Phyra) — same author, independent
repo, designed to sit under the **Phyra Center** umbrella:

```
phyra-proj/
├── Phyra/                          # the Claude Code research plugin
└── phyra-center/                   # the hub / landing page (:8035)
    ├── phyra-archbase/             # the paper archive WebUI       (:8037)
    └── phyra-dualtrans/            # this repo — translation WebUI (:8039)
```

It was extracted from Phyra's `paper-translate` skill. The only shared
code (`_retry.py`, `resolve_input.py`, the PyMuPDF slice/build steps, the
translation prompts) was **vendored / ported in**, so this project has
**zero runtime dependency on Phyra** — it runs with neither Phyra nor
Claude Code present. Full provenance and re-sync notes are in
[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

## phyra-center / phyra-archbase integration

`phyra-dualtrans` (translate) and
[`phyra-archbase`](../phyra-archbase) (archive / browse) are sibling
WebUIs hosted under [`phyra-center`](..) — the **Phyra Center** landing
page that lists every Phyra service and acts as the entry point:

- The dualtrans WebUI carries a top **「← 🜂 Phyra Center」** banner that
  links back to the Center landing page (the banner is shown only when
  Center is reachable; standalone use stays banner-less). The Center port
  defaults to `:8035` (`PHYRA_DUALTRANS_CENTER_PORT`).
- After a translation finishes, its Jobs card gets a **📥 存入 archbase**
  button. It pops a small dialog (prefilled `YYMM` + `Title`), then copies
  the **original + dual PDF** into archbase's `collection/` under its
  filename convention and re-runs archbase's `generate_index.py` so the
  paper appears in the archive immediately. Once saved the button shows
  **✓ 已入庫（可重存）** — still clickable, since re-saving just overwrites.

When the two repos sit next to each other under Center
(`phyra-proj/phyra-center/{phyra-dualtrans,phyra-archbase}`) it works
with no config — the sibling is auto-detected. Otherwise point
`PHYRA_DUALTRANS_ARCHBASE_DIR` at the archbase checkout (and set
`PHYRA_DUALTRANS_ARCHBASE_PORT` if the archive isn't on `:8037`). The
button is hidden when no archbase is reachable. Honors
`PHYRA_DUALTRANS_DROP_ORIGINAL` — with the original dropped there is
nothing to archive, so the button does not appear.

> Run the whole stack (Center + archbase + dualtrans) with the one-liner
> at `phyra-center/script/start.sh` — it boots all three and opens your
> browser to the Center landing page.

## Development

See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for project layout, the
`os._exit` subprocess-isolation architecture, the NDJSON child protocol,
how to add an LLM backend, and notes on moving the project / resuming the
Claude Code session.

## Security

The server binds `0.0.0.0` and has **no general authentication** — run it
only on a trusted network, or bind localhost only:

```bash
HOST=127.0.0.1 scripts/start.sh
```

Job state is in-memory (lost on restart by design; finished PDFs remain on
disk under the jobs dir).

### Disk usage

Each job has a workdir under
`~/.local/share/phyra-dualtrans/jobs/<job_id>/`. On **success** the
throwaway intermediates (`*.no_refs*` sliced / BabelDOC files +
`child.log`, ~90 MB for a typical paper) are deleted automatically;
the final `*_bilingual.<lang>.dual.pdf` (+ `.mono.pdf`) and the original
upload are kept. A **failed** job keeps everything (the intermediates and
log are how you debug it). Nothing is auto-deleted by age, and the
restart-wiped job list does not remove these files — prune old
`<job_id>/` dirs yourself (or use the 🗑 button before restart, which
deletes a job's whole workdir, output included).

- `PHYRA_DUALTRANS_KEEP_INTERMEDIATES=1` — keep intermediates (old
  behavior / debugging).
- `PHYRA_DUALTRANS_DROP_ORIGINAL=1` — also delete the original PDF on
  success (footprint then ≈ just the final PDFs).

### Password gate for the `claude_cli` backend

The `claude_cli` backend spends **this host's** Claude Code auth (no
key, billed to you). `ollama` (your local GPU) and `openai` (caller's
key) are **not** gated. With no login and a `0.0.0.0` bind, set a
password so randoms can't burn your Claude quota:

```bash
PHYRA_DUALTRANS_CLAUDE_CLI_PASSWORD='choose-a-secret' scripts/start.sh
```

When set, the UI shows an **Admin password** field for `claude_cli` and
`POST /api/translate` (and `/batch`) returns `401` without the correct
password (constant-time). Unset = `claude_cli` is open. It is
**env-only by design** — never in `config.json` / the API, which are
unauthenticated; never logged, echoed, or persisted. (To keep others
off your local GPU when exposing `ollama`, bind localhost — see below.)

### Other hardening / known limits

- **arXiv field is validated**: it must be a real arXiv id / `arxiv.org`
  URL. (Otherwise `resolve_input` would treat an arbitrary string as a
  local filesystem path — an arbitrary-file read on this open service.)
- **No TLS**: the admin password and any API key travel in clear text.
  On an untrusted network, bind localhost (`HOST=127.0.0.1`) or put a
  TLS reverse proxy in front.
- **`ollama` is not gated**: anyone reachable can run jobs on your
  local GPU. If that matters, bind localhost (`HOST=127.0.0.1`) or run
  on a trusted network only.
- **No request limits**: anyone reachable can enqueue jobs; the
  queue/disk can grow unbounded. Prune the jobs dir; trusted network.
- Untrusted PDFs are parsed by PyMuPDF/BabelDOC — inherent to the tool;
  only translate PDFs you're willing to feed a parser.

## Rendering quality / known limitations

- **Dense inline math can reflow imperfectly.** On equation-heavy pages
  (many inline formulas in a two-column layout), BabelDOC's IL re-layout
  can break a paragraph's lines or scatter a formula's sub/superscript
  fragments — the translated text is correct but the *visual* line order
  in that block looks shuffled. This happens inside BabelDOC's text
  rebuild, upstream of the dual-PDF assembly, so it is not something this
  tool post-processes away. **Mitigation:** enable **Enhance
  compatibility** for such papers — it rasterizes complex pages, so the
  equations keep the original layout (no reflow) at the cost of larger,
  non-selectable pages.
- **Reasoning-model control tokens are stripped.** Hybrid models such as
  qwen3 can leak a `<think>…</think>` block or a bare `/no_think`
  soft-switch token into their output; both are removed before the text
  reaches the PDF (`pipeline/prompts.py::clean`).

## License

Apache-2.0.
