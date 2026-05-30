# phyra-model-service

Shared model layer for the Phyra service suite. One place that owns how
Phyra talks to local/remote models, so every service — and any future
plugin — reuses it instead of re-implementing it.

It is **both**:

- a **Python library** you import in-process (no HTTP hop on the hot path):
  - `phyra_model_service.backends` — pluggable LLM backends
    (`ollama` native `/api/chat` with thinking off · `openai`-compatible ·
    `claude_cli` headless), a registry, and `get_backend(cfg)`.
  - `phyra_model_service.managed.ManagedOllama` — spawn / supervise / tear
    down a dedicated Ollama on a loopback port (default `:11500`), pull +
    build the tuned model, reuse an already-running instance instead of
    double-spawning.
  - `phyra_model_service.runtime.collect()` — GPU (`nvidia-smi`) + VRAM
    placement (`/api/ps`) snapshot that catches the silent CPU-fallback.
  - `phyra_model_service.settings.ModelSettings` — the **single source of
    truth** for Ollama defaults (port, model, idle-unload window, …).

- a **standalone control-plane service** (`phyra_model_service.service.app`)
  that keeps one shared, consistently-configured managed Ollama up and
  answers status queries:
  - `GET /healthz`
  - `GET /api/ollama` — managed-Ollama status
  - `GET /api/models` — installed models
  - `GET /api/runtime` — GPU + VRAM-placement snapshot

## Why a shared service

Only phyra-dualtrans uses a model today (Ollama / Claude headless). Pulling
that into its own service means:

1. **One Ollama, one config.** A single managed instance with one idle-unload
   window — VRAM frees consistently (`keep_alive` rides every chat call and
   resets while a job runs; ~10 s after the last call Ollama unloads).
2. **Reuse.** A future plugin points its `ollama` backend at `:11500` (or
   imports this package) and inherits the same behaviour for free.
3. **Clear boundary.** The model layer no longer lives inside a translation
   service.

When run under phyra-center, the model-service starts first and brings up
Ollama; phyra-dualtrans then detects the running instance and reuses it
(never double-spawns, never kills it on its own shutdown). Run standalone,
phyra-dualtrans still spawns its own via the same shared code.

## Run

```bash
./scripts/start.sh            # control plane on :8041, managed Ollama on :11500
```

## Settings (env / .env)

Canonical `PHYRA_MODEL_*` names, with the legacy `PHYRA_DUALTRANS_OLLAMA_*`
/ `OLLAMA_HOST` names still accepted so existing setups keep working:

| Env | Default | Meaning |
|---|---|---|
| `PHYRA_MODEL_SERVICE_PORT` | `8041` | control-plane HTTP port |
| `PHYRA_MODEL_MANAGE_OLLAMA` | `1` | manage a dedicated Ollama (0 = use your own) |
| `PHYRA_MODEL_OLLAMA_PORT` | `11500` | managed Ollama loopback port |
| `PHYRA_MODEL_OLLAMA_HOST` | `http://localhost:11434` | fallback host when unmanaged |
| `PHYRA_MODEL_OLLAMA_MODEL` | `phyra-trans` | tuned model the UI defaults to |
| `PHYRA_MODEL_OLLAMA_BASE_MODEL` | `qwen3:14b` | base the tuned model is built from |
| `PHYRA_MODEL_OLLAMA_NUM_PARALLEL` | `2` | Ollama concurrency |
| `PHYRA_MODEL_OLLAMA_KEEP_ALIVE` | `10s` | idle window before VRAM is freed |
| `PHYRA_MODEL_OLLAMA_MODELS_DIR` | — | override `OLLAMA_MODELS` |
