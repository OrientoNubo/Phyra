#!/usr/bin/env python3
"""Scan collection/ and emit a self-contained index.html browse page.

Naming convention:
  - Old files: {YYMM}_{ShortName}_{Title}{suffix}
  - New files: {YYMM}_{Title}{suffix}
  - In the title portion: original ' ' → '_', original ': ' → '__'.

Title and short name are authoritatively taken from the paper's
`_analysis.zh-TW.md` (rows `| Paper full title | … |`, `| Paper short name | … |`)
when available. Otherwise the title is reconstructed from the filename and
the short name is empty. The internal `key` is the filename stem
(everything before the suffix) — it uniquely identifies one paper's
artifact group and is not shown in the UI.
"""

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLLECTION = ROOT / "collection"
OUTPUT = ROOT / "index.html"

# Port of the Phyra Center landing page (the hub that lists every sibling
# service). Baked into the top banner so this generated page can link back
# to Center. The hostname is resolved client-side (so LAN access works);
# only the port is fixed here. Matches phyra-center/script/start.sh PORT.
CENTER_PORT = os.environ.get("PHYRA_CENTER_PORT", "8035")

# Order matters: bilingual.pdf must precede plain .pdf
SUFFIXES = [
    ("_analysis.zh-TW.html",      "analysis_html"),
    ("_analysis.zh-TW.md",        "analysis_md"),
    ("_draftslide.html",          "draftslide_html"),
    (".pdf",                      "original_pdf"),
]

# bilingual dual PDF in ANY target language: {stem}_bilingual.<lang>.dual.pdf
BILINGUAL_RE = re.compile(r"^(.*)_bilingual\.[A-Za-z0-9-]+\.dual\.pdf$")

YYMM_RE = re.compile(r"^(\d{4})_")
TITLE_FIELD_RE = re.compile(r"\|\s*Paper full title\s*\|\s*(.+?)\s*\|")
SHORT_FIELD_RE = re.compile(r"\|\s*Paper short name\s*\|\s*(.+?)\s*\|")
PLACEHOLDERS = {"", "未知", "unknown", "n/a", "-", "—"}


def split_filename(name: str):
    """Return (stem, suffix_kind) or None."""
    m = BILINGUAL_RE.match(name)        # any-language bilingual, before .pdf
    if m:
        return m.group(1), "bilingual_pdf"
    for suffix, kind in SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)], kind
    return None


def filename_to_display(rest: str) -> str:
    """Reverse filename encoding for display: '__' → ': ',  '_' → ' '."""
    return rest.replace("__", ": ").replace("_", " ")


def extract_md_fields(md_path: Path):
    """Return (title, short); each may be None if missing or placeholder."""
    title = short = None
    try:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, None
    for line in text.splitlines():
        if title is None:
            m = TITLE_FIELD_RE.search(line)
            if m:
                v = m.group(1).strip()
                if v.lower() not in PLACEHOLDERS:
                    title = v
        if short is None:
            m = SHORT_FIELD_RE.search(line)
            if m:
                v = m.group(1).strip()
                if v.lower() not in PLACEHOLDERS:
                    short = v
        if title and short:
            break
    return title, short


def scan():
    papers: dict[str, dict] = {}
    for entry in sorted(os.listdir(COLLECTION)):
        path = COLLECTION / entry
        if not path.is_file():
            continue
        parsed = split_filename(entry)
        if not parsed:
            continue
        stem, kind = parsed
        m = YYMM_RE.match(stem)
        if not m:
            continue
        yymm = m.group(1)
        rest = stem[len(yymm) + 1:]  # everything after "{yymm}_"
        rec = papers.setdefault(stem, {
            "key": stem,
            "yymm": yymm,
            "title": "",
            "short": "",
            "files": {},
            "_rest": rest,
        })
        rec["files"][kind] = entry

    # Resolve title/short from MD when present
    for rec in papers.values():
        md_name = rec["files"].get("analysis_md")
        if md_name:
            t, s = extract_md_fields(COLLECTION / md_name)
            if t:
                rec["title"] = t
            if s:
                rec["short"] = s
        if not rec["title"]:
            rec["title"] = filename_to_display(rec["_rest"])
        rec.pop("_rest", None)
    return list(papers.values())


def yymm_sort_key(p: dict) -> int:
    try:
        return -int(p["yymm"])
    except ValueError:
        return 0


