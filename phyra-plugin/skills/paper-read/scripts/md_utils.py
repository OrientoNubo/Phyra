"""md_utils.py — shared subset Markdown→HTML converter.

Used by both ``build_slide.py`` (no anchor IDs) and
``build_analysis_html.py`` (with anchor IDs on headings) so the two
scripts stay in sync.

Sibling-import pattern (as used in _retry.py):

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from md_utils import md_to_html, normalize_md
"""

import html
import re

# Match `(約 N words; ...)` or `(N words; §X 約 Y)` style ugly breakdowns.
# Replace with a clean `(約 N words)` for downstream rendering.
_RX_WORD_COUNT_BREAKDOWN = re.compile(
    r"\((?:約\s*)?(\d{2,5})\s*words?\s*[;；][^)]*\)"
)
# Convert `$$short$$` (single-line, no whitespace at edges) → `$short$` so
# KaTeX renders inline. Display math (`$$...$$` spanning lines) stays.
_RX_DISPLAY_MATH_INLINE = re.compile(
    r"\$\$\s*([^$\n]{1,80}?)\s*\$\$"
)


def normalize_md(md: str) -> str:
    """Light pre-pass before MD→HTML to fix two LLM tics:

      1. ``(約 N words; §X 約 Y、§Z 約 W)`` → ``(約 N words)``
      2. ``$$short$$`` (no newline inside) → ``$short$`` so it renders
         inline instead of breaking into a display block.
    """
    md = _RX_WORD_COUNT_BREAKDOWN.sub(r"(約 \1 words)", md)
    md = _RX_DISPLAY_MATH_INLINE.sub(r"$\1$", md)
    return md


def md_to_html(md: str, *, include_anchor_ids: bool = False) -> str:
    """Convert a small subset of Markdown to HTML, sufficient for analysis
    output (headings, paragraphs, fenced code blocks, lists, tables,
    bold/italic, inline code).

    When ``include_anchor_ids`` is True, headings get a slugified ``id``
    attribute (used by ``build_analysis_html.py`` for the in-page TOC);
    when False, headings are emitted without an id (used by
    ``build_slide.py``).
    """
    md = normalize_md(md)
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    def render_inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
        return s

    while i < n:
        line = lines[i]
        m_h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m_h:
            lvl = len(m_h.group(1))
            text = m_h.group(2)
            if include_anchor_ids:
                anchor = re.sub(r"[^\w一-鿿]+", "-",
                                text.strip().lower()).strip("-")
                out.append(
                    f"<h{lvl} id=\"{anchor}\">{render_inline(text)}</h{lvl}>"
                )
            else:
                out.append(f"<h{lvl}>{render_inline(text)}</h{lvl}>")
            i += 1
            continue
        if line.strip().startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append(
                "<pre class=\"codeblock\"><code>"
                + html.escape("\n".join(buf))
                + "</code></pre>"
            )
            continue
        # Tables
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            tbl = ["<table><thead><tr>"]
            for h in header:
                tbl.append(f"<th>{render_inline(h)}</th>")
            tbl.append("</tr></thead><tbody>")
            for r in rows:
                tbl.append("<tr>")
                for c in r:
                    tbl.append(f"<td>{render_inline(c)}</td>")
                tbl.append("</tr>")
            tbl.append("</tbody></table>")
            out.append("".join(tbl))
            continue
        # Bullet lists
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(
                f"<li>{render_inline(it)}</li>" for it in items
            ) + "</ul>")
            continue
        # Numbered lists
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(
                f"<li>{render_inline(it)}</li>" for it in items
            ) + "</ol>")
            continue
        # Blank → paragraph break
        if not line.strip():
            i += 1
            continue
        # Plain paragraph (collect consecutive non-blank lines)
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,6})\s|^```|^\s*[-*]\s|^\s*\d+\.\s", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + render_inline(" ".join(para)) + "</p>")

    return "\n".join(out)
