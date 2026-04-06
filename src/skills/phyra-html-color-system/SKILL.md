---
name: phyra-html-color-system
description: "Color system for all Phyra HTML reports. Provides 100 Japanese color themes (from nipponcolors.com) with light/dark classification, 3-layer background, theme switcher, and per-report-type color rules."
---

# Phyra HTML Color System

所有 Phyra HTML 報告的配色系統。基於 nipponcolors.com 的 100 種日本傳統色，分為淺色系（42 種）和深色系（58 種），自動適配文字、卡片、公式等元素的配色。

## Light/Dark 分類規則

分類依據：`--theme-text` 值。
- `#1C1C1C`（深色文字） → **淺色系主題**（背景較亮，使用深色文字）
- `#F5F2EB`（淺色文字） → **深色系主題**（背景較暗，使用淺色文字）

此分類通過 `data-theme-mode` 屬性（`light` 或 `dark`）設置在 `<html>` 元素上，由主題切換器自動管理。

## CSS 變數合約

### 基礎變數（每個主題定義）

| 變數 | 用途 |
|------|------|
| `--theme-primary` | 主題色（底色） |
| `--theme-light` | 淡色（卡片背景候選） |
| `--theme-accent` | 強調色（CTA、圖表主線） |
| `--theme-dark` | 深色（深底、導航） |
| `--theme-neutral` | 柔和底（surface、分隔線） |
| `--theme-text` | 建議文字色 |

### 語義別名（從主題變數映射）

```css
:root {
  --p-primary : var(--theme-primary);
  --p-light   : var(--theme-light);
  --p-accent  : var(--theme-accent);
  --p-dark    : var(--theme-dark);
  --p-neutral : var(--theme-neutral);
  --p-text    : var(--theme-text);
}
```

### 衍生變數（依 light/dark mode 自動設定）

```css
/* 淺色系模式 */
[data-theme-mode="light"] {
  --p-bg-card        : rgba(255, 255, 255, 0.92);
  --p-formula-bg     : rgba(255, 255, 255, 0.92);
  --p-border         : rgba(28, 28, 28, 0.12);
  --p-text-secondary : rgba(28, 28, 28, 0.60);
  --p-bold-highlight : color-mix(in srgb, var(--p-accent) 15%, transparent);
  --p-gloss-top      : 0.22;
  --p-gloss-mid      : 0.06;
}

/* 深色系模式 */
[data-theme-mode="dark"] {
  --p-bg-card        : rgba(0, 0, 0, 0.35);
  --p-formula-bg     : rgba(0, 0, 0, 0.35);
  --p-border         : rgba(245, 242, 235, 0.12);
  --p-text-secondary : rgba(245, 242, 235, 0.60);
  --p-bold-highlight : color-mix(in srgb, var(--p-accent) 20%, transparent);
  --p-gloss-top      : 0.10;
  --p-gloss-mid      : 0.03;
}
```

## 淺色系主題（42 種）

| # | 漢字 | id | Primary |
|---|------|----|---------|
| 001 | 撫子 | nadeshiko | #DC9FB4 |
| 004 | 退紅 | taikoh | #F8C3CD |
| 005 | 桃 | momo | #F596AA |
| 009 | 鴇 | toki | #EEA9A9 |
| 011 | 甚三紅 | jinzamomi | #EB7A77 |
| 014 | 灰桜 | haizakura | #D7C4BB |
| 015 | 曙 | akebono | #F19483 |
| 016 | 珊瑚朱 | sangosyu | #F17C67 |
| 021 | 洗朱 | araisyu | #FB966E |
| 026 | 赤香 | akakoh | #E3916E |
| 027 | 深支子 | kokikuchinashi | #FB9966 |
| 029 | 萱草 | kanzo | #FC9F4D |
| 030 | 紅鬱金 | beniukon | #E98B2A |
| 032 | 朽葉 | kuchiba | #E2943B |
| 033 | 山吹 | yamabuki | #FFB11B |
| 034 | 櫨染 | hajizome | #DDA52D |
| 035 | 玉子 | tamago | #F9BF45 |
| 036 | 玉蜀黍 | tamamorokoshi | #E8B647 |
| 037 | 浅黄 | usuki | #FAD689 |
| 038 | 梔子 | kuchinashi | #F6C555 |
| 039 | 籐黄 | tohoh | #FFC408 |
| 040 | 鬱金 | ukon | #EFBB24 |
| 041 | 砥粉 | tonoko | #D7B98E |
| 043 | 刈安 | kariyasu | #E9CD4C |
| 044 | 鶸 | hiwa | #BEC23F |
| 046 | 鶸萌黄 | hiwamoegi | #90B44B |
| 047 | 柳染 | yanagizome | #91AD70 |
| 049 | 苗 | nae | #86C166 |
| 052 | 若竹 | wakatake | #5DAC81 |
| 054 | 白緑 | byakuroku | #A8D8B9 |
| 058 | 青磁 | seiji | #69B0AC |
| 059 | 水浅葱 | mizuasagi | #66BAB7 |
| 060 | 白群 | byakugun | #78C2C4 |
| 061 | 瓶覗 | kamenozoki | #A5DEE4 |
| 062 | 水 | mizu | #81C7D4 |
| 066 | 空 | sora | #58B2DC |
| 069 | 勿忘草 | wasurenagusa | #7DB9DE |
| 070 | 露草 | tsuyukusa | #2EA9DF |
| 071 | 群青 | gunjyo | #51A8DD |
| 085 | 薄 | usu | #B28FCE |
| 091 | 白練 | shironeri | #FCFAF2 |
| 092 | 白鼠 | shironezumi | #BDC0BA |

