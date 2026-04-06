# 背景三層系統

所有 Phyra HTML 報告的背景由三層疊加組成。紋理和光澤使用 nipponcolors.com 的原始 PNG 資源（需網路連線）。

## 三層結構

```
┌──────────────────────────────────────────────────────┐
│ ③ .phyra-gloss  nipponcolors gloss.png 頂部光澤      │
│    → 頂部偏亮的光澤感，製造隱性漸層視覺               │
├──────────────────────────────────────────────────────┤
│ ② .phyra-bg     texture.png repeat 和紙顆粒紋理      │
│    → 半透明雜訊，和紙/底片顆粒質感                     │
├──────────────────────────────────────────────────────┤
│ ① .phyra-bg     background-color: var(--p-primary)   │
│    → 主題色純色，transition: 2s ease-in 平滑切換       │
└──────────────────────────────────────────────────────┘
```

## HTML 結構範本

```html
<!DOCTYPE html>
<html lang="zh-Hant" data-theme="wakatake" data-theme-mode="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Phyra Report</title>
  <style>
    /* [此處 inline 所有主題 CSS、背景 CSS、頁面 CSS] */
  </style>
</head>
<body>
  <!-- 層① + 層② 背景 -->
  <div class="phyra-bg"></div>

  <!-- 層③ 光澤 -->
  <div class="phyra-gloss"></div>

  <!-- 內容寬度控制手柄 -->
  <div class="phyra-width-handle" id="phyra-width-handle"></div>

  <!-- 主題切換器 -->
  <div class="phyra-switcher">
    <select id="phyra-select" onchange="phyraApply(this.value)">
      <optgroup label="淺色系">...</optgroup>
      <optgroup label="深色系">...</optgroup>
    </select>
    <button onclick="phyraRandom()">Random</button>
  </div>

  <!-- 頁面內容 -->
  <main id="phyra-main">
    ...
  </main>

  <!-- 統一頁腳 -->
  <footer class="phyra-footer">
    Phyra NT Workflow | Report Type | YYYY-MM-DD
  </footer>

  <script>
    /* [此處 inline 主題切換 JS + 寬度拖動 JS] */
  </script>
</body>
</html>
```

## CSS 實現

```css
/* === 語義別名 === */
:root {
  --p-primary : var(--theme-primary);
  --p-light   : var(--theme-light);
  --p-accent  : var(--theme-accent);
  --p-dark    : var(--theme-dark);
  --p-neutral : var(--theme-neutral);
  --p-text    : var(--theme-text);
  --phyra-content-width: 900px;
}

/* === 層① 主題色底色 + 層② 紋理 === */
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

/* === 層③ 頂部光澤 === */
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

/* === 內容層 z-index === */
body > *:not(.phyra-bg):not(.phyra-gloss):not(.phyra-switcher):not(.phyra-width-handle) {
  position: relative;
  z-index: 2;
}

/* === 內容寬度控制 === */
main, #phyra-main {
  max-width: var(--phyra-content-width);
  margin: 0 auto;
  padding: 0 20px;
  box-sizing: border-box;
  transition: max-width 0.15s ease;
}

/* 寬度拖動手柄（內容塊右側外面） */
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

/* === 統一頁腳 === */
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

/* === 主題切換器 UI === */
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

/* 選單文字強制黑色（白色底的 dropdown 需要深色文字才可讀） */
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

/* #phyra-label 已移除，選單本身已顯示當前主題名稱 */
```

## 內容寬度拖動 JS

```javascript
/* 內容寬度拖動控制 */
(function() {
  const handle = document.getElementById('phyra-width-handle');
  if (!handle) return;
  let dragging = false;

  function updateHandlePos(contentWidth) {
    const vw = window.innerWidth;
    const gap = (vw - contentWidth) / 2;
    // 手柄在內容右邊外面，保持最少 4px 可見
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
    // 滑鼠離中心的距離 × 2 = 內容寬度
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

  // 初始位置
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

## 注意事項

- `.phyra-bg` 的 `background-color` 必須是全不透明主色
- 紋理和光澤使用 nipponcolors.com 的 PNG 資源（需網路連線才能顯示）
- 紋理 URL: `https://nipponcolors.com/images/texture.png`
- 光澤 URL: `https://nipponcolors.com/images/gloss.png`
- 所有三層都必須出現在每個 HTML 報告中
- 選單 `<select>` 的文字必須是黑色（`#1C1C1C`），背景用白色半透明，確保在所有主題下都可讀
- 內容寬度可通過右側手柄拖動調整（最小 400px，最大視窗寬度 - 40px）
