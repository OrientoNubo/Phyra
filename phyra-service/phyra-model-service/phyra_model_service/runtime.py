"""
Runtime / hardware status.

The slow-translation footgun in practice is silent: an NVIDIA driver can
crash (or never load) so `nvidia-smi` stops talking to it, and Ollama then
quietly loads the model into RAM and runs it on the CPU — same output,
~10× slower, no error anywhere. This module surfaces that by combining two
cheap, best-effort probes:

  • `nvidia-smi` — is a GPU + working driver visible at all?
  • Ollama `/api/ps` — is the running model resident in VRAM (`size_vram`)
    or has it fallen back to CPU (`size_vram == 0`)?

Everything degrades gracefully: any probe failure becomes a field in the
returned dict, never an exception. No secrets are read or returned.
"""

from __future__ import annotations

import shutil
import subprocess

import httpx

from .backends.ollama import normalize_host


def _int(s: str) -> int | None:
    try:
        return int(float(s.strip()))
    except (ValueError, AttributeError):
        return None


def probe_nvidia(timeout: float = 4.0) -> dict:
    """Run `nvidia-smi` and report GPU(s) + driver health. `available` is
    False (with a human reason) when the binary is missing or the driver
    is unreachable — the common 'driver crashed' case."""
    exe = shutil.which("nvidia-smi")
    if not exe:
        return {"available": False,
                "reason": "找不到 nvidia-smi（未安裝 NVIDIA 驅動或非 NVIDIA GPU）"}
    try:
        p = subprocess.run(
            [exe, "--query-gpu=name,memory.used,memory.total,"
             "utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"available": False, "reason": f"nvidia-smi 執行失敗：{e}"}
    if p.returncode != 0:
        # e.g. "NVIDIA-SMI has failed because it couldn't communicate with
        # the NVIDIA driver." → driver crashed / not loaded.
        msg = (p.stderr or p.stdout or "").strip().splitlines()
        return {"available": False,
                "reason": (msg[0] if msg else f"nvidia-smi rc={p.returncode}")}
    gpus: list[dict] = []
    for line in p.stdout.strip().splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 4:
            continue
        gpus.append({
            "name": parts[0],
            "mem_used_mb": _int(parts[1]),
            "mem_total_mb": _int(parts[2]),
            "util_pct": _int(parts[3]),
        })
    if not gpus:
        return {"available": False, "reason": "nvidia-smi 未回報任何 GPU"}
    return {"available": True, "gpus": gpus}


def _placement(size: int, vram: int) -> str:
    if not size:
        return "unknown"
    if vram <= 0:
        return "cpu"
    if vram >= size:
        return "gpu"
    return "partial"


def probe_ollama_ps(host: str | None, timeout: float = 3.0) -> dict:
    """Query Ollama `/api/ps` (currently-loaded models). Each model's
    `size_vram` vs `size` tells us whether it sits in GPU or fell back to
    CPU."""
    base = normalize_host(host)
    try:
        r = httpx.get(base + "/api/ps", timeout=timeout)
        r.raise_for_status()
        models = r.json().get("models", [])
    except Exception as e:  # noqa: BLE001 — degrade, never raise
        return {"reachable": False, "host": base, "reason": str(e)[:160]}
    out: list[dict] = []
    for m in models:
        size = int(m.get("size") or 0)
        vram = int(m.get("size_vram") or 0)
        out.append({
            "name": m.get("name") or m.get("model") or "?",
            "size": size,
            "size_vram": vram,
            "placement": _placement(size, vram),
            "vram_fraction": round(vram / size, 3) if size else 0,
        })
    return {"reachable": True, "host": base, "models": out}


def _worst_placement(models: list[dict]) -> str | None:
    """The least-GPU placement among loaded models (cpu < partial < gpu).
    None when nothing is loaded."""
    if not models:
        return None
    order = {"cpu": 0, "partial": 1, "unknown": 2, "gpu": 3}
    return min((m["placement"] for m in models),
               key=lambda p: order.get(p, 2))


def collect(host: str | None = None) -> dict:
    """Full runtime snapshot + a zh-TW one-line `summary`, a `detail`
    (tooltip) string, and a `level` (ok|warn|error) the UI colours by."""
    gpu = probe_nvidia()
    olm = probe_ollama_ps(host)
    gpu_ok = bool(gpu.get("available"))

    placement = _worst_placement(olm.get("models", [])) \
        if olm.get("reachable") else None

    # ---- verdict ----
    if placement == "cpu":
        level = "error"
        summary = "⚠ 模型跑在 CPU — 翻譯會非常慢"
    elif placement == "partial":
        level = "warn"
        summary = "部分在 GPU、部分在 CPU"
    elif placement == "gpu":
        level = "ok"
        summary = "GPU 運算中"
    elif olm.get("reachable"):  # reachable but no model loaded yet
        if gpu_ok:
            level = "ok"
            summary = "GPU 可用（模型尚未載入）"
        else:
            level = "error"
            summary = "偵測不到 GPU — 載入後將以 CPU 運算"
    else:  # ollama not reachable
        if gpu_ok:
            level = "warn"
            summary = "GPU 可用，但 Ollama 尚未連線"
        else:
            level = "error"
            summary = "偵測不到 GPU，且 Ollama 尚未連線"

    # ---- detail (multi-line tooltip) ----
    lines: list[str] = []
    if gpu_ok:
        for g in gpu["gpus"]:
            used, total = g.get("mem_used_mb"), g.get("mem_total_mb")
            mem = f"{used}/{total} MiB" if used is not None and total else "?"
            lines.append(
                f"GPU：{g['name']} · 顯存 {mem} · 使用率 {g.get('util_pct')}%")
    else:
        lines.append(f"GPU：✗ {gpu.get('reason', '不可用')}")
    if olm.get("reachable"):
        if olm["models"]:
            label = {"gpu": "GPU", "cpu": "CPU", "partial": "GPU+CPU",
                     "unknown": "?"}
            for m in olm["models"]:
                lines.append(
                    f"模型 {m['name']}：{label.get(m['placement'], '?')}"
                    f"（VRAM {int(m['vram_fraction'] * 100)}%）")
        else:
            lines.append(f"Ollama：已連線（{olm['host']}），尚無載入中的模型")
    else:
        lines.append(f"Ollama：✗ 無法連線 {olm.get('host', '')}"
                     f"（{olm.get('reason', '')}）")

    return {
        "level": level,
        "summary": summary,
        "detail": "\n".join(lines),
        "gpu": gpu,
        "ollama": olm,
    }