def main():
    if not COLLECTION.is_dir():
        raise SystemExit(f"collection directory not found: {COLLECTION}")

    papers = scan()
    papers.sort(key=lambda p: (yymm_sort_key(p), (p["short"] or p["title"]).lower()))

    fully = sum(
        1 for p in papers
        if all(k in p["files"]
               for k in ("analysis_html", "draftslide_html", "bilingual_pdf", "original_pdf"))
    )

    data_json = json.dumps(papers, ensure_ascii=False).replace("</", "<\\/")

    html = (TEMPLATE
            .replace("__TOTAL__", str(len(papers)))
            .replace("__FULLY__", str(fully))
            .replace("__CENTER_PORT__", str(CENTER_PORT))
            .replace("__DATA__", data_json))

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} — {len(papers)} papers ({fully} fully analyzed)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phyra ArchBase</title>
<style>
  :root {
    --p-primary:  #f8f8f6;            /* header 條背景（頁面頂部標題列） */
    --p-light:    #f8f8f6;            /* body 整頁背景 */
    --p-accent:   #c96c49;            /* 重點色：YYMM 徽章底、focus 光暈、切換鈕邊框 */
    --p-dark:     #373734;            /* 強調文字：h1 標題、卡片論文標題、按鈕文字 */
    --p-text:     #0b0b0b;            /* 主要正文文字 */
    --p-muted:    #898781;            /* 次要淡字：stats 統計、卡片短名副標 */
    --p-card-bg:  #ebebe6;            /* 卡片底色、切換鈕底色 */
    --p-border:   #d7d7d5;            /* 卡片邊框、按鈕邊框、搜尋框邊框 */
    --p-card-alt: #f4f4f1;            /* 只有 PDF 卡片的略灰背景（尚未分析） */
    --p-shadow:   rgba(31, 30, 29, 0.08);   /* 卡片 hover 時的投影 */
    --p-focus:    rgba(217, 119, 87, 0.25); /* 搜尋框與切換鈕 focus 時的外光暈 */
    --p-toggle-bg:     rgba(0, 0, 0, 0.04); /* 主題切換 segmented 容器底色 */
    --p-toggle-active: #ffffff;             /* 主題切換 segmented 當前選中那一格的底色 */
    --p-header-border: #f8f8f6;             /* header 最下方那條分隔線 */
  }
  [data-theme="dark"] {
    --p-primary:  #1f1f1e;            /* header 條背景 */
    --p-light:    #1f1f1e;            /* body 整頁背景 */
    --p-accent:   #c96c49;            /* 重點色（兩個模式一致） */
    --p-dark:     #c2c2c2;            /* 強調文字：標題、按鈕文字） */
    --p-text:     #ffffff;            /* 主要正文文字 */
    --p-muted:    #c2c2b7;            /* 次要淡字 */
    --p-card-bg:  #171717;            /* 卡片底色、切換鈕底色 */
    --p-border:   #292929;            /* 卡片邊框、按鈕邊框、搜尋框邊框 */
    --p-card-alt: #171717;            /* 只有 PDF 卡片的略深背景 */
    --p-shadow:   rgba(0, 0, 0, 0.4);       /* 卡片 hover 時的投影 */
    --p-focus:    rgba(217, 119, 87, 0.4);  /* 搜尋框與切換鈕 focus 時的外光暈 */
    --p-toggle-bg:     rgba(255, 255, 255, 0.04); /* 主題切換 segmented 容器底色 */
    --p-toggle-active: #2c2c2b;                   /* 主題切換 segmented 當前選中那一格的底色 */
    --p-header-border: #1f1f1e;                   /* header 最下方那條分隔線 */
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang TC", "Microsoft JhengHei", "Noto Sans CJK TC", sans-serif;
    background: var(--p-light);
    color: var(--p-text);
    line-height: 1.5;
  }
  .hub-bar {
    display: flex; align-items: center; gap: 14px;
    padding: 7px 28px;
    background: var(--p-accent);
    color: #fff;
    font-size: 13px;
  }
  .hub-bar .hub-link {
    color: #fff; text-decoration: none; font-weight: 600;
    padding: 3px 11px; border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    transition: background 0.12s;
    display: inline-flex; align-items: center; gap: 6px;
  }
  .hub-bar .hub-link:hover { background: rgba(255, 255, 255, 0.16); }
  .hub-bar .hub-brand { font-weight: 700; letter-spacing: 0.5px; }
  .hub-bar .hub-arrow { opacity: 0.85; }
  header {
    background: var(--p-primary);
    padding: 8px 28px;
    border-bottom: 1px solid var(--p-header-border);
    display: flex;
    align-items: center;
    gap: 20px;
    position: sticky;
    top: 0;
    z-index: 20;
  }
  .hdr-left {
    flex-shrink: 0;
    min-width: 0;
  }
  .theme-toggle {
    display: inline-flex;
    align-items: center;
    padding: 3px;
    gap: 2px;
    background: var(--p-toggle-bg);
    border: 1px solid var(--p-border);
    border-radius: 8px;
    flex-shrink: 0;
  }
  .theme-toggle button {
    width: 28px;
    height: 26px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--p-muted);
    cursor: pointer;
    border-radius: 5px;
    transition: background 0.12s, color 0.12s;
  }
  .theme-toggle button:hover { color: var(--p-text); }
  .theme-toggle button[aria-pressed="true"] {
    background: var(--p-toggle-active);
    color: var(--p-text);
    box-shadow: 0 1px 2px var(--p-shadow);
  }
  .theme-toggle svg {
    width: 15px;
    height: 15px;
    stroke: currentColor;
    fill: none;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  header h1 {
    margin: 0 0 2px;
    font-size: 22px;
    color: var(--p-dark);
    letter-spacing: 0.5px;
  }
  .stats {
    color: var(--p-dark);
    font-size: 12.5px;
    opacity: 0.78;
  }
  .controls {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: center;
    gap: 10px;
    flex: 1 1 auto;
    min-width: 0;
  }
  /* search + tag-filter stacked: the tag bar sits directly under the search
     box, sharing its left edge (it's the column's first flex row). */
  .search-col {
    --add-w: 38px;            /* "+" button width  */
    --add-gap: 8px;           /* gap between "+" and the search box */
    flex: 1 1 280px;
    max-width: 460px;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .search-row { display: flex; gap: var(--add-gap); align-items: stretch; }
  .search-row #search { flex: 1 1 auto; }
  /* square rounded "+" button — same low-key treatment as the filter/sort
     controls (matches its height to the search box via align-items:stretch) */
  .add-btn {
    flex: 0 0 auto; width: var(--add-w);
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--p-toggle-bg); color: var(--p-muted);
    border: 1px solid var(--p-border); border-radius: 6px;
    cursor: pointer;
    transition: color 0.12s, border-color 0.12s, background 0.12s;
  }
  .add-btn:hover {
    color: var(--p-accent); border-color: var(--p-accent);
    background: var(--p-toggle-active);
  }
  .add-btn svg {
    width: 16px; height: 16px; stroke: currentColor; fill: none;
    stroke-width: 2; stroke-linecap: round;
  }
  #search {
    width: 100%;
    padding: 9px 13px;
    font-size: 14px;
    border: 2px solid var(--p-accent);
    border-radius: 6px;
    background: var(--p-card-bg);
    color: var(--p-text);
    outline: none;
    transition: box-shadow 0.15s;
  }
  #search:focus {
    box-shadow: 0 0 0 3px var(--p-focus);
  }
  .filter {
    display: inline-flex;
    align-items: center;
    padding: 3px;
    gap: 2px;
    background: var(--p-toggle-bg);
    border: 1px solid var(--p-border);
    border-radius: 6px;
  }
  .filter button {
    padding: 5px 10px;
    border: 0;
    background: transparent;
    color: var(--p-muted);
    cursor: pointer;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    font-family: inherit;
    transition: background 0.12s, color 0.12s;
  }
  .filter button:hover { color: var(--p-text); }
  .filter button[aria-pressed="true"] {
    background: var(--p-toggle-active);
    color: var(--p-text);
    box-shadow: 0 1px 2px var(--p-shadow);
  }
  .sort-btn {
    padding: 6px 11px;
    background: var(--p-toggle-bg);
    border: 1px solid var(--p-border);
    border-radius: 6px;
    color: var(--p-muted);
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    font-family: inherit;
    transition: color 0.12s, background 0.12s;
  }
  .sort-btn:hover {
    color: var(--p-text);
    background: var(--p-toggle-active);
  }
  main { padding: 26px 40px 48px; }
  #cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 14px;
  }
  .card {
    background: var(--p-card-bg);
    border: 1px solid var(--p-border);
    border-radius: 8px;
    padding: 13px 15px 11px;
    display: flex;
    flex-direction: column;
    transition: box-shadow 0.15s, transform 0.15s;
  }
  .card:hover {
    box-shadow: 0 4px 12px var(--p-shadow);
    transform: translateY(-1px);
  }
  .card.pdf-only {
    background: var(--p-card-alt);
  }
  .card-top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }
  .badge {
    font-size: 11px;
    background: var(--p-accent);
    color: #fff;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
    letter-spacing: 0.4px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }
  .short {
    color: var(--p-muted);
    font-size: 12px;
    font-weight: 500;
  }
  .title {
    font-size: 14.5px;
    font-weight: 600;
    color: var(--p-dark);
    margin: 0 0 10px;
    line-height: 1.4;
    flex: 1;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: auto;
  }
  .actions a {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 5px 9px;
    background: var(--p-light);
    color: var(--p-dark);
    border: 1px solid var(--p-border);
    border-radius: 4px;
    text-decoration: none;
    font-size: 12px;
    font-weight: 500;
    transition: background 0.12s, border-color 0.12s;
  }
  .actions a:hover {
    background: var(--p-primary);
    border-color: var(--p-accent);
  }
  /* per-artifact chip: the action link with a tiny ✕ that floats over its
     top-right corner ONLY on hover. Absolutely positioned so it never adds
     width/height — the action row keeps its single-line layout. */
  .art { position: relative; display: inline-flex; }
  .art-del {
    position: absolute; top: -7px; right: -7px;
    width: 17px; height: 17px; padding: 0;
    display: inline-flex; align-items: center; justify-content: center;
    border: 1px solid var(--p-border); border-radius: 999px;
    background: var(--p-light); color: var(--p-muted);
    cursor: pointer; font-size: 10px; line-height: 1;
    opacity: 0; transform: scale(0.8);
    transition: opacity .12s, transform .12s, background .12s, color .12s, border-color .12s;
  }
  .art:hover .art-del, .art-del:focus-visible { opacity: 1; transform: scale(1); }
  .art-del:hover { background: #b3402f; color: #fff; border-color: #b3402f; }
  /* ghost chip to upload a missing artifact (analysis / slide) */
  .art-up {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 9px; font-family: inherit; font-size: 12px; font-weight: 500;
    background: transparent; color: var(--p-muted);
    border: 1px dashed var(--p-border); border-radius: 4px; cursor: pointer;
    transition: color .12s, border-color .12s;
  }
  .art-up:hover { color: var(--p-accent); border-color: var(--p-accent); }
  /* missing bilingual → generate via DualTrans; same ghost look as .art-up */
  .art-dt {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 9px; font-family: inherit; font-size: 12px; font-weight: 500;
    background: transparent; color: var(--p-muted);
    border: 1px dashed var(--p-border); border-radius: 4px; cursor: pointer;
    transition: color .12s, border-color .12s;
  }
  .art-dt:hover { color: var(--p-accent); border-color: var(--p-accent); }
  .art-dt:disabled { cursor: progress; opacity: .85; }
  .empty {
    color: var(--p-muted);
    font-size: 14px;
    grid-column: 1 / -1;
    text-align: center;
    padding: 40px;
  }
  /* delete button (top-right of each card) — gated by admin password server-side */
  .card-del {
    margin-left: auto;
    border: 0; background: transparent; cursor: pointer;
    color: var(--p-muted); font-size: 14px; line-height: 1;
    padding: 2px 4px; border-radius: 4px;
    opacity: 0.45; transition: opacity 0.12s, color 0.12s, background 0.12s;
  }
  .card:hover .card-del { opacity: 1; }
  .card-del:hover { color: #fff; background: #b3402f; }
  /* per-card tags row */
  .card-tags {
    display: flex; flex-wrap: wrap; gap: 5px; align-items: center;
    margin: 0 0 10px;
  }
  .ctag {
    display: inline-flex; align-items: center; gap: 3px;
    font-size: 11px; font-weight: 600;
    padding: 2px 4px 2px 8px;
    background: rgba(201, 108, 73, 0.16);     /* accent 淡色底，凸顯標籤 */
    border: 1px solid rgba(201, 108, 73, 0.42);
    border-radius: 999px;
    color: var(--p-accent);
  }
  .ctag-x {
    border: 0; background: transparent; cursor: pointer;
    color: var(--p-accent); opacity: 0.65; font-size: 13px; line-height: 1;
    padding: 0 2px; border-radius: 999px;
  }
  .ctag-x:hover { opacity: 1; }
  .ctag-add {
    font-family: inherit; font-size: 11px; font-weight: 600;
    padding: 2px 9px; cursor: pointer;
    background: transparent; color: var(--p-muted);
    border: 1px dashed var(--p-border); border-radius: 999px;
    transition: color 0.12s, border-color 0.12s;
  }
  .ctag-add:hover { color: var(--p-accent); border-color: var(--p-accent); }
  .ctag-input {
    width: 110px; padding: 2px 8px; font: inherit; font-size: 11px;
    border: 1px solid var(--p-accent); border-radius: 999px;
    background: var(--p-light); color: var(--p-text); outline: none;
  }
  /* tag-filter bar: its OWN full-width row under the controls, left-aligned to
     the controls' left edge. The dropdown sits at the left and active chips
     run rightward across the whole width — lots of room when many are picked. */
  .tagbar {
    flex: 1 0 100%;
    display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
    margin: 0;
  }
  .tagbar[hidden] { display: none; }
  .tag-dd { position: relative; }
  .tag-filter-btn {
    font-family: inherit; font-size: 12px; font-weight: 600;
    padding: 7px 12px; cursor: pointer;
    background: var(--p-toggle-bg); color: var(--p-dark);
    border: 1px solid var(--p-border); border-radius: 6px;
    transition: border-color 0.12s;
  }
  .tag-filter-btn:hover { border-color: var(--p-accent); }
  .tag-menu {
    position: absolute; top: calc(100% + 6px); left: 0; z-index: 30;
    min-width: 200px; max-height: 320px; overflow-y: auto;
    padding: 6px;
    background: var(--p-card-bg);
    border: 1px solid var(--p-border); border-radius: 8px;
    box-shadow: 0 8px 26px var(--p-shadow);
  }
  .tag-menu[hidden] { display: none; }
  .tag-opt {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 8px; border-radius: 6px; cursor: pointer; font-size: 13px;
  }
  .tag-opt:hover { background: var(--p-toggle-bg); }
  .tag-opt input { margin: 0; cursor: pointer; }
  .tag-empty { padding: 8px 10px; color: var(--p-muted); font-size: 12px; }
  .tag-active { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .tag-active .ctag { background: var(--p-accent); color: #fff; border-color: var(--p-accent); }
  .tag-active .ctag-x { color: rgba(255, 255, 255, 0.85); }
  .tag-active .ctag-x:hover { color: #fff; }
  .tag-clear {
    font-family: inherit; font-size: 11px; cursor: pointer;
    background: transparent; border: 0; color: var(--p-muted);
    text-decoration: underline;
  }
  .tag-clear:hover { color: var(--p-accent); }
  /* ---- import-paper modal (search arXiv → download → new block) ---- */
  .modal-backdrop {
    position: fixed; inset: 0; z-index: 100;
    display: flex; align-items: flex-start; justify-content: center;
    padding: 8vh 16px 16px;
    background: rgba(0, 0, 0, 0.45);
  }
  .modal-backdrop[hidden] { display: none; }
  .modal {
    width: 100%; max-width: 620px; max-height: 84vh;
    display: flex; flex-direction: column;
    background: var(--p-light); color: var(--p-text);
    border: 1px solid var(--p-border); border-radius: 12px;
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
    overflow: hidden;
  }
  .modal-head {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 18px; border-bottom: 1px solid var(--p-border);
    background: var(--p-primary);
  }
  .modal-head h2 {
    margin: 0; font-size: 16px; color: var(--p-dark); flex: 1;
    letter-spacing: 0.3px;
  }
  .modal-x {
    border: 0; background: transparent; cursor: pointer;
    color: var(--p-muted); font-size: 22px; line-height: 1; padding: 2px 6px;
    border-radius: 6px;
  }
  .modal-x:hover { color: var(--p-text); background: var(--p-toggle-bg); }
  .modal-body { padding: 16px 18px; overflow-y: auto; }
  .import-search { display: flex; gap: 8px; }
  .import-search input {
    flex: 1 1 auto; padding: 9px 13px; font-size: 14px;
    border: 2px solid var(--p-accent); border-radius: 6px;
    background: var(--p-card-bg); color: var(--p-text); outline: none;
  }
  .import-search input:focus { box-shadow: 0 0 0 3px var(--p-focus); }
  .modal-btn {
    flex: 0 0 auto; padding: 9px 16px; cursor: pointer;
    font-family: inherit; font-size: 13px; font-weight: 600;
    background: var(--p-accent); color: #fff; border: 0; border-radius: 6px;
    transition: opacity 0.12s;
  }
  .modal-btn:hover { opacity: 0.9; }
  .modal-btn:disabled { opacity: 0.5; cursor: default; }
  .imp-sec { margin-top: 16px; }
  .imp-sec:first-of-type { margin-top: 2px; }
  .imp-label {
    font-size: 12px; font-weight: 600; color: var(--p-muted);
    margin-bottom: 7px; letter-spacing: 0.3px;
  }
  .imp-msg { font-size: 12px; color: var(--p-muted); margin-top: 8px; min-height: 1em; }
  .imp-msg.err { color: #d06a52; }
  .modal-btn.ghost {
    background: transparent; color: var(--p-dark);
    border: 1px dashed var(--p-border);
  }
  .modal-btn.ghost:hover { color: var(--p-accent); border-color: var(--p-accent); opacity: 1; }
  .imp-file { font-size: 12px; color: var(--p-muted); margin-left: 10px; }
  /* drag-and-drop PDF upload box */
  .imp-drop {
    margin-top: 4px; padding: 20px 14px; cursor: pointer; text-align: center;
    border: 1.5px dashed var(--p-border); border-radius: 8px;
    background: var(--p-card-bg);
    transition: border-color .12s, background .12s;
  }
  .imp-drop:hover, .imp-drop:focus-visible { border-color: var(--p-accent); outline: none; }
  .imp-drop.dragover { border-color: var(--p-accent); background: rgba(201, 108, 73, 0.10); }
  .imp-drop-main { font-size: 13px; font-weight: 500; color: var(--p-dark); }
  .imp-drop-sub { font-size: 12px; color: var(--p-muted); margin-top: 5px; }
  .imp-drop-btn {
    background: transparent; border: 0; padding: 0; cursor: pointer;
    font: inherit; font-size: 12px; color: var(--p-accent); text-decoration: underline;
  }
  .imp-drop .imp-file { display: block; margin: 9px 0 0; color: var(--p-accent); font-weight: 500; }
  .imp-drop .imp-file.err { color: #d06a52; }
  /* shared confirm (yymm + title) shown after 取得 / picking a file */
  .imp-confirm { margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--p-border); }
  .imp-confirm[hidden] { display: none; }
  .imp-confirm-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .imp-confirm-row label { font-size: 12px; color: var(--p-muted); }
  .f-yymm {
    width: 76px; padding: 7px 9px; font: inherit; font-size: 13px;
    border: 1px solid var(--p-border); border-radius: 6px;
    background: var(--p-light); color: var(--p-text);
  }
  .f-title {
    flex: 1 1 220px; min-width: 150px; padding: 7px 9px; font: inherit; font-size: 13px;
    border: 1px solid var(--p-border); border-radius: 6px;
    background: var(--p-light); color: var(--p-text);
  }
  .imp-confirm-foot { display: flex; align-items: center; gap: 10px; margin-top: 12px; }
  .imp-confirm-foot .imp-msg { margin-top: 0; flex: 1; }
  .imp-confirm-foot .modal-btn { margin-left: auto; }
  /* generic confirm dialog (reuses .modal*) — replaces native confirm/prompt */
  .modal.dlg { max-width: 440px; }
  .dlg-msg { font-size: 13.5px; line-height: 1.6; color: var(--p-text); white-space: pre-line; }
  .dlg-pw-row { margin-top: 14px; display: flex; flex-direction: column; gap: 6px; }
  .dlg-pw-row[hidden] { display: none; }   /* class display:flex would defeat [hidden] otherwise */
  .dlg-pw-row label { font-size: 12px; color: var(--p-muted); }
  .dlg-pw-row input {
    width: 100%; padding: 8px 10px; font: inherit; font-size: 13px;
    border: 1px solid var(--p-border); border-radius: 6px;
    background: var(--p-light); color: var(--p-text); outline: none;
  }
  .dlg-pw-row input:focus { border-color: var(--p-accent); box-shadow: 0 0 0 3px var(--p-focus); }
  /* DualTrans common settings inside the confirm dialog */
  .dlg-dt { margin-top: 16px; display: flex; flex-direction: column; gap: 12px; }
  .dlg-dt[hidden] { display: none; }
  .dlg-dt-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .dlg-dt-row > label { font-size: 12px; color: var(--p-muted); min-width: 118px; }
  .dlg-dt-row input[list] {
    flex: 1 1 140px; padding: 7px 9px; font: inherit; font-size: 13px;
    border: 1px solid var(--p-border); border-radius: 6px;
    background: var(--p-light); color: var(--p-text); outline: none;
  }
  .dlg-dt-row input[list]:focus { border-color: var(--p-accent); box-shadow: 0 0 0 3px var(--p-focus); }
  .dlg-seg { display: inline-flex; padding: 3px; gap: 2px; background: var(--p-toggle-bg); border: 1px solid var(--p-border); border-radius: 6px; }
  .dlg-seg button {
    padding: 5px 11px; border: 0; background: transparent; color: var(--p-muted);
    cursor: pointer; border-radius: 4px; font-size: 12px; font-weight: 500; font-family: inherit;
    transition: background .12s, color .12s;
  }
  .dlg-seg button:hover { color: var(--p-text); }
  .dlg-seg button[aria-pressed="true"] { background: var(--p-toggle-active); color: var(--p-text); box-shadow: 0 1px 2px var(--p-shadow); }
  .dlg-check { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; color: var(--p-text); cursor: pointer; }
  .dlg-check input { cursor: pointer; }
  .dlg-foot { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
  .modal-btn.danger { background: #b3402f; }
  .modal-btn.danger:hover { background: #9a3526; opacity: 1; }
  .section-head {
    grid-column: 1 / -1;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: var(--p-muted);
    padding: 10px 2px 6px;
    margin-top: 4px;
    border-bottom: 1px solid var(--p-border);
    position: sticky;
    top: var(--header-h, 64px);
    background: var(--p-light);
    z-index: 5;
  }
  .section-head:first-child {
    margin-top: 0;
    padding-top: 2px;
  }
  @media (max-width: 760px) {
    header {
      display: block;
      padding: 16px 18px;
      position: relative;
    }
    .theme-toggle {
      position: absolute;
      top: 14px;
      right: 14px;
    }
    .controls { margin-top: 12px; }
    main { padding-left: 18px; padding-right: 18px; }
    #cards { grid-template-columns: 1fr; }
    .section-head { top: 0; }
  }
</style>
<script>
  (function () {
    const mode = localStorage.getItem("phyra-archbase-theme") || "system";
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const actual = mode === "system" ? (prefersDark ? "dark" : "light") : mode;
    document.documentElement.setAttribute("data-theme", actual);
  })();
</script>
</head>
<body>
<div class="hub-bar">
  <a class="hub-link" id="hub-center" href="#"><span class="hub-arrow">←</span> <span class="hub-brand">🜂 Phyra Center</span></a>
</div>
<header>
  <div class="hdr-left">
    <h1>Phyra ArchBase</h1>
    <div class="stats">__TOTAL__ papers · __FULLY__ fully analyzed</div>
  </div>
  <div class="controls">
    <div class="search-col">
      <div class="search-row">
        <button type="button" id="add-paper" class="add-btn" title="搜尋並匯入論文" aria-label="新增論文">
          <svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
        </button>
        <input type="search" id="search" placeholder="Filter by title or short name… (press /)" autocomplete="off">
      </div>
    </div>
    <div class="filter" role="group" aria-label="Filter">
      <button type="button" data-filter="all" aria-pressed="true">All</button>
      <button type="button" data-filter="analyzed" aria-pressed="false">Analyzed</button>
      <button type="button" data-filter="bilingual" aria-pressed="false">Bilingual</button>
      <button type="button" data-filter="pending" aria-pressed="false">PDF only</button>
    </div>
    <button type="button" id="sort-btn" class="sort-btn" title="Sort"></button>
    <div class="tagbar" id="tagbar" hidden>
      <div class="tag-dd">
        <button type="button" id="tag-dd-btn" class="tag-filter-btn">🏷 依標籤篩選 ▾</button>
        <div class="tag-menu" id="tag-menu" hidden></div>
      </div>
      <div class="tag-active" id="tag-active"></div>
    </div>
  </div>
  <div class="theme-toggle" role="group" aria-label="Appearance">
    <button type="button" data-mode="system" title="System" aria-label="System">
      <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
    </button>
    <button type="button" data-mode="light" title="Light" aria-label="Light">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
    </button>
    <button type="button" data-mode="dark" title="Dark" aria-label="Dark">
      <svg viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
  </div>
</header>
<main>
  <datalist id="all-tags-list"></datalist>
  <div id="cards"></div>
</main>
<div class="modal-backdrop" id="import-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-label="新增論文">
    <div class="modal-head">
      <h2>＋ 新增論文</h2>
      <button type="button" class="modal-x" id="import-close" aria-label="關閉">×</button>
    </div>
    <div class="modal-body">
      <div class="imp-sec">
        <div class="imp-label">從 arXiv 連結 / id</div>
        <div class="import-search">
          <input type="text" id="import-ref" placeholder="https://arxiv.org/abs/2401.12345　或　2401.12345" autocomplete="off">
          <button type="button" id="import-fetch" class="modal-btn">取得</button>
        </div>
        <div class="imp-msg" id="arxiv-msg"></div>
      </div>
      <div class="imp-sec">
        <div class="imp-label">或 上傳 PDF</div>
        <div class="imp-drop" id="import-drop" tabindex="0" role="button" aria-label="拖曳或選擇 PDF 檔">
          <div class="imp-drop-main">拖曳 PDF 到此</div>
          <div class="imp-drop-sub">或 <button type="button" id="import-pick" class="imp-drop-btn">選擇檔案</button></div>
          <span class="imp-file" id="import-fname"></span>
        </div>
        <input type="file" id="import-file" accept=".pdf,application/pdf" hidden>
      </div>
      <div class="imp-confirm" id="imp-confirm" hidden>
        <div class="imp-label">確認資訊（YYMM + 標題）</div>
        <div class="imp-confirm-row">
          <label>YYMM</label>
          <input class="f-yymm" id="imp-yymm" maxlength="4" placeholder="2401">
          <input class="f-title" id="imp-title" placeholder="論文標題">
        </div>
        <div class="imp-confirm-foot">
          <span class="imp-msg" id="imp-msg"></span>
          <button type="button" id="imp-do" class="modal-btn">匯入</button>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="modal-backdrop" id="dlg-backdrop" hidden>
  <div class="modal dlg" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2 id="dlg-title"></h2>
      <button type="button" class="modal-x" id="dlg-x" aria-label="關閉">×</button>
    </div>
    <div class="modal-body">
      <div class="dlg-msg" id="dlg-msg"></div>
      <div class="dlg-dt" id="dlg-dt" hidden>
        <div class="dlg-dt-row">
          <label for="dlg-lang">Target language</label>
          <input id="dlg-lang" list="dlg-lang-list" value="zh-TW" autocomplete="off">
          <datalist id="dlg-lang-list">
            <option value="zh-TW"></option><option value="zh-HK"></option>
            <option value="zh-CN"></option><option value="ja"></option><option value="ko"></option>
          </datalist>
        </div>
        <div class="dlg-dt-row">
          <label>Compression</label>
          <div class="dlg-seg" id="dlg-compress" role="group">
            <button type="button" data-v="off">off</button>
            <button type="button" data-v="lossless">lossless</button>
            <button type="button" data-v="lossy" aria-pressed="true">lossy</button>
          </div>
        </div>
        <label class="dlg-check"><input type="checkbox" id="dlg-compat"><span>Enhance compatibility</span></label>
      </div>
      <div class="dlg-pw-row" id="dlg-pw-row" hidden>
        <label id="dlg-pw-label">管理員密碼</label>
        <input type="password" id="dlg-pw" autocomplete="current-password">
      </div>
      <div class="dlg-foot">
        <button type="button" class="modal-btn ghost" id="dlg-cancel">取消</button>
        <button type="button" class="modal-btn" id="dlg-ok">確定</button>
      </div>
    </div>
  </div>
</div>
<script>
const PAPERS = __DATA__;
let TAGS = {};                       // { paperKey: [tag, …] } — fetched from /api/tags
const selectedTags = new Set();      // tags currently chosen in the filter dropdown
const ADMIN_PW_KEY = "phyra-archbase-admin-pw";   // sessionStorage; remembered per browser session

// "← 返回 Phyra Center" link. Built from THIS browser's hostname so the
// same generated page works locally and over the LAN; the Center port is
// baked at generation time (PHYRA_CENTER_PORT, default 8035).
(function () {
  const l = document.getElementById("hub-center");
  if (l) l.href = location.protocol + "//" + location.hostname + ":__CENTER_PORT__/";
})();

// Keep the sticky date/letter section headers flush under the (also-sticky)
// page header, whatever its current height — it wraps taller on narrow screens.
(function () {
  const header = document.querySelector("header");
  if (!header) return;
  const setH = () => document.documentElement.style.setProperty(
    "--header-h", header.offsetHeight + "px");
  setH();
  window.addEventListener("resize", setH);
  // The tag bar lives inside the (sticky) header and toggles visibility once
  // tags load, changing the header's height — keep the section-head offset
  // in sync so date/letter headers never tuck under or float below it.
  if (window.ResizeObserver) new ResizeObserver(setH).observe(header);
})();

function enc(name) { return "collection/" + encodeURIComponent(name); }

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => (
    {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]
  ));
}

/* ---- reusable styled dialog (replaces native confirm/prompt) ---------- */
const _dlg = {
  backdrop: document.getElementById("dlg-backdrop"),
  title:    document.getElementById("dlg-title"),
  msg:      document.getElementById("dlg-msg"),
  dtBox:    document.getElementById("dlg-dt"),
  lang:     document.getElementById("dlg-lang"),
  compress: document.getElementById("dlg-compress"),
  compat:   document.getElementById("dlg-compat"),
  pwRow:    document.getElementById("dlg-pw-row"),
  pwLabel:  document.getElementById("dlg-pw-label"),
  pw:       document.getElementById("dlg-pw"),
  ok:       document.getElementById("dlg-ok"),
  cancel:   document.getElementById("dlg-cancel"),
  x:        document.getElementById("dlg-x"),
};
let _dlgResolve = null;

// compression segmented control (single-select)
_dlg.compress.addEventListener("click", (e) => {
  const b = e.target.closest("button[data-v]");
  if (!b) return;
  _dlg.compress.querySelectorAll("button").forEach(
    x => x.setAttribute("aria-pressed", x === b));
});

// openDialog(opts) → Promise. Resolves to: null if cancelled; the entered
// password string when opts.password; otherwise true. opts: {title, message,
// confirmLabel, danger, password, passwordLabel}.
function openDialog(opts) {
  return new Promise((resolve) => {
    _dlgResolve = resolve;
    _dlg.title.textContent = opts.title || "";
    _dlg.msg.textContent = opts.message || "";
    _dlg.ok.textContent = opts.confirmLabel || "確定";
    _dlg.ok.classList.toggle("danger", !!opts.danger);
    const needPw = !!opts.password;
    _dlg.pwRow.hidden = !needPw;
    _dlg.pw.value = "";
    if (needPw) _dlg.pwLabel.textContent = opts.passwordLabel || "管理員密碼";
    const dt = !!opts.dtOptions;             // show common translation settings
    _dlg.dtBox.hidden = !dt;
    if (dt) {
      _dlg.lang.value = "zh-TW";
      _dlg.compat.checked = false;
      _dlg.compress.querySelectorAll("button").forEach(
        x => x.setAttribute("aria-pressed", x.dataset.v === "lossy"));
    }
    _dlg.cancel.hidden = !!opts.info;       // info dialogs show only the confirm button
    _dlg.backdrop.hidden = false;
    setTimeout(() => (needPw ? _dlg.pw : _dlg.ok).focus(), 0);
  });
}
function _closeDialog(result) {
  _dlg.backdrop.hidden = true;
  _dlg.ok.classList.remove("danger");
  const r = _dlgResolve; _dlgResolve = null;
  if (r) r(result);
}
_dlg.cancel.addEventListener("click", () => _closeDialog(null));
_dlg.x.addEventListener("click", () => _closeDialog(null));
_dlg.backdrop.addEventListener("click", (e) => { if (e.target === _dlg.backdrop) _closeDialog(null); });
_dlg.ok.addEventListener("click", () => {
  if (!_dlg.pwRow.hidden) {
    const pw = _dlg.pw.value;
    if (!pw) { _dlg.pw.focus(); return; }   // a password is required
    _closeDialog(pw);
  } else if (!_dlg.dtBox.hidden) {
    const seg = _dlg.compress.querySelector('button[aria-pressed="true"]');
    _closeDialog({
      lang_out: (_dlg.lang.value || "zh-TW").trim() || "zh-TW",
      compress: seg ? seg.dataset.v : "lossy",
      compat: _dlg.compat.checked,
    });
  } else {
    _closeDialog(true);
  }
});
_dlg.pw.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); _dlg.ok.click(); } });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !_dlg.backdrop.hidden) { e.stopPropagation(); _closeDialog(null); }
});

