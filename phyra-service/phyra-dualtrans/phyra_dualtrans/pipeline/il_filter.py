"""
Paragraph-level translate / keep-source policy for BabelDOC.

BabelDOC's `ILTranslator` (the path we use — `do_llm_translate` raises
NotImplementedError) translates EVERY paragraph regardless of region,
and page-granular reference slicing is unreliable in BOTH directions
(observed: 2501_CubeDiff refs translated wholesale; ref pages replaced by
grey placeholders instead of staying 「原樣」). The user's mental model:

  * the ONLY thing not translated is the References section
  * figure / table CONTENT is kept verbatim (their CAPTION is translated)
  * everything with body content IS translated (mixed pages handled)
  * references stay visible in the original — just untranslated

The doclayout YOLO model emits exactly these 10 `layout_label` values
(`doclayout_yolo_docstructbench_imgsz1024.onnx` metadata `names`):

    0 title           1 plain text      2 abandon
    3 figure          4 figure_caption  5 table
    6 table_caption   7 table_footnote  8 isolate_formula
    9 formula_caption

Injection: subclass `ILTranslator` and override `pre_translate_paragraph`
to return ``(None, None)`` — that is BabelDOC's OWN skip path (used for
short / vertical text); `translate_paragraph` then returns immediately
and the paragraph stays verbatim original, with all placeholder / layout
handling untouched. The subclass is monkey-patched into
`babeldoc.format.pdf.high_level` inside the translation CHILD only (the
server never imports babeldoc), so the os._exit isolation boundary is
unaffected.
"""

from __future__ import annotations

import re

# Regions whose interior text is KEPT AS SOURCE purely by label (no LLM
# call, verbatim), regardless of document context:
#   figure / table   — the user wants figure & table content left as-is
#   table_footnote    — table apparatus (tables 保持原樣)
#   isolate_formula   — mathematics, never translated
# Everything else is translated — importantly the CAPTIONS
# (figure_caption / table_caption / formula_caption) and body
# (title / plain text), and any label the model missed (None / "" /
# "fallback_line") which is conservatively treated as translatable body.
#
# NOTE: `abandon` is deliberately NOT here. The doclayout YOLO model lumps
# real FOOTNOTES into `abandon` alongside genuine page furniture (running
# headers / footers / page numbers / the arXiv stamp). Blanket-skipping the
# whole class left footnotes — which ARE body content the user wants
# translated — untranslated (the reported "some content not translated"
# bug). `abandon` is instead resolved per-document by
# `collect_abandon_keep_ids`: furniture stays source, footnote prose is
# translated.
KEEP_SOURCE_LABELS = frozenset(
    {"figure", "table", "table_footnote", "isolate_formula"}
)


def keep_source_for_label(label: str | None) -> bool:
    """True → keep this paragraph verbatim by label alone (figure / table /
    table_footnote / isolate_formula). `abandon` is NOT decided here — see
    `collect_abandon_keep_ids`."""
    return (label or "") in KEEP_SOURCE_LABELS


# --- References-section detection (document order, paragraph level) -----
# A standalone bibliography heading: a short line that is exactly
# References / Bibliography (optionally a leading section number / letter).
# "References to prior work" etc. do NOT match (the line must BE the
# heading). Letter-spaced PDF extraction ("R E F E R E N C E S") is
# handled by also testing a despaced copy.
_REF_HEADER_RX = re.compile(
    r"^\s*(?:\d+\.?\s+|[A-Z]\.?\s+)?"
    r"(references?|bibliography)\s*$",
    re.IGNORECASE,
)
# A Supplementary / Appendix heading AFTER references is real content
# again → translation resumes there.
_SUPP_HEADER_RX = re.compile(
    r"^\s*(?:\d+\.?\s+|[A-Z]\.?\s+)?"
    r"(supplement(?:ary|al)(?:\s+materials?)?|appendix(?:es)?|appendices)"
    r"\b.*$",
    re.IGNORECASE,
)

