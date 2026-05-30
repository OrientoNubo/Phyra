"""
build_analysis_html.py (v0.8.1) — render analysis.<lang>.md to a clean
viewer HTML so the user can read the analysis in a browser (and print
to PDF if desired) without needing a Markdown viewer.

Output: a single self-contained HTML file (no external deps except KaTeX
CDN for math). Layout = continuous scroll, Phyra's slide colour theme
applied at lower contrast, full-width cards per top-level section.

Usage:
  uv run python build_analysis_html.py \\
      <analysis.md> <BIBLIO.json> <out.html> [--lang-out zh-TW]
"""

import argparse
import html
import json
import logging
import re
import sys
import textwrap
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_utils import md_to_html as _md_to_html  # noqa: E402
from theme_kit import inject as inject_theme  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build-analysis-html")


# Use the shared converter with anchor IDs enabled (analysis HTML has an
# in-page TOC pointing at heading anchors).
md_to_html = partial(_md_to_html, include_anchor_ids=True)


# ---------------------------------------------------------------------------
# Build TOC from H2 / H3 headings of the analysis MD
# ---------------------------------------------------------------------------

def build_toc(md: str) -> str:
    items: list[tuple[int, str, str]] = []  # (level, text, anchor)
    for line in md.split("\n"):
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if not m:
            continue
        lvl = len(m.group(1))
        text = m.group(2).strip()
        anchor = re.sub(r"[^\w一-鿿]+", "-", text.lower()).strip("-")
        items.append((lvl, text, anchor))
    if not items:
        return ""
    parts = ["<nav class=\"toc\"><h3>目錄 / Table of Contents</h3><ul>"]
    for lvl, text, anchor in items:
        cls = "toc-l2" if lvl == 2 else "toc-l3"
        parts.append(
            f"<li class=\"{cls}\"><a href=\"#{anchor}\">{html.escape(text)}</a></li>"
        )
    parts.append("</ul></nav>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CSS / page assembly
# ---------------------------------------------------------------------------

CSS = r"""
:root {
  --p-primary: #DDE5C8;
  --p-light: #F1F5E5;
  --p-accent: #7B9750;
  --p-dark: #3E5424;
  --p-text: #1C1C1C;
  --p-bg-card: #FFFFFF;
  --p-formula-bg: rgba(0,0,0,0.03);
  --p-border: rgba(0,0,0,0.10);
  --p-bold-highlight: rgba(123,151,80,0.18);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; font-family:
  "Noto Sans TC", "Source Han Sans", "PingFang TC", "Microsoft JhengHei", sans-serif;
  font-size: 16px; line-height: 1.7; color: var(--p-text);
  background: linear-gradient(180deg, var(--p-light) 0%, var(--p-primary) 100%);
  background-attachment: fixed; min-height: 100vh; }
.layout { display: grid; grid-template-columns: 240px 1fr; gap: 32px;
          max-width: 1200px; margin: 0 auto; padding: 32px 24px 80px 24px; }
.toc { position: sticky; top: 24px; align-self: start; max-height: calc(100vh - 48px);
       overflow: auto; padding: 16px; background: var(--p-bg-card);
       border: 1px solid var(--p-border); border-radius: 8px; font-size: 0.9rem; }
.toc h3 { margin: 0 0 12px 0; color: var(--p-dark); font-size: 1rem;
          border-bottom: 2px solid var(--p-accent); padding-bottom: 6px; }
.toc ul { list-style: none; padding: 0; margin: 0; }
.toc li { margin: 4px 0; }
.toc-l2 { font-weight: 600; }
.toc-l3 { padding-left: 12px; font-size: 0.85rem; }
.toc a { color: var(--p-text); text-decoration: none; }
.toc a:hover { color: var(--p-accent); }
main { background: var(--p-bg-card); border: 1px solid var(--p-border);
       border-radius: 8px; padding: 40px 48px; }
h1 { font-size: 1.9rem; margin: 0 0 24px 0; color: var(--p-dark);
     border-bottom: 3px solid var(--p-accent); padding-bottom: 12px; }
h2 { font-size: 1.4rem; margin: 36px 0 16px 0; color: var(--p-dark);
     border-bottom: 2px solid var(--p-accent); padding-bottom: 6px; }
h3 { font-size: 1.15rem; margin: 24px 0 10px 0; color: var(--p-dark); }
h4 { font-size: 1.05rem; margin: 20px 0 8px 0; color: var(--p-dark); }
p { margin: 8px 0 14px 0; }
strong { background: var(--p-bold-highlight); padding: 1px 4px; border-radius: 3px;
         font-weight: 700; }
code { background: rgba(0,0,0,0.05); padding: 1px 6px; border-radius: 4px;
       font-family: "JetBrains Mono", "Fira Code", "SF Mono", monospace;
       font-size: 0.92em; }
pre.codeblock { background: rgba(0,0,0,0.04); border: 1px solid var(--p-border);
                border-radius: 6px; padding: 14px 18px; overflow-x: auto;
                font-family: "JetBrains Mono", "Fira Code", "SF Mono", monospace;
                font-size: 0.85rem; line-height: 1.55; white-space: pre; }
table { width: 100%; border-collapse: collapse; margin: 16px 0;
        font-size: 0.95rem; }
th { background: var(--p-accent); color: #FFF; padding: 10px 12px; text-align: left; }
td { padding: 8px 12px; border-bottom: 1px solid var(--p-border); }
tr:hover td { background: rgba(0,0,0,0.03); }
ul, ol { margin: 8px 0 14px 24px; padding: 0; }
li { margin: 4px 0; }
.katex-display { background: var(--p-formula-bg); border: 1px solid var(--p-border);
                 border-radius: 6px; padding: 8px 12px; margin: 12px 0; }
@media print {
  body { background: #FFF; }
  .layout { display: block; max-width: 100%; padding: 0; }
  .toc { display: none; }
  main { box-shadow: none; border: 0; padding: 0; }
}
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .toc { position: static; max-height: none; }
}
"""


def render_page(*, md: str, biblio: dict, lang_out: str) -> str:
    bi = biblio.get("basic_info", {}) or {}
    short = bi.get("short_name") or ""
    full = bi.get("full_title") or ""
    page_title = f"{short} — {full}" if short and full else (full or short or "Phyra Analysis")
    head_lang = "zh-Hant" if lang_out.startswith("zh") else lang_out

    toc = build_toc(md)
    body = md_to_html(md)

    page = textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="{head_lang}">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{html.escape(page_title)}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
        <style>{CSS}</style>
        </head>
        <body>
        <div class="layout">
        {toc}
        <main>
        {body}
        </main>
        </div>
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
          onload="renderMathInElement(document.body, {{
            delimiters: [
              {{left: '$$', right: '$$', display: true}},
              {{left: '$', right: '$', display: false}}
            ]
          }});">
        </script>
        </body>
        </html>
        """)
    return inject_theme(page)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("analysis_md")
    p.add_argument("biblio_json")
    p.add_argument("out_html")
    p.add_argument("--lang-out", default="zh-TW")
    args = p.parse_args()

    md = Path(args.analysis_md).read_text(encoding="utf-8")
    # Drop the leading HTML comment header and re-print plain front-matter
    biblio = json.loads(Path(args.biblio_json).read_text(encoding="utf-8"))

    text = render_page(md=md, biblio=biblio, lang_out=args.lang_out)

    out = Path(args.out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    log.info("wrote %s (%.1f KB)", out, out.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    sys.exit(main())