const ART_LABEL  = { bilingual: "雙語", analysis: "Analysis", slide: "Slide" };
const ART_ACCEPT = { analysis: ".html,.md", slide: ".html" };

function artChip(href, label, kind, key) {
  return `<span class="art"><a href="${href}" target="_blank">${label}</a>` +
    `<button class="art-del" data-key="${escapeHtml(key)}" data-kind="${kind}" ` +
    `title="刪除此 ${ART_LABEL[kind]} 檔" aria-label="刪除">✕</button></span>`;
}
function uploadChip(kind, key) {
  return `<button class="art-up" data-key="${escapeHtml(key)}" data-kind="${kind}" ` +
    `title="上傳 ${ART_LABEL[kind]} 檔">⤒ ${ART_LABEL[kind]}</button>`;
}
function dualtransChip(key) {
  return `<button class="art-dt" data-key="${escapeHtml(key)}" ` +
    `title="用 Phyra DualTrans 產生雙語對照 PDF 並存回此處">🌐 雙語</button>`;
}

function cardHtml(p) {
  const f = p.files || {};
  const btn = [];
  if (f.original_pdf) btn.push(`<a href="${enc(f.original_pdf)}" target="_blank">📄 PDF</a>`);
  // analysis / slide: a deletable chip when present, an upload chip when not
  btn.push(f.analysis_html
    ? artChip(enc(f.analysis_html), "📖 Analysis", "analysis", p.key)
    : uploadChip("analysis", p.key));
  btn.push(f.draftslide_html
    ? artChip(enc(f.draftslide_html), "🎞 Slide", "slide", p.key)
    : uploadChip("slide", p.key));
  // bilingual: deletable when present; otherwise offer one-click DualTrans
  if (f.bilingual_pdf) btn.push(artChip(enc(f.bilingual_pdf), "🌐 雙語", "bilingual", p.key));
  else if (f.original_pdf) btn.push(dualtransChip(p.key));
  const pdfOnly = !f.analysis_html && !f.draftslide_html && !f.bilingual_pdf;
  const titleEq = p.short && p.title && p.short.toLowerCase() === p.title.toLowerCase();
  const shortHtml = (p.short && !titleEq)
    ? `<span class="short">${escapeHtml(p.short)}</span>` : '';
  const title = p.title || p.short || p.key;
  const tags = TAGS[p.key] || [];
  const chips = tags.map(t =>
    `<span class="ctag">${escapeHtml(t)}<button class="ctag-x" data-tag="${escapeHtml(t)}" title="移除標籤" aria-label="移除">×</button></span>`).join('');
  return `<div class="card${pdfOnly ? ' pdf-only' : ''}">
    <div class="card-top">
      <span class="badge">${escapeHtml(p.yymm)}</span>
      ${shortHtml}
      <button class="card-del" data-key="${escapeHtml(p.key)}" data-title="${escapeHtml(title)}" title="從論文庫刪除" aria-label="刪除">🗑</button>
    </div>
    <h3 class="title">${escapeHtml(title)}</h3>
    <div class="card-tags" data-key="${escapeHtml(p.key)}">
      ${chips}
      <button class="ctag-add" type="button">＋ 標籤</button>
    </div>
    <div class="actions">${btn.join('')}</div>
  </div>`;
}

