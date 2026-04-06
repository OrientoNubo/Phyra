# 主題切換器（選單版）

替換舊版 Next/Random 按鈕，改為 `<select>` 下拉選單 + Random 按鈕。選單按 light/dark 分組。

## JavaScript

```javascript
/* phyra-switcher.js — 選單式主題切換器 */

const PHYRA_THEMES = [
  // 淺色系 (42)
  { id: "nadeshiko", label: "撫子 Nadeshiko", mode: "light" },
  { id: "taikoh", label: "退紅 Taikoh", mode: "light" },
  { id: "momo", label: "桃 Momo", mode: "light" },
  { id: "toki", label: "鴇 Toki", mode: "light" },
  { id: "jinzamomi", label: "甚三紅 Jinzamomi", mode: "light" },
  { id: "haizakura", label: "灰桜 Haizakura", mode: "light" },
  { id: "akebono", label: "曙 Akebono", mode: "light" },
  { id: "sangosyu", label: "珊瑚朱 Sangosyu", mode: "light" },
  { id: "araisyu", label: "洗朱 Araisyu", mode: "light" },
  { id: "akakoh", label: "赤香 Akakoh", mode: "light" },
  { id: "kokikuchinashi", label: "深支子 Kokikuchinashi", mode: "light" },
  { id: "kanzo", label: "萱草 Kanzo", mode: "light" },
  { id: "beniukon", label: "紅鬱金 Beniukon", mode: "light" },
  { id: "kuchiba", label: "朽葉 Kuchiba", mode: "light" },
  { id: "yamabuki", label: "山吹 Yamabuki", mode: "light" },
  { id: "hajizome", label: "櫨染 Hajizome", mode: "light" },
  { id: "tamago", label: "玉子 Tamago", mode: "light" },
  { id: "tamamorokoshi", label: "玉蜀黍 Tamamorokoshi", mode: "light" },
  { id: "usuki", label: "浅黄 Usuki", mode: "light" },
  { id: "kuchinashi", label: "梔子 Kuchinashi", mode: "light" },
  { id: "tohoh", label: "籐黄 Tohoh", mode: "light" },
  { id: "ukon", label: "鬱金 Ukon", mode: "light" },
  { id: "tonoko", label: "砥粉 Tonoko", mode: "light" },
  { id: "kariyasu", label: "刈安 Kariyasu", mode: "light" },
  { id: "hiwa", label: "鶸 Hiwa", mode: "light" },
  { id: "hiwamoegi", label: "鶸萌黄 Hiwamoegi", mode: "light" },
  { id: "yanagizome", label: "柳染 Yanagizome", mode: "light" },
  { id: "nae", label: "苗 Nae", mode: "light" },
  { id: "wakatake", label: "若竹 Wakatake", mode: "light" },
  { id: "byakuroku", label: "白緑 Byakuroku", mode: "light" },
  { id: "seiji", label: "青磁 Seiji", mode: "light" },
  { id: "mizuasagi", label: "水浅葱 Mizuasagi", mode: "light" },
  { id: "byakugun", label: "白群 Byakugun", mode: "light" },
  { id: "kamenozoki", label: "瓶覗 Kamenozoki", mode: "light" },
  { id: "mizu", label: "水 Mizu", mode: "light" },
  { id: "sora", label: "空 Sora", mode: "light" },
  { id: "wasurenagusa", label: "勿忘草 Wasurenagusa", mode: "light" },
  { id: "tsuyukusa", label: "露草 Tsuyukusa", mode: "light" },
  { id: "gunjyo", label: "群青 Gunjyo", mode: "light" },
  { id: "usu", label: "薄 Usu", mode: "light" },
  { id: "shironeri", label: "白練 Shironeri", mode: "light" },
  { id: "shironezumi", label: "白鼠 Shironezumi", mode: "light" },
  // 深色系 (58)
  { id: "kohbai", label: "紅梅 Kohbai", mode: "dark" },
  { id: "suoh", label: "蘇芳 Suoh", mode: "dark" },
  { id: "ichigo", label: "苺 Ichigo", mode: "dark" },
  { id: "karakurenai", label: "韓紅花 Karakurenai", mode: "dark" },
  { id: "kurenai", label: "紅 Kurenai", mode: "dark" },
  { id: "kokiake", label: "深緋 Kokiake", mode: "dark" },
  { id: "azuki", label: "小豆 Azuki", mode: "dark" },
  { id: "akabeni", label: "赤紅 Akabeni", mode: "dark" },
  { id: "syojyohi", label: "猩猩緋 Syojyohi", mode: "dark" },
  { id: "entan", label: "鉛丹 Entan", mode: "dark" },
  { id: "benihi", label: "紅緋 Benihi", mode: "dark" },
  { id: "terigaki", label: "照柿 Terigaki", mode: "dark" },
  { id: "ohni", label: "黄丹 Ohni", mode: "dark" },
  { id: "sohi", label: "纁 Sohi", mode: "dark" },
  { id: "ensyucha", label: "遠州茶 Ensyucha", mode: "dark" },
  { id: "kogecha", label: "焦茶 Kogecha", mode: "dark" },
  { id: "taisya", label: "代赭 Taisya", mode: "dark" },
  { id: "kohaku", label: "琥珀 Kohaku", mode: "dark" },
  { id: "kenpohzome", label: "憲法染 Kenpohzome", mode: "dark" },
  { id: "koke", label: "苔 Koke", mode: "dark" },
  { id: "moegi", label: "萌黄 Moegi", mode: "dark" },
  { id: "matsuba", label: "松葉 Matsuba", mode: "dark" },
  { id: "tokiwa", label: "常磐 Tokiwa", mode: "dark" },
  { id: "midori", label: "緑 Midori", mode: "dark" },
  { id: "tokusa", label: "木賊 Tokusa", mode: "dark" },
  { id: "rokusyoh", label: "緑青 Rokusyoh", mode: "dark" },
  { id: "aomidori", label: "青緑 Aomidori", mode: "dark" },
  { id: "asagi", label: "浅葱 Asagi", mode: "dark" },
  { id: "shinbashi", label: "新橋 Shinbashi", mode: "dark" },
  { id: "hanaasagi", label: "花浅葱 Hanaasagi", mode: "dark" },
  { id: "chigusa", label: "千草 Chigusa", mode: "dark" },
  { id: "hanada", label: "縹 Hanada", mode: "dark" },
  { id: "ruri", label: "瑠璃 Ruri", mode: "dark" },
  { id: "rurikon", label: "瑠璃紺 Rurikon", mode: "dark" },
  { id: "benimidori", label: "紅碧 Benimidori", mode: "dark" },
  { id: "fujinezumi", label: "藤鼠 Fujinezumi", mode: "dark" },
  { id: "benikakehana", label: "紅掛花 Benikakehana", mode: "dark" },
  { id: "konjyo", label: "紺青 Konjyo", mode: "dark" },
  { id: "kon", label: "紺 Kon", mode: "dark" },
  { id: "konkikyo", label: "紺桔梗 Konkikyo", mode: "dark" },
  { id: "kurotsurubami", label: "黒橡 Kurotsurubami", mode: "dark" },
  { id: "fuji", label: "藤 Fuji", mode: "dark" },
  { id: "fujimurasaki", label: "藤紫 Fujimurasaki", mode: "dark" },
  { id: "kikyo", label: "桔梗 Kikyo", mode: "dark" },
  { id: "shion", label: "紫苑 Shion", mode: "dark" },
  { id: "edomurasaki", label: "江戸紫 Edomurasaki", mode: "dark" },
  { id: "murasaki", label: "紫 Murasaki", mode: "dark" },
  { id: "benifuji", label: "紅藤 Benifuji", mode: "dark" },
  { id: "botan", label: "牡丹 Botan", mode: "dark" },
  { id: "tsutsuji", label: "躑躅 Tsutsuji", mode: "dark" },
  { id: "ginnezumi", label: "銀鼠 Ginnezumi", mode: "dark" },
  { id: "namari", label: "鉛 Namari", mode: "dark" },
  { id: "hai", label: "灰 Hai", mode: "dark" },
  { id: "nibi", label: "鈍 Nibi", mode: "dark" },
  { id: "aonibi", label: "青鈍 Aonibi", mode: "dark" },
  { id: "keshizumi", label: "消炭 Keshizumi", mode: "dark" },
  { id: "sumi", label: "墨 Sumi", mode: "dark" },
  { id: "kuro", label: "黒 Kuro", mode: "dark" }
];

function phyraApply(id) {
  const html = document.documentElement;
  html.setAttribute('data-theme', id);
  const t = PHYRA_THEMES.find(x => x.id === id);
  if (t) {
    html.setAttribute('data-theme-mode', t.mode);
    const select = document.getElementById('phyra-select');
    if (select) select.value = id;
  }
}

function phyraRandom() {
  const idx = Math.floor(Math.random() * PHYRA_THEMES.length);
  phyraApply(PHYRA_THEMES[idx].id);
}

// Build <select> options on init
function phyraBuildSelect() {
  const select = document.getElementById('phyra-select');
  if (!select) return;
  const lightGroup = document.createElement('optgroup');
  lightGroup.label = '淺色系 (42)';
  const darkGroup = document.createElement('optgroup');
  darkGroup.label = '深色系 (58)';
  PHYRA_THEMES.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.id;
    opt.textContent = t.label;
    if (t.mode === 'light') lightGroup.appendChild(opt);
    else darkGroup.appendChild(opt);
  });
  select.appendChild(lightGroup);
  select.appendChild(darkGroup);
}

// Initialize
(function() {
  phyraBuildSelect();
  const current = document.documentElement.getAttribute('data-theme') || 'keshizumi';
  phyraApply(current);
})();
```

## HTML 結構

主題切換器的 HTML 放在 `<body>` 末尾：

```html
<div class="phyra-switcher">
  <select id="phyra-select" onchange="phyraApply(this.value)"></select>
  <button onclick="phyraRandom()">Random</button>
</div>
```

`<select>` 的 `<optgroup>` 由 `phyraBuildSelect()` 在初始化時動態生成。
