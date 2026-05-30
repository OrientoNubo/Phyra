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
    ("_bilingual.zh-TW.dual.pdf", "bilingual_pdf"),
    ("_draftslide.html",          "draftslide_html"),
    (".pdf",                      "original_pdf"),
]

YYMM_RE = re.compile(r"^(\d{4})_")
TITLE_FIELD_RE = re.compile(r"\|\s*Paper full title\s*\|\s*(.+?)\s*\|")
SHORT_FIELD_RE = re.compile(r"\|\s*Paper short name\s*\|\s*(.+?)\s*\|")
PLACEHOLDERS = {"", "未知", "unknown", "n/a", "-", "—"}


def split_filename(name: str):
    """Return (stem, suffix_kind) or None."""
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
<title>phyra-archbase</title>
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
    padding: 14px 28px;
    border-bottom: 3px solid var(--p-header-border);
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
    align-items: center;
    justify-content: center;
    gap: 10px;
    flex: 1 1 auto;
    min-width: 0;
  }
  #search {
    flex: 1 1 280px;
    max-width: 460px;
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
  /* tag-filter bar (below the header search) */
  .tagbar {
    display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
    margin: 0 0 18px;
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
    <h1>phyra-archbase</h1>
    <div class="stats">__TOTAL__ papers · __FULLY__ fully analyzed</div>
  </div>
  <div class="controls">
    <input type="search" id="search" placeholder="Filter by title or short name… (press /)" autocomplete="off">
    <div class="filter" role="group" aria-label="Filter">
      <button type="button" data-filter="all" aria-pressed="true">All</button>
      <button type="button" data-filter="analyzed" aria-pressed="false">Analyzed</button>
      <button type="button" data-filter="bilingual" aria-pressed="false">Bilingual</button>
      <button type="button" data-filter="pending" aria-pressed="false">PDF only</button>
    </div>
    <button type="button" id="sort-btn" class="sort-btn" title="Sort"></button>
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
  <div class="tagbar" id="tagbar" hidden>
    <div class="tag-dd">
      <button type="button" id="tag-dd-btn" class="tag-filter-btn">🏷 依標籤篩選 ▾</button>
      <div class="tag-menu" id="tag-menu" hidden></div>
    </div>
    <div class="tag-active" id="tag-active"></div>
  </div>
  <datalist id="all-tags-list"></datalist>
  <div id="cards"></div>
</main>
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
})();

function enc(name) { return "collection/" + encodeURIComponent(name); }

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => (
    {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]
  ));
}

function cardHtml(p) {
  const f = p.files || {};
  const btn = [];
  if (f.original_pdf)    btn.push(`<a href="${enc(f.original_pdf)}"    target="_blank">📄 PDF</a>`);
  if (f.analysis_html)   btn.push(`<a href="${enc(f.analysis_html)}"   target="_blank">📖 Analysis</a>`);
  if (f.draftslide_html) btn.push(`<a href="${enc(f.draftslide_html)}" target="_blank">🎞 Slide</a>`);
  if (f.bilingual_pdf)   btn.push(`<a href="${enc(f.bilingual_pdf)}"   target="_blank">🌐 雙語</a>`);
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

async function deletePaper(key, title) {
  if (!confirm(`確定從論文庫刪除「${title}」？\n會移除該論文在 collection/ 的所有檔案（原文 PDF、雙語 PDF、analysis、slide），且無法復原。`))
    return;
  let pw = sessionStorage.getItem(ADMIN_PW_KEY) || "";
  if (!pw) { pw = prompt("請輸入管理員密碼以刪除：") || ""; if (!pw) return; }
  let r;
  try {
    r = await fetch("/api/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, password: pw }),
    });
  } catch (_) { alert("刪除失敗（伺服器無回應）。"); return; }
  if (r.status === 401) { sessionStorage.removeItem(ADMIN_PW_KEY); alert("管理員密碼錯誤。"); return; }
  if (r.status === 403) {
    const e = await r.json().catch(() => ({}));
    alert(e.error || "刪除功能未啟用（啟動時未設定管理員密碼）。");
    return;
  }
  if (!r.ok) { alert("刪除失敗：" + (await r.text())); return; }
  sessionStorage.setItem(ADMIN_PW_KEY, pw);    // remember for the rest of this session
  location.reload();                            // index.html was regenerated server-side
}

cardsRoot.addEventListener("click", (e) => {
  const del = e.target.closest(".card-del");
  if (del) { deletePaper(del.dataset.key, del.dataset.title); return; }
  const x = e.target.closest(".ctag-x");
  if (x) { removeTag(x.closest(".card-tags").dataset.key, x.dataset.tag); return; }
  const add = e.target.closest(".ctag-add");
  if (add) { openTagInput(add); return; }
});

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