function sectionFor(p, mode) {
  if (mode === "title-asc") {
    const t = (p.title || p.short || '').trim();
    const ch = t.charAt(0).toUpperCase();
    if (ch >= 'A' && ch <= 'Z') return { key: ch, label: ch };
    return { key: '#', label: '#' };
  }
  const y = p.yymm || '';
  if (/^\d{4}$/.test(y)) {
    return { key: y, label: '20' + y.slice(0, 2) + ' · ' + y.slice(2) };
  }
  return { key: y || '?', label: y || '?' };
}

function render(list) {
  const root = document.getElementById("cards");
  if (!list.length) {
    root.innerHTML = '<div class="empty">No matches</div>';
    return;
  }
  const parts = [];
  let lastKey = null;
  for (const p of list) {
    const sec = sectionFor(p, sortMode);
    if (sec.key !== lastKey) {
      parts.push(`<div class="section-head">${escapeHtml(sec.label)}</div>`);
      lastKey = sec.key;
    }
    parts.push(cardHtml(p));
  }
  root.innerHTML = parts.join('');
}

const themeToggle = document.querySelector(".theme-toggle");
const themeButtons = themeToggle.querySelectorAll("button[data-mode]");
const prefersDarkMQ = window.matchMedia("(prefers-color-scheme: dark)");
let themeMode = localStorage.getItem("phyra-archbase-theme") || "system";

