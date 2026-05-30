#!/usr/bin/env python3
"""
Preflight gate for /phyra:paper-read (v0.9.0). Checks that the LLM
backend is reachable. The analyzer + slide-maker have no external binary
dependencies (build_slide.py is pure Python; build_analysis_html.py is
pure Python).

For translation dependencies (BabelDOC, CJK font, Ghostscript), see the
separate `/phyra:paper-translate` command — its own preflight at
`skills/paper-translate/scripts/preflight.py` covers those.

Usage:
  preflight.py [--lang-out zh-TW]

Exits 0 on success. Exits non-zero with copy-paste install hints on failure.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

OK = "✓"
FAIL = "✗"


def report(level: str, msg: str) -> None:
    print(f"  {level} {msg}", file=sys.stderr)


def check_plugin_root() -> bool:
    val = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not val:
        report(FAIL, "${CLAUDE_PLUGIN_ROOT} is not set")
        report(" ", "  → ensure you invoke this via the Phyra plugin "
                   "(skills/paper-read/SKILL.md) rather than running the "
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


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lang-out", default="zh-TW",
                   help="Target language code (informational; analysis can "
                        "be produced in any language without extra deps)")
    p.add_argument("--skip-plugin-root", action="store_true",
                   help="Skip the ${CLAUDE_PLUGIN_ROOT} check (for standalone runs)")
    args = p.parse_args()

    print("Phyra paper-read preflight (v0.9.0)", file=sys.stderr)
    print(f"  lang-out: {args.lang_out}", file=sys.stderr)
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

    if all(checks):
        print("---", file=sys.stderr)
        print("preflight OK", file=sys.stderr)
        return 0
    print("---", file=sys.stderr)
    print("preflight FAILED — fix the items above and retry", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
