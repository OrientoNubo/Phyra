# 3-Layer Background System

The background of all Phyra HTML reports consists of three stacked layers. Textures and gloss use original PNG assets from nipponcolors.com (requires internet connection).

## 3-Layer Structure

```
┌──────────────────────────────────────────────────────┐
│ ③ .phyra-gloss  nipponcolors gloss.png top gloss     │
│    → Brighter gloss at the top, creating a subtle    │
│      gradient visual effect                          │
├──────────────────────────────────────────────────────┤
│ ② .phyra-bg     texture.png repeat washi grain       │
│    → Semi-transparent noise, washi paper / film      │
│      grain texture                                   │
├──────────────────────────────────────────────────────┤
│ ① .phyra-bg     background-color: var(--p-primary)   │
│    → Theme solid color, transition: 2s ease-in       │
│      smooth switching                                │
└──────────────────────────────────────────────────────┘
```

## HTML Structure Template

```html
<!DOCTYPE html>
<html lang="zh-Hant" data-theme="wakatake" data-theme-mode="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Phyra Report</title>
  <style>
    /* [Inline all theme CSS, background CSS, page CSS here] */
  </style>
</head>
<body>
  <!-- Layer ① + Layer ② background -->
  <div class="phyra-bg"></div>

  <!-- Layer ③ gloss -->
  <div class="phyra-gloss"></div>

  <!-- Content width control handle -->
  <div class="phyra-width-handle" id="phyra-width-handle"></div>

  <!-- Theme switcher -->
  <div class="phyra-switcher">
    <select id="phyra-select" onchange="phyraApply(this.value)">
      <optgroup label="Light">...</optgroup>
      <optgroup label="Dark">...</optgroup>
    </select>
    <button onclick="phyraRandom()">Random</button>
  </div>

  <!-- Page content -->
  <main id="phyra-main">
    ...
  </main>

  <!-- Unified footer -->
  <footer class="phyra-footer">
    Phyra NT Workflow | Report Type | YYYY-MM-DD
  </footer>

  <script>
    /* [Inline theme switching JS + width drag JS here] */
  </script>
</body>
</html>
```

## CSS Implementation

```css
/* === Semantic aliases === */
:root {
  --p-primary : var(--theme-primary);
  --p-light   : var(--theme-light);
  --p-accent  : var(--theme-accent);
  --p-dark    : var(--theme-dark);
  --p-neutral : var(--theme-neutral);
  --p-text    : var(--theme-text);
  --phyra-content-width: 900px;
}

/* === Layer ① theme solid color + Layer ② texture === */
.phyra-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background-color: var(--p-primary);
  background-image: url('https://nipponcolors.com/images/texture.png');
  background-repeat: repeat;
  transition: background-color 2s ease-in;
  pointer-events: none;
}

/* === Layer ③ top gloss === */
.phyra-gloss {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 478px;
  z-index: 1;
  background: url('https://nipponcolors.com/images/gloss.png') repeat-x;
  pointer-events: none;
  transition: opacity 2s ease-in;
}

/* === Content layer z-index === */
body > *:not(.phyra-bg):not(.phyra-gloss):not(.phyra-switcher):not(.phyra-width-handle) {
  position: relative;
  z-index: 2;
}

/* === Content width control === */
main, #phyra-main {
  max-width: var(--phyra-content-width);
  margin: 0 auto;
  padding: 0 20px;
  box-sizing: border-box;
  transition: max-width 0.15s ease;
}

/* Width drag handle (outside right edge of content block) */
.phyra-width-handle {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 60px;
  background: rgba(128, 128, 128, 0.3);
  border-radius: 3px;
  cursor: col-resize;
  z-index: 99;
  transition: background 0.2s, opacity 0.3s;
  opacity: 0.4;
}

.phyra-width-handle:hover,
.phyra-width-handle.dragging {
  background: var(--p-accent);
  opacity: 1;
}

/* === Unified footer === */
.phyra-footer {
  text-align: center;
  padding: 24px 20px;
  font-size: 12px;
  color: var(--p-text);
  opacity: 0.5;
  letter-spacing: 0.05em;
  position: relative;
  z-index: 2;
}

/* === Theme switcher UI === */
.phyra-switcher {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(128, 128, 128, 0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 24px;
  transition: background 0.3s;
}

/* Force black text in dropdown (white background dropdown needs dark text for readability) */
.phyra-switcher select {
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(128, 128, 128, 0.3);
  border-radius: 12px;
  color: #1C1C1C;
  font-size: 12px;
  cursor: pointer;
  outline: none;
  max-width: 200px;
}

.phyra-switcher select option {
  color: #1C1C1C;
  background: #fff;
}

.phyra-switcher select optgroup {
  font-weight: bold;
  color: #1C1C1C;
}

.phyra-switcher button {
  padding: 4px 12px;
  background: rgba(128, 128, 128, 0.2);
  border: 1px solid rgba(128, 128, 128, 0.3);
  border-radius: 12px;
  color: var(--p-text);
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.phyra-switcher button:hover {
  background: rgba(128, 128, 128, 0.35);
}

/* #phyra-label removed; the dropdown itself shows the current theme name */
```

## Content Width Drag JS

```javascript
/* Content width drag control */
(function() {
  const handle = document.getElementById('phyra-width-handle');
  if (!handle) return;
  let dragging = false;

  function updateHandlePos(contentWidth) {
    const vw = window.innerWidth;
    const gap = (vw - contentWidth) / 2;
    // Handle is outside the right edge of content, keep at least 4px visible
    handle.style.right = Math.max(4, gap - 16) + 'px';
  }

  handle.addEventListener('mousedown', (e) => {
    dragging = true;
    handle.classList.add('dragging');
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const vw = window.innerWidth;
    // Distance from center x 2 = content width
    const distFromCenter = Math.abs(e.clientX - vw / 2);
    const newWidth = Math.max(400, distFromCenter * 2);
    document.documentElement.style.setProperty('--phyra-content-width', newWidth + 'px');
    updateHandlePos(newWidth);
  });

  document.addEventListener('mouseup', () => {
    if (dragging) {
      dragging = false;
      handle.classList.remove('dragging');
    }
  });

  // Initial position
  const initWidth = parseInt(getComputedStyle(document.documentElement)
    .getPropertyValue('--phyra-content-width')) || 900;
  updateHandlePos(initWidth);

  window.addEventListener('resize', () => {
    const w = parseInt(getComputedStyle(document.documentElement)
      .getPropertyValue('--phyra-content-width')) || 900;
    updateHandlePos(w);
  });
})();
```

## Notes

- `.phyra-bg`'s `background-color` must be fully opaque theme color
- Texture and gloss use PNG assets from nipponcolors.com (requires internet connection to display)
- Texture URL: `https://nipponcolors.com/images/texture.png`
- Gloss URL: `https://nipponcolors.com/images/gloss.png`
- All three layers must be present in every HTML report
- The `<select>` dropdown text must be black (`#1C1C1C`) with semi-transparent white background to ensure readability across all themes
- Content width can be adjusted by dragging the right-side handle (minimum 400px, maximum viewport width - 40px)