function resolveActual(mode) {
  if (mode === "system") return prefersDarkMQ.matches ? "dark" : "light";
  return mode;
}
function applyTheme(mode) {
  themeMode = mode;
  document.documentElement.setAttribute("data-theme", resolveActual(mode));
  themeButtons.forEach(b => b.setAttribute("aria-pressed", b.dataset.mode === mode));
  localStorage.setItem("phyra-archbase-theme", mode);
}
themeButtons.forEach(b => {
  b.addEventListener("click", () => applyTheme(b.dataset.mode));
});
prefersDarkMQ.addEventListener?.("change", () => {
  if (themeMode === "system") applyTheme("system");
});
applyTheme(themeMode);

const search = document.getElementById("search");
const filterButtons = document.querySelectorAll(".filter button[data-filter]");
const sortBtn = document.getElementById("sort-btn");

let filterMode = "all";       // all | analyzed | bilingual | pending
let sortMode = "date-desc";   // date-desc | date-asc | title-asc
const SORT_ORDER = ["date-desc", "date-asc", "title-asc"];
const SORT_LABELS = {
  "date-desc": "↓ Date",
  "date-asc":  "↑ Date",
  "title-asc": "A→Z",
};

function isAnalyzed(p) {
  const f = p.files || {};
  return !!(f.analysis_html || f.draftslide_html || f.bilingual_pdf);
}
function isBilingual(p) { return !!(p.files && p.files.bilingual_pdf); }

