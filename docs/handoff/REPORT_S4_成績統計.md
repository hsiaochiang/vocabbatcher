# REPORT_S4_成績統計 — 執行結果

- 執行時間：2026-08-01 07:52:33 +08:00
- 狀態：完成

## 改了什麼

- `exam-vocab-batcher/src/pages/ExamResultPage.tsx`：考完儲存成績時，改用 Firestore batch 同步寫入 `examResults`，並對每筆作答紀錄累加 `users/{uid}/wordStats/{word}` 的 `attempts` 與 `wrong`；`wrongRate` 沒有寫入資料庫。
- `exam-vocab-batcher/src/pages/ExamHistoryPage.tsx`：新增「成績歷史」頁，登入後讀取 `users/{uid}/examResults`，依 `date` 新到舊顯示日期、模式、頁數、分數，並可展開逐題對錯與發音。
- `exam-vocab-batcher/src/pages/WordStatsPage.tsx`：新增「單字統計」頁，登入後讀取 `users/{uid}/wordStats`，前端即時計算 `wrong / attempts`，依錯誤率由高到低排序，並提供每字發音按鈕。
- `exam-vocab-batcher/src/App.tsx`：新增 `/history` 與 `/stats` 路由；維持既有 `BrowserRouter`。
- `exam-vocab-batcher/src/pages/HomePage.tsx`：新增「成績歷史」與「單字統計」兩個入口，未登入也可看見入口。
- 型別檔 `src/types/exam.ts` 未調整，沿用既有 `ExamResult`、`ExamQuestionRecord`、`WordStat`。

## 是否偏離 BRIEF

無。

## npm run lint / npm run build 結果

- `npm run lint`：通過。
- `npm run build`：通過。
- 備註：PowerShell 直接執行 `npm run ...` 時，環境中的 `npm.ps1` 會印出一段權限雜訊；改用等價的 `npm.cmd run lint`、`npm.cmd run build` 後已乾淨通過。

## ★ 負責人驗收步驟（白話、按順序）

1. 先部署這版到 Firebase Hosting。
2. 用你的帳號登入 App。
3. 進「開始考試」，選同一個頁數範圍，連續考三次。可以故意答錯幾題，這樣比較容易看出統計有沒有累加。
4. 回首頁，點「成績歷史」。你應該看得到三筆成績，最新的在最上面，每筆都有日期、考試模式、頁數範圍、得分。
5. 在「成績歷史」點開其中一筆，確認看得到每題單字、對錯，以及喇叭發音按鈕。
6. 回首頁，點「單字統計」。你應該看得到考過的單字，錯誤率高的排在前面，每筆有錯誤率、答錯次數/作答次數、喇叭發音按鈕。
7. 登出後，再點「成績歷史」與「單字統計」。頁面應該顯示需要登入的提示，不應該白畫面或報錯。
8. 用 iPhone Safari 與 Android Chrome 各跑一次：登入、考一次、看「成績歷史」、看「單字統計」。

## 遇到的問題 / 卡住的地方（若有）

沒有卡住。建置時 Vite 顯示 chunk 大小提醒，這是既有 bundle 體積提醒，不影響本次 S4 功能與 build 結果。