# Per-paragraph "this is a bibliography entry" test. Position alone is
# NOT enough: an appendix can follow References with NO "Appendix"
# heading (observed: 2604 p25 "A.1 Existing Data Processing ..." — real
# body that MUST be translated). So in the post-heading region we keep a
# paragraph as source ONLY when it actually looks like a citation
# (numbered marker, or a year together with a venue/identifier hint),
# or is trivial noise (a bare page number). Substantial non-bib prose
# after the heading (appendix) is still translated.
_ENTRY_MARKER_RX = re.compile(r"^\s*(?:\[\d{1,4}\]|\(\d{1,4}\)|\d{1,3}\.)\s+\S")
_BIB_HINT_RX = re.compile(
    r"(arxiv:|arxiv\b|doi:|doi\.org|https?://|"
    r"\bin proc(?:\.|eedings)?\b|\bproceedings of\b|"
    r"\bconference on\b|\bjournal of\b|\btransactions on\b|"
    r"\bpp\.\s*\d|\bvol\.\s*\d|\bno\.\s*\d|\bet al\.?|"
    r"\bpreprint\b|\bin advances in\b|"
    r"\b(?:neurips|nips|icml|iclr|cvpr|eccv|iccv|aaai|acl|emnlp|"
    r"siggraph|iros|icra|tpami|corr)\b)",
    re.IGNORECASE,
)
_YEAR_RX = re.compile(r"\b(?:18|19|20)\d{2}\b")
_TRIVIAL_NOISE_RX = re.compile(
    r"^\s*(?:\d{1,4}|[ivxlcdm]{1,6}|\d+\s*/\s*\d+)\s*$", re.IGNORECASE
)


def looks_like_bib_entry(text: str) -> bool:
    """True when a paragraph reads like a reference-list entry. Robust to
    a whole reference column collapsed into one paragraph (many markers /
    years / venues) and to author–year style (year + venue hint)."""
    t = (text or "").strip()
    if not t:
        return False
    if _ENTRY_MARKER_RX.match(t):
        return True
    has_year = _YEAR_RX.search(t) is not None
    has_hint = _BIB_HINT_RX.search(t) is not None
    if has_year and has_hint:
        return True
    # A dense bibliography paragraph: several year tokens + a venue hint.
    if has_hint and len(_YEAR_RX.findall(t)) >= 3:
        return True
    return False


def is_trivial_noise(text: str) -> bool:
    """A bare page number / roman numeral line — skip (don't translate)."""
    return _TRIVIAL_NOISE_RX.match((text or "").strip()) is not None


def _matches(rx: re.Pattern[str], text: str, *, maxlen: int) -> bool:
    t = (text or "").strip()
    if not t or len(t) > maxlen:
        return False
    if rx.match(t):
        return True
    # letter-spaced extraction artifact: "R E F E R E N C E S"
    despaced = re.sub(r"\s+", "", t)
    return len(despaced) <= 24 and rx.match(despaced) is not None


def is_reference_header(text: str) -> bool:
    return _matches(_REF_HEADER_RX, text, maxlen=40)


def is_supplementary_header(text: str) -> bool:
    return _matches(_SUPP_HEADER_RX, text, maxlen=60)


# Within the `abandon` class, a paragraph this short is treated as page
# furniture (a running header/footer line, an author/venue strip, the
# arXiv stamp) rather than a footnote. Footnote prose is materially longer.
_ABANDON_FURNITURE_MAXLEN = 60


def _norm(text: str) -> str:
    """Whitespace-collapsed, lower-cased text for cross-page identity."""
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def collect_abandon_keep_ids(docs) -> set[int]:
    """`id()` of every `abandon` paragraph that is genuine PAGE FURNITURE
    (kept verbatim) — as opposed to a FOOTNOTE (which is body content and
    must be translated). The doclayout YOLO model puts both in `abandon`.

    A paragraph is furniture when it is empty, a bare page number, repeats
    (near-)identically on ≥2 pages (a running header/footer), or is short
    (≤60 chars — an author/venue strip, the arXiv stamp). A long, unique
    paragraph is a footnote → NOT kept (it gets translated). Never raises.
    """
    flat: list[tuple[object, str]] = []
    pages_of: dict[str, set[int]] = {}
    try:
        for pi, page in enumerate(docs.page):
            for para in page.pdf_paragraph:
                if (getattr(para, "layout_label", None) or "") != "abandon":
                    continue
                txt = getattr(para, "unicode", "") or ""
                flat.append((para, txt))
                n = _norm(txt)
                if n:
                    pages_of.setdefault(n, set()).add(pi)
    except Exception:  # noqa: BLE001 — policy must never break a job
        return set()

    keep: set[int] = set()
    for para, txt in flat:
        t = txt.strip()
        repeated = len(pages_of.get(_norm(txt), ())) >= 2
        if (
            not t
            or is_trivial_noise(t)
            or repeated
            or len(t) <= _ABANDON_FURNITURE_MAXLEN
        ):
            keep.add(id(para))
        # else: long unique prose = footnote → leave translatable.
    return keep