function applyFilters() {
  const q = search.value.trim().toLowerCase();
  let list = PAPERS.filter(p => {
    if (filterMode === "analyzed"  && !isAnalyzed(p))  return false;
    if (filterMode === "bilingual" && !isBilingual(p)) return false;
    if (filterMode === "pending"   &&  isAnalyzed(p))  return false;
    if (selectedTags.size) {
      const tg = TAGS[p.key] || [];           // OR: keep papers having ANY selected tag
      if (![...selectedTags].some(t => tg.includes(t))) return false;
    }
    if (q) {
      const t = (p.title || '').toLowerCase();
      const s = (p.short || '').toLowerCase();
      if (!t.includes(q) && !s.includes(q)) return false;
    }
    return true;
  });
  list.sort((a, b) => {
    if (sortMode === "title-asc") {
      return (a.title || '').localeCompare(b.title || '');
    }
    const da = parseInt(a.yymm, 10) || 0;
    const db = parseInt(b.yymm, 10) || 0;
    const tieBreak = (a.short || a.title || '').localeCompare(b.short || b.title || '');
    return sortMode === "date-asc" ? (da - db || tieBreak) : (db - da || tieBreak);
  });
  render(list);
}

filterButtons.forEach(b => {
  b.addEventListener("click", () => {
    filterMode = b.dataset.filter;
    filterButtons.forEach(x => x.setAttribute("aria-pressed", x.dataset.filter === filterMode));
    applyFilters();
  });
});

sortBtn.addEventListener("click", () => {
  const i = SORT_ORDER.indexOf(sortMode);
  sortMode = SORT_ORDER[(i + 1) % SORT_ORDER.length];
  sortBtn.textContent = SORT_LABELS[sortMode];
  applyFilters();
});
sortBtn.textContent = SORT_LABELS[sortMode];

search.addEventListener("input", applyFilters);

document.addEventListener("keydown", (e) => {
  const tag = (document.activeElement && document.activeElement.tagName) || "";
  const inField = tag === "INPUT" || tag === "TEXTAREA";
  if (e.key === "/" && !inField) {
    e.preventDefault();
    search.focus();
    search.select();
  } else if (e.key === "Escape" && document.activeElement === search) {
    if (search.value) {
      search.value = "";
      applyFilters();
    } else {
      search.blur();
    }
  }
});

/* ---- tags + delete ---------------------------------------------------- */
const cardsRoot = document.getElementById("cards");
const tagbar = document.getElementById("tagbar");
const tagMenu = document.getElementById("tag-menu");
const tagMenuBtn = document.getElementById("tag-dd-btn");
const tagActive = document.getElementById("tag-active");
const tagDatalist = document.getElementById("all-tags-list");

function allTags() {
  const s = new Set();
  for (const k in TAGS) (TAGS[k] || []).forEach(t => s.add(t));
  return [...s].sort((a, b) => a.localeCompare(b));
}