## 深色系主題（58 種）

| # | 漢字 | id | Primary |
|---|------|----|---------|
| 002 | 紅梅 | kohbai | #E16B8C |
| 003 | 蘇芳 | suoh | #8E354A |
| 006 | 苺 | ichigo | #B5495B |
| 007 | 韓紅花 | karakurenai | #D0104C |
| 008 | 紅 | kurenai | #CB1B45 |
| 010 | 深緋 | kokiake | #86473F |
| 012 | 小豆 | azuki | #954A45 |
| 013 | 赤紅 | akabeni | #CB4042 |
| 017 | 猩猩緋 | syojyohi | #E83015 |
| 018 | 鉛丹 | entan | #D75455 |
| 019 | 紅緋 | benihi | #F75C2F |
| 020 | 照柿 | terigaki | #C46243 |
| 022 | 黄丹 | ohni | #F05E1C |
| 023 | 纁 | sohi | #ED784A |
| 024 | 遠州茶 | ensyucha | #CA7853 |
| 025 | 焦茶 | kogecha | #563F2E |
| 028 | 代赭 | taisya | #A36336 |
| 031 | 琥珀 | kohaku | #CA7A2C |
| 042 | 憲法染 | kenpohzome | #43341B |
| 045 | 苔 | koke | #838A2D |
| 048 | 萌黄 | moegi | #7BA23F |
| 050 | 松葉 | matsuba | #42602D |
| 051 | 常磐 | tokiwa | #1B813E |
| 053 | 緑 | midori | #227D51 |
| 055 | 木賊 | tokusa | #2D6D4B |
| 056 | 緑青 | rokusyoh | #24936E |
| 057 | 青緑 | aomidori | #00AA90 |
| 063 | 浅葱 | asagi | #33A6B8 |
| 064 | 新橋 | shinbashi | #0089A7 |
| 065 | 花浅葱 | hanaasagi | #1E88A8 |
| 067 | 千草 | chigusa | #3A8FB7 |
| 068 | 縹 | hanada | #006284 |
| 072 | 瑠璃 | ruri | #005CAF |
| 073 | 瑠璃紺 | rurikon | #0B346E |
| 074 | 紅碧 | benimidori | #7B90D2 |
| 075 | 藤鼠 | fujinezumi | #6E75A4 |
| 076 | 紅掛花 | benikakehana | #4E4F97 |
| 077 | 紺青 | konjyo | #113285 |
| 078 | 紺 | kon | #0F2540 |
| 079 | 紺桔梗 | konkikyo | #211E55 |
| 080 | 黒橡 | kurotsurubami | #0B1013 |
| 081 | 藤 | fuji | #8B81C3 |
| 082 | 藤紫 | fujimurasaki | #8A6BBE |
| 083 | 桔梗 | kikyo | #6A4C9C |
| 084 | 紫苑 | shion | #8F77B5 |
| 086 | 江戸紫 | edomurasaki | #77428D |
| 087 | 紫 | murasaki | #592C63 |
| 088 | 紅藤 | benifuji | #B481BB |
| 089 | 牡丹 | botan | #C1328E |
| 090 | 躑躅 | tsutsuji | #E03C8A |
| 093 | 銀鼠 | ginnezumi | #91989F |
| 094 | 鉛 | namari | #787878 |
| 095 | 灰 | hai | #828282 |
| 096 | 鈍 | nibi | #656765 |
| 097 | 青鈍 | aonibi | #535953 |
| 098 | 消炭 | keshizumi | #434343 |
| 099 | 墨 | sumi | #1C1C1C |
| 100 | 黒 | kuro | #080808 |

## Agent 引用指引

生成 HTML 報告前，依報告類型讀取以下 reference 文件：

### 所有 HTML 報告都必須讀取

1. `references/bg-layers.md` — 三層背景系統和 HTML 結構範本
2. `references/switcher.js.md` — 主題選單切換器 JS
3. 對應的色板文件：`references/palette-light.md` 和 `references/palette-dark.md`

### 依報告類型額外讀取

| 報告類型 | 額外讀取 |
|---------|---------|
| Paper Read (slides) | `references/slide-theme.md` |
| Paper Survey (scroll + graph) | `references/scroll-theme.md` + `references/graph-theme.md` |
| Paper Graph (scroll + graph) | `references/scroll-theme.md` + `references/graph-theme.md` |
| Peer Review (scroll) | `references/scroll-theme.md` |
| Paper Write (scroll) | `references/scroll-theme.md` |

## 統一頁腳

所有 HTML 報告底部必須包含統一格式頁腳：

```html
<footer class="phyra-footer">
  Phyra NT Workflow | Paper Read Report | 2026-04-05
</footer>
```

格式：`Phyra {NT|AT} Workflow | {Report Type} | {YYYY-MM-DD}`

Report Type 可用值：Paper Read Report, Peer Review Report, Paper Survey Report, Paper Graph Report, Paper Write Report

預設主題：keshizumi（消炭）。其他推薦：hanada（縹）、kurenai（紅）、yamabuki（山吹）、fujimurasaki（藤紫）