def collect_reference_paragraph_ids(docs) -> set[int]:
    """`id()` of every BIBLIOGRAPHY paragraph: after the LAST standalone
    References / Bibliography heading, a paragraph is force-kept only
    when it actually reads like a citation (or is a bare page number).
    Substantial non-bib prose after the heading — e.g. an appendix with
    no "Appendix" heading (2604 p25 "A.1 Existing Data Processing ...") —
    is still translated, and an explicit Supplementary / Appendix heading
    hard-stops the region. Empty when there is no references heading
    (behaviour unchanged for those papers). Never raises."""
    flat: list[tuple[object, str]] = []
    try:
        for page in docs.page:
            for para in page.pdf_paragraph:
                flat.append((para, getattr(para, "unicode", "") or ""))
    except Exception:  # noqa: BLE001 — policy must never break a job
        return set()

    ref_idx: int | None = None
    for i, (_, txt) in enumerate(flat):
        if is_reference_header(txt):
            ref_idx = i  # take the LAST (a body subsection won't match)
    if ref_idx is None:
        return set()

    skip: set[int] = set()
    for para, txt in flat[ref_idx + 1:]:
        if is_supplementary_header(txt):
            break  # explicit appendix → translation resumes
        if looks_like_bib_entry(txt) or is_trivial_noise(txt):
            skip.add(id(para))
        # else: substantial non-bib paragraph (appendix body) → leave
        # translatable; keep scanning (a stray line between entries must
        # not end the whole bibliography).
    return skip


def patch_high_level_il_translator(*, skip_references: bool = True):
    """Rebind ``babeldoc.format.pdf.high_level.ILTranslator`` to a
    subclass that applies the keep-source policy. Call AFTER importing
    babeldoc's high_level and BEFORE ``async_translate``. Returns the
    subclass (for tests)."""
    import babeldoc.format.pdf.high_level as hl
    from babeldoc.format.pdf.document_il.midend.il_translator import (
        ILTranslator,
    )

    class PhyraILTranslator(ILTranslator):  # type: ignore[valid-type,misc]
        """ILTranslator + per-paragraph keep-source policy."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._phyra_skip_ids: set[int] = set()
            self._phyra_skip_refs = skip_references
            self._phyra_kept = 0  # paragraphs kept as source by policy

        def translate(self, docs):  # noqa: D401
            ids: set[int] = set()
            if self._phyra_skip_refs:
                ids |= collect_reference_paragraph_ids(docs)
            # `abandon`: keep page furniture, translate footnote prose.
            ids |= collect_abandon_keep_ids(docs)
            self._phyra_skip_ids = ids
            return super().translate(docs)

        def pre_translate_paragraph(
            self, paragraph, tracker, page_font_map, xobj_font_map
        ):
            label = getattr(paragraph, "layout_label", None)
            if keep_source_for_label(label) or (
                id(paragraph) in self._phyra_skip_ids
            ):
                # BabelDOC's own keep-original path (short/vertical text):
                # translate_paragraph() returns immediately, the paragraph
                # is emitted verbatim with layout/placeholders intact.
                self._phyra_kept += 1
                return None, None
            return super().pre_translate_paragraph(
                paragraph, tracker, page_font_map, xobj_font_map
            )

    hl.ILTranslator = PhyraILTranslator
    return PhyraILTranslator