// rebuild the filter dropdown + datalist whenever the tag universe changes
function rebuildTagUI() {
  const tags = allTags();
  tagbar.hidden = tags.length === 0;
  tagDatalist.innerHTML = tags.map(t => `<option value="${escapeHtml(t)}">`).join("");
  for (const t of [...selectedTags]) if (!tags.includes(t)) selectedTags.delete(t);
  tagMenu.innerHTML = tags.length
    ? tags.map(t =>
        `<label class="tag-opt"><input type="checkbox" value="${escapeHtml(t)}"${selectedTags.has(t) ? " checked" : ""}><span>${escapeHtml(t)}</span></label>`).join("")
    : `<div class="tag-empty">尚無標籤</div>`;
  renderActiveTags();
}

function renderActiveTags() {
  if (!selectedTags.size) { tagActive.innerHTML = ""; return; }
  const chips = [...selectedTags].sort((a, b) => a.localeCompare(b)).map(t =>
    `<span class="ctag">${escapeHtml(t)}<button class="ctag-x" data-unsel="${escapeHtml(t)}" aria-label="取消">×</button></span>`).join("");
  tagActive.innerHTML = chips + `<button type="button" class="tag-clear" id="tag-clear">清除</button>`;
}

tagMenuBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  tagMenu.hidden = !tagMenu.hidden;
});
tagMenu.addEventListener("click", (e) => e.stopPropagation());
tagMenu.addEventListener("change", (e) => {
  const cb = e.target.closest("input[type=checkbox]");
  if (!cb) return;
  if (cb.checked) selectedTags.add(cb.value); else selectedTags.delete(cb.value);
  renderActiveTags();
  applyFilters();
});
tagActive.addEventListener("click", (e) => {
  if (e.target.id === "tag-clear") { selectedTags.clear(); rebuildTagUI(); applyFilters(); return; }
  const x = e.target.closest("[data-unsel]");
  if (x) { selectedTags.delete(x.dataset.unsel); rebuildTagUI(); applyFilters(); }
});
document.addEventListener("click", () => { tagMenu.hidden = true; });

async function postTags(key, tags) {
  try {
    const r = await fetch("/api/tags", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, tags }),
    });
    const res = await r.json();
    if (res && res.ok) {
      if (res.tags && res.tags.length) TAGS[key] = res.tags; else delete TAGS[key];
    } else {
      alert("標籤儲存失敗。");
    }
  } catch (_) {
    alert("標籤儲存失敗（伺服器無回應）。");
  }
  rebuildTagUI();
  applyFilters();
}

function addTag(key, tag) {
  const cur = (TAGS[key] || []).slice();
  if (!cur.some(t => t.toLowerCase() === tag.toLowerCase())) cur.push(tag);
  return postTags(key, cur);
}
function removeTag(key, tag) {
  return postTags(key, (TAGS[key] || []).filter(t => t !== tag));
}

function openTagInput(btn) {
  const row = btn.closest(".card-tags");
  const key = row.dataset.key;
  const wrap = document.createElement("span");
  wrap.innerHTML = `<input class="ctag-input" list="all-tags-list" placeholder="標籤名稱" maxlength="40">`;
  btn.replaceWith(wrap);
  const input = wrap.querySelector("input");
  input.focus();
  let done = false;
  const commit = () => {
    if (done) return; done = true;
    const v = input.value.trim();
    if (v) addTag(key, v); else applyFilters();   // re-render restores the ＋ button
  };
  input.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") { ev.preventDefault(); commit(); }
    else if (ev.key === "Escape") { ev.preventDefault(); done = true; applyFilters(); }
  });
  input.addEventListener("blur", commit);
}

// Shared admin-gated delete flow (whole paper or one artifact). Asks for the
// password in the styled dialog only when it isn't remembered this session.
async function adminDelete({ title, message, endpoint, payload }) {
  const saved = sessionStorage.getItem(ADMIN_PW_KEY) || "";
  const res = await openDialog({
    title, message, confirmLabel: "刪除", danger: true,
    password: !saved, passwordLabel: "管理員密碼",
  });
  if (!res) return;                       // cancelled
  const pw = saved || res;                // res is the typed password when prompted
  let r;
  try {
    r = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, password: pw }),
    });
  } catch (_) {
    await openDialog({ title: "刪除失敗", message: "伺服器無回應。", confirmLabel: "好", info: true });
    return;
  }
  if (r.status === 401) {
    sessionStorage.removeItem(ADMIN_PW_KEY);
    await openDialog({ title: "密碼錯誤", message: "管理員密碼錯誤，請再試一次。", confirmLabel: "好", info: true });
    return;
  }
  if (r.status === 403) {
    const e = await r.json().catch(() => ({}));
    await openDialog({ title: "刪除未啟用", message: e.error || "刪除功能未啟用（啟動時未設定管理員密碼）。", confirmLabel: "好", info: true });
    return;
  }
  if (!r.ok) {
    await openDialog({ title: "刪除失敗", message: await r.text(), confirmLabel: "好", info: true });
    return;
  }
  sessionStorage.setItem(ADMIN_PW_KEY, pw);    // remember for the rest of this session
  location.reload();                            // index.html was regenerated server-side
}

function deletePaper(key, title) {
  return adminDelete({
    title: "刪除論文",
    message: `確定從論文庫刪除「${title}」？\n會移除該論文在 collection/ 的所有檔案（原文 PDF、雙語 PDF、analysis、slide），且無法復原。`,
    endpoint: "/api/delete",
    payload: { key },
  });
}

function deleteArtifact(key, kind) {
  const label = ART_LABEL[kind] || kind;
  return adminDelete({
    title: "刪除檔案",
    message: `確定刪除此論文的「${label}」檔？此操作無法復原。`,
    endpoint: "/api/delete-artifact",
    payload: { key, kind },
  });
}

// Upload a missing analysis/slide file (no password — additive). html/md are
// text, so we send the file content as a JSON string and let the server name
// it by the paper's stem + kind.
function uploadArtifact(key, kind) {
  const inp = document.createElement("input");
  inp.type = "file";
  inp.accept = ART_ACCEPT[kind] || "";
  inp.addEventListener("change", async () => {
    const file = inp.files && inp.files[0];
    if (!file) return;
    let content;
    try { content = await file.text(); }
    catch (_) { alert("讀取檔案失敗。"); return; }
    let r;
    try {
      r = await fetch("/api/upload-artifact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, kind, filename: file.name, content }),
      });
    } catch (_) { alert("上傳失敗（伺服器無回應）。"); return; }
    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      alert("上傳失敗：" + (e.error || r.status));
      return;
    }
    location.reload();
  });
  inp.click();
}

/* ---- one-click DualTrans (generate a missing bilingual PDF) ----------- */
const dtPolling = new Set();   // stems currently being polled

function dtFail(btn, msg) {
  if (btn) { btn.disabled = false; btn.textContent = "🌐 雙語"; }
  openDialog({ title: "DualTrans 失敗", message: String(msg), confirmLabel: "好", info: true });
}

function pollDualtrans(key, btn) {
  if (dtPolling.has(key)) return;
  dtPolling.add(key);
  const tick = async () => {
    let st;
    try { st = await (await fetch("/api/dualtrans/status?key=" + encodeURIComponent(key))).json(); }
    catch (_) { setTimeout(tick, 3000); return; }
    if (st.state === "done") { dtPolling.delete(key); location.reload(); return; }
    if (st.state === "error") { dtPolling.delete(key); dtFail(btn, st.error || "翻譯失敗"); return; }
    if (btn) {
      const pct = st.pct || 0;
      btn.textContent = st.state === "archiving" ? "🌐 寫入中…" : `🌐 翻譯中… ${pct}%`;
    }
    setTimeout(tick, 3000);
  };
  tick();
}

async function startDualtrans(btn) {
  const key = btn.dataset.key;
  if (btn.disabled) return;
  const go = await openDialog({
    title: "雙語翻譯",
    message: "要用 Phyra DualTrans 為這篇論文產生雙語對照 PDF 嗎？\n以下為通用翻譯設定；翻譯會在背景進行，完成後自動存回此處。",
    confirmLabel: "開始翻譯",
    dtOptions: true,
  });
  if (!go) return;                 // null when cancelled; settings object when confirmed
  btn.disabled = true;
  btn.textContent = "🌐 啟動中…";
  let r;
  try {
    r = await fetch("/api/dualtrans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, lang_out: go.lang_out, compress: go.compress, compat: go.compat }),
    });
  } catch (_) { dtFail(btn, "無法連線伺服器"); return; }
  if (!r.ok) { const e = await r.json().catch(() => ({})); dtFail(btn, e.error || r.status); return; }
  const res = await r.json();
  if (res.state === "done") { location.reload(); return; }
  pollDualtrans(key, btn);
}

