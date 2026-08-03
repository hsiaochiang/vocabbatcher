# REPORT_UIUX2_頁次篩選與自動化驗證 — 執行結果

- 執行時間：2026-08-03 10:59:43 +08:00
- 狀態：完成

## 改了什麼

- `exam-vocab-batcher/src/pages/BatchBuilderPage.tsx`：新增「頁次範圍」作為最上方主要篩選，預設使用 `getPageRange(allWords)` 取得全書範圍 3-62 頁；單字只要任一 `source_page` 落在設定範圍內就會顯示。「顯示 N 筆」會反映頁次、頻率、詞性、搜尋全部條件後的結果。
- 原本頻率、詞性、搜尋功能保留，移到頁次篩選下方並標示為「進階篩選」。
- `exam-vocab-batcher/src/pages/ExamSetupPage.tsx`：Playwright 驗證時發現直接開 `/exam` 會因單字庫尚未載入，頁碼預設停在 1-1，導致無法開始考試；已改成與批次建立器相同的衍生頁碼預設，資料載入後會正確使用全書範圍。
- `exam-vocab-batcher/package.json`、`package-lock.json`：新增 `@playwright/test` devDependency 與 `npm run test:e2e` 指令。
- `exam-vocab-batcher/playwright.config.ts`：新增 Playwright Chromium 設定，會連到本機 `http://127.0.0.1:5173`，並可自動啟動或重用 Vite dev server。
- `exam-vocab-batcher/e2e/uiux2.spec.ts`：新增 4 項不需真實 Google 登入的 UI/UX 驗證。

## Playwright 驗證結果

- 通過：首頁無批次時主 CTA 是「建立新批次」，模擬已有批次後主 CTA 改為「開始考試」。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/home-empty-primary-cta.png`
  - 截圖：`exam-vocab-batcher/e2e/screenshots/home-existing-batch-primary-cta.png`
- 通過：批次建立器顯示「頁次範圍」，把範圍縮到第 3-3 頁後，「顯示 N 筆」確實變少。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/builder-page-range-filter.png`
- 通過：用第 3-3 頁範圍全選建立批次後，可以進入批次頁並打開翻牌學習。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/flashcard-created-from-page-range.png`
- 通過：考試設定頁可以正常顯示、開始 5 題考試，答題後選項顯示勾叉圖示。
  - 截圖：`exam-vocab-batcher/e2e/screenshots/exam-setup.png`
  - 截圖：`exam-vocab-batcher/e2e/screenshots/exam-run-feedback-icons.png`
- 指令結果：`npm.cmd run test:e2e`，4 tests passed。

## 是否偏離 BRIEF

無。

## npm run lint / npm run build 結果

- `npm run lint`：通過。
- `npm run build`：通過。
- 備註：PowerShell 環境仍會在命令結束時印出既有的 `npm.ps1` 權限雜訊，但兩個命令 exit code 皆為 0。另以 `npm.cmd run lint`、`npm.cmd run build` 驗證也通過。

## ★ 負責人驗收步驟（白話、按順序）

1. 部署後進首頁，點「建立新批次」。
2. 你現在會先看到「頁次範圍」在畫面最上面，可以直接輸入課本頁數，例如 3 到 3，下面單字列表會立刻變少。
3. 確認原本的「高頻／中頻／低頻」「詞性」「搜尋英文單字」都還在，只是變成頁次下方的進階篩選。
4. 用頁次範圍篩出單字後，點「全選篩選結果」，再點「建立批次」，確認流程仍會進到批次頁，並能打開翻牌學習。
5. 不需要你自己重跑 Playwright；我已自動測過首頁 CTA、頁次篩選、建立批次到翻牌、考試設定到答題回饋 4 條路徑，全部通過，截圖也已留在 `exam-vocab-batcher/e2e/screenshots/`。
6. Playwright 不能取代真機，所以 iPhone Safari、Android Chrome 還是各測一次批次建立流程。

## 遇到的問題 / 卡住的地方（若有）

- `npm install -D @playwright/test` 與 `npx playwright install chromium` 需要網路與使用者 AppData 寫入權限，因此用核准後的命令完成。
- Playwright 第一次跑時抓到 `/exam` 直接開頁的頁碼預設問題，已修正後重跑，4 項測試全數通過。
- `npm install` 顯示目前專案依賴有 6 個 audit 弱點，這不是本次 UI/UX BRIEF 範圍，未執行 `npm audit fix`，避免引入非必要套件升級。
