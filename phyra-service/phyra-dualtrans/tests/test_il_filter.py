"""Unit tests for the paragraph-level keep-source policy. Pure — no
babeldoc import (the monkeypatch itself is exercised by the real
end-to-end runs, not here)."""

from __future__ import annotations

from dataclasses import dataclass, field

from phyra_dualtrans.pipeline.il_filter import (
    collect_abandon_keep_ids,
    collect_reference_paragraph_ids,
    is_reference_header,
    is_supplementary_header,
    is_trivial_noise,
    keep_source_for_label,
    looks_like_bib_entry,
)


def test_keep_source_label_policy():
    # kept verbatim by label alone: figure/table content, table apparatus,
    # math. (`abandon` is NOT label-decided — see collect_abandon_keep_ids.)
    for lbl in ("figure", "table", "table_footnote", "isolate_formula"):
        assert keep_source_for_label(lbl) is True
    # translated: body + ALL captions (the user wants captions translated)
    for lbl in ("title", "plain text", "figure_caption",
                "table_caption", "formula_caption"):
        assert keep_source_for_label(lbl) is False
    # `abandon` carries BOTH furniture and footnotes → not a label decision
    assert keep_source_for_label("abandon") is False
    # unknown / missing label → translate (conservative: it's body)
    assert keep_source_for_label(None) is False
    assert keep_source_for_label("") is False
    assert keep_source_for_label("fallback_line") is False


def test_reference_header_detection():
    for ok in ("References", "REFERENCES", "Bibliography",
               "  references  ", "7 References", "A. References",
               "R E F E R E N C E S"):           # letter-spaced extraction
        assert is_reference_header(ok), ok
    for no in ("References to prior work are discussed",
               "See the references section for details",
               "Related Work", "", "Referenced architectures"):
        assert not is_reference_header(no), no


def test_supplementary_header_detection():
    for ok in ("Appendix", "Appendix A", "Supplementary Material",
               "Supplementary", "A Supplementary Materials", "Appendices"):
        assert is_supplementary_header(ok), ok
    for no in ("We append the following note", "Related Work", ""):
        assert not is_supplementary_header(no), no


# --- duck-typed fake IL doc ------------------------------------------
@dataclass
class _Para:
    unicode: str
    layout_label: str | None = "plain text"


@dataclass
class _Page:
    pdf_paragraph: list = field(default_factory=list)


@dataclass
class _Docs:
    page: list = field(default_factory=list)


def _doc(*paras_per_page):
    return _Docs(page=[_Page(pdf_paragraph=list(ps)) for ps in paras_per_page])


def test_looks_like_bib_entry():
    for ok in (
        "[12] Daniel DeTone, A. Rabinovich. Superpoint. In Proceedings "
        "of the IEEE conference, pages 224-236, 2018.",
        "(3) C. Coder. Yet another work. arXiv:2101.00001, 2021.",
        "7. E. Eng. Even more. CVPR, 2023.",
        "Smith, J. and Doe, A. A study of things. NeurIPS, 2020.",
        "He et al. Deep residual learning. CVPR 2016. doi:10.1/x",
    ):
        assert looks_like_bib_entry(ok), ok
    for no in (
        "A.1 Existing Data Processing To facilitate multi-dataset "
        "training, we standardize all 29 publicly available datasets.",
        "– Loop roaming: departing from and returning to the same "
        "location to form closed-loop sequences.",
        "We evaluate on six scenes and report the mean error.",
        "Algorithm 2 Street Network Random Walk Input: graph G",
        "",
    ):
        assert not looks_like_bib_entry(no), no


def test_is_trivial_noise():
    for ok in ("27", "  iv ", "12 / 30"):
        assert is_trivial_noise(ok)
    for no in ("Page 27 of the appendix", "Section 3", ""):
        assert not is_trivial_noise(no)


