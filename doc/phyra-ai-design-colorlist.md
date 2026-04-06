# Phyra AI Design — Color System

> **一份供 AI agent 使用的完整設計系統**
> 100 種日本傳統色主題，單頁 HTML 即可全數內建，透過一個按鈕即時切換。
> 資料來源：[nipponcolors.com](https://nipponcolors.com/) × [lolcolors](https://www.webdesignrankings.com/resources/lolcolors/)

---

## 📁 檔案結構

```
./
├── phyra-ai-design-colorlist.md   ← 本文件（設計系統規格）
└── assets/
    ├── texture.png   ← 帶 alpha 的半透明雜訊 PNG，128×128，tile 鋪滿全頁
    └── gloss.png     ← 頂部光澤 PNG，水平 repeat-x，製造上方偏亮的視覺層次
```

> **注意：** texture.png 和 gloss.png 必須放在 `assets/` 目錄，
> 與本 MD 文件同層。兩者均為原 nipponcolors.com 使用的資源，本地端保留正確版本。

---

## 🎨 背景效果原理（三層疊加）

```
┌──────────────────────────────────────────────────────┐
│ ③ gloss.png   repeat-x   height: 478px              │
│    → 頂部偏亮的光澤感，製造隱性漸層視覺              │
├──────────────────────────────────────────────────────┤
│ ② texture.png  repeat  width/height: 100%           │
│    → 半透明雜訊，和紙/底片顆粒質感                   │
├──────────────────────────────────────────────────────┤
│ ① background-color: var(--p-primary)                │
│    → 主題色純色，transition: 2s ease-in 平滑切換     │
└──────────────────────────────────────────────────────┘
```

---

## 🔧 Agent 使用指南

### 快速整合步驟

1. 將 `phyra-bg.css` 和 `phyra-themes.css`（見下方）引入 HTML
2. 加入 `assets/texture.png` 和 `assets/gloss.png`
3. 在 `<html>` 設定初始主題：`data-theme="wakatake"`
4. 加入主題切換按鈕與 JS

### HTML 結構範本

```html
<!DOCTYPE html>
<html lang="zh-Hant" data-theme="wakatake">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="phyra-themes.css">
</head>
<body>
  <!-- 層① + 層② 背景 -->
  <div class="phyra-bg"></div>

  <!-- 層③ 光澤 -->
  <div class="phyra-gloss"></div>

  <!-- 主題切換器 -->
  <div class="phyra-switcher">
    <button onclick="phyraNext()">次の色 ▶</button>
    <span id="phyra-label"></span>
  </div>

  <!-- 頁面內容，使用 CSS 變數 -->
  <main style="color: var(--p-text)">
    <h1 style="color: var(--p-text)">標題</h1>
    <p>內文</p>
    <button style="background: var(--p-accent); color: #fff">CTA</button>
  </main>

  <script src="phyra-switcher.js"></script>
</body>
</html>
```

---

## 🖌 phyra-bg.css — 背景與佈局基礎

```css
/* phyra-bg.css
   背景三層結構 + CSS 變數語義別名 */

/* 語義別名（從主題變數映射） */
:root {
  --p-primary : var(--theme-primary);
  --p-light   : var(--theme-light);
  --p-accent  : var(--theme-accent);
  --p-dark    : var(--theme-dark);
  --p-neutral : var(--theme-neutral);
  --p-text    : var(--theme-text);
}

/* 層① + 層② */
.phyra-bg {
  position: fixed; inset: 0; z-index: 0;
  background-color   : var(--p-primary);
  background-image   : url('./assets/texture.png');
  background-repeat  : repeat;
  transition         : background-color 2s ease-in;
  pointer-events     : none;
}

/* 層③ */
.phyra-gloss {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 478px; z-index: 1;
  background   : url('./assets/gloss.png') repeat-x;
  pointer-events: none;
}

/* gloss.png 無法取得時的純 CSS 替代 */
.phyra-gloss-fallback {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 478px; z-index: 1;
  background: linear-gradient(to bottom,
    rgba(255,255,255,.22) 0%,
    rgba(255,255,255,.00) 100%);
  pointer-events: none;
}

/* 頁面內容層 */
body > *:not(.phyra-bg):not(.phyra-gloss) {
  position: relative; z-index: 2;
}

/* 主題切換器 UI */
.phyra-switcher {
  position: fixed; bottom: 20px; right: 20px;
  z-index: 100;
  display: flex; align-items: center; gap: 10px;
}
.phyra-switcher button {
  padding: 6px 14px;
  background: rgba(255,255,255,.25);
  border: 1px solid rgba(255,255,255,.5);
  border-radius: 20px;
  color: var(--p-text);
  cursor: pointer;
  backdrop-filter: blur(4px);
  font-size: 13px;
  transition: background .2s;
}
.phyra-switcher button:hover {
  background: rgba(255,255,255,.4);
}
#phyra-label {
  font-size: 12px;
  color: var(--p-text);
  opacity: .8;
  letter-spacing: .05em;
}
```

---

## ⚙️ phyra-switcher.js — 主題切換邏輯

```javascript
/* phyra-switcher.js
   從 data-theme 屬性讀取並切換 100 種主題 */

const PHYRA_THEMES = [
  { id: "nadeshiko", label: "撫子 NADESHIKO" },
  { id: "kohbai", label: "紅梅 KOHBAI" },
  { id: "suoh", label: "蘇芳 SUOH" },
  { id: "taikoh", label: "退紅 TAIKOH" },
  { id: "momo", label: "桃 MOMO" },
  { id: "ichigo", label: "苺 ICHIGO" },
  { id: "karakurenai", label: "韓紅花 KARAKURENAI" },
  { id: "kurenai", label: "紅 KURENAI" },
  { id: "toki", label: "鴇 TOKI" },
  { id: "kokiake", label: "深緋 KOKIAKE" },
  { id: "jinzamomi", label: "甚三紅 JINZAMOMI" },
  { id: "azuki", label: "小豆 AZUKI" },
  { id: "akabeni", label: "赤紅 AKABENI" },
  { id: "haizakura", label: "灰桜 HAIZAKURA" },
  { id: "akebono", label: "曙 AKEBONO" },
  { id: "sangosyu", label: "珊瑚朱 SANGOSYU" },
  { id: "syojyohi", label: "猩猩緋 SYOJYOHI" },
  { id: "entan", label: "鉛丹 ENTAN" },
  { id: "benihi", label: "紅緋 BENIHI" },
  { id: "terigaki", label: "照柿 TERIGAKI" },
  { id: "araisyu", label: "洗朱 ARAISYU" },
  { id: "ohni", label: "黄丹 OHNI" },
  { id: "sohi", label: "纁 SOHI" },
  { id: "ensyucha", label: "遠州茶 ENSYUCHA" },
  { id: "kogecha", label: "焦茶 KOGECHA" },
  { id: "akakoh", label: "赤香 AKAKOH" },
  { id: "kokikuchinashi", label: "深支子 KOKIKUCHINASHI" },
  { id: "taisya", label: "代赭 TAISYA" },
  { id: "kanzo", label: "萱草 KANZO" },
  { id: "beniukon", label: "紅鬱金 BENIUKON" },
  { id: "kohaku", label: "琥珀 KOHAKU" },
  { id: "kuchiba", label: "朽葉 KUCHIBA" },
  { id: "yamabuki", label: "山吹 YAMABUKI" },
  { id: "hajizome", label: "櫨染 HAJIZOME" },
  { id: "tamago", label: "玉子 TAMAGO" },
  { id: "tamamorokoshi", label: "玉蜀黍 TAMAMOROKOSHI" },
  { id: "usuki", label: "浅黄 USUKI" },
  { id: "kuchinashi", label: "梔子 KUCHINASHI" },
  { id: "tohoh", label: "籐黄 TOHOH" },
  { id: "ukon", label: "鬱金 UKON" },
  { id: "tonoko", label: "砥粉 TONOKO" },
  { id: "kenpohzome", label: "憲法染 KENPOHZOME" },
  { id: "kariyasu", label: "刈安 KARIYASU" },
  { id: "hiwa", label: "鶸 HIWA" },
  { id: "koke", label: "苔 KOKE" },
  { id: "hiwamoegi", label: "鶸萌黄 HIWAMOEGI" },
  { id: "yanagizome", label: "柳染 YANAGIZOME" },
  { id: "moegi", label: "萌黄 MOEGI" },
  { id: "nae", label: "苗 NAE" },
  { id: "matsuba", label: "松葉 MATSUBA" },
  { id: "tokiwa", label: "常磐 TOKIWA" },
  { id: "wakatake", label: "若竹 WAKATAKE" },
  { id: "midori", label: "緑 MIDORI" },
  { id: "byakuroku", label: "白緑 BYAKUROKU" },
  { id: "tokusa", label: "木賊 TOKUSA" },
  { id: "rokusyoh", label: "緑青 ROKUSYOH" },
  { id: "aomidori", label: "青緑 AOMIDORI" },
  { id: "seiji", label: "青磁 SEIJI" },
  { id: "mizuasagi", label: "水浅葱 MIZUASAGI" },
  { id: "byakugun", label: "白群 BYAKUGUN" },
  { id: "kamenozoki", label: "瓶覗 KAMENOZOKI" },
  { id: "mizu", label: "水 MIZU" },
  { id: "asagi", label: "浅葱 ASAGI" },
  { id: "shinbashi", label: "新橋 SHINBASHI" },
  { id: "hanaasagi", label: "花浅葱 HANAASAGI" },
  { id: "sora", label: "空 SORA" },
  { id: "chigusa", label: "千草 CHIGUSA" },
  { id: "hanada", label: "縹 HANADA" },
  { id: "wasurenagusa", label: "勿忘草 WASURENAGUSA" },
  { id: "tsuyukusa", label: "露草 TSUYUKUSA" },
  { id: "gunjyo", label: "群青 GUNJYO" },
  { id: "ruri", label: "瑠璃 RURI" },
  { id: "rurikon", label: "瑠璃紺 RURIKON" },
  { id: "benimidori", label: "紅碧 BENIMIDORI" },
  { id: "fujinezumi", label: "藤鼠 FUJINEZUMI" },
  { id: "benikakehana", label: "紅掛花 BENIKAKEHANA" },
  { id: "konjyo", label: "紺青 KONJYO" },
  { id: "kon", label: "紺 KON" },
  { id: "konkikyo", label: "紺桔梗 KONKIKYO" },
  { id: "kurotsurubami", label: "黒橡 KUROTSURUBAMI" },
  { id: "fuji", label: "藤 FUJI" },
  { id: "fujimurasaki", label: "藤紫 FUJIMURASAKI" },
  { id: "kikyo", label: "桔梗 KIKYO" },
  { id: "shion", label: "紫苑 SHION" },
  { id: "usu", label: "薄 USU" },
  { id: "edomurasaki", label: "江戸紫 EDOMURASAKI" },
  { id: "murasaki", label: "紫 MURASAKI" },
  { id: "benifuji", label: "紅藤 BENIFUJI" },
  { id: "botan", label: "牡丹 BOTAN" },
  { id: "tsutsuji", label: "躑躅 TSUTSUJI" },
  { id: "shironeri", label: "白練 SHIRONERI" },
  { id: "shironezumi", label: "白鼠 SHIRONEZUMI" },
  { id: "ginnezumi", label: "銀鼠 GINNEZUMI" },
  { id: "namari", label: "鉛 NAMARI" },
  { id: "hai", label: "灰 HAI" },
  { id: "nibi", label: "鈍 NIBI" },
  { id: "aonibi", label: "青鈍 AONIBI" },
  { id: "keshizumi", label: "消炭 KESHIZUMI" },
  { id: "sumi", label: "墨 SUMI" },
  { id: "kuro", label: "黒 KURO" }
];

let phyraIndex = 0;

function phyraApply(id) {
  document.documentElement.setAttribute('data-theme', id);
  const t = PHYRA_THEMES.find(x => x.id === id);
  const label = document.getElementById('phyra-label');
  if (label && t) label.textContent = t.label;
}

function phyraNext() {
  phyraIndex = (phyraIndex + 1) % PHYRA_THEMES.length;
  phyraApply(PHYRA_THEMES[phyraIndex].id);
}

function phyraPrev() {
  phyraIndex = (phyraIndex - 1 + PHYRA_THEMES.length) % PHYRA_THEMES.length;
  phyraApply(PHYRA_THEMES[phyraIndex].id);
}

function phyraRandom() {
  phyraIndex = Math.floor(Math.random() * PHYRA_THEMES.length);
  phyraApply(PHYRA_THEMES[phyraIndex].id);
}

// 初始化
(function() {
  const current = document.documentElement.getAttribute('data-theme') || 'wakatake';
  phyraIndex = PHYRA_THEMES.findIndex(x => x.id === current);
  if (phyraIndex < 0) phyraIndex = 0;
  phyraApply(PHYRA_THEMES[phyraIndex].id);
})();
```

---

## 🎨 phyra-themes.css — 100 種主題定義

> 將整個 CSS 區塊貼入 `<style>` 或獨立 `phyra-themes.css` 文件。
> 每個主題透過 `[data-theme="romaji"]` 選擇器啟用。

```css
/* phyra-themes.css — 100 Nippon Color Themes */
/* 每個 [data-theme] 區塊定義 6 個 CSS 變數：
   --theme-primary  主題色（底色）
   --theme-light    淡色（卡片背景、輸入框）
   --theme-accent   強調色（CTA、圖表主線）
   --theme-dark     深色（深底投影片、導航）
   --theme-neutral  柔和底（surface、分隔線）
   --theme-text     建議文字色（自動判斷深/淺）
*/

/* 🌸 紅・桃 */
[data-theme="nadeshiko"] {
  --theme-primary : #DC9FB4;   /* 撫子 */
  --theme-light   : #F3E6EB;
  --theme-accent  : #92E566;
  --theme-dark    : #471727;
  --theme-neutral : #E7E3E4;
  --theme-text    : #1C1C1C;
}

[data-theme="kohbai"] {
  --theme-primary : #E16B8C;   /* 紅梅 */
  --theme-light   : #F3E6EA;
  --theme-accent  : #80FA51;
  --theme-dark    : #470B1C;
  --theme-neutral : #E8E2E4;
  --theme-text    : #F5F2EB;
}

[data-theme="suoh"] {
  --theme-primary : #8E354A;   /* 蘇芳 */
  --theme-light   : #F3E6E9;
  --theme-accent  : #3DA51D;
  --theme-dark    : #260C12;
  --theme-neutral : #E7E3E4;
  --theme-text    : #F5F2EB;
}

[data-theme="taikoh"] {
  --theme-primary : #F8C3CD;   /* 退紅 */
  --theme-light   : #F3E6E9;
  --theme-accent  : #6EFE4C;
  --theme-dark    : #600D1D;
  --theme-neutral : #E8E2E3;
  --theme-text    : #1C1C1C;
}

[data-theme="momo"] {
  --theme-primary : #F596AA;   /* 桃 */
  --theme-light   : #F3E6E9;
  --theme-accent  : #72FE4C;
  --theme-dark    : #560C1B;
  --theme-neutral : #E8E2E4;
  --theme-text    : #1C1C1C;
}

[data-theme="ichigo"] {
  --theme-primary : #B5495B;   /* 苺 */
  --theme-light   : #F3E6E8;
  --theme-accent  : #47D22B;
  --theme-dark    : #2E1015;
  --theme-neutral : #E7E3E4;
  --theme-text    : #F5F2EB;
}

[data-theme="karakurenai"] {
  --theme-primary : #D0104C;   /* 韓紅花 */
  --theme-light   : #F3E6EA;
  --theme-accent  : #46E000;
  --theme-dark    : #300714;
  --theme-neutral : #E8E2E4;
  --theme-text    : #F5F2EB;
}

[data-theme="kurenai"] {
  --theme-primary : #CB1B45;   /* 紅 */
  --theme-light   : #F3E6E9;
  --theme-accent  : #36E500;
  --theme-dark    : #320711;
  --theme-neutral : #E8E2E4;
  --theme-text    : #F5F2EB;
}

[data-theme="toki"] {
  --theme-primary : #EEA9A9;   /* 鴇 */
  --theme-light   : #F3E6E6;
  --theme-accent  : #50FA50;
  --theme-dark    : #580D0D;
  --theme-neutral : #E8E2E2;
  --theme-text    : #1C1C1C;
}

[data-theme="kokiake"] {
  --theme-primary : #86473F;   /* 深緋 */
  --theme-light   : #F3E8E6;
  --theme-accent  : #299B36;
  --theme-dark    : #23110F;
  --theme-neutral : #E7E4E3;
  --theme-text    : #F5F2EB;
}

[data-theme="jinzamomi"] {
  --theme-primary : #EB7A77;   /* 甚三紅 */
  --theme-light   : #F3E7E6;
  --theme-accent  : #4CFE51;
  --theme-dark    : #4D0C0B;
  --theme-neutral : #E8E3E2;
  --theme-text    : #1C1C1C;
}

[data-theme="azuki"] {
  --theme-primary : #954A45;   /* 小豆 */
  --theme-light   : #F3E7E6;
  --theme-accent  : #2CAD34;
  --theme-dark    : #261110;
  --theme-neutral : #E7E4E3;
  --theme-text    : #F5F2EB;
}

[data-theme="akabeni"] {
  --theme-primary : #CB4042;   /* 赤紅 */
  --theme-light   : #F3E6E7;
  --theme-accent  : #22EB1F;
  --theme-dark    : #360C0C;
  --theme-neutral : #E8E2E3;
  --theme-text    : #F5F2EB;
}

[data-theme="haizakura"] {
  --theme-primary : #D7C4BB;   /* 灰桜 */
  --theme-light   : #F1EBE8;
  --theme-accent  : #7CCE97;
  --theme-dark    : #402D23;
  --theme-neutral : #E6E5E4;
  --theme-text    : #1C1C1C;
}

/* 🍂 朱・橙 */
[data-theme="akebono"] {
  --theme-primary : #F19483;   /* 曙 */
  --theme-light   : #F3E8E6;
  --theme-accent  : #4CFE68;
  --theme-dark    : #51160B;
  --theme-neutral : #E8E3E2;
  --theme-text    : #1C1C1C;
}

[data-theme="sangosyu"] {
  --theme-primary : #F17C67;   /* 珊瑚朱 */
  --theme-light   : #F3E8E6;
  --theme-accent  : #4CFE67;
  --theme-dark    : #4B140A;
  --theme-neutral : #E8E3E2;
  --theme-text    : #1C1C1C;
}

[data-theme="syojyohi"] {
  --theme-primary : #E83015;   /* 猩猩緋 */
  --theme-light   : #F3E8E6;
  --theme-accent  : #00FD20;
  --theme-dark    : #370D07;
  --theme-neutral : #E8E3E2;
  --theme-text    : #F5F2EB;
}

[data-theme="entan"] {
  --theme-primary : #D75455;   /* 鉛丹 */
  --theme-light   : #F3E6E6;
  --theme-accent  : #38F337;
  --theme-dark    : #3E0B0C;
  --theme-neutral : #E8E2E2;
  --theme-text    : #F5F2EB;
}

[data-theme="benihi"] {
  --theme-primary : #F75C2F;   /* 紅緋 */
  --theme-light   : #F3E9E6;
  --theme-accent  : #26FF57;
  --theme-dark    : #401509;
  --theme-neutral : #E8E4E2;
  --theme-text    : #F5F2EB;
}

[data-theme="terigaki"] {
  --theme-primary : #C46243;   /* 照柿 */
  --theme-light   : #F3E9E6;
  --theme-accent  : #23E351;
  --theme-dark    : #33170D;
  --theme-neutral : #E7E4E3;
  --theme-text    : #F5F2EB;
}

[data-theme="araisyu"] {
  --theme-primary : #FB966E;   /* 洗朱 */
  --theme-light   : #F3EAE6;
  --theme-accent  : #4CFE7F;
  --theme-dark    : #4E1E0B;
  --theme-neutral : #E8E4E2;
  --theme-text    : #1C1C1C;
}

[data-theme="ohni"] {
  --theme-primary : #F05E1C;   /* 黄丹 */
  --theme-light   : #F3EAE6;
  --theme-accent  : #0DFE58;
  --theme-dark    : #3A1808;
  --theme-neutral : #E8E4E2;
  --theme-text    : #F5F2EB;
}

[data-theme="sohi"] {
  --theme-primary : #ED784A;   /* 纁 */
  --theme-light   : #F3EAE6;
  --theme-accent  : #38FF70;
  --theme-dark    : #441A09;
  --theme-neutral : #E8E4E2;
  --theme-text    : #F5F2EB;
}

[data-theme="ensyucha"] {
  --theme-primary : #CA7853;   /* 遠州茶 */
  --theme-light   : #F3EAE6;
  --theme-accent  : #36E66D;
  --theme-dark    : #381B0E;
  --theme-neutral : #E7E4E3;
  --theme-text    : #F5F2EB;
}

[data-theme="kogecha"] {
  --theme-primary : #563F2E;   /* 焦茶 */
  --theme-light   : #F2ECE7;
  --theme-accent  : #2F9259;
  --theme-dark    : #221810;
  --theme-neutral : #E6E5E4;
  --theme-text    : #F5F2EB;
}

[data-theme="akakoh"] {
  --theme-primary : #E3916E;   /* 赤香 */
  --theme-light   : #F3EAE6;
  --theme-accent  : #4FFB83;
  --theme-dark    : #491D0A;
  --theme-neutral : #E8E4E2;
  --theme-text    : #1C1C1C;
}

[data-theme="kokikuchinashi"] {
  --theme-primary : #FB9966;   /* 深支子 */
  --theme-light   : #F3EBE6;
  --theme-accent  : #4CFE89;
  --theme-dark    : #4D210B;
  --theme-neutral : #E8E4E2;
  --theme-text    : #1C1C1C;
}

[data-theme="taisya"] {
  --theme-primary : #A36336;   /* 代赭 */
  --theme-light   : #F3ECE6;
  --theme-accent  : #1ABE5E;
  --theme-dark    : #2A180C;
  --theme-neutral : #E7E5E3;
  --theme-text    : #F5F2EB;
}

/* 🌾 黄・茶 */
[data-theme="kanzo"] {
  --theme-primary : #FC9F4D;   /* 萱草 */
  --theme-light   : #F3ECE6;
  --theme-accent  : #4AFE9E;
  --theme-dark    : #47270A;
  --theme-neutral : #E8E5E2;
  --theme-text    : #1C1C1C;
}

[data-theme="beniukon"] {
  --theme-primary : #E98B2A;   /* 紅鬱金 */
  --theme-light   : #F3EDE6;
  --theme-accent  : #14FE8B;
  --theme-dark    : #3C2208;
  --theme-neutral : #E8E5E2;
  --theme-text    : #1C1C1C;
}

[data-theme="kohaku"] {
  --theme-primary : #CA7A2C;   /* 琥珀 */
  --theme-light   : #F3EDE6;
  --theme-accent  : #09EC79;
  --theme-dark    : #341E09;
  --theme-neutral : #E8E5E2;
  --theme-text    : #F5F2EB;
}

[data-theme="kuchiba"] {
  --theme-primary : #E2943B;   /* 朽葉 */
  --theme-light   : #F3EDE6;
  --theme-accent  : #1EFF95;
  --theme-dark    : #3E2508;
  --theme-neutral : #E8E5E2;
  --theme-text    : #1C1C1C;
}

[data-theme="yamabuki"] {
  --theme-primary : #FFB11B;   /* 山吹 */
  --theme-light   : #F3EFE6;
  --theme-accent  : #1BFFB0;
  --theme-dark    : #3D2B08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="hajizome"] {
  --theme-primary : #DDA52D;   /* 櫨染 */
  --theme-light   : #F3EFE6;
  --theme-accent  : #0BFEB1;
  --theme-dark    : #3A2A08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tamago"] {
  --theme-primary : #F9BF45;   /* 玉子 */
  --theme-light   : #F3EFE6;
  --theme-accent  : #3FFFC1;
  --theme-dark    : #453209;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tamamorokoshi"] {
  --theme-primary : #E8B647;   /* 玉蜀黍 */
  --theme-light   : #F3EFE6;
  --theme-accent  : #30FFBE;
  --theme-dark    : #423009;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="usuki"] {
  --theme-primary : #FAD689;   /* 浅黄 */
  --theme-light   : #F3EFE6;
  --theme-accent  : #4CFEC6;
  --theme-dark    : #543D0C;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="kuchinashi"] {
  --theme-primary : #F6C555;   /* 梔子 */
  --theme-light   : #F3EFE6;
  --theme-accent  : #4CFEC8;
  --theme-dark    : #48350A;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tohoh"] {
  --theme-primary : #FFC408;   /* 籐黄 */
  --theme-light   : #F3F0E6;
  --theme-accent  : #07FFC4;
  --theme-dark    : #392D08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="ukon"] {
  --theme-primary : #EFBB24;   /* 鬱金 */
  --theme-light   : #F3F0E6;
  --theme-accent  : #14FEC2;
  --theme-dark    : #3C2E08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tonoko"] {
  --theme-primary : #D7B98E;   /* 砥粉 */
  --theme-light   : #F3EEE6;
  --theme-accent  : #65E6B1;
  --theme-dark    : #443015;
  --theme-neutral : #E7E5E3;
  --theme-text    : #1C1C1C;
}

[data-theme="kenpohzome"] {
  --theme-primary : #43341B;   /* 憲法染 */
  --theme-light   : #F3EEE6;
  --theme-accent  : #20A070;
  --theme-dark    : #251C0D;
  --theme-neutral : #E7E5E3;
  --theme-text    : #F5F2EB;
}

/* 🌿 緑 */
[data-theme="kariyasu"] {
  --theme-primary : #E9CD4C;   /* 刈安 */
  --theme-light   : #F3F1E6;
  --theme-accent  : #35FFDB;
  --theme-dark    : #433909;
  --theme-neutral : #E8E7E2;
  --theme-text    : #1C1C1C;
}

[data-theme="hiwa"] {
  --theme-primary : #BEC23F;   /* 鶸 */
  --theme-light   : #F3F3E6;
  --theme-accent  : #1EDCE2;
  --theme-dark    : #31320D;
  --theme-neutral : #E7E7E3;
  --theme-text    : #1C1C1C;
}

[data-theme="koke"] {
  --theme-primary : #838A2D;   /* 苔 */
  --theme-light   : #F2F3E6;
  --theme-accent  : #179FAA;
  --theme-dark    : #25270B;
  --theme-neutral : #E7E7E3;
  --theme-text    : #F5F2EB;
}

[data-theme="hiwamoegi"] {
  --theme-primary : #90B44B;   /* 鶸萌黄 */
  --theme-light   : #EFF3E6;
  --theme-accent  : #2D99D1;
  --theme-dark    : #242E11;
  --theme-neutral : #E6E7E3;
  --theme-text    : #1C1C1C;
}

[data-theme="yanagizome"] {
  --theme-primary : #91AD70;   /* 柳染 */
  --theme-light   : #EDF1E8;
  --theme-accent  : #5992C3;
  --theme-dark    : #242E19;
  --theme-neutral : #E5E6E4;
  --theme-text    : #1C1C1C;
}

[data-theme="moegi"] {
  --theme-primary : #7BA23F;   /* 萌黄 */
  --theme-light   : #EEF3E6;
  --theme-accent  : #2480BC;
  --theme-dark    : #1F290E;
  --theme-neutral : #E5E7E3;
  --theme-text    : #F5F2EB;
}

[data-theme="nae"] {
  --theme-primary : #86C166;   /* 苗 */
  --theme-light   : #EBF3E6;
  --theme-accent  : #4C7EDA;
  --theme-dark    : #1F3613;
  --theme-neutral : #E4E7E3;
  --theme-text    : #1C1C1C;
}

[data-theme="matsuba"] {
  --theme-primary : #42602D;   /* 松葉 */
  --theme-light   : #ECF3E6;
  --theme-accent  : #285699;
  --theme-dark    : #17230F;
  --theme-neutral : #E5E7E3;
  --theme-text    : #F5F2EB;
}

[data-theme="tokiwa"] {
  --theme-primary : #1B813E;   /* 常磐 */
  --theme-light   : #E6F3EB;
  --theme-accent  : #4406BB;
  --theme-dark    : #072B13;
  --theme-neutral : #E2E8E4;
  --theme-text    : #F5F2EB;
}

[data-theme="wakatake"] {
  --theme-primary : #5DAC81;   /* 若竹 */
  --theme-light   : #E7F2EC;
  --theme-accent  : #7E42C6;
  --theme-dark    : #152C20;
  --theme-neutral : #E4E6E5;
  --theme-text    : #1C1C1C;
}

[data-theme="midori"] {
  --theme-primary : #227D51;   /* 緑 */
  --theme-light   : #E6F3ED;
  --theme-accent  : #630FB1;
  --theme-dark    : #09291A;
  --theme-neutral : #E2E8E5;
  --theme-text    : #F5F2EB;
}

[data-theme="byakuroku"] {
  --theme-primary : #A8D8B9;   /* 白緑 */
  --theme-light   : #E6F3EB;
  --theme-accent  : #956FDB;
  --theme-dark    : #1B442A;
  --theme-neutral : #E3E7E4;
  --theme-text    : #1C1C1C;
}

[data-theme="tokusa"] {
  --theme-primary : #2D6D4B;   /* 木賊 */
  --theme-light   : #E6F3EC;
  --theme-accent  : #5C229F;
  --theme-dark    : #0D2518;
  --theme-neutral : #E3E7E5;
  --theme-text    : #F5F2EB;
}

[data-theme="rokusyoh"] {
  --theme-primary : #24936E;   /* 緑青 */
  --theme-light   : #E6F3EF;
  --theme-accent  : #7D0BB5;
  --theme-dark    : #082A1F;
  --theme-neutral : #E2E8E6;
  --theme-text    : #F5F2EB;
}

/* 🌊 藍 */
[data-theme="aomidori"] {
  --theme-primary : #00AA90;   /* 青緑 */
  --theme-light   : #E6F3F1;
  --theme-accent  : #A400C1;
  --theme-dark    : #062C26;
  --theme-neutral : #E2E8E7;
  --theme-text    : #F5F2EB;
}

[data-theme="seiji"] {
  --theme-primary : #69B0AC;   /* 青磁 */
  --theme-light   : #E7F2F2;
  --theme-accent  : #C150C8;
  --theme-dark    : #172F2D;
  --theme-neutral : #E4E6E6;
  --theme-text    : #1C1C1C;
}

[data-theme="mizuasagi"] {
  --theme-primary : #66BAB7;   /* 水浅葱 */
  --theme-light   : #E6F3F2;
  --theme-accent  : #CE4CD3;
  --theme-dark    : #153231;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="byakugun"] {
  --theme-primary : #78C2C4;   /* 白群 */
  --theme-light   : #E6F3F3;
  --theme-accent  : #DA61D6;
  --theme-dark    : #163738;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="kamenozoki"] {
  --theme-primary : #A5DEE4;   /* 瓶覗 */
  --theme-light   : #E6F2F3;
  --theme-accent  : #EC5EDF;
  --theme-dark    : #14484E;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="mizu"] {
  --theme-primary : #81C7D4;   /* 水 */
  --theme-light   : #E6F1F3;
  --theme-accent  : #E763D3;
  --theme-dark    : #133A41;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="asagi"] {
  --theme-primary : #33A6B8;   /* 浅葱 */
  --theme-light   : #E6F1F3;
  --theme-accent  : #D614BC;
  --theme-dark    : #0B2A2F;
  --theme-neutral : #E2E7E8;
  --theme-text    : #F5F2EB;
}

[data-theme="shinbashi"] {
  --theme-primary : #0089A7;   /* 新橋 */
  --theme-light   : #E6F1F3;
  --theme-accent  : #C1009E;
  --theme-dark    : #06252C;
  --theme-neutral : #E2E7E8;
  --theme-text    : #F5F2EB;
}

[data-theme="hanaasagi"] {
  --theme-primary : #1E88A8;   /* 花浅葱 */
  --theme-light   : #E6F0F3;
  --theme-accent  : #C40197;
  --theme-dark    : #06232C;
  --theme-neutral : #E2E6E8;
  --theme-text    : #F5F2EB;
}

[data-theme="sora"] {
  --theme-primary : #58B2DC;   /* 空 */
  --theme-light   : #E6EFF3;
  --theme-accent  : #F83BBC;
  --theme-dark    : #0A3042;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

[data-theme="chigusa"] {
  --theme-primary : #3A8FB7;   /* 千草 */
  --theme-light   : #E6EFF3;
  --theme-accent  : #D51B9A;
  --theme-dark    : #0C242F;
  --theme-neutral : #E3E6E7;
  --theme-text    : #F5F2EB;
}

[data-theme="hanada"] {
  --theme-primary : #006284;   /* 縹 */
  --theme-light   : #E6F0F3;
  --theme-accent  : #C1008F;
  --theme-dark    : #06222C;
  --theme-neutral : #E2E6E8;
  --theme-text    : #F5F2EB;
}

[data-theme="wasurenagusa"] {
  --theme-primary : #7DB9DE;   /* 勿忘草 */
  --theme-light   : #E6EEF3;
  --theme-accent  : #F258B8;
  --theme-dark    : #0E3247;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

[data-theme="tsuyukusa"] {
  --theme-primary : #2EA9DF;   /* 露草 */
  --theme-light   : #E6EFF3;
  --theme-accent  : #FE0EB5;
  --theme-dark    : #082B3A;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

/* 💙 青・紺 */
[data-theme="gunjyo"] {
  --theme-primary : #51A8DD;   /* 群青 */
  --theme-light   : #E6EEF3;
  --theme-accent  : #FA33AF;
  --theme-dark    : #092C41;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

[data-theme="ruri"] {
  --theme-primary : #005CAF;   /* 瑠璃 */
  --theme-light   : #E6EDF3;
  --theme-accent  : #C10065;
  --theme-dark    : #061A2C;
  --theme-neutral : #E2E5E8;
  --theme-text    : #F5F2EB;
}

[data-theme="rurikon"] {
  --theme-primary : #0B346E;   /* 瑠璃紺 */
  --theme-light   : #E6ECF3;
  --theme-accent  : #C10050;
  --theme-dark    : #06162C;
  --theme-neutral : #E2E5E8;
  --theme-text    : #F5F2EB;
}

[data-theme="benimidori"] {
  --theme-primary : #7B90D2;   /* 紅碧 */
  --theme-light   : #E6E9F3;
  --theme-accent  : #E76383;
  --theme-dark    : #131D40;
  --theme-neutral : #E3E4E7;
  --theme-text    : #F5F2EB;
}

[data-theme="fujinezumi"] {
  --theme-primary : #6E75A4;   /* 藤鼠 */
  --theme-light   : #E9EAF1;
  --theme-accent  : #BB5663;
  --theme-dark    : #191B2A;
  --theme-neutral : #E4E4E6;
  --theme-text    : #F5F2EB;
}

[data-theme="benikakehana"] {
  --theme-primary : #4E4F97;   /* 紅掛花 */
  --theme-light   : #E7E7F2;
  --theme-accent  : #AF3537;
  --theme-dark    : #121226;
  --theme-neutral : #E4E4E6;
  --theme-text    : #F5F2EB;
}

[data-theme="konjyo"] {
  --theme-primary : #113285;   /* 紺青 */
  --theme-light   : #E6EAF3;
  --theme-accent  : #C10037;
  --theme-dark    : #06112C;
  --theme-neutral : #E2E4E8;
  --theme-text    : #F5F2EB;
}

[data-theme="kon"] {
  --theme-primary : #0F2540;   /* 紺 */
  --theme-light   : #E6ECF3;
  --theme-accent  : #B70A58;
  --theme-dark    : #08172A;
  --theme-neutral : #E2E5E8;
  --theme-text    : #F5F2EB;
}

[data-theme="konkikyo"] {
  --theme-primary : #211E55;   /* 紺桔梗 */
  --theme-light   : #E7E6F3;
  --theme-accent  : #A7221A;
  --theme-dark    : #0D0C26;
  --theme-neutral : #E3E3E7;
  --theme-text    : #F5F2EB;
}

[data-theme="kurotsurubami"] {
  --theme-primary : #0B1013;   /* 黒橡 */
  --theme-light   : #E8EEF1;
  --theme-accent  : #8E336C;
  --theme-dark    : #121B20;
  --theme-neutral : #E4E5E6;
  --theme-text    : #F5F2EB;
}

/* 💜 紫 */
[data-theme="fuji"] {
  --theme-primary : #8B81C3;   /* 藤 */
  --theme-light   : #E8E6F3;
  --theme-accent  : #D77C6C;
  --theme-dark    : #1D1838;
  --theme-neutral : #E4E3E7;
  --theme-text    : #F5F2EB;
}

[data-theme="fujimurasaki"] {
  --theme-primary : #8A6BBE;   /* 藤紫 */
  --theme-light   : #EBE6F3;
  --theme-accent  : #D68352;
  --theme-dark    : #211535;
  --theme-neutral : #E5E3E7;
  --theme-text    : #F5F2EB;
}

[data-theme="kikyo"] {
  --theme-primary : #6A4C9C;   /* 桔梗 */
  --theme-light   : #EBE6F3;
  --theme-accent  : #B56332;
  --theme-dark    : #1A1228;
  --theme-neutral : #E5E3E7;
  --theme-text    : #F5F2EB;
}

[data-theme="shion"] {
  --theme-primary : #8F77B5;   /* 紫苑 */
  --theme-light   : #EBE7F2;
  --theme-accent  : #CA8A61;
  --theme-dark    : #221931;
  --theme-neutral : #E5E4E6;
  --theme-text    : #F5F2EB;
}

[data-theme="usu"] {
  --theme-primary : #B28FCE;   /* 薄 */
  --theme-light   : #EDE6F3;
  --theme-accent  : #DDAB6E;
  --theme-dark    : #2D183E;
  --theme-neutral : #E5E3E7;
  --theme-text    : #1C1C1C;
}

[data-theme="edomurasaki"] {
  --theme-primary : #77428D;   /* 江戸紫 */
  --theme-light   : #EFE6F3;
  --theme-accent  : #A4802A;
  --theme-dark    : #1E0F24;
  --theme-neutral : #E6E3E7;
  --theme-text    : #F5F2EB;
}

[data-theme="murasaki"] {
  --theme-primary : #592C63;   /* 紫 */
  --theme-light   : #F1E6F3;
  --theme-accent  : #9C8625;
  --theme-dark    : #200E24;
  --theme-neutral : #E6E3E7;
  --theme-text    : #F5F2EB;
}

[data-theme="benifuji"] {
  --theme-primary : #B481BB;   /* 紅藤 */
  --theme-light   : #F1E7F2;
  --theme-accent  : #CFC36C;
  --theme-dark    : #311A34;
  --theme-neutral : #E6E4E6;
  --theme-text    : #F5F2EB;
}

[data-theme="botan"] {
  --theme-primary : #C1328E;   /* 牡丹 */
  --theme-light   : #F3E6EE;
  --theme-accent  : #97E111;
  --theme-dark    : #320A24;
  --theme-neutral : #E8E2E6;
  --theme-text    : #F5F2EB;
}

[data-theme="tsutsuji"] {
  --theme-primary : #E03C8A;   /* 躑躅 */
  --theme-light   : #F3E6EC;
  --theme-accent  : #88FF1D;
  --theme-dark    : #3E0822;
  --theme-neutral : #E8E2E5;
  --theme-text    : #F5F2EB;
}

/* ⬜ 白灰黒 */
[data-theme="shironeri"] {
  --theme-primary : #FCFAF2;   /* 白練 */
  --theme-light   : #F3F0E6;
  --theme-accent  : #55F6D5;
  --theme-dark    : #685713;
  --theme-neutral : #E8E7E2;
  --theme-text    : #1C1C1C;
}

[data-theme="shironezumi"] {
  --theme-primary : #BDC0BA;   /* 白鼠 */
  --theme-light   : #EDEDEC;
  --theme-accent  : #93A5B8;
  --theme-dark    : #2F312C;
  --theme-neutral : #E5E5E5;
  --theme-text    : #1C1C1C;
}

[data-theme="ginnezumi"] {
  --theme-primary : #91989F;   /* 銀鼠 */
  --theme-light   : #EBEDEE;
  --theme-accent  : #AF8098;
  --theme-dark    : #232628;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

[data-theme="namari"] {
  --theme-primary : #787878;   /* 鉛 */
  --theme-light   : #EDEDED;
  --theme-accent  : #668966;
  --theme-dark    : #1D1D1D;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

[data-theme="hai"] {
  --theme-primary : #828282;   /* 灰 */
  --theme-light   : #EDEDED;
  --theme-accent  : #6F946F;
  --theme-dark    : #202020;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

[data-theme="nibi"] {
  --theme-primary : #656765;   /* 鈍 */
  --theme-light   : #ECEDEC;
  --theme-accent  : #555576;
  --theme-dark    : #191919;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

[data-theme="aonibi"] {
  --theme-primary : #535953;   /* 青鈍 */
  --theme-light   : #ECEDEC;
  --theme-accent  : #4E4E73;
  --theme-dark    : #181A18;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

[data-theme="keshizumi"] {
  --theme-primary : #434343;   /* 消炭 */
  --theme-light   : #EDEDED;
  --theme-accent  : #526F52;
  --theme-dark    : #191919;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

[data-theme="sumi"] {
  --theme-primary : #1C1C1C;   /* 墨 */
  --theme-light   : #EDEDED;
  --theme-accent  : #526F52;
  --theme-dark    : #191919;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

[data-theme="kuro"] {
  --theme-primary : #080808;   /* 黒 */
  --theme-light   : #EDEDED;
  --theme-accent  : #526F52;
  --theme-dark    : #191919;
  --theme-neutral : #E5E5E5;
  --theme-text    : #F5F2EB;
}

```

---

## 📊 色盤速查表（100 種）

### 🌸 紅・桃

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 001 | 撫子 | `nadeshiko` | `#DC9FB4` | `#F3E6EB` | `#92E566` | `#471727` | `#E7E3E4` | `#1C1C1C` |
| 002 | 紅梅 | `kohbai` | `#E16B8C` | `#F3E6EA` | `#80FA51` | `#470B1C` | `#E8E2E4` | `#F5F2EB` |
| 003 | 蘇芳 | `suoh` | `#8E354A` | `#F3E6E9` | `#3DA51D` | `#260C12` | `#E7E3E4` | `#F5F2EB` |
| 004 | 退紅 | `taikoh` | `#F8C3CD` | `#F3E6E9` | `#6EFE4C` | `#600D1D` | `#E8E2E3` | `#1C1C1C` |
| 005 | 桃 | `momo` | `#F596AA` | `#F3E6E9` | `#72FE4C` | `#560C1B` | `#E8E2E4` | `#1C1C1C` |
| 006 | 苺 | `ichigo` | `#B5495B` | `#F3E6E8` | `#47D22B` | `#2E1015` | `#E7E3E4` | `#F5F2EB` |
| 007 | 韓紅花 | `karakurenai` | `#D0104C` | `#F3E6EA` | `#46E000` | `#300714` | `#E8E2E4` | `#F5F2EB` |
| 008 | 紅 | `kurenai` | `#CB1B45` | `#F3E6E9` | `#36E500` | `#320711` | `#E8E2E4` | `#F5F2EB` |
| 009 | 鴇 | `toki` | `#EEA9A9` | `#F3E6E6` | `#50FA50` | `#580D0D` | `#E8E2E2` | `#1C1C1C` |
| 010 | 深緋 | `kokiake` | `#86473F` | `#F3E8E6` | `#299B36` | `#23110F` | `#E7E4E3` | `#F5F2EB` |
| 011 | 甚三紅 | `jinzamomi` | `#EB7A77` | `#F3E7E6` | `#4CFE51` | `#4D0C0B` | `#E8E3E2` | `#1C1C1C` |
| 012 | 小豆 | `azuki` | `#954A45` | `#F3E7E6` | `#2CAD34` | `#261110` | `#E7E4E3` | `#F5F2EB` |
| 013 | 赤紅 | `akabeni` | `#CB4042` | `#F3E6E7` | `#22EB1F` | `#360C0C` | `#E8E2E3` | `#F5F2EB` |
| 014 | 灰桜 | `haizakura` | `#D7C4BB` | `#F1EBE8` | `#7CCE97` | `#402D23` | `#E6E5E4` | `#1C1C1C` |

### 🍂 朱・橙

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 015 | 曙 | `akebono` | `#F19483` | `#F3E8E6` | `#4CFE68` | `#51160B` | `#E8E3E2` | `#1C1C1C` |
| 016 | 珊瑚朱 | `sangosyu` | `#F17C67` | `#F3E8E6` | `#4CFE67` | `#4B140A` | `#E8E3E2` | `#1C1C1C` |
| 017 | 猩猩緋 | `syojyohi` | `#E83015` | `#F3E8E6` | `#00FD20` | `#370D07` | `#E8E3E2` | `#F5F2EB` |
| 018 | 鉛丹 | `entan` | `#D75455` | `#F3E6E6` | `#38F337` | `#3E0B0C` | `#E8E2E2` | `#F5F2EB` |
| 019 | 紅緋 | `benihi` | `#F75C2F` | `#F3E9E6` | `#26FF57` | `#401509` | `#E8E4E2` | `#F5F2EB` |
| 020 | 照柿 | `terigaki` | `#C46243` | `#F3E9E6` | `#23E351` | `#33170D` | `#E7E4E3` | `#F5F2EB` |
| 021 | 洗朱 | `araisyu` | `#FB966E` | `#F3EAE6` | `#4CFE7F` | `#4E1E0B` | `#E8E4E2` | `#1C1C1C` |
| 022 | 黄丹 | `ohni` | `#F05E1C` | `#F3EAE6` | `#0DFE58` | `#3A1808` | `#E8E4E2` | `#F5F2EB` |
| 023 | 纁 | `sohi` | `#ED784A` | `#F3EAE6` | `#38FF70` | `#441A09` | `#E8E4E2` | `#F5F2EB` |
| 024 | 遠州茶 | `ensyucha` | `#CA7853` | `#F3EAE6` | `#36E66D` | `#381B0E` | `#E7E4E3` | `#F5F2EB` |
| 025 | 焦茶 | `kogecha` | `#563F2E` | `#F2ECE7` | `#2F9259` | `#221810` | `#E6E5E4` | `#F5F2EB` |
| 026 | 赤香 | `akakoh` | `#E3916E` | `#F3EAE6` | `#4FFB83` | `#491D0A` | `#E8E4E2` | `#1C1C1C` |
| 027 | 深支子 | `kokikuchinashi` | `#FB9966` | `#F3EBE6` | `#4CFE89` | `#4D210B` | `#E8E4E2` | `#1C1C1C` |
| 028 | 代赭 | `taisya` | `#A36336` | `#F3ECE6` | `#1ABE5E` | `#2A180C` | `#E7E5E3` | `#F5F2EB` |

### 🌾 黄・茶

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 029 | 萱草 | `kanzo` | `#FC9F4D` | `#F3ECE6` | `#4AFE9E` | `#47270A` | `#E8E5E2` | `#1C1C1C` |
| 030 | 紅鬱金 | `beniukon` | `#E98B2A` | `#F3EDE6` | `#14FE8B` | `#3C2208` | `#E8E5E2` | `#1C1C1C` |
| 031 | 琥珀 | `kohaku` | `#CA7A2C` | `#F3EDE6` | `#09EC79` | `#341E09` | `#E8E5E2` | `#F5F2EB` |
| 032 | 朽葉 | `kuchiba` | `#E2943B` | `#F3EDE6` | `#1EFF95` | `#3E2508` | `#E8E5E2` | `#1C1C1C` |
| 033 | 山吹 | `yamabuki` | `#FFB11B` | `#F3EFE6` | `#1BFFB0` | `#3D2B08` | `#E8E6E2` | `#1C1C1C` |
| 034 | 櫨染 | `hajizome` | `#DDA52D` | `#F3EFE6` | `#0BFEB1` | `#3A2A08` | `#E8E6E2` | `#1C1C1C` |
| 035 | 玉子 | `tamago` | `#F9BF45` | `#F3EFE6` | `#3FFFC1` | `#453209` | `#E8E6E2` | `#1C1C1C` |
| 036 | 玉蜀黍 | `tamamorokoshi` | `#E8B647` | `#F3EFE6` | `#30FFBE` | `#423009` | `#E8E6E2` | `#1C1C1C` |
| 037 | 浅黄 | `usuki` | `#FAD689` | `#F3EFE6` | `#4CFEC6` | `#543D0C` | `#E8E6E2` | `#1C1C1C` |
| 038 | 梔子 | `kuchinashi` | `#F6C555` | `#F3EFE6` | `#4CFEC8` | `#48350A` | `#E8E6E2` | `#1C1C1C` |
| 039 | 籐黄 | `tohoh` | `#FFC408` | `#F3F0E6` | `#07FFC4` | `#392D08` | `#E8E6E2` | `#1C1C1C` |
| 040 | 鬱金 | `ukon` | `#EFBB24` | `#F3F0E6` | `#14FEC2` | `#3C2E08` | `#E8E6E2` | `#1C1C1C` |
| 041 | 砥粉 | `tonoko` | `#D7B98E` | `#F3EEE6` | `#65E6B1` | `#443015` | `#E7E5E3` | `#1C1C1C` |
| 042 | 憲法染 | `kenpohzome` | `#43341B` | `#F3EEE6` | `#20A070` | `#251C0D` | `#E7E5E3` | `#F5F2EB` |

### 🌿 緑

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 043 | 刈安 | `kariyasu` | `#E9CD4C` | `#F3F1E6` | `#35FFDB` | `#433909` | `#E8E7E2` | `#1C1C1C` |
| 044 | 鶸 | `hiwa` | `#BEC23F` | `#F3F3E6` | `#1EDCE2` | `#31320D` | `#E7E7E3` | `#1C1C1C` |
| 045 | 苔 | `koke` | `#838A2D` | `#F2F3E6` | `#179FAA` | `#25270B` | `#E7E7E3` | `#F5F2EB` |
| 046 | 鶸萌黄 | `hiwamoegi` | `#90B44B` | `#EFF3E6` | `#2D99D1` | `#242E11` | `#E6E7E3` | `#1C1C1C` |
| 047 | 柳染 | `yanagizome` | `#91AD70` | `#EDF1E8` | `#5992C3` | `#242E19` | `#E5E6E4` | `#1C1C1C` |
| 048 | 萌黄 | `moegi` | `#7BA23F` | `#EEF3E6` | `#2480BC` | `#1F290E` | `#E5E7E3` | `#F5F2EB` |
| 049 | 苗 | `nae` | `#86C166` | `#EBF3E6` | `#4C7EDA` | `#1F3613` | `#E4E7E3` | `#1C1C1C` |
| 050 | 松葉 | `matsuba` | `#42602D` | `#ECF3E6` | `#285699` | `#17230F` | `#E5E7E3` | `#F5F2EB` |
| 051 | 常磐 | `tokiwa` | `#1B813E` | `#E6F3EB` | `#4406BB` | `#072B13` | `#E2E8E4` | `#F5F2EB` |
| 052 | 若竹 | `wakatake` | `#5DAC81` | `#E7F2EC` | `#7E42C6` | `#152C20` | `#E4E6E5` | `#1C1C1C` |
| 053 | 緑 | `midori` | `#227D51` | `#E6F3ED` | `#630FB1` | `#09291A` | `#E2E8E5` | `#F5F2EB` |
| 054 | 白緑 | `byakuroku` | `#A8D8B9` | `#E6F3EB` | `#956FDB` | `#1B442A` | `#E3E7E4` | `#1C1C1C` |
| 055 | 木賊 | `tokusa` | `#2D6D4B` | `#E6F3EC` | `#5C229F` | `#0D2518` | `#E3E7E5` | `#F5F2EB` |
| 056 | 緑青 | `rokusyoh` | `#24936E` | `#E6F3EF` | `#7D0BB5` | `#082A1F` | `#E2E8E6` | `#F5F2EB` |

### 🌊 藍

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 057 | 青緑 | `aomidori` | `#00AA90` | `#E6F3F1` | `#A400C1` | `#062C26` | `#E2E8E7` | `#F5F2EB` |
| 058 | 青磁 | `seiji` | `#69B0AC` | `#E7F2F2` | `#C150C8` | `#172F2D` | `#E4E6E6` | `#1C1C1C` |
| 059 | 水浅葱 | `mizuasagi` | `#66BAB7` | `#E6F3F2` | `#CE4CD3` | `#153231` | `#E3E7E7` | `#1C1C1C` |
| 060 | 白群 | `byakugun` | `#78C2C4` | `#E6F3F3` | `#DA61D6` | `#163738` | `#E3E7E7` | `#1C1C1C` |
| 061 | 瓶覗 | `kamenozoki` | `#A5DEE4` | `#E6F2F3` | `#EC5EDF` | `#14484E` | `#E3E7E7` | `#1C1C1C` |
| 062 | 水 | `mizu` | `#81C7D4` | `#E6F1F3` | `#E763D3` | `#133A41` | `#E3E7E7` | `#1C1C1C` |
| 063 | 浅葱 | `asagi` | `#33A6B8` | `#E6F1F3` | `#D614BC` | `#0B2A2F` | `#E2E7E8` | `#F5F2EB` |
| 064 | 新橋 | `shinbashi` | `#0089A7` | `#E6F1F3` | `#C1009E` | `#06252C` | `#E2E7E8` | `#F5F2EB` |
| 065 | 花浅葱 | `hanaasagi` | `#1E88A8` | `#E6F0F3` | `#C40197` | `#06232C` | `#E2E6E8` | `#F5F2EB` |
| 066 | 空 | `sora` | `#58B2DC` | `#E6EFF3` | `#F83BBC` | `#0A3042` | `#E2E6E8` | `#1C1C1C` |
| 067 | 千草 | `chigusa` | `#3A8FB7` | `#E6EFF3` | `#D51B9A` | `#0C242F` | `#E3E6E7` | `#F5F2EB` |
| 068 | 縹 | `hanada` | `#006284` | `#E6F0F3` | `#C1008F` | `#06222C` | `#E2E6E8` | `#F5F2EB` |
| 069 | 勿忘草 | `wasurenagusa` | `#7DB9DE` | `#E6EEF3` | `#F258B8` | `#0E3247` | `#E2E6E8` | `#1C1C1C` |
| 070 | 露草 | `tsuyukusa` | `#2EA9DF` | `#E6EFF3` | `#FE0EB5` | `#082B3A` | `#E2E6E8` | `#1C1C1C` |

### 💙 青・紺

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 071 | 群青 | `gunjyo` | `#51A8DD` | `#E6EEF3` | `#FA33AF` | `#092C41` | `#E2E6E8` | `#1C1C1C` |
| 072 | 瑠璃 | `ruri` | `#005CAF` | `#E6EDF3` | `#C10065` | `#061A2C` | `#E2E5E8` | `#F5F2EB` |
| 073 | 瑠璃紺 | `rurikon` | `#0B346E` | `#E6ECF3` | `#C10050` | `#06162C` | `#E2E5E8` | `#F5F2EB` |
| 074 | 紅碧 | `benimidori` | `#7B90D2` | `#E6E9F3` | `#E76383` | `#131D40` | `#E3E4E7` | `#F5F2EB` |
| 075 | 藤鼠 | `fujinezumi` | `#6E75A4` | `#E9EAF1` | `#BB5663` | `#191B2A` | `#E4E4E6` | `#F5F2EB` |
| 076 | 紅掛花 | `benikakehana` | `#4E4F97` | `#E7E7F2` | `#AF3537` | `#121226` | `#E4E4E6` | `#F5F2EB` |
| 077 | 紺青 | `konjyo` | `#113285` | `#E6EAF3` | `#C10037` | `#06112C` | `#E2E4E8` | `#F5F2EB` |
| 078 | 紺 | `kon` | `#0F2540` | `#E6ECF3` | `#B70A58` | `#08172A` | `#E2E5E8` | `#F5F2EB` |
| 079 | 紺桔梗 | `konkikyo` | `#211E55` | `#E7E6F3` | `#A7221A` | `#0D0C26` | `#E3E3E7` | `#F5F2EB` |
| 080 | 黒橡 | `kurotsurubami` | `#0B1013` | `#E8EEF1` | `#8E336C` | `#121B20` | `#E4E5E6` | `#F5F2EB` |

### 💜 紫

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 081 | 藤 | `fuji` | `#8B81C3` | `#E8E6F3` | `#D77C6C` | `#1D1838` | `#E4E3E7` | `#F5F2EB` |
| 082 | 藤紫 | `fujimurasaki` | `#8A6BBE` | `#EBE6F3` | `#D68352` | `#211535` | `#E5E3E7` | `#F5F2EB` |
| 083 | 桔梗 | `kikyo` | `#6A4C9C` | `#EBE6F3` | `#B56332` | `#1A1228` | `#E5E3E7` | `#F5F2EB` |
| 084 | 紫苑 | `shion` | `#8F77B5` | `#EBE7F2` | `#CA8A61` | `#221931` | `#E5E4E6` | `#F5F2EB` |
| 085 | 薄 | `usu` | `#B28FCE` | `#EDE6F3` | `#DDAB6E` | `#2D183E` | `#E5E3E7` | `#1C1C1C` |
| 086 | 江戸紫 | `edomurasaki` | `#77428D` | `#EFE6F3` | `#A4802A` | `#1E0F24` | `#E6E3E7` | `#F5F2EB` |
| 087 | 紫 | `murasaki` | `#592C63` | `#F1E6F3` | `#9C8625` | `#200E24` | `#E6E3E7` | `#F5F2EB` |
| 088 | 紅藤 | `benifuji` | `#B481BB` | `#F1E7F2` | `#CFC36C` | `#311A34` | `#E6E4E6` | `#F5F2EB` |
| 089 | 牡丹 | `botan` | `#C1328E` | `#F3E6EE` | `#97E111` | `#320A24` | `#E8E2E6` | `#F5F2EB` |
| 090 | 躑躅 | `tsutsuji` | `#E03C8A` | `#F3E6EC` | `#88FF1D` | `#3E0822` | `#E8E2E5` | `#F5F2EB` |

### ⬜ 白灰黒

| # | 漢字 | id | Primary | Light | Accent | Dark | Neutral | Text |
|---|------|----|---------|-------|--------|------|---------|------|
| 091 | 白練 | `shironeri` | `#FCFAF2` | `#F3F0E6` | `#55F6D5` | `#685713` | `#E8E7E2` | `#1C1C1C` |
| 092 | 白鼠 | `shironezumi` | `#BDC0BA` | `#EDEDEC` | `#93A5B8` | `#2F312C` | `#E5E5E5` | `#1C1C1C` |
| 093 | 銀鼠 | `ginnezumi` | `#91989F` | `#EBEDEE` | `#AF8098` | `#232628` | `#E5E5E5` | `#F5F2EB` |
| 094 | 鉛 | `namari` | `#787878` | `#EDEDED` | `#668966` | `#1D1D1D` | `#E5E5E5` | `#F5F2EB` |
| 095 | 灰 | `hai` | `#828282` | `#EDEDED` | `#6F946F` | `#202020` | `#E5E5E5` | `#F5F2EB` |
| 096 | 鈍 | `nibi` | `#656765` | `#ECEDEC` | `#555576` | `#191919` | `#E5E5E5` | `#F5F2EB` |
| 097 | 青鈍 | `aonibi` | `#535953` | `#ECEDEC` | `#4E4E73` | `#181A18` | `#E5E5E5` | `#F5F2EB` |
| 098 | 消炭 | `keshizumi` | `#434343` | `#EDEDED` | `#526F52` | `#191919` | `#E5E5E5` | `#F5F2EB` |
| 099 | 墨 | `sumi` | `#1C1C1C` | `#EDEDED` | `#526F52` | `#191919` | `#E5E5E5` | `#F5F2EB` |
| 100 | 黒 | `kuro` | `#080808` | `#EDEDED` | `#526F52` | `#191919` | `#E5E5E5` | `#F5F2EB` |

---

## 📌 Agent 使用提示

```
生成 HTML 頁面或 Slide 時：

1. 引入 phyra-themes.css（或將 CSS 區塊 inline 至 <style>）
2. 引入 phyra-bg.css（或 inline）
3. 在 <html data-theme="{romaji}"> 設定預設主題
4. 加入 .phyra-bg 和 .phyra-gloss 兩個 div
5. 確認 assets/texture.png 和 assets/gloss.png 路徑正確
6. 所有顏色使用 var(--p-primary/light/accent/dark/neutral/text)
7. 加入 phyra-switcher.js 啟用 100 種主題即時切換

推薦預設主題：wakatake（若竹）、hanada（縹）、kurenai（紅）
              yamabuki（山吹）、fujimurasaki（藤紫）
```

---

## 🎬 單檔 All-in-One 範本片段

> Agent 可直接複製此完整片段到 HTML 的 `<head>` 中，
> 無需外部 CSS 文件，僅需 `assets/` 目錄存在。

```html
<style>
/* === PHYRA DESIGN SYSTEM === */
:root{--p-primary:var(--theme-primary);--p-light:var(--theme-light);--p-accent:var(--theme-accent);--p-dark:var(--theme-dark);--p-neutral:var(--theme-neutral);--p-text:var(--theme-text)}
.phyra-bg{position:fixed;inset:0;z-index:0;background-color:var(--p-primary);background-image:url('./assets/texture.png');background-repeat:repeat;transition:background-color 2s ease-in;pointer-events:none}
.phyra-gloss{position:fixed;top:0;left:0;width:100%;height:478px;z-index:1;background:url('./assets/gloss.png') repeat-x;pointer-events:none}
.phyra-switcher{position:fixed;bottom:20px;right:20px;z-index:100;display:flex;align-items:center;gap:10px}
.phyra-switcher button{padding:6px 14px;background:rgba(255,255,255,.25);border:1px solid rgba(255,255,255,.5);border-radius:20px;color:var(--p-text);cursor:pointer;font-size:13px;transition:background .2s}
/* Themes */
[data-theme="nadeshiko"{--theme-primary:#DC9FB4;--theme-light:#F3E6EB;--theme-accent:#92E566;--theme-dark:#471727;--theme-neutral:#E7E3E4;--theme-text:#1C1C1C}
[data-theme="kohbai"{--theme-primary:#E16B8C;--theme-light:#F3E6EA;--theme-accent:#80FA51;--theme-dark:#470B1C;--theme-neutral:#E8E2E4;--theme-text:#F5F2EB}
[data-theme="suoh"{--theme-primary:#8E354A;--theme-light:#F3E6E9;--theme-accent:#3DA51D;--theme-dark:#260C12;--theme-neutral:#E7E3E4;--theme-text:#F5F2EB}
[data-theme="taikoh"{--theme-primary:#F8C3CD;--theme-light:#F3E6E9;--theme-accent:#6EFE4C;--theme-dark:#600D1D;--theme-neutral:#E8E2E3;--theme-text:#1C1C1C}
[data-theme="momo"{--theme-primary:#F596AA;--theme-light:#F3E6E9;--theme-accent:#72FE4C;--theme-dark:#560C1B;--theme-neutral:#E8E2E4;--theme-text:#1C1C1C}
[data-theme="ichigo"{--theme-primary:#B5495B;--theme-light:#F3E6E8;--theme-accent:#47D22B;--theme-dark:#2E1015;--theme-neutral:#E7E3E4;--theme-text:#F5F2EB}
[data-theme="karakurenai"{--theme-primary:#D0104C;--theme-light:#F3E6EA;--theme-accent:#46E000;--theme-dark:#300714;--theme-neutral:#E8E2E4;--theme-text:#F5F2EB}
[data-theme="kurenai"{--theme-primary:#CB1B45;--theme-light:#F3E6E9;--theme-accent:#36E500;--theme-dark:#320711;--theme-neutral:#E8E2E4;--theme-text:#F5F2EB}
[data-theme="toki"{--theme-primary:#EEA9A9;--theme-light:#F3E6E6;--theme-accent:#50FA50;--theme-dark:#580D0D;--theme-neutral:#E8E2E2;--theme-text:#1C1C1C}
[data-theme="kokiake"{--theme-primary:#86473F;--theme-light:#F3E8E6;--theme-accent:#299B36;--theme-dark:#23110F;--theme-neutral:#E7E4E3;--theme-text:#F5F2EB}
[data-theme="jinzamomi"{--theme-primary:#EB7A77;--theme-light:#F3E7E6;--theme-accent:#4CFE51;--theme-dark:#4D0C0B;--theme-neutral:#E8E3E2;--theme-text:#1C1C1C}
[data-theme="azuki"{--theme-primary:#954A45;--theme-light:#F3E7E6;--theme-accent:#2CAD34;--theme-dark:#261110;--theme-neutral:#E7E4E3;--theme-text:#F5F2EB}
[data-theme="akabeni"{--theme-primary:#CB4042;--theme-light:#F3E6E7;--theme-accent:#22EB1F;--theme-dark:#360C0C;--theme-neutral:#E8E2E3;--theme-text:#F5F2EB}
[data-theme="haizakura"{--theme-primary:#D7C4BB;--theme-light:#F1EBE8;--theme-accent:#7CCE97;--theme-dark:#402D23;--theme-neutral:#E6E5E4;--theme-text:#1C1C1C}
[data-theme="akebono"{--theme-primary:#F19483;--theme-light:#F3E8E6;--theme-accent:#4CFE68;--theme-dark:#51160B;--theme-neutral:#E8E3E2;--theme-text:#1C1C1C}
[data-theme="sangosyu"{--theme-primary:#F17C67;--theme-light:#F3E8E6;--theme-accent:#4CFE67;--theme-dark:#4B140A;--theme-neutral:#E8E3E2;--theme-text:#1C1C1C}
[data-theme="syojyohi"{--theme-primary:#E83015;--theme-light:#F3E8E6;--theme-accent:#00FD20;--theme-dark:#370D07;--theme-neutral:#E8E3E2;--theme-text:#F5F2EB}
[data-theme="entan"{--theme-primary:#D75455;--theme-light:#F3E6E6;--theme-accent:#38F337;--theme-dark:#3E0B0C;--theme-neutral:#E8E2E2;--theme-text:#F5F2EB}
[data-theme="benihi"{--theme-primary:#F75C2F;--theme-light:#F3E9E6;--theme-accent:#26FF57;--theme-dark:#401509;--theme-neutral:#E8E4E2;--theme-text:#F5F2EB}
[data-theme="terigaki"{--theme-primary:#C46243;--theme-light:#F3E9E6;--theme-accent:#23E351;--theme-dark:#33170D;--theme-neutral:#E7E4E3;--theme-text:#F5F2EB}
[data-theme="araisyu"{--theme-primary:#FB966E;--theme-light:#F3EAE6;--theme-accent:#4CFE7F;--theme-dark:#4E1E0B;--theme-neutral:#E8E4E2;--theme-text:#1C1C1C}
[data-theme="ohni"{--theme-primary:#F05E1C;--theme-light:#F3EAE6;--theme-accent:#0DFE58;--theme-dark:#3A1808;--theme-neutral:#E8E4E2;--theme-text:#F5F2EB}
[data-theme="sohi"{--theme-primary:#ED784A;--theme-light:#F3EAE6;--theme-accent:#38FF70;--theme-dark:#441A09;--theme-neutral:#E8E4E2;--theme-text:#F5F2EB}
[data-theme="ensyucha"{--theme-primary:#CA7853;--theme-light:#F3EAE6;--theme-accent:#36E66D;--theme-dark:#381B0E;--theme-neutral:#E7E4E3;--theme-text:#F5F2EB}
[data-theme="kogecha"{--theme-primary:#563F2E;--theme-light:#F2ECE7;--theme-accent:#2F9259;--theme-dark:#221810;--theme-neutral:#E6E5E4;--theme-text:#F5F2EB}
[data-theme="akakoh"{--theme-primary:#E3916E;--theme-light:#F3EAE6;--theme-accent:#4FFB83;--theme-dark:#491D0A;--theme-neutral:#E8E4E2;--theme-text:#1C1C1C}
[data-theme="kokikuchinashi"{--theme-primary:#FB9966;--theme-light:#F3EBE6;--theme-accent:#4CFE89;--theme-dark:#4D210B;--theme-neutral:#E8E4E2;--theme-text:#1C1C1C}
[data-theme="taisya"{--theme-primary:#A36336;--theme-light:#F3ECE6;--theme-accent:#1ABE5E;--theme-dark:#2A180C;--theme-neutral:#E7E5E3;--theme-text:#F5F2EB}
[data-theme="kanzo"{--theme-primary:#FC9F4D;--theme-light:#F3ECE6;--theme-accent:#4AFE9E;--theme-dark:#47270A;--theme-neutral:#E8E5E2;--theme-text:#1C1C1C}
[data-theme="beniukon"{--theme-primary:#E98B2A;--theme-light:#F3EDE6;--theme-accent:#14FE8B;--theme-dark:#3C2208;--theme-neutral:#E8E5E2;--theme-text:#1C1C1C}
[data-theme="kohaku"{--theme-primary:#CA7A2C;--theme-light:#F3EDE6;--theme-accent:#09EC79;--theme-dark:#341E09;--theme-neutral:#E8E5E2;--theme-text:#F5F2EB}
[data-theme="kuchiba"{--theme-primary:#E2943B;--theme-light:#F3EDE6;--theme-accent:#1EFF95;--theme-dark:#3E2508;--theme-neutral:#E8E5E2;--theme-text:#1C1C1C}
[data-theme="yamabuki"{--theme-primary:#FFB11B;--theme-light:#F3EFE6;--theme-accent:#1BFFB0;--theme-dark:#3D2B08;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="hajizome"{--theme-primary:#DDA52D;--theme-light:#F3EFE6;--theme-accent:#0BFEB1;--theme-dark:#3A2A08;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="tamago"{--theme-primary:#F9BF45;--theme-light:#F3EFE6;--theme-accent:#3FFFC1;--theme-dark:#453209;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="tamamorokoshi"{--theme-primary:#E8B647;--theme-light:#F3EFE6;--theme-accent:#30FFBE;--theme-dark:#423009;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="usuki"{--theme-primary:#FAD689;--theme-light:#F3EFE6;--theme-accent:#4CFEC6;--theme-dark:#543D0C;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="kuchinashi"{--theme-primary:#F6C555;--theme-light:#F3EFE6;--theme-accent:#4CFEC8;--theme-dark:#48350A;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="tohoh"{--theme-primary:#FFC408;--theme-light:#F3F0E6;--theme-accent:#07FFC4;--theme-dark:#392D08;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="ukon"{--theme-primary:#EFBB24;--theme-light:#F3F0E6;--theme-accent:#14FEC2;--theme-dark:#3C2E08;--theme-neutral:#E8E6E2;--theme-text:#1C1C1C}
[data-theme="tonoko"{--theme-primary:#D7B98E;--theme-light:#F3EEE6;--theme-accent:#65E6B1;--theme-dark:#443015;--theme-neutral:#E7E5E3;--theme-text:#1C1C1C}
[data-theme="kenpohzome"{--theme-primary:#43341B;--theme-light:#F3EEE6;--theme-accent:#20A070;--theme-dark:#251C0D;--theme-neutral:#E7E5E3;--theme-text:#F5F2EB}
[data-theme="kariyasu"{--theme-primary:#E9CD4C;--theme-light:#F3F1E6;--theme-accent:#35FFDB;--theme-dark:#433909;--theme-neutral:#E8E7E2;--theme-text:#1C1C1C}
[data-theme="hiwa"{--theme-primary:#BEC23F;--theme-light:#F3F3E6;--theme-accent:#1EDCE2;--theme-dark:#31320D;--theme-neutral:#E7E7E3;--theme-text:#1C1C1C}
[data-theme="koke"{--theme-primary:#838A2D;--theme-light:#F2F3E6;--theme-accent:#179FAA;--theme-dark:#25270B;--theme-neutral:#E7E7E3;--theme-text:#F5F2EB}
[data-theme="hiwamoegi"{--theme-primary:#90B44B;--theme-light:#EFF3E6;--theme-accent:#2D99D1;--theme-dark:#242E11;--theme-neutral:#E6E7E3;--theme-text:#1C1C1C}
[data-theme="yanagizome"{--theme-primary:#91AD70;--theme-light:#EDF1E8;--theme-accent:#5992C3;--theme-dark:#242E19;--theme-neutral:#E5E6E4;--theme-text:#1C1C1C}
[data-theme="moegi"{--theme-primary:#7BA23F;--theme-light:#EEF3E6;--theme-accent:#2480BC;--theme-dark:#1F290E;--theme-neutral:#E5E7E3;--theme-text:#F5F2EB}
[data-theme="nae"{--theme-primary:#86C166;--theme-light:#EBF3E6;--theme-accent:#4C7EDA;--theme-dark:#1F3613;--theme-neutral:#E4E7E3;--theme-text:#1C1C1C}
[data-theme="matsuba"{--theme-primary:#42602D;--theme-light:#ECF3E6;--theme-accent:#285699;--theme-dark:#17230F;--theme-neutral:#E5E7E3;--theme-text:#F5F2EB}
[data-theme="tokiwa"{--theme-primary:#1B813E;--theme-light:#E6F3EB;--theme-accent:#4406BB;--theme-dark:#072B13;--theme-neutral:#E2E8E4;--theme-text:#F5F2EB}
[data-theme="wakatake"{--theme-primary:#5DAC81;--theme-light:#E7F2EC;--theme-accent:#7E42C6;--theme-dark:#152C20;--theme-neutral:#E4E6E5;--theme-text:#1C1C1C}
[data-theme="midori"{--theme-primary:#227D51;--theme-light:#E6F3ED;--theme-accent:#630FB1;--theme-dark:#09291A;--theme-neutral:#E2E8E5;--theme-text:#F5F2EB}
[data-theme="byakuroku"{--theme-primary:#A8D8B9;--theme-light:#E6F3EB;--theme-accent:#956FDB;--theme-dark:#1B442A;--theme-neutral:#E3E7E4;--theme-text:#1C1C1C}
[data-theme="tokusa"{--theme-primary:#2D6D4B;--theme-light:#E6F3EC;--theme-accent:#5C229F;--theme-dark:#0D2518;--theme-neutral:#E3E7E5;--theme-text:#F5F2EB}
[data-theme="rokusyoh"{--theme-primary:#24936E;--theme-light:#E6F3EF;--theme-accent:#7D0BB5;--theme-dark:#082A1F;--theme-neutral:#E2E8E6;--theme-text:#F5F2EB}
[data-theme="aomidori"{--theme-primary:#00AA90;--theme-light:#E6F3F1;--theme-accent:#A400C1;--theme-dark:#062C26;--theme-neutral:#E2E8E7;--theme-text:#F5F2EB}
[data-theme="seiji"{--theme-primary:#69B0AC;--theme-light:#E7F2F2;--theme-accent:#C150C8;--theme-dark:#172F2D;--theme-neutral:#E4E6E6;--theme-text:#1C1C1C}
[data-theme="mizuasagi"{--theme-primary:#66BAB7;--theme-light:#E6F3F2;--theme-accent:#CE4CD3;--theme-dark:#153231;--theme-neutral:#E3E7E7;--theme-text:#1C1C1C}
[data-theme="byakugun"{--theme-primary:#78C2C4;--theme-light:#E6F3F3;--theme-accent:#DA61D6;--theme-dark:#163738;--theme-neutral:#E3E7E7;--theme-text:#1C1C1C}
[data-theme="kamenozoki"{--theme-primary:#A5DEE4;--theme-light:#E6F2F3;--theme-accent:#EC5EDF;--theme-dark:#14484E;--theme-neutral:#E3E7E7;--theme-text:#1C1C1C}
[data-theme="mizu"{--theme-primary:#81C7D4;--theme-light:#E6F1F3;--theme-accent:#E763D3;--theme-dark:#133A41;--theme-neutral:#E3E7E7;--theme-text:#1C1C1C}
[data-theme="asagi"{--theme-primary:#33A6B8;--theme-light:#E6F1F3;--theme-accent:#D614BC;--theme-dark:#0B2A2F;--theme-neutral:#E2E7E8;--theme-text:#F5F2EB}
[data-theme="shinbashi"{--theme-primary:#0089A7;--theme-light:#E6F1F3;--theme-accent:#C1009E;--theme-dark:#06252C;--theme-neutral:#E2E7E8;--theme-text:#F5F2EB}
[data-theme="hanaasagi"{--theme-primary:#1E88A8;--theme-light:#E6F0F3;--theme-accent:#C40197;--theme-dark:#06232C;--theme-neutral:#E2E6E8;--theme-text:#F5F2EB}
[data-theme="sora"{--theme-primary:#58B2DC;--theme-light:#E6EFF3;--theme-accent:#F83BBC;--theme-dark:#0A3042;--theme-neutral:#E2E6E8;--theme-text:#1C1C1C}
[data-theme="chigusa"{--theme-primary:#3A8FB7;--theme-light:#E6EFF3;--theme-accent:#D51B9A;--theme-dark:#0C242F;--theme-neutral:#E3E6E7;--theme-text:#F5F2EB}
[data-theme="hanada"{--theme-primary:#006284;--theme-light:#E6F0F3;--theme-accent:#C1008F;--theme-dark:#06222C;--theme-neutral:#E2E6E8;--theme-text:#F5F2EB}
[data-theme="wasurenagusa"{--theme-primary:#7DB9DE;--theme-light:#E6EEF3;--theme-accent:#F258B8;--theme-dark:#0E3247;--theme-neutral:#E2E6E8;--theme-text:#1C1C1C}
[data-theme="tsuyukusa"{--theme-primary:#2EA9DF;--theme-light:#E6EFF3;--theme-accent:#FE0EB5;--theme-dark:#082B3A;--theme-neutral:#E2E6E8;--theme-text:#1C1C1C}
[data-theme="gunjyo"{--theme-primary:#51A8DD;--theme-light:#E6EEF3;--theme-accent:#FA33AF;--theme-dark:#092C41;--theme-neutral:#E2E6E8;--theme-text:#1C1C1C}
[data-theme="ruri"{--theme-primary:#005CAF;--theme-light:#E6EDF3;--theme-accent:#C10065;--theme-dark:#061A2C;--theme-neutral:#E2E5E8;--theme-text:#F5F2EB}
[data-theme="rurikon"{--theme-primary:#0B346E;--theme-light:#E6ECF3;--theme-accent:#C10050;--theme-dark:#06162C;--theme-neutral:#E2E5E8;--theme-text:#F5F2EB}
[data-theme="benimidori"{--theme-primary:#7B90D2;--theme-light:#E6E9F3;--theme-accent:#E76383;--theme-dark:#131D40;--theme-neutral:#E3E4E7;--theme-text:#F5F2EB}
[data-theme="fujinezumi"{--theme-primary:#6E75A4;--theme-light:#E9EAF1;--theme-accent:#BB5663;--theme-dark:#191B2A;--theme-neutral:#E4E4E6;--theme-text:#F5F2EB}
[data-theme="benikakehana"{--theme-primary:#4E4F97;--theme-light:#E7E7F2;--theme-accent:#AF3537;--theme-dark:#121226;--theme-neutral:#E4E4E6;--theme-text:#F5F2EB}
[data-theme="konjyo"{--theme-primary:#113285;--theme-light:#E6EAF3;--theme-accent:#C10037;--theme-dark:#06112C;--theme-neutral:#E2E4E8;--theme-text:#F5F2EB}
[data-theme="kon"{--theme-primary:#0F2540;--theme-light:#E6ECF3;--theme-accent:#B70A58;--theme-dark:#08172A;--theme-neutral:#E2E5E8;--theme-text:#F5F2EB}
[data-theme="konkikyo"{--theme-primary:#211E55;--theme-light:#E7E6F3;--theme-accent:#A7221A;--theme-dark:#0D0C26;--theme-neutral:#E3E3E7;--theme-text:#F5F2EB}
[data-theme="kurotsurubami"{--theme-primary:#0B1013;--theme-light:#E8EEF1;--theme-accent:#8E336C;--theme-dark:#121B20;--theme-neutral:#E4E5E6;--theme-text:#F5F2EB}
[data-theme="fuji"{--theme-primary:#8B81C3;--theme-light:#E8E6F3;--theme-accent:#D77C6C;--theme-dark:#1D1838;--theme-neutral:#E4E3E7;--theme-text:#F5F2EB}
[data-theme="fujimurasaki"{--theme-primary:#8A6BBE;--theme-light:#EBE6F3;--theme-accent:#D68352;--theme-dark:#211535;--theme-neutral:#E5E3E7;--theme-text:#F5F2EB}
[data-theme="kikyo"{--theme-primary:#6A4C9C;--theme-light:#EBE6F3;--theme-accent:#B56332;--theme-dark:#1A1228;--theme-neutral:#E5E3E7;--theme-text:#F5F2EB}
[data-theme="shion"{--theme-primary:#8F77B5;--theme-light:#EBE7F2;--theme-accent:#CA8A61;--theme-dark:#221931;--theme-neutral:#E5E4E6;--theme-text:#F5F2EB}
[data-theme="usu"{--theme-primary:#B28FCE;--theme-light:#EDE6F3;--theme-accent:#DDAB6E;--theme-dark:#2D183E;--theme-neutral:#E5E3E7;--theme-text:#1C1C1C}
[data-theme="edomurasaki"{--theme-primary:#77428D;--theme-light:#EFE6F3;--theme-accent:#A4802A;--theme-dark:#1E0F24;--theme-neutral:#E6E3E7;--theme-text:#F5F2EB}
[data-theme="murasaki"{--theme-primary:#592C63;--theme-light:#F1E6F3;--theme-accent:#9C8625;--theme-dark:#200E24;--theme-neutral:#E6E3E7;--theme-text:#F5F2EB}
[data-theme="benifuji"{--theme-primary:#B481BB;--theme-light:#F1E7F2;--theme-accent:#CFC36C;--theme-dark:#311A34;--theme-neutral:#E6E4E6;--theme-text:#F5F2EB}
[data-theme="botan"{--theme-primary:#C1328E;--theme-light:#F3E6EE;--theme-accent:#97E111;--theme-dark:#320A24;--theme-neutral:#E8E2E6;--theme-text:#F5F2EB}
[data-theme="tsutsuji"{--theme-primary:#E03C8A;--theme-light:#F3E6EC;--theme-accent:#88FF1D;--theme-dark:#3E0822;--theme-neutral:#E8E2E5;--theme-text:#F5F2EB}
[data-theme="shironeri"{--theme-primary:#FCFAF2;--theme-light:#F3F0E6;--theme-accent:#55F6D5;--theme-dark:#685713;--theme-neutral:#E8E7E2;--theme-text:#1C1C1C}
[data-theme="shironezumi"{--theme-primary:#BDC0BA;--theme-light:#EDEDEC;--theme-accent:#93A5B8;--theme-dark:#2F312C;--theme-neutral:#E5E5E5;--theme-text:#1C1C1C}
[data-theme="ginnezumi"{--theme-primary:#91989F;--theme-light:#EBEDEE;--theme-accent:#AF8098;--theme-dark:#232628;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
[data-theme="namari"{--theme-primary:#787878;--theme-light:#EDEDED;--theme-accent:#668966;--theme-dark:#1D1D1D;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
[data-theme="hai"{--theme-primary:#828282;--theme-light:#EDEDED;--theme-accent:#6F946F;--theme-dark:#202020;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
[data-theme="nibi"{--theme-primary:#656765;--theme-light:#ECEDEC;--theme-accent:#555576;--theme-dark:#191919;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
[data-theme="aonibi"{--theme-primary:#535953;--theme-light:#ECEDEC;--theme-accent:#4E4E73;--theme-dark:#181A18;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
[data-theme="keshizumi"{--theme-primary:#434343;--theme-light:#EDEDED;--theme-accent:#526F52;--theme-dark:#191919;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
[data-theme="sumi"{--theme-primary:#1C1C1C;--theme-light:#EDEDED;--theme-accent:#526F52;--theme-dark:#191919;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
[data-theme="kuro"{--theme-primary:#080808;--theme-light:#EDEDED;--theme-accent:#526F52;--theme-dark:#191919;--theme-neutral:#E5E5E5;--theme-text:#F5F2EB}
</style>

<script>
const PT=[
  {id:"nadeshiko",l:"撫子"},
  {id:"kohbai",l:"紅梅"},
  {id:"suoh",l:"蘇芳"},
  {id:"taikoh",l:"退紅"},
  {id:"momo",l:"桃"},
  {id:"ichigo",l:"苺"},
  {id:"karakurenai",l:"韓紅花"},
  {id:"kurenai",l:"紅"},
  {id:"toki",l:"鴇"},
  {id:"kokiake",l:"深緋"},
  {id:"jinzamomi",l:"甚三紅"},
  {id:"azuki",l:"小豆"},
  {id:"akabeni",l:"赤紅"},
  {id:"haizakura",l:"灰桜"},
  {id:"akebono",l:"曙"},
  {id:"sangosyu",l:"珊瑚朱"},
  {id:"syojyohi",l:"猩猩緋"},
  {id:"entan",l:"鉛丹"},
  {id:"benihi",l:"紅緋"},
  {id:"terigaki",l:"照柿"},
  {id:"araisyu",l:"洗朱"},
  {id:"ohni",l:"黄丹"},
  {id:"sohi",l:"纁"},
  {id:"ensyucha",l:"遠州茶"},
  {id:"kogecha",l:"焦茶"},
  {id:"akakoh",l:"赤香"},
  {id:"kokikuchinashi",l:"深支子"},
  {id:"taisya",l:"代赭"},
  {id:"kanzo",l:"萱草"},
  {id:"beniukon",l:"紅鬱金"},
  {id:"kohaku",l:"琥珀"},
  {id:"kuchiba",l:"朽葉"},
  {id:"yamabuki",l:"山吹"},
  {id:"hajizome",l:"櫨染"},
  {id:"tamago",l:"玉子"},
  {id:"tamamorokoshi",l:"玉蜀黍"},
  {id:"usuki",l:"浅黄"},
  {id:"kuchinashi",l:"梔子"},
  {id:"tohoh",l:"籐黄"},
  {id:"ukon",l:"鬱金"},
  {id:"tonoko",l:"砥粉"},
  {id:"kenpohzome",l:"憲法染"},
  {id:"kariyasu",l:"刈安"},
  {id:"hiwa",l:"鶸"},
  {id:"koke",l:"苔"},
  {id:"hiwamoegi",l:"鶸萌黄"},
  {id:"yanagizome",l:"柳染"},
  {id:"moegi",l:"萌黄"},
  {id:"nae",l:"苗"},
  {id:"matsuba",l:"松葉"},
  {id:"tokiwa",l:"常磐"},
  {id:"wakatake",l:"若竹"},
  {id:"midori",l:"緑"},
  {id:"byakuroku",l:"白緑"},
  {id:"tokusa",l:"木賊"},
  {id:"rokusyoh",l:"緑青"},
  {id:"aomidori",l:"青緑"},
  {id:"seiji",l:"青磁"},
  {id:"mizuasagi",l:"水浅葱"},
  {id:"byakugun",l:"白群"},
  {id:"kamenozoki",l:"瓶覗"},
  {id:"mizu",l:"水"},
  {id:"asagi",l:"浅葱"},
  {id:"shinbashi",l:"新橋"},
  {id:"hanaasagi",l:"花浅葱"},
  {id:"sora",l:"空"},
  {id:"chigusa",l:"千草"},
  {id:"hanada",l:"縹"},
  {id:"wasurenagusa",l:"勿忘草"},
  {id:"tsuyukusa",l:"露草"},
  {id:"gunjyo",l:"群青"},
  {id:"ruri",l:"瑠璃"},
  {id:"rurikon",l:"瑠璃紺"},
  {id:"benimidori",l:"紅碧"},
  {id:"fujinezumi",l:"藤鼠"},
  {id:"benikakehana",l:"紅掛花"},
  {id:"konjyo",l:"紺青"},
  {id:"kon",l:"紺"},
  {id:"konkikyo",l:"紺桔梗"},
  {id:"kurotsurubami",l:"黒橡"},
  {id:"fuji",l:"藤"},
  {id:"fujimurasaki",l:"藤紫"},
  {id:"kikyo",l:"桔梗"},
  {id:"shion",l:"紫苑"},
  {id:"usu",l:"薄"},
  {id:"edomurasaki",l:"江戸紫"},
  {id:"murasaki",l:"紫"},
  {id:"benifuji",l:"紅藤"},
  {id:"botan",l:"牡丹"},
  {id:"tsutsuji",l:"躑躅"},
  {id:"shironeri",l:"白練"},
  {id:"shironezumi",l:"白鼠"},
  {id:"ginnezumi",l:"銀鼠"},
  {id:"namari",l:"鉛"},
  {id:"hai",l:"灰"},
  {id:"nibi",l:"鈍"},
  {id:"aonibi",l:"青鈍"},
  {id:"keshizumi",l:"消炭"},
  {id:"sumi",l:"墨"},
  {id:"kuro",l:"黒"}
];
let pi=0;
function phyraNext(){pi=(pi+1)%PT.length;const el=document.documentElement;el.setAttribute('data-theme',PT[pi].id);const lb=document.getElementById('phyra-label');if(lb)lb.textContent=PT[pi].l+' '+PT[pi].id.toUpperCase()}
function phyraRandom(){pi=Math.floor(Math.random()*PT.length);phyraNext();pi--;}
</script>
```

---

*Phyra AI Design System · 2026-04*