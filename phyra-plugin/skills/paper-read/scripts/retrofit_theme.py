"""
retrofit_theme.py — apply the paper-read light/dark theme kit to
already-generated HTML files in place.

The current build_analysis_html.py / build_slide.py already inject the
theme on fresh runs. This CLI is for HTML produced *before* that change:
it splices the same theme kit into existing files via the idempotent
theme_kit.inject(). Purely additive (only inserts at </head>, <body>,
</body>; never rewrites existing bytes); safe to re-run.

Usage:
  uv run python retrofit_theme.py <dir-or-glob> [<dir-or-glob> ...]
                                  [--pattern GLOB] [--dry-run]

Defaults: for each DIR argument, processes
  <dir>/**/*_analysis.*.html  and  <dir>/**/*_draftslide.html
Pass explicit globs (or --pattern) to override. --dry-run reports what
would change without writing.
"""

import argparse
import glob
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme_kit import inject  # noqa: E402

DEFAULT_PATTERNS = ("**/*_analysis.*.html", "**/*_draftslide.html")


def collect(arg: str, patterns: tuple[str, ...]) -> list[str]:
    """An arg may be a directory (expanded with patterns) or a glob/file."""
    if os.path.isdir(arg):
        out: list[str] = []
        for pat in patterns:
            out += glob.glob(os.path.join(arg, pat), recursive=True)
        return out
    return glob.glob(arg, recursive=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+", help="directories and/or globs")
    ap.add_argument("--pattern", action="append", default=None,
                    help="override the per-directory glob(s); repeatable")
    ap.add_argument("--dry-run", action="store_true",
                    help="report only; do not write")
    args = ap.parse_args()

    patterns = tuple(args.pattern) if args.pattern else DEFAULT_PATTERNS

    files: list[str] = []
    for t in args.targets:
        files += collect(t, patterns)
    files = sorted(set(os.path.abspath(f) for f in files))

    if not files:
        print("no matching files")
        return 1

    modified = skipped = errors = 0
    for fp in files:
        try:
            src = Path(fp).read_text(encoding="utf-8")
            out = inject(src)
            if out == src:
                skipped += 1               # already themed (idempotent)
            elif args.dry_run:
                modified += 1
            else:
                Path(fp).write_text(out, encoding="utf-8")
                modified += 1
        except Exception as e:             # noqa: BLE001
            errors += 1
            print(f"  ERR {fp}: {e!r}")

    verb = "would modify" if args.dry_run else "modified"
    print(f"total={len(files)}  {verb}={modified}  "
          f"skipped(already-themed)={skipped}  errors={errors}")
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