cardsRoot.addEventListener("click", (e) => {
  const del = e.target.closest(".card-del");
  if (del) { deletePaper(del.dataset.key, del.dataset.title); return; }
  const artDel = e.target.closest(".art-del");
  if (artDel) { deleteArtifact(artDel.dataset.key, artDel.dataset.kind); return; }
  const artUp = e.target.closest(".art-up");
  if (artUp) { uploadArtifact(artUp.dataset.key, artUp.dataset.kind); return; }
  const dt = e.target.closest(".art-dt");
  if (dt) { startDualtrans(dt); return; }
  const x = e.target.closest(".ctag-x");
  if (x) { removeTag(x.closest(".card-tags").dataset.key, x.dataset.tag); return; }
  const add = e.target.closest(".ctag-add");
  if (add) { openTagInput(add); return; }
});

/* ---- import-paper modal (arXiv link or PDF upload → new block) ------- */
const importModal = document.getElementById("import-modal");
const importRef = document.getElementById("import-ref");
const importFetch = document.getElementById("import-fetch");
const arxivMsg = document.getElementById("arxiv-msg");
const importPick = document.getElementById("import-pick");
const importFileEl = document.getElementById("import-file");
const importFname = document.getElementById("import-fname");
const impConfirm = document.getElementById("imp-confirm");
const impYymm = document.getElementById("imp-yymm");
const impTitle = document.getElementById("imp-title");
const impMsg = document.getElementById("imp-msg");
const impDo = document.getElementById("imp-do");

let importMode = null;       // 'arxiv' | 'upload'
let importArxivRef = "";     // the link/id being imported
let importPdfFile = null;    // the chosen File

function resetImport() {
  importMode = null; importArxivRef = ""; importPdfFile = null;
  impConfirm.hidden = true;
  importFname.textContent = ""; importFname.classList.remove("err");
  arxivMsg.textContent = ""; arxivMsg.classList.remove("err");
  impMsg.textContent = ""; impMsg.classList.remove("err");
  impYymm.value = ""; impTitle.value = ""; importFileEl.value = "";
}
function openImport() { resetImport(); importModal.hidden = false; importRef.value = ""; importRef.focus(); }
function closeImport() { importModal.hidden = true; }

document.getElementById("add-paper").addEventListener("click", openImport);
document.getElementById("import-close").addEventListener("click", closeImport);
importModal.addEventListener("click", (e) => { if (e.target === importModal) closeImport(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !importModal.hidden) closeImport();
});

function showConfirm(yymm, title) {
  impYymm.value = yymm || "";
  impTitle.value = title || "";
  impMsg.textContent = ""; impMsg.classList.remove("err");
  impConfirm.hidden = false;
}

// A. arXiv link / id → best-effort metadata → confirm
async function fetchArxiv() {
  const ref = importRef.value.trim();
  if (!ref) return;
  importFetch.disabled = true;
  arxivMsg.textContent = "取得中…"; arxivMsg.classList.remove("err");
  let res;
  try {
    res = await (await fetch("/api/arxiv-meta?ref=" + encodeURIComponent(ref))).json();
  } catch (_) {
    arxivMsg.textContent = "取得失敗（伺服器無回應）。"; arxivMsg.classList.add("err");
    importFetch.disabled = false; return;
  }
  importFetch.disabled = false;
  if (!res.ok) { arxivMsg.textContent = res.error || "無法辨識連結。"; arxivMsg.classList.add("err"); return; }
  importMode = "arxiv"; importArxivRef = ref;
  importFname.textContent = "";   // clear the upload path's label
  arxivMsg.textContent = res.title
    ? `已辨識 ${res.arxiv_id}`
    : `已辨識 ${res.arxiv_id}（未取得標題，請手動填寫）`;
  showConfirm(res.yymm, res.title || "");
  impTitle.focus();
}
importFetch.addEventListener("click", fetchArxiv);
importRef.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); fetchArxiv(); } });

// B. upload PDF → confirm (prefill from filename). Source: file picker OR drop.
const importDrop = document.getElementById("import-drop");

function selectPdfFile(f) {
  if (!f) return;
  if (!/\.pdf$/i.test(f.name) && f.type !== "application/pdf") {
    importFname.textContent = "請選擇 PDF 檔案";
    importFname.classList.add("err");
    return;
  }
  importFname.classList.remove("err");
  importMode = "upload"; importPdfFile = f;
  importFname.textContent = f.name;
  arxivMsg.textContent = "";      // clear the arXiv path's message
  const base = f.name.replace(/\.pdf$/i, "");
  const m = base.match(/^(\d{4})_(.*)$/);     // "2401_Some_Title.pdf"
  const yymm = m ? m[1] : "";
  const title = (m ? m[2] : base).replace(/__/g, ": ").replace(/_/g, " ").trim();
  showConfirm(yymm, title);
  impTitle.focus();
}

importPick.addEventListener("click", (e) => { e.stopPropagation(); importFileEl.click(); });
importDrop.addEventListener("click", () => importFileEl.click());
importDrop.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); importFileEl.click(); }
});
importFileEl.addEventListener("change", () => selectPdfFile(importFileEl.files && importFileEl.files[0]));

["dragenter", "dragover"].forEach(ev => importDrop.addEventListener(ev, (e) => {
  e.preventDefault(); e.stopPropagation(); importDrop.classList.add("dragover");
}));
["dragleave", "dragend", "drop"].forEach(ev => importDrop.addEventListener(ev, (e) => {
  e.preventDefault(); e.stopPropagation(); importDrop.classList.remove("dragover");
}));
importDrop.addEventListener("drop", (e) => {
  const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
  selectPdfFile(f);
});

// shared: 匯入
async function doImport() {
  const yymm = impYymm.value.trim();
  const title = impTitle.value.trim();
  if (!/^\d{4}$/.test(yymm)) { impMsg.textContent = "YYMM 需為 4 位數字。"; impMsg.classList.add("err"); return; }
  if (!title) { impMsg.textContent = "標題不可為空。"; impMsg.classList.add("err"); return; }
  impDo.disabled = true; impMsg.classList.remove("err");
  impMsg.textContent = importMode === "upload" ? "上傳中…" : "下載中…";
  let res;
  try {
    if (importMode === "arxiv") {
      res = await fetch("/api/import-arxiv", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ref: importArxivRef, yymm, title }),
      });
    } else if (importMode === "upload") {
      const qs = "yymm=" + encodeURIComponent(yymm) + "&title=" + encodeURIComponent(title);
      res = await fetch("/api/import-upload?" + qs, {
        method: "POST", headers: { "Content-Type": "application/pdf" },
        body: importPdfFile,
      });
    } else {
      impMsg.textContent = "請先貼上 arXiv 連結或選擇 PDF。"; impMsg.classList.add("err");
      impDo.disabled = false; return;
    }
  } catch (_) {
    impMsg.textContent = "匯入失敗（伺服器無回應）。"; impMsg.classList.add("err");
    impDo.disabled = false; return;
  }
  const j = await res.json().catch(() => ({}));
  if (!res.ok || !j.ok) {
    impMsg.textContent = "匯入失敗：" + (j.error || res.status); impMsg.classList.add("err");
    impDo.disabled = false; return;
  }
  location.reload();   // index regenerated server-side; the new block appears
}
impDo.addEventListener("click", doImport);

applyFilters();                          // first paint (tags fill in once fetched)
(async function loadTags() {
  try { TAGS = (await (await fetch("/api/tags")).json()) || {}; }
  catch (_) { TAGS = {}; }
  rebuildTagUI();
  applyFilters();
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
