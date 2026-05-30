#!/usr/bin/env python3
"""
Preflight gate for /phyra:paper-translate (v0.9.0). Translation has heavier
external dependencies than analysis (BabelDOC, CJK font, optional Ghostscript)
and is its own slash command, so the checks here are unconditional rather
than guarded by flags.

Required:
  - ${CLAUDE_PLUGIN_ROOT} resolves
  - `uv` in PATH
  - `claude` in PATH (CC headless backend)
  - `babeldoc` in PATH (must be 0.5.x line)
  - SourceHan font for the chosen --lang-out present in
    ~/.cache/babeldoc/fonts/

Conditionally required:
  - `gs` (Ghostscript) when --compress=lossy

Usage:
  preflight.py [--lang-out zh-TW] [--compress lossy|lossless|off]

Exits 0 on success. Exits non-zero with copy-paste install hints on failure.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

LANG_FONT_MAP = {
    "zh-TW": "SourceHanSerifTW-Regular.ttf",
    "zh-HK": "SourceHanSerifHK-Regular.ttf",
    "zh-CN": "SourceHanSerifCN-Regular.ttf",
    "ja":    "SourceHanSerifJP-Regular.ttf",
    "ko":    "SourceHanSerifKR-Regular.ttf",
    "en":    "SourceHanSerifTW-Regular.ttf",
}

OK = "✓"
FAIL = "✗"


def report(level: str, msg: str) -> None:
    print(f"  {level} {msg}", file=sys.stderr)


def check_plugin_root() -> bool:
    val = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not val:
        report(FAIL, "${CLAUDE_PLUGIN_ROOT} is not set")
        report(" ", "  → ensure you invoke this via the Phyra plugin "
                   "(skills/paper-translate/SKILL.md) rather than running the "
                   "script standalone")
        return False
    if not Path(val).exists():
        report(FAIL, f"${{CLAUDE_PLUGIN_ROOT}} points to non-existent path: {val}")
        return False
    report(OK, f"${{CLAUDE_PLUGIN_ROOT}} = {val}")
    return True


def check_bin(name: str, hint_lines: list[str],
              version_args: list[str] | None = None) -> bool:
    p = shutil.which(name)
    if not p:
        report(FAIL, f"`{name}` not found in PATH")
        for h in hint_lines:
            report(" ", f"  → {h}")
        return False
    if version_args is not None:
        try:
            res = subprocess.run(
                [p, *version_args], capture_output=True, text=True, timeout=15,
            )
            if res.returncode != 0:
                report(FAIL, f"`{name} {' '.join(version_args)}` exited rc={res.returncode}")
                report(" ", f"  stderr: {res.stderr.strip()[:200]}")
                return False
            ver = (res.stdout or res.stderr).strip().splitlines()[0] \
                if (res.stdout or res.stderr) else "?"
            report(OK, f"{name} → {p}  ({ver})")
        except Exception as e:
            report(FAIL, f"failed to invoke `{name}`: {e}")
            return False
    else:
        report(OK, f"{name} → {p}")
    return True


def check_font(lang_out: str) -> bool:
    fname = LANG_FONT_MAP.get(lang_out)
    if not fname:
        report(FAIL, f"--lang-out={lang_out} has no mapped font in LANG_FONT_MAP")
        report(" ", "  → supported codes: " + ", ".join(LANG_FONT_MAP))
        return False
    fpath = Path.home() / ".cache/babeldoc/fonts" / fname
    if not fpath.exists():
        report(FAIL, f"font missing for lang_out={lang_out}: {fpath}")
        report(" ", "  → run `babeldoc --warmup` to download font assets "
                   "(one-time, ~340MB)")
        return False
    report(OK, f"font for {lang_out}: {fpath.name}")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lang-out", default="zh-TW")
    p.add_argument("--compress", default="lossy",
                   choices=["lossy", "lossless", "off"],
                   help="PDF compression mode (lossy needs Ghostscript)")
    p.add_argument("--skip-plugin-root", action="store_true",
                   help="Skip the ${CLAUDE_PLUGIN_ROOT} check (for standalone runs)")
    args = p.parse_args()

    print("Phyra paper-translate preflight (v0.9.0)", file=sys.stderr)
    print(f"  lang-out: {args.lang_out}  compress: {args.compress}",
          file=sys.stderr)
    print("---", file=sys.stderr)

    checks = []
    if not args.skip_plugin_root:
        checks.append(check_plugin_root())
    checks.append(check_bin("uv", [
        "Install: curl -LsSf https://astral.sh/uv/install.sh | sh",
    ], ["--version"]))
    checks.append(check_bin("claude", [
        "Install: https://docs.anthropic.com/en/docs/claude-code/quickstart",
        "You appear to be running inside Claude Code already — that's fine,",
        "but `claude` must also be on PATH for headless subprocess calls.",
    ], ["--version"]))
    checks.append(check_bin("babeldoc", [
        "Install: uv tool install babeldoc==0.5.24",
        "Then run `babeldoc --warmup` once to download models + fonts (~340MB).",
    ], ["--version"]))
    checks.append(check_font(args.lang_out))
    if args.compress == "lossy":
        checks.append(check_bin("gs", [
            "Lossy PDF compression needs Ghostscript.",
            "Install: sudo apt install ghostscript   (Ubuntu/Debian)",
            "         brew install ghostscript        (macOS)",
            "Or pass --compress=lossless to skip this dependency.",
        ], ["--version"]))

    if all(checks):
        print("---", file=sys.stderr)
        print("preflight OK", file=sys.stderr)
        return 0
    print("---", file=sys.stderr)
    print("preflight FAILED — fix the items above and retry", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
