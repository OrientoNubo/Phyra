"""
build_slide.py (v0.8.0) — assemble a single self-contained HTML slide deck
from analysis.<lang>.md + extracted figures + BIBLIO.json.

The slide deck:
  - Single HTML file with all CSS / JS inlined and PNGs embedded as
    base64 (no external deps except optional KaTeX CDN for math).
  - Fixed viewport-sized slides; keyboard ←/→/Space switches.
  - Bottom bar shows progress + slide index + theme switcher.
  - Slides are grouped from the analysis Markdown:
      Cover, Overview, Paper Structure,
      Introduction, Problem Definition, Related Work,
      Method Overview + main pipeline figure,
      Method Module 1..N (one slide each, capped at ~6),
      Experiments — Settings, Main Results, Ablations,
      Limitations & Open Questions, Conclusion.

Usage:
  uv run --with pymupdf python build_slide.py \\
      <analysis.md> <BIBLIO.json> <figures_dir> <out.html> \\
      [--lang-out zh-TW]
"""

import argparse
import base64
import html
import json
import logging
import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_utils import md_to_html  # noqa: E402
from theme_kit import inject as inject_theme  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build-slide")

MAX_METHOD_MODULE_SLIDES = 6


# Markdown → HTML conversion is delegated to md_utils.md_to_html (no
# anchor IDs needed for slide content).


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------

def split_top_level(md: str) -> dict[str, str]:
    """Split analysis Markdown by top-level `## N. Title` headings.

    Returns dict keyed by heading text (e.g. "## 1. Basic Information") to
    body text (everything from the heading line through the next `## ...`
    heading exclusive)."""
    out: dict[str, str] = {}
    matches = list(re.finditer(r"^## .*$", md, re.MULTILINE))
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(md)
        key = m.group(0).strip()
        out[key] = md[m.start():end]
    return out


def extract_subsection(section: str, sub_heading_prefix: str) -> str:
    """Extract one ### subsection by its `### N.M Title` prefix."""
    rx = re.compile(rf"^### {re.escape(sub_heading_prefix)}.*$", re.MULTILINE)
    m = rx.search(section)
    if not m:
        return ""
    rest = section[m.end():]
    next_h = re.search(r"^### ", rest, re.MULTILINE)
    if next_h:
        return rest[:next_h.start()].strip()
    next_h2 = re.search(r"^## ", rest, re.MULTILINE)
    if next_h2:
        return rest[:next_h2.start()].strip()
    return rest.strip()


def extract_section3_outline(s3: str) -> str:
    """Build a roadmap from §3's subsection headings only (no body text).

    The "Paper Structure" slide used to render the entire §3 via
    md_to_html(s3). But §3.2 / §3.3 / §3.6 are *also* carried by their own
    dedicated slides (Introduction / Related Work / Conclusion), so dumping
    the whole walkthrough made that text appear twice in the deck and made
    "Paper Structure" an over-long wall of text. Here we keep it as a pure
    map: the ordered list of `### 3.x <title>` headings only."""
    items = [
        html.escape(m.group(1).strip())
        for m in re.finditer(r"^### (3\.\d+\s+.*)$", s3, re.MULTILINE)
    ]
    if not items:
        return ""
    lis = "\n".join(f"<li>{it}</li>" for it in items)
    return f'<div class="card"><ul class="toc">{lis}</ul></div>'


def extract_method_modules(method_section: str) -> list[tuple[str, str]]:
    """Split §5.3 into per-module chunks: returns [(module title, body), ...]."""
    rx_53 = re.compile(r"^### 5\.3 .*$", re.MULTILINE)
    m = rx_53.search(method_section)
    if not m:
        return []
    body = method_section[m.end():]
    end = re.search(r"^## ", body, re.MULTILINE)
    if end:
        body = body[:end.start()]
    parts: list[tuple[str, str]] = []
    for sub in re.finditer(r"^#### 5\.3\.\d+\s+.*$", body, re.MULTILINE):
        head = sub.group(0).strip()
        s = sub.end()
        next_sub = re.search(r"^#### 5\.3\.\d+\s", body[s:], re.MULTILINE)
        e = (s + next_sub.start()) if next_sub else len(body)
        parts.append((head.lstrip("# ").strip(), body[s:e].strip()))
    return parts[:MAX_METHOD_MODULE_SLIDES]


