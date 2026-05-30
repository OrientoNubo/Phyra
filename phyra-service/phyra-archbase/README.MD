# phyra-archbase

個人論文歸檔與瀏覽頁（原 Paper Base）。`collection/` 內每篇論文最多有 5 種 artifact，根目錄 `index.html` 是自動產生的索引首頁。它是 Phyra 家族的「歸檔／瀏覽出口」，掛在主頁 [phyra-center](..) 之下，與翻譯服務 [phyra-dualtrans](../phyra-dualtrans) 是 sibling 服務。

## 目錄結構

```
phyra-archbase/
├── collection/                 # 所有論文檔案（每篇 1–5 個 artifact）
├── script/
│   ├── generate_index.py       # 掃描 collection/、產生 index.html
│   ├── server.py               # 純 stdlib 後端：靜態瀏覽 + 標籤/刪除 API
│   ├── serve.sh                # 啟動本機 HTTP 服務（前台、Ctrl+C 結束）
│   └── install-service.sh      # 裝 systemd user service（背景常駐 / 開機自動跑）
├── index.html                  # 自動產生的瀏覽首頁（self-contained）
├── README.MD
└── CHANGELOG.MD
```

## Phyra Center 與 dualtrans 整合

首頁頂部有一條 **「← 返回 Phyra Center」** banner，連回主頁 phyra-center。連結由瀏覽器當下的 hostname 動態組成（內網也通），port 在產生時烘焙：

```bash
PHYRA_CENTER_PORT=8035 script/generate_index.py   # 預設 8035
```

反向地，在 phyra-dualtrans 完成一篇翻譯後，可在其 Jobs 卡片按「📥 存入 archbase」，把原文 PDF + 雙語 PDF 依本專案檔名規約複製進 `collection/` 並自動重跑本腳本——該論文便會出現在這裡。dualtrans 預設自動偵測 sibling `../phyra-archbase`（同層的 phyra-center 目錄下）。

> 平時整套服務由 `phyra-center/script/start.sh` 一鍵拉起（主頁 + 翻譯 + 論文庫），單獨啟動 archbase 則直接 `script/serve.sh`。

## 檔名規約

每篇論文以 `{YYMM}_{Title}` 為前綴（過去也接受 `{YYMM}_{Short}_{Title}`），可帶以下 5 種 suffix：

| Suffix                          | 內容              |
| ------------------------------- | ----------------- |
| `.pdf`                          | 原文 PDF          |
| `_bilingual.zh-TW.dual.pdf`     | 雙語對照 PDF      |
| `_analysis.zh-TW.md`            | 中文分析 Markdown |
| `_analysis.zh-TW.html`          | 中文分析 HTML     |
| `_draftslide.html`              | 投影片            |

標題部分的編碼：原始 ` ` → `_`，原始 `: ` → `__`（`:` 不能出現在檔名中）。卡片顯示時優先讀 MD 內的 `| Paper full title |` 欄位取得乾淨標題，沒有 MD 則由檔名反向還原。

## 使用流程

**重生首頁**（新增論文後跑一次）：

```bash
script/generate_index.py
```

**本機瀏覽**：直接開 `index.html` (`file://`) 即可。

**分享給內網**：

```bash
script/serve.sh             # 前台啟動；Ctrl+C 結束；其他人開 http://<你IP>:8037/
script/install-service.sh   # 背景常駐（systemd user service，開機自動跑）
```

兩個 server 腳本都吃 `PORT` 環境變數，預設 `8037`，底層跑 `script/server.py`。

> `file://` 直接開 `index.html` 仍可純瀏覽，但**標籤與刪除需要 `server.py` 的 API**，務必透過 `serve.sh` 開啟。

## 標籤與刪除（需 server.py）

`server.py` 在靜態服務外多開三個端點：

| 端點 | 用途 | 密碼 |
| --- | --- | --- |
| `GET /api/tags` | 取回 `collection/tags.json` | 否 |
| `POST /api/tags` | 設定某論文的標籤 | 否 |
| `POST /api/delete` | 刪除某論文全部 artifact 並重生首頁 | **是** |

- **標籤**：卡片右上 hover 出現 `＋ 標籤`，可自由新增/移除（一篇可多標籤）；搜尋列下方的「🏷 依標籤篩選」下拉可複選標籤過濾（OR：含任一選取標籤即顯示）。資料持久化於 `collection/tags.json`（`{stem: [tags…]}`），不會被 `generate_index.py` 當成論文掃描。
- **刪除**：卡片右上 🗑 → 確認彈框 → 輸入管理員密碼。密碼用環境變數啟動時帶入，**未設＝刪除停用**（回 403）：

  ```bash
  PHYRA_ARCHBASE_ADMIN_PASSWORD='choose-a-secret' script/serve.sh
  ```

  密碼比對為 constant-time；通過後存 sessionStorage，本次瀏覽不再重複詢問。後端對論文 key 做路徑穿越防護（限定 `collection/` 內、不含 `/` 與 `..`）。

> 安全提醒：服務綁 `0.0.0.0` 且無一般認證，請只在可信內網跑（或 `HOST=127.0.0.1`）。標籤刻意設計為免密碼自由編輯——若不希望內網他人改標籤，請綁 localhost。

## 搜尋 / 過濾 / 排序

Header 中央那條是即時控制列：

| 控制 | 行為 |
| --- | --- |
| 搜尋框 | 即時比對標題與短名（case-insensitive） |
| `All` / `Analyzed` / `Bilingual` / `PDF only` | 過濾 — Analyzed = 至少有 analysis / slide / 雙語其一；Bilingual = 有雙語 PDF；PDF only = 只有原文 PDF |
| `↓ Date` / `↑ Date` / `A→Z` | 點一下循環下一個排序：日期新→舊（預設）／日期舊→新／標題字母序 |

排序時卡片區會自動插入 sticky 分節標題：日期模式用「年 · 月」（例 `2025 · 03`），標題模式用首字母（`A` … `Z`，非字母歸 `#`）。

鍵盤：`/` 聚焦搜尋框；搜尋框內 `Esc` 清空、再按一次失焦。

## 卡片連結

每張卡片只渲染實際存在的 artifact 連結：📄 PDF · 📖 Analysis · 🎞 Slide · 🌐 雙語。只有原文 PDF 的卡片背景略灰，方便辨識「尚未分析」。

## 外觀

頁面右上角有 segmented 主題切換 — 三段：

| 圖示 | 模式 | 行為 |
| --- | --- | --- |
| 🖥 | System | 跟著作業系統 `prefers-color-scheme`，OS 切深淺時頁面即時跟著切 |
| ☀ | Light | 強制亮色 |
| ☾ | Dark | 強制暗色 |

選擇存於 `localStorage["phyra-archbase-theme"]`，預設 `system`。要調色到 `generate_index.py` 的 `:root` 與 `[data-theme="dark"]` 兩段 CSS 變數，每個變數旁有註解標明對應的 UI 位置；改完重跑 `python3 generate_index.py` 即生效。