def test_abandon_keeps_furniture_translates_footnotes():
    """The reported NetLLM bug: footnotes share the `abandon` label with
    running headers/footers. Furniture stays source; footnote prose is
    translated."""
    def ab(t):
        return _Para(t, "abandon")

    # furniture (kept): repeated running header (2 pages), short author
    # strip, page number, the arXiv stamp
    hdr1 = ab("ACM SIGCOMM '24, August 4-8, 2024, Sydney, NSW, Australia")
    hdr2 = ab("ACM SIGCOMM '24, August 4-8, 2024, Sydney, NSW, Australia")
    author = ab("Wu et al.")
    pageno = ab("6")
    arxiv = ab("2024 ug I] 6 A N 3 [cs. 02338v :2402. iv arX")
    # footnotes (translated): long unique prose
    fn1 = ab("4We leave deeper investigation of the efficacy of multimodal "
             "LLMs in networking for future work.")
    fn2 = ab("3An episode in RL refers to a single round of a RL model to "
             "interact with the environment from the start to the end.")

    docs = _doc([hdr1, author, pageno, arxiv, fn1],
                [hdr2, fn2])
    keep = collect_abandon_keep_ids(docs)
    for furniture in (hdr1, hdr2, author, pageno, arxiv):
        assert id(furniture) in keep, furniture.unicode
    for footnote in (fn1, fn2):
        assert id(footnote) not in keep, footnote.unicode


def test_abandon_keep_ignores_non_abandon_and_is_crash_safe():
    body = _Para("A long unique sentence of real body text here.", "plain text")
    docs = _doc([body])
    assert collect_abandon_keep_ids(docs) == set()  # only `abandon` considered

    class Bad:
        @property
        def page(self):
            raise RuntimeError("boom")
    assert collect_abandon_keep_ids(Bad()) == set()


def test_appendix_after_refs_without_heading_is_translated():
    """The 2604 case: References, then an appendix that has NO
    'Appendix' heading ('A.1 Existing Data Processing ...'). Bib
    entries are kept English; the appendix body MUST be translated."""
    head = _Para("References", "title")
    r1 = _Para("[12] Daniel DeTone, A. Rabinovich. Superpoint. In "
               "Proceedings of the IEEE conference, pp. 224-236, 2018.")
    r2 = _Para("[13] B. Writer. Another paper. NeurIPS, 2021.")
    ap1 = _Para("A.1 Existing Data Processing To facilitate multi-"
                "dataset training, we standardize all 29 datasets.")
    ap2 = _Para("Loop roaming: departing from and returning to the "
                "same location to form closed-loop sequences.")
    docs = _doc([_Para("Conclusion body.")], [head, r1, r2], [ap1, ap2])
    ids = collect_reference_paragraph_ids(docs)
    assert id(r1) in ids and id(r2) in ids          # refs kept English
    assert id(ap1) not in ids and id(ap2) not in ids  # appendix TRANSLATED


def test_collect_reference_ids_after_heading_until_supp():
    body1 = _Para("Introduction. We propose a method.")
    body2 = _Para("Method. The architecture is as follows.")
    head = _Para("References", "title")
    r1 = _Para("[1] A. Author. A paper. CVPR, 2020.")
    r2 = _Para("[2] B. Writer. Another. NeurIPS, 2021.")
    supp = _Para("Appendix A", "title")
    appx = _Para("Additional experiments and ablations.")
    docs = _doc([body1, body2], [head, r1, r2], [supp, appx])

    ids = collect_reference_paragraph_ids(docs)
    # only the two bib entries are force-kept; heading + body + appendix
    # are still translated (heading 'References' → '參考文獻' is fine)
    assert ids == {id(r1), id(r2)}
    assert id(body1) not in ids and id(head) not in ids
    assert id(appx) not in ids                     # supp resumes


def test_collect_reference_ids_takes_last_heading():
    """An early 'References to prior work' must NOT trigger; only the
    real standalone heading does (take the last match)."""
    early = _Para("References", "title")           # real heading p? -> last
    e1 = _Para("[1] Real bib entry. 2020.")
    docs = _doc([_Para("Body.")], [early, e1])
    ids = collect_reference_paragraph_ids(docs)
    assert ids == {id(e1)}


def test_no_reference_heading_keeps_nothing():
    docs = _doc([_Para("Only body text, no bibliography heading.")])
    assert collect_reference_paragraph_ids(docs) == set()


def test_collect_is_crash_safe_on_bad_docs():
    class Bad:
        @property
        def page(self):
            raise RuntimeError("boom")
    assert collect_reference_paragraph_ids(Bad()) == set()