# ---------------------------------------------------------------------------
# Slide deck builder
# ---------------------------------------------------------------------------

def img_b64(path: Path) -> str:
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("ascii")


_RX_WC_LEAD = re.compile(r"^\s*\((?:約\s*)?\d{2,5}\s*words?\)\s*$",
                         re.MULTILINE)


def _wrap_walkthrough_paragraphs(md_section: str) -> str:
    """Walkthrough sections (§3.2 Introduction, §3.3 Related, §3.6 Conclusion)
    are typically one big paragraph from the LLM. For the slide deck we want
    structure: split into paragraphs and render each as its own card so the
    eye has anchors. The leading `(N words)` line is shown as a small
    annotation, not as a card.
    """
    # Pull off the optional leading "(N words)" line as annotation
    word_count = ""
    m = _RX_WC_LEAD.search(md_section)
    if m:
        word_count = m.group(0).strip()
        md_section = md_section.replace(m.group(0), "", 1).lstrip()

    # Split on blank-line paragraph boundaries first
    parts = [p.strip() for p in re.split(r"\n\s*\n", md_section) if p.strip()]
    # If the LLM emitted ONE paragraph, soft-split on Chinese / English
    # sentence boundaries so the slide doesn't show a wall of text.
    if len(parts) == 1 and len(parts[0]) > 700:
        text = parts[0]
        sents = re.split(r"(?<=[。；])\s+(?=\S)", text)
        # Group sentences into 3-sentence chunks ≈ paragraphs
        parts = []
        for i in range(0, len(sents), 3):
            parts.append(" ".join(sents[i:i + 3]).strip())
        parts = [p for p in parts if p]

    cards = "\n".join(f"<div class=\"card\">{md_to_html(p)}</div>" for p in parts)
    if word_count:
        cards = (
            f"<p class=\"section-meta\">{html.escape(word_count)}</p>\n"
            + cards
        )
    return cards


