# Translation speed — analysis & tuning

Measured on this host (RTX 5090, Ollama 0.24, `qwen3-32b-trans`,
`zh-TW`). All numbers are for the model call, which dominates wall time.

## TL;DR

1. **Hidden reasoning was the dominant cost.** `qwen3` is a hybrid
   reasoning model; on the OpenAI-compatible `/v1` shim it keeps
   *thinking* and you cannot turn it off there.
2. **Fix shipped:** the Ollama backend now calls the **native
   `/api/chat`** with `"think": false`. ~9× fewer generated tokens,
   3–8× lower latency, no measurable translation-quality loss.
3. **Fewer LLM calls:** references / figure-table interiors / formulas
   are no longer translated (kept verbatim), so those segments cost ~0.
4. **Cache is OFF by default** (it silently poisoned output — see
   below); a local re-run is cheap, a wrong PDF is not.
5. **Retry backoff lowered to 10s×5** (was 60×8 ≈ 8 min): a
   misclassified local hiccup no longer freezes a paragraph for minutes
   (the reported "等很久").
6. Everything else (qps, keep-alive, context distillation) is
   secondary tuning on top of that.

## The measurement that drove the change

One short sentence (`en → zh-TW`, ~40-token correct answer):

| path | latency | generated tokens | hidden CoT |
|---|---|---|---|
| `/v1` chat-completions (old) | 6–15 s | **405–694** | ~1500 chars, not in `content` but still generated & billed in time |
| `/v1` + `/no_think` / `chat_template_kwargs` / `think` | 6–9 s | 390–570 | **not disabled** — `/v1` ignores all of these |
| native `/api/chat` `think:false` (new) | **0.8–2.5 s** | **48** | none |

So a ~40-token translation was paying for ~400–700 tokens of
chain-of-thought it then threw away. Across a ~200-paragraph paper that
is the difference between ~10 min and ~50+ min.

`clean()` was also extended to strip any leaked `<think>…</think>`
block defensively — if one ever reached BabelDOC it would corrupt the
reassembled PDF. (No-op for Claude, which never emits them.)

## How the pipeline calls the model

BabelDOC parses the FULL PDF (no page slicing — see below), splits it
into paragraph segments, and calls `BabelDocTranslator.do_translate(
text)` **once per segment** from a thread pool of size `qps`. Each call
is independent: fixed per-language system prompt + that one segment.
Implications:

- Throughput ≈ `qps` × (1 / per-call latency). Lowering per-call
  latency (the no-think fix) helps every segment linearly.
- **Fewer calls now.** A per-paragraph keep-source policy (`il_filter`)
  skips the LLM entirely for the References section, figure/table
  interiors, formulas and running headers — the expensive part of those
  pages costs ~0. This both speeds the job and is the correct output
  (captions and body are still translated).
- **The cache is OFF by default — and that is on purpose.** BabelDOC's
  `BaseTranslator` caches whatever `do_translate()` returns, including
  the source-text fallback we emit on a failed call, keyed (engine,
  params, text) with no guard. One failed run then poisons
  `~/.cache/babeldoc/cache.v1.db` so every later run of that paper
  returns the English source ("all-English succeeded"). Correctness
  beats a re-run cache for a local backend. Re-enable with
  `PHYRA_DUALTRANS_USE_CACHE=1` only when every backend is known-good.

## Tuning knobs (in priority order)

1. **Keep thinking off.** Default for the `ollama` backend. It is a
   per-job **user choice** (an "Enable model thinking" toggle in the UI
   / `BackendConfig.think`) — leave it off for translation; turn it on
   only if you have a specific reason. Model choice is likewise the
   user's. For the `openai` backend pointed at other servers, prefer a
   non-reasoning model for translation — reasoning adds latency without
   translation gain.
2. **`qps` vs `OLLAMA_NUM_PARALLEL`.** One 32 B model on one GPU:
   parallel requests share compute, so gains are sub-linear and can hurt
   per-call latency. Keep `qps` ≈ `OLLAMA_NUM_PARALLEL` (their doc sets
   `2`). Try `qps=3–4` only if `nvidia-smi` shows GPU head-room; back
   off if latency balloons. Bigger is **not** always faster — past the
   GPU's limit you also start hitting rate-limit waits.
3. **Keep the model warm.** `OLLAMA_KEEP_ALIVE=-1` (already in
   `docs/ollama.md`) avoids a multi-second reload mid-paper.
4. **Context distillation (see DEVELOPMENT.md).** A one-shot pre-pass
   produces a compact "translation guide" injected into every segment's
   system prompt. It adds a *small fixed* prompt prefix (prompt tokens
   are cheap to process; with thinking off, generation stays short), so
   the per-call cost rise is minor — while giving document-wide term
   consistency **without** feeding the whole document (which a 32 K
   model can't do anyway). It improves quality and bounds context use;
   it is not itself a speed-up.
5. **`enhance_compatibility` off** unless a PDF needs it (it rasterizes
   complex pages → slower, larger).

## Considered but not done

- **Many segments per call.** Would amortize round-trips but BabelDOC's
  placeholder protocol is per-segment; batching risks silent
  reassembly corruption (the placeholder tuples must stay byte-exact).
  Not worth the integrity risk for the gain now that per-call latency
  is ~1 s.
- **Streaming.** We need the whole translated segment before handing it
  back to BabelDOC; streaming adds complexity with no throughput gain.
