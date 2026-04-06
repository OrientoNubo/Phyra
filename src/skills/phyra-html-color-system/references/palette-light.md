# 淺色系色板（42 種）

淺色系主題的 CSS 定義。這些主題使用深色文字（`#1C1C1C`）搭配較亮的背景色。

將以下 CSS 貼入 `<style>` 中（與深色系合併使用）。

## 衍生變數（淺色系）

```css
[data-theme-mode="light"] {
  --p-bg-card        : rgba(255, 255, 255, 0.92);
  --p-formula-bg     : rgba(255, 255, 255, 0.92);
  --p-border         : rgba(28, 28, 28, 0.12);
  --p-text-secondary : rgba(28, 28, 28, 0.60);
  --p-bold-highlight : color-mix(in srgb, var(--p-accent) 15%, transparent);
  --p-gloss-top      : 0.22;
  --p-gloss-mid      : 0.06;
}
```

## 主題定義

```css
/* === 淺色系 Light Themes (42) === */
/* 分類依據：--theme-text: #1C1C1C（深色文字 = 淺色背景） */

/* 🌸 紅・桃 */
[data-theme="nadeshiko"] {
  --theme-primary : #DC9FB4;   /* 撫子 */
  --theme-light   : #F3E6EB;
  --theme-accent  : #92E566;
  --theme-dark    : #471727;
  --theme-neutral : #E7E3E4;
  --theme-text    : #1C1C1C;
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

[data-theme="toki"] {
  --theme-primary : #EEA9A9;   /* 鴇 */
  --theme-light   : #F3E6E6;
  --theme-accent  : #50FA50;
  --theme-dark    : #580D0D;
  --theme-neutral : #E8E2E2;
  --theme-text    : #1C1C1C;
}

[data-theme="jinzamomi"] {
  --theme-primary : #EB7A77;   /* 甚三紅 */
  --theme-light   : #F3E7E6;
  --theme-accent  : #4CFE51;
  --theme-dark    : #4D0C0B;
  --theme-neutral : #E8E3E2;
  --theme-text    : #1C1C1C;
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

[data-theme="araisyu"] {
  --theme-primary : #FB966E;   /* 洗朱 */
  --theme-light   : #F3EAE6;
  --theme-accent  : #4CFE7F;
  --theme-dark    : #4E1E0B;
  --theme-neutral : #E8E4E2;
  --theme-text    : #1C1C1C;
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
  --theme-primary : #FFC408;   /* 藤黄 */
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

[data-theme="nae"] {
  --theme-primary : #86C166;   /* 苗 */
  --theme-light   : #EBF3E6;
  --theme-accent  : #4C7EDA;
  --theme-dark    : #1F3613;
  --theme-neutral : #E4E7E3;
  --theme-text    : #1C1C1C;
}

[data-theme="wakatake"] {
  --theme-primary : #5DAC81;   /* 若竹 */
  --theme-light   : #E7F2EC;
  --theme-accent  : #7E42C6;
  --theme-dark    : #152C20;
  --theme-neutral : #E4E6E5;
  --theme-text    : #1C1C1C;
}

[data-theme="byakuroku"] {
  --theme-primary : #A8D8B9;   /* 白緑 */
  --theme-light   : #E6F3EB;
  --theme-accent  : #956FDB;
  --theme-dark    : #1B442A;
  --theme-neutral : #E3E7E4;
  --theme-text    : #1C1C1C;
}

/* 🌊 藍 */
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

[data-theme="sora"] {
  --theme-primary : #58B2DC;   /* 空 */
  --theme-light   : #E6EFF3;
  --theme-accent  : #F83BBC;
  --theme-dark    : #0A3042;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
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

/* 💜 紫 */
[data-theme="usu"] {
  --theme-primary : #B28FCE;   /* 薄 */
  --theme-light   : #EDE6F3;
  --theme-accent  : #DDAB6E;
  --theme-dark    : #2D183E;
  --theme-neutral : #E5E3E7;
  --theme-text    : #1C1C1C;
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
```
