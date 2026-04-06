# Graph / D3.js Color Rules

Color and interaction rules for force-directed relationship graphs in Survey and Graph reports.

## D3.js Requirements

All relationship graphs must be implemented using D3.js v7 (inline embedded), using SVG rather than Canvas.

### Required Interactive Features

1. **Zoom/Pan** (`d3.zoom`)
2. **Node dragging** (`d3.drag`)  
3. **Hover tooltip** showing node details
4. **Click highlight** for related nodes and edges
5. **Fullscreen button** allowing users to view the graph in fullscreen

### D3.js Embedding

```html
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
```

## Graph CSS Variables

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

## Node Cluster Color Palette

Defines 10 cluster colors visible in both light and dark themes:

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

## Edge Styles

```css
.edge {
  stroke: var(--p-text-secondary);
  stroke-opacity: 0.4;
  fill: none;
}

/* Edge thickness represents relationship strength */
.edge-strong  { stroke-width: 3px; }
.edge-normal  { stroke-width: 1.5px; }
.edge-weak    { stroke-width: 0.8px; stroke-dasharray: 4 2; }
```

## Edge Type Colors (Citation Network)

```css
.edge-builds-on    { stroke: var(--cluster-0); }
.edge-contradicts  { stroke: var(--cluster-2); }
.edge-parallel     { stroke: var(--cluster-3); }
.edge-supersedes   { stroke: var(--cluster-1); }
.edge-applies      { stroke: var(--cluster-4); }
.edge-critiques    { stroke: var(--cluster-6); }
```

## Node Styles

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

## Multi-Attribute Gradient Nodes

When a node belongs to multiple clusters, use SVG `<linearGradient>` to display gradient colors:

```javascript
// Create SVG gradient for multi-attribute nodes
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

// Usage
node.select('circle')
  .attr('fill', d => {
    if (d.clusters.length === 1) return clusterColor(d.clusters[0]);
    createGradient(defs, d.id, d.clusters.map(c => clusterColor(c)));
    return 'url(#grad-' + d.id + ')';
  });
```

## Zoom and Drag

```javascript
// Zoom/Pan
const zoom = d3.zoom()
  .scaleExtent([0.3, 5])
  .on('zoom', (event) => {
    container.attr('transform', event.transform);
  });
svg.call(zoom);

// Node dragging
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

## Legend

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

## Fullscreen Button

The graph container must have a fullscreen toggle button at the top-right corner:

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

/* Fullscreen dark overlay */
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

HTML structure (add overlay div before graph-container):
```html
<div class="graph-fullscreen-overlay" id="graph-overlay"></div>
<div class="graph-container" style="position: relative;">
  <button class="graph-fullscreen-btn" onclick="toggleGraphFullscreen(this.parentElement)">⛶</button>
  <!-- legend, svg, tooltip, etc. -->
</div>
```

```javascript
// Fullscreen toggle (with dark overlay)
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

// Clicking the overlay also exits fullscreen
document.getElementById('graph-overlay')?.addEventListener('click', () => {
  const fc = document.querySelector('.graph-container.fullscreen');
  if (fc) toggleGraphFullscreen(fc);
});

```

HTML structure:
```html
<div class="graph-container" style="position: relative;">
  <button class="graph-fullscreen-btn" onclick="toggleGraphFullscreen(this.parentElement)">⛶</button>
  <!-- legend, svg, tooltip, etc. -->
</div>
```

## Theme Switch Adaptation

Graphs must adapt when the theme is switched. The following CSS variables ensure graph elements follow theme changes:

- Node text color: `var(--p-text)`
- Edge color: `var(--p-text-secondary)`  
- Background color: `var(--p-bg-card)`
- Tooltip: uses CSS variables, adapts automatically

SVG elements using CSS variables automatically update colors when the theme is switched (because CSS variables are dynamic).
