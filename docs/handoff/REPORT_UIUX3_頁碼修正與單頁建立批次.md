# REPORT_UIUX3_頁碼修正與單頁建立批次 — 執行結果

- 執行時間：2026-08-03 11:30 +08:00
- 狀態：完成，待負責人用實體課本抽查驗收

## 改了什麼

- `exam-vocab-batcher/public/data/vocab.cleaned.json`、`output/vocab.cleaned.json`：所有 `source_page` 統一減 2，從 PDF 內部頁碼 3~62 改為課本印刷頁碼 1~60；修正後 1231 筆資料皆有效，沒有 0 或負數頁碼。
- `src/pdf_parser/rules/top2025_md.py`：新增 `PRINTED_PAGE_OFFSET = 2`，讓未來重新從 `top2025.md` 產生資料時，直接輸出課本印刷頁碼。
- `tests/test_top2025_md.py`：補上頁碼偏移測試，固定 `3 -> 1`、`62 -> 60`、未知頁 `0` 保持 `0`。
- `exam-vocab-batcher/src/pages/BatchBuilderPage.tsx`：移除 UIUX2 的頁碼範圍輸入，改為「快速建立：選課本頁碼」。每一頁都是一個按鈕，按下就建立該頁所有單字的批次並進入批次頁。
- `exam-vocab-batcher/src/store/AppContext.tsx`：`createBatch` 支援自訂批次名稱，頁碼按鈕建立的批次會顯示「批次 #N（第 X 頁）」。
- `exam-vocab-batcher/e2e/uiux2.spec.ts`：更新為 UIUX3 驗證案例；保留同一檔名是為了沿用既有 Playwright 設定。

## 資料驗證

- `exam-vocab-batcher/public/data/vocab.cleaned.json`：1231 筆，最小頁 1，最大頁 60，第 1 頁 19 字，第 60 頁 19 字，非正數頁碼 0 筆。
- `output/vocab.cleaned.json`：1231 筆，最小頁 1，最大頁 60，第 1 頁 19 字，第 60 頁 19 字，非正數頁碼 0 筆。

## Playwright 驗證結果

- 通過：首頁無批次時主 CTA 是「建立新批次」，模擬已有批次後主 CTA 改為「開始考試」。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/home-empty-primary-cta.png`
  - 截圖：`exam-vocab-batcher/e2e/screenshots/home-existing-batch-primary-cta.png`
- 通過：批次建立器顯示「快速建立：選課本頁碼」、共 60 頁，且可看到第 1 頁與第 60 頁按鈕。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/builder-page-buttons.png`
- 通過：批次建立器在手機尺寸 390x844 仍可看到頁碼按鈕與底部「建立批次」按鈕。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/builder-page-buttons-mobile.png`
- 通過：點「第 1 頁」按鈕會直接建立「批次 #1（第 1 頁）」，批次頁顯示 19 個單字。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/builder-one-page-created.png`
- 通過：進階篩選仍可搜尋 `about` 並手動建立 1 字批次。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/builder-advanced-filter.png`
- 通過：考試設定頁顯示修正後的全書範圍「1~60 頁」。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/exam-setup-corrected-page-range.png`

## 驗證指令

- `python -m pytest tests\test_top2025_md.py`：15 passed。
- `npm.cmd run lint`：通過。
- `npm.cmd run build`：通過；Vite 仍提示單一 chunk 超過 500 kB，為既有提醒，未在本片處理。
- `npm.cmd run test:e2e`：6 passed。

## 是否偏離 BRIEF

無。依 BRIEF 執行資料快修、修 parser 主力路徑、批次建立器改為一頁一按鈕，未重跑整份 PDF 解析，也未改登入、Firestore rules、路由或 PWA 設定。

## ★ 負責人驗收步驟（白話、按順序）

1. 部署後進首頁，點「建立新批次」。
2. 畫面最上方會看到「快速建立：選課本頁碼」，從 1 到 60 都是可點的頁碼按鈕。
3. 拿實體課本翻到第 1 頁，點 App 的「1」按鈕，確認建立出的批次是「第 1 頁」，且單字大致對得上課本第 1 頁。
4. 回到「建立新批次」，再抽查幾個頁碼，例如 7、20、60，確認 App 頁碼跟課本印刷頁碼一致。
5. 確認下方「進階篩選：手動選字」仍可搜尋英文單字，例如輸入 `about`，勾選後按「建立批次」。
6. 到「考試設定」，確認頁數範圍旁顯示「全書 1~60 頁」。

## 遇到的問題 / 卡住的地方（若有）

- Playwright 第一次重跑時，舊測試初始化多做了一次 `localStorage.clear()`，剛好撞到首頁載入中的導向競態；已移除多餘初始化後重跑，並補手機尺寸案例，6 項測試全數通過。