def build_slides(*, analysis_md: str, biblio: dict, figures_dir: Path,
                 lang_out: str) -> list[tuple[str, str]]:
    """Return list of (slide_title, slide_body_html) tuples."""
    sections = split_top_level(analysis_md)

    bi = biblio.get("basic_info", {}) or {}
    short = bi.get("short_name") or ""
    full = bi.get("full_title") or ""
    arxiv = bi.get("arxiv_id") or ""
    venue = bi.get("venue") or ""
    release = bi.get("release_date") or ""
    authors_brief = bi.get("authors_brief") or ""

    # v0.8.1: drop main_pipeline_figure embed entirely. Per user feedback,
    # rasterized whole-page PNGs were a poor substitute for cropped figures
    # and just made slides look like "a PDF page glued in". Future work:
    # crop actual figure regions; until then, render no images.
    _ = figures_dir  # no longer used here

    slides: list[tuple[str, str]] = []

    # 1 Cover
    research_topic = ""
    s2 = sections.get("## 2. Research Overview", "")
    research_topic = extract_subsection(s2, "2.1") or ""
    research_topic_html = md_to_html(research_topic)
    slides.append((
        "Cover",
        f"""
        <div class="cover-block">
          <h1 class="cover-title">{html.escape(full or short)}</h1>
          <p class="cover-meta">{html.escape(authors_brief)}</p>
          <p class="cover-meta">{html.escape(arxiv)} · {html.escape(venue)} · {html.escape(release)}</p>
          <div class="cover-tagline">{research_topic_html}</div>
        </div>
        """,
    ))

    # 2 Overview (problem / method / contributions)
    core_arg = extract_subsection(s2, "2.4")
    s4 = sections.get("## 4. Critical Profile", "")
    highlights = extract_subsection(s4, "4.1")
    slides.append((
        "Overview",
        f"""
        <div class="grid-3">
          <div class="card"><h3>Research Topic</h3>{md_to_html(research_topic)}</div>
          <div class="card"><h3>Core Argument</h3>{md_to_html(core_arg)}</div>
          <div class="card"><h3>Highlights</h3>{md_to_html(highlights)}</div>
        </div>
        """,
    ))

    # 3 Paper Structure — roadmap only (subsection headings of §3). The
    # actual §3.2 / §3.3 / §3.6 prose is carried by the dedicated
    # Introduction / Related Work / Conclusion slides below; dumping the
    # whole §3 here duplicated it.
    s3 = sections.get("## 3. Section Walkthrough", "")
    if s3:
        outline = extract_section3_outline(s3)
        if outline:
            slides.append(("Paper Structure", outline))

    # 4 Introduction
    intro = extract_subsection(s3, "3.2")
    if intro:
        slides.append(("Introduction", _wrap_walkthrough_paragraphs(intro)))

    # 5 Related Work
    related = extract_subsection(s3, "3.3")
    if related:
        slides.append(("Related Work", _wrap_walkthrough_paragraphs(related)))

    # 6 Method — Overview (narrative + tensor-shape pipeline)
    s5 = sections.get("## 5. Methodology Deep Dive", "")
    method_overview = extract_subsection(s5, "5.1")
    pipeline_diagram = extract_subsection(s5, "5.2")
    slides.append((
        "Method — Overview",
        f"""
        <div class="grid-2">
          <div class="card"><h3>Narrative</h3>{md_to_html(method_overview)}</div>
          <div class="card"><h3>Pipeline (tensor shapes)</h3>{md_to_html(pipeline_diagram)}</div>
        </div>
        """,
    ))

    # 7..N Method modules
    for mod_title, mod_body in extract_method_modules(s5):
        slides.append((
            f"Method — {html.escape(mod_title)}",
            f"<div class=\"card\">{md_to_html(mod_body)}</div>",
        ))

    # Experiments
    s6 = sections.get("## 6. Experiments", "")
    if s6:
        ds = extract_subsection(s6, "6.1")
        metrics = extract_subsection(s6, "6.2")
        settings = extract_subsection(s6, "6.3")
        slides.append((
            "Experiments — Setup",
            f"""
            <div class="grid-3">
              <div class="card"><h3>Datasets</h3>{md_to_html(ds)}</div>
              <div class="card"><h3>Metrics</h3>{md_to_html(metrics)}</div>
              <div class="card"><h3>Settings</h3>{md_to_html(settings)}</div>
            </div>
            """,
        ))
        results = extract_subsection(s6, "6.4")
        slides.append(("Experiments — Main Results",
                       f"<div class=\"card\">{md_to_html(results)}</div>"))
        ablations = extract_subsection(s6, "6.5")
        assess = extract_subsection(s6, "6.6")
        slides.append((
            "Experiments — Ablations & Assessment",
            f"""
            <div class="grid-2">
              <div class="card"><h3>Ablations</h3>{md_to_html(ablations)}</div>
              <div class="card"><h3>Phyra Assessment</h3>{md_to_html(assess)}</div>
            </div>
            """,
        ))

    # Critical / Limitations
    weakness = extract_subsection(s4, "4.2")
    if weakness:
        slides.append((
            "Weaknesses",
            f"<div class=\"card\">{md_to_html(weakness)}</div>",
        ))

    # Phyra's Judgment + Open Q
    s7 = sections.get("## 7. Phyra's Judgment", "")
    if s7:
        slides.append((
            "Phyra's Judgment",
            f"<div class=\"card\">{md_to_html(s7)}</div>",
        ))
    s8 = sections.get("## 8. Open Questions and Improvement Ideas", "")
    if s8:
        slides.append((
            "Open Questions",
            f"<div class=\"card\">{md_to_html(s8)}</div>",
        ))

    # Conclusion (closing)
    closing = extract_subsection(s3, "3.6")
    if closing:
        slides.append(("Conclusion", _wrap_walkthrough_paragraphs(closing)))

    log.info("built %d slides", len(slides))
    return slides


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

