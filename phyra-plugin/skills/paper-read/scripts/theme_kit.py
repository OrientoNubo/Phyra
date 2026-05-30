"""
theme_kit.py — shared light/dark/system appearance toggle for paper-read
HTML outputs (analysis viewer + slide deck).

Design goals (per user constraint):
  - Add a light/dark mode and its control component WITHOUT changing any
    existing layout, spacing, or DOM structure.
  - Keep the change tiny so already-generated HTML files can be
    retrofitted later by the exact same `inject()` call.

It works purely additively:
  - one extra <style> placed right before </head> (so its :root override
    wins by source order over the generator's own <style>); it also
    carries a [data-theme="dark"] block and a few dark "patch" rules for
    the handful of non-variable colours in the base CSS;
  - a no-FOUC inline <script> in <head> that sets data-theme before paint;
  - a fixed-position segmented control (.theme-toggle) right after <body>
    — position:fixed, so it never reflows existing content;
  - a wiring <script> before </body> (localStorage key "phyra-theme").

Palette is adapted from
`paper-base/script/generate_index.py` lines 156-188 (the #c96c49 accent /
warm-grey scheme), mapped onto the CSS variable names the paper-read
generators already use (--p-primary / --p-light / --p-accent / --p-dark /
--p-text / --p-bg-card / --p-formula-bg / --p-border / --p-bold-highlight)
so not a single existing rule has to be rewritten.

`inject()` is idempotent: if the HTML already contains a `.theme-toggle`
it is returned unchanged, so re-running a generator or re-retrofitting a
file never double-injects.
"""

import re

THEME_CSS = r"""
:root {
  --p-primary: #f8f8f6;
  --p-light: #f8f8f6;
  --p-accent: #c96c49;
  --p-dark: #373734;
  --p-text: #0b0b0b;
  --p-bg-card: #ebebe6;
  --p-formula-bg: #f4f4f1;
  --p-border: #d7d7d5;
  --p-bold-highlight: rgba(201,108,73,0.16);
  --p-muted: #898781;
  --p-shadow: rgba(31,30,29,0.08);
  --p-toggle-bg: rgba(0,0,0,0.04);
  --p-toggle-active: #ffffff;
}
[data-theme="dark"] {
  --p-primary: #1f1f1e;
  --p-light: #1f1f1e;
  --p-accent: #c96c49;
  --p-dark: #c2c2c2;
  --p-text: #ffffff;
  --p-bg-card: #171717;
  --p-formula-bg: #171717;
  --p-border: #292929;
  --p-bold-highlight: rgba(201,108,73,0.30);
  --p-muted: #c2c2b7;
  --p-shadow: rgba(0,0,0,0.4);
  --p-toggle-bg: rgba(255,255,255,0.04);
  --p-toggle-active: #2c2c2b;
}
/* dark patches for the few non-variable colours baked into the base CSS */
[data-theme="dark"] code,
[data-theme="dark"] pre.codeblock,
[data-theme="dark"] .codeblock { background: rgba(255,255,255,0.06); }
[data-theme="dark"] tr:hover td { background: rgba(255,255,255,0.05); }
[data-theme="dark"] .bottom-bar { background: rgba(255,255,255,0.04); }
[data-theme="dark"] .bottom-bar .progress { background: rgba(255,255,255,0.10); }
/* fixed-position appearance switcher — additive, never reflows content */
.theme-toggle {
  position: fixed; top: 14px; right: 16px; z-index: 1000;
  display: inline-flex; align-items: center; gap: 2px; padding: 3px;
  background: var(--p-toggle-bg); border: 1px solid var(--p-border);
  border-radius: 8px; backdrop-filter: blur(6px);
}
.theme-toggle button {
  width: 28px; height: 26px; display: inline-flex; align-items: center;
  justify-content: center; padding: 0; border: 0; background: transparent;
  color: var(--p-muted); cursor: pointer; border-radius: 5px;
  transition: background .12s, color .12s;
}
.theme-toggle button:hover { color: var(--p-text); }
.theme-toggle button[aria-pressed="true"] {
  background: var(--p-toggle-active); color: var(--p-text);
  box-shadow: 0 1px 2px var(--p-shadow);
}
.theme-toggle svg {
  width: 15px; height: 15px; stroke: currentColor; fill: none;
  stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
}
@media print { .theme-toggle { display: none; } }
"""

THEME_HEAD_SCRIPT = r"""
(function () {
  var mode = localStorage.getItem("phyra-theme") || "system";
  var prefersDark = window.matchMedia
    && window.matchMedia("(prefers-color-scheme: dark)").matches;
  var actual = mode === "system" ? (prefersDark ? "dark" : "light") : mode;
  document.documentElement.setAttribute("data-theme", actual);
})();
"""

THEME_TOGGLE_HTML = r"""
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
"""

THEME_TOGGLE_SCRIPT = r"""
(function () {
  var t = document.querySelector(".theme-toggle");
  if (!t) return;
  var btns = t.querySelectorAll("button[data-mode]");
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  var mode = localStorage.getItem("phyra-theme") || "system";
  function resolve(m) { return m === "system" ? (mq.matches ? "dark" : "light") : m; }
  function apply(m) {
    mode = m;
    document.documentElement.setAttribute("data-theme", resolve(m));
    btns.forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.mode === m);
    });
    localStorage.setItem("phyra-theme", m);
  }
  btns.forEach(function (b) {
    b.addEventListener("click", function () { apply(b.dataset.mode); });
  });
  if (mq.addEventListener) mq.addEventListener("change", function () {
    if (mode === "system") apply("system");
  });
  apply(mode);
})();
"""


def inject(html: str) -> str:
    """Add the theme kit to a finished HTML document. Idempotent.

    Insertion points (all additive, none modify existing nodes):
      - before </head>:  the override <style> + no-FOUC <script>
      - after <body ...>: the .theme-toggle control
      - before </body>:   the wiring <script>
    """
    if 'class="theme-toggle"' in html:
        return html  # already themed — re-run / re-retrofit safe

    head_blob = (
        f"<style>{THEME_CSS}</style>\n"
        f"<script>{THEME_HEAD_SCRIPT}</script>\n"
    )
    html = html.replace("</head>", head_blob + "</head>", 1)

    m = re.search(r"<body[^>]*>", html)
    if m:
        i = m.end()
        html = html[:i] + "\n" + THEME_TOGGLE_HTML + html[i:]

    html = html.replace(
        "</body>",
        f"<script>{THEME_TOGGLE_SCRIPT}</script>\n</body>",
        1,
    )
    return html
