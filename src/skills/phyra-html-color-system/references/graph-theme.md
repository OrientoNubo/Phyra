# 圖表/D3.js 配色規則

適用於 Survey 和 Graph 報告中力導向關係圖的配色和互動規則。

## D3.js 要求

所有關係圖必須使用 D3.js v7（inline 嵌入）實現，使用 SVG 而非 Canvas。

### 必要互動功能

1. **縮放/平移** (`d3.zoom`)
2. **節點拖動** (`d3.drag`)  
3. **Hover tooltip** 顯示節點詳情
4. **點擊高亮** 相關節點和連線
5. **全螢幕按鈕** 讓使用者可以全螢幕檢視圖表

### D3.js 嵌入方式

```html
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
```

## 圖表 CSS 變數

```css
.graph-container {
  background: var(--p-bg-card);
  border: 1px solid var(--p-border);
  border-radius: 8px;
  overflow: hidden;
}

.graph-container svg {
  width: 100%;
  height: 600px;
}
```

## 節點聚類色板

定義 10 個在淺色系和深色系中都可見的聚類顏色：

```css
:root {
  --cluster-0: #4E79A7;  /* steel blue */
  --cluster-1: #F28E2B;  /* tangerine */
  --cluster-2: #E15759;  /* coral red */
  --cluster-3: #76B7B2;  /* teal */
  --cluster-4: #59A14F;  /* sage green */
  --cluster-5: #EDC948;  /* gold */
  --cluster-6: #B07AA1;  /* mauve */
  --cluster-7: #FF9DA7;  /* salmon pink */
  --cluster-8: #9C755F;  /* brown */
  --cluster-9: #BAB0AC;  /* warm gray */
}
```

## 邊（Edge）樣式

```css
.edge {
  stroke: var(--p-text-secondary);
  stroke-opacity: 0.4;
  fill: none;
}

/* 邊的粗細代表關係緊密程度 */
.edge-strong  { stroke-width: 3px; }
.edge-normal  { stroke-width: 1.5px; }
.edge-weak    { stroke-width: 0.8px; stroke-dasharray: 4 2; }
```

## 邊類型顏色（Citation Network）

```css
.edge-builds-on    { stroke: var(--cluster-0); }
.edge-contradicts  { stroke: var(--cluster-2); }
.edge-parallel     { stroke: var(--cluster-3); }
.edge-supersedes   { stroke: var(--cluster-1); }
.edge-applies      { stroke: var(--cluster-4); }
.edge-critiques    { stroke: var(--cluster-6); }
```

## 節點樣式

```css
.node circle {
  stroke: var(--p-text);
  stroke-width: 1.5px;
  cursor: grab;
  transition: r 0.2s;
}

.node circle:hover {
  stroke-width: 3px;
}

.node text {
  font-size: 11px;
  fill: var(--p-text);
  pointer-events: none;
  text-anchor: middle;
  dominant-baseline: central;
}
```

## 多屬性漸變節點

當一個節點屬於多個聚類時，使用 SVG `<linearGradient>` 顯示漸變色：

```javascript
// 為多屬性節點建立 SVG 漸變
function createGradient(defs, nodeId, colors) {
  const grad = defs.append('linearGradient')
    .attr('id', 'grad-' + nodeId)
    .attr('x1', '0%').attr('y1', '0%')
    .attr('x2', '100%').attr('y2', '100%');
  colors.forEach((color, i) => {
    grad.append('stop')
      .attr('offset', (i / (colors.length - 1) * 100) + '%')
      .attr('stop-color', color);
  });
}

// 使用方式
node.select('circle')
  .attr('fill', d => {
    if (d.clusters.length === 1) return clusterColor(d.clusters[0]);
    createGradient(defs, d.id, d.clusters.map(c => clusterColor(c)));
    return 'url(#grad-' + d.id + ')';
  });
```

## 縮放和拖動

