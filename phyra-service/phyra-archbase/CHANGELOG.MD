# Changelog

## 2026-05-22

- **靜態站 → 加一層純 stdlib 後端** `script/server.py`（取代 `python3 -m http.server`）：仍服務原本的靜態首頁，另開三個 API（`GET/POST /api/tags`、`POST /api/delete`）。`serve.sh` / `install-service.sh` 改用它，預設埠不變（8037）
- **標籤系統**：每張論文卡片右上 hover 出現 `＋ 標籤`，可自由新增/移除（多標籤，免密碼）；搜尋列下方多了「🏷 依標籤篩選」下拉複選（OR：含任一選取標籤即顯示）。標籤持久化於 `collection/tags.json`（`{stem: [tags…]}`），不被 `generate_index.py` 當成論文掃描
- **刪除論文**：卡片右上 🗑（hover 顯現）→ 確認彈框 → 管理員密碼 → 移除該 stem 在 `collection/` 的所有 artifact 檔並就地重生 `index.html`。密碼由環境變數 `PHYRA_ARCHBASE_ADMIN_PASSWORD` 在啟動時帶入（**未設＝刪除停用**，回 403）；密碼比對為 constant-time，輸入後存 sessionStorage、本次瀏覽不再重複詢問。後端對 key 做路徑穿越防護（限定 `collection/` 內、無 `/`、無 `..`）
- 新增過濾 chip **Bilingual**（只顯示有雙語 PDF 的論文），位於 Analyzed 與 PDF only 之間
- 分節標題（年月「2026 · 05」/ 字母）字級 `11px → 15px`，letter-spacing 收斂為 `0.6px`

## 2026-05-21

- 改名 **Paper Base → phyra-archbase**：`<title>` / `<h1>` 改名；localStorage theme key `paperbase-theme` → `phyra-archbase-theme`；systemd unit `paperbase.service` → `phyra-archbase.service`（舊 unit 若已安裝請自行 `systemctl --user disable --now paperbase && rm ~/.config/systemd/user/paperbase.service`）
- 首頁頂部新增 **Phyra Center** banner，連到 sibling 翻譯服務 phyra-dualtrans；連結由瀏覽器 hostname 動態組成（內網可用），port 由 `PHYRA_DUALTRANS_PORT`（預設 8080）在產生時烘焙
- 與 phyra-dualtrans 的「📥 存入 archbase」按鈕對接：dualtrans 把原文 + 雙語 PDF 複製進 `collection/` 後會自動重跑 `generate_index.py`；存過的任務改顯示「✓ 已入庫（可重存）」(dualtrans 端 `job.archived`，持久化於 `job.json`)
- header 改為 `position: sticky` 釘在頁面頂部；sticky 的分節標題改用 `top: var(--header-h)` 跟隨 header 實際高度（JS 量測、resize 時更新），避免兩者在頂部重疊
- Phyra Center banner 按鈕文字「📝 翻譯 DualTrans →」→「📝 雙語翻譯 DualTrans →」
- **改 port**：phyra-archbase `serve.sh` 預設 `8000 → 8037`；banner 回連的 dualtrans 預設 `PHYRA_DUALTRANS_PORT` `8080 → 8039`

## 2026-05-14

- 新增 `generate_index.py` 與 `index.html` 瀏覽首頁，自掃 `collection/` 產出每篇論文的 artifact 卡片
- `collection/` 全面把檔名中標題的空白替換為 `_`、原始 `: ` 編碼為 `__`（共 330 個檔案重新命名）
- 解析器改以 `_analysis.zh-TW.md` 的 `| Paper full title |` / `| Paper short name |` 為標題真值來源，檔名只作 fallback
- 確認新檔名規約：`{YYMM}_{完整論文標題}_{suffix}`，不再要求標題簡稱
- 首頁配色改用 Claude.ai 風（米黃奶油底 + 招牌橘 `#D97757`），CSS 變數集中於 `:root` 與 `[data-theme="dark"]` 兩處
- 右上角加 segmented 主題切換（System / Light / Dark），選擇存於 `localStorage["paperbase-theme"]`；System 模式跟隨 OS `prefers-color-scheme` 並即時監聽變化
- 修正搜尋框 dark mode 下底色寫死 `#fff` 的 bug，改用 `var(--p-card-bg)`
- 首頁加 segmented 過濾 chip（All / Analyzed / PDF only）；Analyzed 定義 = 至少有 analysis / slide / bilingual 三者之一（與卡片 `pdf-only` 灰底判定一致）
- 加一個排序循環按鈕：`↓ Date` → `↑ Date` → `A→Z`，預設仍是日期由新到舊
- 鍵盤捷徑：`/` 聚焦搜尋框（不在輸入區時）、`Esc` 在搜尋框內清空 / 再按一次失焦；placeholder 多了 `(press /)` 提示
- Header 改成單列水平 row（左：標題+統計；中：搜尋與過濾控制；右：主題切換），h1/stats 字級縮小，padding 從 `28/40/22` 收成 `14/28`；窄螢幕（<760px）自動回到舊版垂直堆疊
- 新增 `--p-header-border` CSS 變數，header 下緣分隔線顏色從 accent 橘改為中性灰（light `#d7d7d5` / dark `#3b3b39`）
- 卡片區依排序模式插入 sticky 分節標題：日期排序時用「`2025 · 03`」（年 · 月），標題排序時用首字母（`A` … `Z`，非字母歸 `#`）
- 卡片內 artifact 按鈕順序改為 `📄 PDF · 📖 Analysis · 🎞 Slide · 🌐 雙語`（原本 Analysis 在第一）
- 目錄重整：`generate_index.py` 移入 `script/`；新增 `script/serve.sh`（前台啟動 HTTP 服務）與 `script/install-service.sh`（裝 systemd user service 背景常駐）；三個檔皆 `chmod +x`，吃 `PORT` 環境變數
