# REPORT_S5_錯題複習卷 — 執行結果

- 執行時間：2026-08-02 23:26:05 +08:00
- 狀態：完成

## 改了什麼

- `exam-vocab-batcher/src/services/exam.ts`：新增 `GenerateReviewExamOptions` 與 `generateReviewExam(allWords, wordStats, options)`。新函式會篩選 `wrong > 0` 且 `attempts > 0` 的單字，依錯誤率、錯誤次數、作答次數排序，取前 10 題候選，並重用既有 `buildQuestion()` 產生選擇題。
- `exam-vocab-batcher/src/pages/WordStatsPage.tsx`：新增「錯題複習」按鈕。登入且有錯題資料時，按下後會用目前已載入的 `stats` 與 `allWords` 產生複習卷，導向既有 `/exam/run` 作答流程；沒有錯題資料或單字資料尚未載入時按鈕停用。
- 沒有加「複習卷標籤」可選功能，結果頁與成績歷史沿用既有一般考試資料格式，避免擴大影響範圍。

## 是否偏離 BRIEF

無。

## npm run lint / npm run build 結果

- `npm run lint`：通過。
- `npm run build`：通過。
- 備註：PowerShell 環境仍會在命令結束時印出既有的 `npm.ps1` 權限雜訊，但兩個命令 exit code 皆為 0。另以 `npm.cmd run lint`、`npm.cmd run build` 驗證也通過。

## ★ 負責人驗收步驟（白話、按順序）

1. 先部署這版到 Firebase Hosting。
2. 用你的帳號登入 App。
3. 先正常考幾次，故意答錯幾個單字，讓「單字統計」裡有錯題資料。
4. 回首頁，進「單字統計」。
5. 點底部「錯題複習」。
6. 確認系統直接進入考試畫面，而且出現的單字大多是你剛剛答錯過、錯誤率比較高的字。
7. 作答到最後，確認可以正常看到得分與結果頁，流程跟一般考試一樣。
8. 換一個沒有錯題資料的狀態測一次：進「單字統計」時，「錯題複習」按鈕應該停用或顯示還沒有錯題可複習，不應該進入空白考卷或報錯。
9. 用 iPhone Safari 與 Android Chrome 各測一次：登入、進「單字統計」、按「錯題複習」、完成一次作答。

## 遇到的問題 / 卡住的地方（若有）

沒有卡住。建置時 Vite 顯示 chunk 大小提醒，這是既有 bundle 體積提醒，不影響本次 S5 功能與 build 結果。
