# Roadmap

> 用來回答：「目前在哪個階段？下一步是什麼？什麼時候可以上線？」

---

## 1. 專案範疇（Scope）

### 產品願景
國中會考英文單字練習 App（Android 優先），讓學生能**勾選最多 25 個單字 → 聽批次錄音或做練習**。

### 三大交付物

| # | 交付物 | 技術棧 | 說明 |
|---|--------|--------|------|
| D1 | **PDF Parser** | Python 3.11 CLI | `top2025.pdf` → `vocab.raw.json` / `vocab.cleaned.json` / `vocab.qa_report.json` |
| D2 | **UI 原型** | Stitch HTML | 6 核心畫面的高保真手機 UI（已完成 10 畫面） |
| D3 | **ExamVocabBatcher App** | React Native + Expo | 完整 App：批次建立 → 音訊播放 → 翻牌學習 → 四題型練習 → 統計 |

### Non-goals（明確不做）
- 帳號系統 / 雲端同步
- 匯出 MP3 到檔案系統
- iOS 版本（MVP 階段）
- 多語系（僅正體中文 + 英文單字）
- 自訂單字庫匯入

---

## 2. 里程碑（Milestones）— 分階段上線

### M1：資料就緒（Data Ready）
> 目標：PDF 轉成可靠的 JSON 單字庫，可被 App 載入

**交付物**：D1（PDF Parser）
**驗收標準**：
- [ ] CLI 可執行：`python parser.py --input top2025.pdf --outdir output/`
- [ ] 產出 `vocab.raw.json`（原始解析）、`vocab.cleaned.json`（清洗後）、`vocab.qa_report.json`
- [ ] `vocab.cleaned.json` 中每筆包含：word, pos, zh_definition, source_page
- [ ] 去重：同 word + pos 合併
- [ ] `parse_confidence` ≥ 0.85（整體）
- [ ] pytest 測試通過
- [ ] QA report 中 issues 數量 < 總詞數 5%
**可上線意義**：JSON 資料可交給 App 團隊或自己開始 App 開發

### M2：核心可用（Core Usable）
> 目標：能建批次 + 聽單字錄音，使用者可以開始用來學習

**交付物**：D3 App（部分功能）
**驗收標準**：
- [ ] 載入 `vocab.cleaned.json`，可搜尋/篩選（頁碼/頻率）
- [ ] 勾選最多 25 字建立批次
- [ ] 25 字滿額時禁止再選並顯示提示
- [ ] TTS 批次播放（expo-speech 方案 A）：英文 → 間隔 → 中文 → 間隔 → 下一字
- [ ] 三種間隔（3/5/10 秒）可選
- [ ] 播放中顯示進度條 + 目前單字高亮
- [ ] 翻牌卡學習（正面英文、背面中文+詞性）
- [ ] 首屏 < 2 秒（中階 Android）
- [ ] 斷網可用
**可上線意義**：學生可以開始用最核心功能學習——建批次、聽錄音、翻牌

### M3：練習完整（Full Practice）
> 目標：四題型練習 + 成績統計 + 歷史批次

**交付物**：D3 App（完整 MVP）
**驗收標準**：
- [ ] 四題型：中→英、英→中、拼字填空、聽音選字
- [ ] 題庫限本批次 25 字
- [ ] 即時判分 + 結果頁
- [ ] 錯題重練功能
- [ ] 批次歷史列表，可重新進入
- [ ] 批次統計（正確率/錯題分布）
- [ ] 自動儲存中斷，首頁顯示「繼續上次」
- [ ] 批次紀錄持久化（AsyncStorage）
**可上線意義**：完整學習閉環——選字 → 聽 → 學 → 練 → 改 → 複習

### M4：品質收斂（Release Quality）
> 目標：效能、邊界情況、UX 細節打磨

**驗收標準**：
- [ ] 邊界情況：0 字批次阻止、重複批次提示、空白搜尋結果處理
- [ ] 效能：500+ 字列表滾動不卡頓（FlatList 虛擬化）
- [ ] Touch target ≥ 44dp
- [ ] 每頁一個主 CTA
- [ ] 無 ANR / 白屏 / 閃退
- [ ] Smoke test 全部通過
- [ ] README 使用說明完整
**可上線意義**：可發布到 Google Play 內部測試軌

---

## 3. 開發階段（Development Stages）

| 階段 | 所屬里程碑 | 內容 |
|------|-----------|------|
| S0 | — | Stitch UI 基準 HTML（✅ 已完成） |
| S1 | — | Bootstrap workspace + 規範建置（✅ 已完成） |
| S2 | M1 前置 | UI/UX 盤點 + Style Freeze |
| S3-D1 | M1 | PDF Parser 規格 → 實作 → 驗收 |
| S3-D3 | M2 前置 | App 規格撰寫（OpenSpec） |
| S4-M2 | M2 | App 核心功能實作（批次+音訊+翻牌） |
| S4-M3 | M3 | App 練習功能實作（四題型+統計+歷史） |
| S5 | M4 | Bugfix 收斂 + Smoke + 效能 |
| S6 | — | 整理素材 / 發布 |

---

## 4. 目前狀態
- Current：S3-D1（2026-02-28）— `pdf-parser` 已完成實作與提交（`a2d8fe0`），進入收尾階段
- Next：修正 code review 的 2 個 CRITICAL 後，執行 `/opsx:sync` 與 `/opsx:archive "pdf-parser"`
- Blockers：`docs/qa/2026-02-28_code-review.md` 中 2 個 CRITICAL（confidence 門檻與 unparseable 行低信心記錄）
- Evidence：`a2d8fe0`、`docs/qa/2026-02-28_code-review.md`、`openspec/changes/pdf-parser/`

## 5. 階段轉換記錄

| 日期 | 從 | 到 | 觸發原因 | 證據 |
|------|----|----|---------|------|
| 2026-02-28 | S0 | S1.5 | Bootstrap + OpenSpec 初始化完成 | docs/decisions/2026-02-28_openspec-workflow-automation.md |
| 2026-02-28 | S1.5 | S3-D1 | 完成 `pdf-parser` change 實作、驗證、提交推送 | a2d8fe0, openspec/changes/pdf-parser/, docs/qa/2026-02-28_code-review.md |
