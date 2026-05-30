"""
Preflight checks (structured + CLI).

Returns a list of check results so the WebUI can render ✓/✗ + hints; also
runnable as `python -m phyra_dualtrans.pipeline.preflight ...` (keeps
stderr output + exit code for scripts).

Always checked:  uv, babeldoc (0.5.x), SourceHan Serif font for lang_out.
Per backend:     claude_cli → `claude` on PATH;
                 openai     → base_url + api_key present;
                 ollama     → <host>/api/tags reachable.
Conditional:     gs only when compress == lossy.

(The upstream ${CLAUDE_PLUGIN_ROOT} check is intentionally dropped — this
is a standalone app, not a Claude Code plugin.)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Ported VERBATIM from upstream preflight.py LANG_FONT_MAP.
LANG_FONT_MAP = {
    "zh-TW": "SourceHanSerifTW-Regular.ttf",
    "zh-HK": "SourceHanSerifHK-Regular.ttf",
    "zh-CN": "SourceHanSerifCN-Regular.ttf",
    "ja": "SourceHanSerifJP-Regular.ttf",
    "ko": "SourceHanSerifKR-Regular.ttf",
    "en": "SourceHanSerifTW-Regular.ttf",
}


def _check(name: str, ok: bool, detail: str = "", hint: str = "") -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail, "hint": hint}


def _bin(name: str, hint: str, version_args: list[str] | None = None) -> dict:
    p = shutil.which(name)
    if not p:
        return _check(name, False, f"`{name}` not found in PATH", hint)
    if version_args is None:
        return _check(name, True, p)
    try:
        res = subprocess.run(
            [p, *version_args], capture_output=True, text=True, timeout=15
        )
        if res.returncode != 0:
            return _check(name, False,
                          f"`{name} {' '.join(version_args)}` rc="
                          f"{res.returncode}", hint)
        ver = (res.stdout or res.stderr).strip().splitlines()
        return _check(name, True, f"{p}  ({ver[0] if ver else '?'})")
    except Exception as e:  # noqa: BLE001
        return _check(name, False, f"failed to invoke `{name}`: {e}", hint)


def _check_babeldoc() -> dict:
    r = _bin(
        "babeldoc",
        "Install: uv tool install babeldoc==0.5.24 ; then `babeldoc --warmup`",
        ["--version"],
    )
    if r["ok"] and "0.5." not in r["detail"]:
        r["ok"] = False
        r["detail"] += "  — expected the 0.5.x line"
        r["hint"] = "uv tool install babeldoc==0.5.24"
    return r


def _check_font(lang_out: str) -> dict:
    fname = LANG_FONT_MAP.get(lang_out)
    if not fname:
        return _check(
            f"font:{lang_out}", False,
            f"no mapped font for lang_out={lang_out}",
            "supported: " + ", ".join(LANG_FONT_MAP),
        )
    fpath = Path.home() / ".cache/babeldoc/fonts" / fname
    if not fpath.exists():
        return _check(
            f"font:{lang_out}", False, f"missing: {fpath}",
            "run `babeldoc --warmup` (one-time, ~340MB) or scripts/warmup.sh",
        )
    return _check(f"font:{lang_out}", True, fpath.name)


def _check_backend(backend: str, base_url: str | None,
                   has_api_key: bool) -> list[dict]:
    if backend == "claude_cli":
        return [_bin(
            "claude",
            "Install Claude Code and ensure `claude` is on PATH "
            "(needed for the claude_cli backend; no API key required).",
            ["--version"],
        )]
    if backend == "openai":
        out = [_check(
            "openai:base_url", bool(base_url),
            base_url or "(unset)",
            "set the OpenAI-compatible base_url (e.g. https://api.openai.com/v1)",
        )]
        out.append(_check(
            "openai:api_key", has_api_key,
            "present" if has_api_key else "(unset)",
            "set an API key in Settings or OPENAI_API_KEY",
        ))
        return out
    if backend == "ollama":
        from ..backends.ollama import list_models

        info = list_models(base_url)
        return [_check(
            "ollama:reachable", info["available"],
            f"{info['host']} — {len(info['models'])} model(s)"
            if info["available"] else info.get("reason", "unreachable"),
            "start Ollama (`ollama serve`) or set the correct host",
        )]
    return [_check(f"backend:{backend}", False, "unknown backend")]


def run_preflight(
    *,
    backend: str = "claude_cli",
    lang_out: str = "zh-TW",
    compress: str = "lossy",
    base_url: str | None = None,
    has_api_key: bool = False,
) -> dict:
    checks: list[dict] = [
        _bin("uv", "Install: curl -LsSf https://astral.sh/uv/install.sh | sh",
             ["--version"]),
        _check_babeldoc(),
        _check_font(lang_out),
    ]
    checks += _check_backend(backend, base_url, has_api_key)
    if compress == "lossy":
        checks.append(_bin(
            "gs",
            "Lossy compression needs Ghostscript "
            "(`sudo apt install ghostscript`), or use --compress=lossless.",
            ["--version"],
        ))
    return {"ok": all(c["ok"] for c in checks), "checks": checks}


def main() -> int:
    p = argparse.ArgumentParser(description="phyra-dualtrans preflight")
    p.add_argument("--backend", default="claude_cli",
                   choices=["openai", "ollama", "claude_cli"])
    p.add_argument("--lang-out", default="zh-TW")
    p.add_argument("--compress", default="lossy",
                   choices=["lossy", "lossless", "off"])
    p.add_argument("--base-url", default=None)
    p.add_argument("--has-api-key", action="store_true")
    args = p.parse_args()

    res = run_preflight(
        backend=args.backend,
        lang_out=args.lang_out,
        compress=args.compress,
        base_url=args.base_url,
        has_api_key=args.has_api_key,
    )
    print(f"phyra-dualtrans preflight (backend={args.backend} "
          f"lang_out={args.lang_out} compress={args.compress})",
          file=sys.stderr)
    print("---", file=sys.stderr)
    for c in res["checks"]:
        mark = "✓" if c["ok"] else "✗"
        print(f"  {mark} {c['name']}: {c['detail']}", file=sys.stderr)
        if not c["ok"] and c["hint"]:
            print(f"      → {c['hint']}", file=sys.stderr)
    print("---", file=sys.stderr)
    print("preflight OK" if res["ok"] else "preflight FAILED", file=sys.stderr)
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