CSS = r"""
:root {
  --p-primary: #DDE5C8;
  --p-light: #F1F5E5;
  --p-accent: #7B9750;
  --p-dark: #3E5424;
  --p-text: #1C1C1C;
  --p-bg-card: rgba(255,255,255,0.86);
  --p-formula-bg: rgba(255,255,255,0.6);
  --p-border: rgba(0,0,0,0.10);
  --p-bold-highlight: rgba(123,151,80,0.18);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100vh; overflow: hidden; font-family:
  "Noto Sans TC", "Source Han Sans", "PingFang TC", "Microsoft JhengHei", sans-serif;
  font-size: 16px; color: var(--p-text); background: var(--p-light); }
.deck { position: relative; width: 100vw; height: 100vh; overflow: hidden; }
.slide { position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
         padding: 56px 80px 80px 80px; overflow: auto; opacity: 0;
         pointer-events: none; transition: opacity 220ms ease-in-out;
         background: linear-gradient(180deg, var(--p-light) 0%, var(--p-primary) 100%); }
.slide.active { opacity: 1; pointer-events: auto; }
.slide-title { font-size: 1.6rem; font-weight: 600; color: var(--p-dark);
               border-bottom: 2px solid var(--p-accent); padding-bottom: 8px;
               margin: 0 0 24px 0; }
.cover-block { display: flex; flex-direction: column; justify-content: center;
               height: 80vh; }
.cover-title { font-size: 2.6rem; line-height: 1.2; color: var(--p-dark);
               margin: 0 0 24px 0; }
.cover-meta { font-size: 1.05rem; color: var(--p-dark); margin: 4px 0; }
.cover-tagline { margin-top: 32px; font-size: 1.05rem; line-height: 1.6;
                 max-width: 1100px; }
.card { background: var(--p-bg-card); border: 1px solid var(--p-border);
        border-left: 4px solid var(--p-accent); border-radius: 8px;
        padding: 20px 24px; margin: 0 0 16px 0; line-height: 1.6; }
.card h3 { margin: 0 0 12px 0; font-size: 1.1rem; color: var(--p-dark); }
.card p { margin: 0 0 10px 0; }
.card ul, .card ol { margin: 8px 0 8px 24px; padding: 0; }
.card li { margin: 4px 0; }
.toc { list-style: none; margin: 8px 0; padding: 0; }
.toc li { margin: 14px 0; font-size: 1.1rem; color: var(--p-dark);
          padding-left: 16px; border-left: 3px solid var(--p-accent); }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.codeblock { background: rgba(255,255,255,0.7); border: 1px solid var(--p-border);
             border-radius: 6px; padding: 12px 16px; font-family:
             "JetBrains Mono", "Fira Code", "SF Mono", monospace;
             font-size: 0.85rem; line-height: 1.55; overflow-x: auto;
             white-space: pre; }
table { width: 100%; border-collapse: collapse; font-size: 0.92rem; margin: 8px 0; }
th { background: var(--p-accent); color: #FFF; padding: 8px 10px; text-align: left; }
td { padding: 7px 10px; border-bottom: 1px solid var(--p-border); }
tr:hover td { background: rgba(0,0,0,0.04); }
strong { background: var(--p-bold-highlight); padding: 1px 4px; border-radius: 3px;
         font-weight: 700; }
.paper-fig { max-width: 100%; max-height: 60vh; display: block; margin: 8px auto;
             border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 56px;
              display: flex; align-items: center; padding: 0 24px;
              background: rgba(0,0,0,0.04); border-top: 1px solid var(--p-border);
              backdrop-filter: blur(6px); gap: 16px; }
.bottom-bar .progress { flex: 1; height: 4px; background: rgba(0,0,0,0.08);
                        border-radius: 2px; overflow: hidden; }
.bottom-bar .progress > div { height: 100%; background: var(--p-accent);
                              transition: width 220ms; }
.bottom-bar .nav { display: flex; align-items: center; gap: 8px; flex: 0 0 auto; }
.bottom-bar button { background: var(--p-accent); color: #FFF; border: 0;
                     padding: 8px 14px; border-radius: 6px; cursor: pointer;
                     font-size: 0.9rem; }
.bottom-bar button:hover { background: var(--p-dark); }
.bottom-bar .index { font-size: 0.9rem; color: var(--p-dark); min-width: 80px;
                     text-align: center; flex: 0 0 auto; }
.bottom-bar .title { font-size: 0.95rem; color: var(--p-dark); flex: 1 1 auto;
                     overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
                     min-width: 0; }
.section-meta { font-size: 0.85rem; color: var(--p-dark); opacity: 0.7;
                margin: 0 0 12px 0; font-style: italic; }
"""