```javascript
// 縮放/平移
const zoom = d3.zoom()
  .scaleExtent([0.3, 5])
  .on('zoom', (event) => {
    container.attr('transform', event.transform);
  });
svg.call(zoom);

// 節點拖動
const drag = d3.drag()
  .on('start', (event, d) => {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x; d.fy = d.y;
  })
  .on('drag', (event, d) => {
    d.fx = event.x; d.fy = event.y;
  })
  .on('end', (event, d) => {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null; d.fy = null;
  });

node.call(drag);
```

## Tooltip

```css
.graph-tooltip {
  position: absolute;
  padding: 8px 12px;
  background: var(--p-bg-card);
  border: 1px solid var(--p-border);
  border-radius: 6px;
  color: var(--p-text);
  font-size: 12px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
  max-width: 300px;
  backdrop-filter: blur(4px);
  z-index: 50;
}

.graph-tooltip.visible {
  opacity: 1;
}
```

## Legend（圖例）

```css
.graph-legend {
  position: absolute;
  top: 12px;
  left: 12px;
  background: var(--p-bg-card);
  border: 1px solid var(--p-border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 11px;
  color: var(--p-text);
  z-index: 10;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
```

## 全螢幕按鈕

圖表容器右上角必須有一個全螢幕切換按鈕：

```css
.graph-fullscreen-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: var(--p-bg-card);
  border: 1px solid var(--p-border);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: var(--p-text);
  z-index: 10;
  transition: background 0.2s;
}

.graph-fullscreen-btn:hover {
  background: color-mix(in srgb, var(--p-accent) 20%, transparent);
}

/* 全螢幕暗色遮罩 */
.graph-fullscreen-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 199;
}

.graph-fullscreen-overlay.active {
  display: block;
}

.graph-container.fullscreen {
  position: fixed;
  inset: 20px;
  z-index: 200;
  border-radius: 12px;
  max-width: none;
  background: var(--p-bg-card);
}

.graph-container.fullscreen svg {
  width: 100%;
  height: calc(100vh - 40px);
}
```

HTML 結構（在 graph-container 前面加遮罩 div）：
```html
<div class="graph-fullscreen-overlay" id="graph-overlay"></div>
<div class="graph-container" style="position: relative;">
  <button class="graph-fullscreen-btn" onclick="toggleGraphFullscreen(this.parentElement)">⛶</button>
  <!-- legend, svg, tooltip 等 -->
</div>
```

```javascript
// 全螢幕切換（帶暗色遮罩）
function toggleGraphFullscreen(container) {
  const overlay = document.getElementById('graph-overlay');
  const isFullscreen = container.classList.toggle('fullscreen');
  const btn = container.querySelector('.graph-fullscreen-btn');

  if (isFullscreen) {
    overlay.classList.add('active');
    btn.textContent = '✕';
    const svg = container.querySelector('svg');
    svg.style.width = '100%';
    svg.style.height = (window.innerHeight - 40) + 'px';
  } else {
    overlay.classList.remove('active');
    btn.textContent = '⛶';
    const svg = container.querySelector('svg');
    svg.style.width = '100%';
    svg.style.height = '600px';
  }
}

// 點擊遮罩也可以退出全螢幕
document.getElementById('graph-overlay')?.addEventListener('click', () => {
  const fc = document.querySelector('.graph-container.fullscreen');
  if (fc) toggleGraphFullscreen(fc);
});

```

HTML 結構：
```html
<div class="graph-container" style="position: relative;">
  <button class="graph-fullscreen-btn" onclick="toggleGraphFullscreen(this.parentElement)">⛶</button>
  <!-- legend, svg, tooltip 等 -->
</div>
```

## 主題切換適應

圖表在主題切換時必須自適應。以下 CSS 變數確保圖表元素跟隨主題變化：

- 節點文字顏色：`var(--p-text)`
- 邊線顏色：`var(--p-text-secondary)`  
- 背景色：`var(--p-bg-card)`
- Tooltip：使用 CSS 變數，自動適應

SVG 元素使用 CSS 變數時，切換主題後顏色自動更新（因為 CSS 變數是動態的）。
