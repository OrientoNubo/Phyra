# 深色系色板（58 種）

深色系主題的 CSS 定義。這些主題使用淺色文字（`#F5F2EB`）搭配較暗的背景色。

將以下 CSS 貼入 `<style>` 中（與淺色系合併使用）。

## 衍生變數（深色系）

```css
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

## 主題定義

```css
/* === 深色系 Dark Themes (58) === */
/* 分類依據：--theme-text: #F5F2EB（淺色文字 = 深色背景） */

/* 🌸 紅・桃 */
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

[data-theme="kokiake"] {
  --theme-primary : #86473F;   /* 深緋 */
  --theme-light   : #F3E8E6;
  --theme-accent  : #299B36;
  --theme-dark    : #23110F;
  --theme-neutral : #E7E4E3;
  --theme-text    : #F5F2EB;
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

/* 🍂 朱・橙 */
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

[data-theme="taisya"] {
  --theme-primary : #A36336;   /* 代赭 */
  --theme-light   : #F3ECE6;
  --theme-accent  : #1ABE5E;
  --theme-dark    : #2A180C;
  --theme-neutral : #E7E5E3;
  --theme-text    : #F5F2EB;
}

/* 🌾 黄・茶 */
[data-theme="kohaku"] {
  --theme-primary : #CA7A2C;   /* 琥珀 */
  --theme-light   : #F3EDE6;
  --theme-accent  : #09EC79;
  --theme-dark    : #341E09;
  --theme-neutral : #E8E5E2;
  --theme-text    : #F5F2EB;
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
[data-theme="koke"] {
  --theme-primary : #838A2D;   /* 苔 */
  --theme-light   : #F2F3E6;
  --theme-accent  : #179FAA;
  --theme-dark    : #25270B;
  --theme-neutral : #E7E7E3;
  --theme-text    : #F5F2EB;
}

[data-theme="moegi"] {
  --theme-primary : #7BA23F;   /* 萌黄 */
  --theme-light   : #EEF3E6;
  --theme-accent  : #2480BC;
  --theme-dark    : #1F290E;
  --theme-neutral : #E5E7E3;
  --theme-text    : #F5F2EB;
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

[data-theme="midori"] {
  --theme-primary : #227D51;   /* 緑 */
  --theme-light   : #E6F3ED;
  --theme-accent  : #630FB1;
  --theme-dark    : #09291A;
  --theme-neutral : #E2E8E5;
  --theme-text    : #F5F2EB;
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

/* 💙 青・紺 */
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
