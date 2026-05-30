# Light Theme Palette (42)

CSS definitions for light themes. These themes use dark text (`#1C1C1C`) with brighter background colors.

Paste the following CSS into `<style>` (combine with dark theme palette).

## Derived Variables (Light)

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

## Theme Definitions

```css
/* === Light Themes (42) === */
/* Classification: --theme-text: #1C1C1C (dark text = light background) */

/* Red / Pink */
[data-theme="nadeshiko"] {
  --theme-primary : #DC9FB4;   /* nadeshiko */
  --theme-light   : #F3E6EB;
  --theme-accent  : #92E566;
  --theme-dark    : #471727;
  --theme-neutral : #E7E3E4;
  --theme-text    : #1C1C1C;
}

[data-theme="taikoh"] {
  --theme-primary : #F8C3CD;   /* taikoh */
  --theme-light   : #F3E6E9;
  --theme-accent  : #6EFE4C;
  --theme-dark    : #600D1D;
  --theme-neutral : #E8E2E3;
  --theme-text    : #1C1C1C;
}

[data-theme="momo"] {
  --theme-primary : #F596AA;   /* momo */
  --theme-light   : #F3E6E9;
  --theme-accent  : #72FE4C;
  --theme-dark    : #560C1B;
  --theme-neutral : #E8E2E4;
  --theme-text    : #1C1C1C;
}

[data-theme="toki"] {
  --theme-primary : #EEA9A9;   /* toki */
  --theme-light   : #F3E6E6;
  --theme-accent  : #50FA50;
  --theme-dark    : #580D0D;
  --theme-neutral : #E8E2E2;
  --theme-text    : #1C1C1C;
}

[data-theme="jinzamomi"] {
  --theme-primary : #EB7A77;   /* jinzamomi */
  --theme-light   : #F3E7E6;
  --theme-accent  : #4CFE51;
  --theme-dark    : #4D0C0B;
  --theme-neutral : #E8E3E2;
  --theme-text    : #1C1C1C;
}

[data-theme="haizakura"] {
  --theme-primary : #D7C4BB;   /* haizakura */
  --theme-light   : #F1EBE8;
  --theme-accent  : #7CCE97;
  --theme-dark    : #402D23;
  --theme-neutral : #E6E5E4;
  --theme-text    : #1C1C1C;
}

/* Vermilion / Orange */
[data-theme="akebono"] {
  --theme-primary : #F19483;   /* akebono */
  --theme-light   : #F3E8E6;
  --theme-accent  : #4CFE68;
  --theme-dark    : #51160B;
  --theme-neutral : #E8E3E2;
  --theme-text    : #1C1C1C;
}

[data-theme="sangosyu"] {
  --theme-primary : #F17C67;   /* sangosyu */
  --theme-light   : #F3E8E6;
  --theme-accent  : #4CFE67;
  --theme-dark    : #4B140A;
  --theme-neutral : #E8E3E2;
  --theme-text    : #1C1C1C;
}

[data-theme="araisyu"] {
  --theme-primary : #FB966E;   /* araisyu */
  --theme-light   : #F3EAE6;
  --theme-accent  : #4CFE7F;
  --theme-dark    : #4E1E0B;
  --theme-neutral : #E8E4E2;
  --theme-text    : #1C1C1C;
}

[data-theme="akakoh"] {
  --theme-primary : #E3916E;   /* akakoh */
  --theme-light   : #F3EAE6;
  --theme-accent  : #4FFB83;
  --theme-dark    : #491D0A;
  --theme-neutral : #E8E4E2;
  --theme-text    : #1C1C1C;
}

[data-theme="kokikuchinashi"] {
  --theme-primary : #FB9966;   /* kokikuchinashi */
  --theme-light   : #F3EBE6;
  --theme-accent  : #4CFE89;
  --theme-dark    : #4D210B;
  --theme-neutral : #E8E4E2;
  --theme-text    : #1C1C1C;
}

/* Yellow / Brown */
[data-theme="kanzo"] {
  --theme-primary : #FC9F4D;   /* kanzo */
  --theme-light   : #F3ECE6;
  --theme-accent  : #4AFE9E;
  --theme-dark    : #47270A;
  --theme-neutral : #E8E5E2;
  --theme-text    : #1C1C1C;
}

[data-theme="beniukon"] {
  --theme-primary : #E98B2A;   /* beniukon */
  --theme-light   : #F3EDE6;
  --theme-accent  : #14FE8B;
  --theme-dark    : #3C2208;
  --theme-neutral : #E8E5E2;
  --theme-text    : #1C1C1C;
}

[data-theme="kuchiba"] {
  --theme-primary : #E2943B;   /* kuchiba */
  --theme-light   : #F3EDE6;
  --theme-accent  : #1EFF95;
  --theme-dark    : #3E2508;
  --theme-neutral : #E8E5E2;
  --theme-text    : #1C1C1C;
}

[data-theme="yamabuki"] {
  --theme-primary : #FFB11B;   /* yamabuki */
  --theme-light   : #F3EFE6;
  --theme-accent  : #1BFFB0;
  --theme-dark    : #3D2B08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="hajizome"] {
  --theme-primary : #DDA52D;   /* hajizome */
  --theme-light   : #F3EFE6;
  --theme-accent  : #0BFEB1;
  --theme-dark    : #3A2A08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tamago"] {
  --theme-primary : #F9BF45;   /* tamago */
  --theme-light   : #F3EFE6;
  --theme-accent  : #3FFFC1;
  --theme-dark    : #453209;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tamamorokoshi"] {
  --theme-primary : #E8B647;   /* tamamorokoshi */
  --theme-light   : #F3EFE6;
  --theme-accent  : #30FFBE;
  --theme-dark    : #423009;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="usuki"] {
  --theme-primary : #FAD689;   /* usuki */
  --theme-light   : #F3EFE6;
  --theme-accent  : #4CFEC6;
  --theme-dark    : #543D0C;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="kuchinashi"] {
  --theme-primary : #F6C555;   /* kuchinashi */
  --theme-light   : #F3EFE6;
  --theme-accent  : #4CFEC8;
  --theme-dark    : #48350A;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tohoh"] {
  --theme-primary : #FFC408;   /* tohoh */
  --theme-light   : #F3F0E6;
  --theme-accent  : #07FFC4;
  --theme-dark    : #392D08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="ukon"] {
  --theme-primary : #EFBB24;   /* ukon */
  --theme-light   : #F3F0E6;
  --theme-accent  : #14FEC2;
  --theme-dark    : #3C2E08;
  --theme-neutral : #E8E6E2;
  --theme-text    : #1C1C1C;
}

[data-theme="tonoko"] {
  --theme-primary : #D7B98E;   /* tonoko */
  --theme-light   : #F3EEE6;
  --theme-accent  : #65E6B1;
  --theme-dark    : #443015;
  --theme-neutral : #E7E5E3;
  --theme-text    : #1C1C1C;
}

/* Green */
[data-theme="kariyasu"] {
  --theme-primary : #E9CD4C;   /* kariyasu */
  --theme-light   : #F3F1E6;
  --theme-accent  : #35FFDB;
  --theme-dark    : #433909;
  --theme-neutral : #E8E7E2;
  --theme-text    : #1C1C1C;
}

[data-theme="hiwa"] {
  --theme-primary : #BEC23F;   /* hiwa */
  --theme-light   : #F3F3E6;
  --theme-accent  : #1EDCE2;
  --theme-dark    : #31320D;
  --theme-neutral : #E7E7E3;
  --theme-text    : #1C1C1C;
}

[data-theme="hiwamoegi"] {
  --theme-primary : #90B44B;   /* hiwamoegi */
  --theme-light   : #EFF3E6;
  --theme-accent  : #2D99D1;
  --theme-dark    : #242E11;
  --theme-neutral : #E6E7E3;
  --theme-text    : #1C1C1C;
}

[data-theme="yanagizome"] {
  --theme-primary : #91AD70;   /* yanagizome */
  --theme-light   : #EDF1E8;
  --theme-accent  : #5992C3;
  --theme-dark    : #242E19;
  --theme-neutral : #E5E6E4;
  --theme-text    : #1C1C1C;
}

[data-theme="nae"] {
  --theme-primary : #86C166;   /* nae */
  --theme-light   : #EBF3E6;
  --theme-accent  : #4C7EDA;
  --theme-dark    : #1F3613;
  --theme-neutral : #E4E7E3;
  --theme-text    : #1C1C1C;
}

[data-theme="wakatake"] {
  --theme-primary : #5DAC81;   /* wakatake */
  --theme-light   : #E7F2EC;
  --theme-accent  : #7E42C6;
  --theme-dark    : #152C20;
  --theme-neutral : #E4E6E5;
  --theme-text    : #1C1C1C;
}

[data-theme="byakuroku"] {
  --theme-primary : #A8D8B9;   /* byakuroku */
  --theme-light   : #E6F3EB;
  --theme-accent  : #956FDB;
  --theme-dark    : #1B442A;
  --theme-neutral : #E3E7E4;
  --theme-text    : #1C1C1C;
}

/* Blue */
[data-theme="seiji"] {
  --theme-primary : #69B0AC;   /* seiji */
  --theme-light   : #E7F2F2;
  --theme-accent  : #C150C8;
  --theme-dark    : #172F2D;
  --theme-neutral : #E4E6E6;
  --theme-text    : #1C1C1C;
}

[data-theme="mizuasagi"] {
  --theme-primary : #66BAB7;   /* mizuasagi */
  --theme-light   : #E6F3F2;
  --theme-accent  : #CE4CD3;
  --theme-dark    : #153231;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="byakugun"] {
  --theme-primary : #78C2C4;   /* byakugun */
  --theme-light   : #E6F3F3;
  --theme-accent  : #DA61D6;
  --theme-dark    : #163738;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="kamenozoki"] {
  --theme-primary : #A5DEE4;   /* kamenozoki */
  --theme-light   : #E6F2F3;
  --theme-accent  : #EC5EDF;
  --theme-dark    : #14484E;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="mizu"] {
  --theme-primary : #81C7D4;   /* mizu */
  --theme-light   : #E6F1F3;
  --theme-accent  : #E763D3;
  --theme-dark    : #133A41;
  --theme-neutral : #E3E7E7;
  --theme-text    : #1C1C1C;
}

[data-theme="sora"] {
  --theme-primary : #58B2DC;   /* sora */
  --theme-light   : #E6EFF3;
  --theme-accent  : #F83BBC;
  --theme-dark    : #0A3042;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

[data-theme="wasurenagusa"] {
  --theme-primary : #7DB9DE;   /* wasurenagusa */
  --theme-light   : #E6EEF3;
  --theme-accent  : #F258B8;
  --theme-dark    : #0E3247;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

[data-theme="tsuyukusa"] {
  --theme-primary : #2EA9DF;   /* tsuyukusa */
  --theme-light   : #E6EFF3;
  --theme-accent  : #FE0EB5;
  --theme-dark    : #082B3A;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

/* Blue / Navy */
[data-theme="gunjyo"] {
  --theme-primary : #51A8DD;   /* gunjyo */
  --theme-light   : #E6EEF3;
  --theme-accent  : #FA33AF;
  --theme-dark    : #092C41;
  --theme-neutral : #E2E6E8;
  --theme-text    : #1C1C1C;
}

/* Purple */
[data-theme="usu"] {
  --theme-primary : #B28FCE;   /* usu */
  --theme-light   : #EDE6F3;
  --theme-accent  : #DDAB6E;
  --theme-dark    : #2D183E;
  --theme-neutral : #E5E3E7;
  --theme-text    : #1C1C1C;
}

/* White / Gray / Black */
[data-theme="shironeri"] {
  --theme-primary : #FCFAF2;   /* shironeri */
  --theme-light   : #F3F0E6;
  --theme-accent  : #55F6D5;
  --theme-dark    : #685713;
  --theme-neutral : #E8E7E2;
  --theme-text    : #1C1C1C;
}

[data-theme="shironezumi"] {
  --theme-primary : #BDC0BA;   /* shironezumi */
  --theme-light   : #EDEDEC;
  --theme-accent  : #93A5B8;
  --theme-dark    : #2F312C;
  --theme-neutral : #E5E5E5;
  --theme-text    : #1C1C1C;
}
```