JS = r"""
let SLIDE_INDEX = 0;
const SLIDES = document.querySelectorAll('.slide');
const TOTAL = SLIDES.length;
function render() {
  SLIDES.forEach((el, i) => el.classList.toggle('active', i === SLIDE_INDEX));
  const cur = document.getElementById('idx');
  if (cur) cur.textContent = `${SLIDE_INDEX + 1} / ${TOTAL}`;
  const bar = document.getElementById('progress-bar');
  if (bar) bar.style.width = `${((SLIDE_INDEX + 1) / TOTAL) * 100}%`;
  const tit = document.getElementById('slide-title-bar');
  if (tit) tit.textContent = SLIDES[SLIDE_INDEX].dataset.title || '';
}
function go(delta) {
  SLIDE_INDEX = Math.max(0, Math.min(TOTAL - 1, SLIDE_INDEX + delta));
  render();
}
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { go(1); e.preventDefault(); }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { go(-1); e.preventDefault(); }
  else if (e.key === 'Home') { SLIDE_INDEX = 0; render(); }
  else if (e.key === 'End') { SLIDE_INDEX = TOTAL - 1; render(); }
});
window.addEventListener('DOMContentLoaded', render);
"""


def render_html(*, slides: list[tuple[str, str]], paper_title: str,
                lang_out: str) -> str:
    body = []
    for i, (title, html_body) in enumerate(slides):
        body.append(
            f'<section class="slide" data-title="{html.escape(title)}">'
            f'<h2 class="slide-title">{html.escape(title)}</h2>'
            f'{html_body}'
            f'</section>'
        )
    deck_html = "\n".join(body)
    head_lang = "zh-Hant" if lang_out.startswith("zh") else lang_out
    page = textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="{head_lang}">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{html.escape(paper_title)}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
        <style>{CSS}</style>
        </head>
        <body>
        <main class="deck">
        {deck_html}
        </main>
        <footer class="bottom-bar">
          <div class="nav">
            <button onclick="go(-1)" aria-label="prev">←</button>
            <button onclick="go(1)" aria-label="next">→</button>
            <span class="index" id="idx"></span>
          </div>
          <div class="title" id="slide-title-bar"></div>
          <div class="progress"><div id="progress-bar"></div></div>
        </footer>
        <script>{JS}</script>
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
    p.add_argument("figures_dir")
    p.add_argument("out_html")
    p.add_argument("--lang-out", default="zh-TW")
    args = p.parse_args()

    analysis_md = Path(args.analysis_md).read_text(encoding="utf-8")
    biblio = json.loads(Path(args.biblio_json).read_text(encoding="utf-8"))
    figures_dir = Path(args.figures_dir)
    out_html = Path(args.out_html)

    slides = build_slides(
        analysis_md=analysis_md,
        biblio=biblio,
        figures_dir=figures_dir,
        lang_out=args.lang_out,
    )

    bi = biblio.get("basic_info") or {}
    paper_title = bi.get("full_title") or bi.get("short_name") or "Phyra paper-read slide"
    html_text = render_html(
        slides=slides,
        paper_title=paper_title,
        lang_out=args.lang_out,
    )

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_text, encoding="utf-8")
    log.info("wrote %s (%d slides, %.1f KB)",
             out_html, len(slides), out_html.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    sys.exit(main())
