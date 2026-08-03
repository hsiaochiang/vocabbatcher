# BRIEF_S4_成績統計.md — M3 切片 4：成績紀錄與累積錯誤率統計

> 交接合約：規劃層 → 執行層，2026-08-01。
> 對應需求：`REQUIREMENTS.md` R11。切片全景見 `STAGE_3_PLAN.md`。
> 前置：S1（發音按鈕）、S2（登入）、S3（考試引擎，含登入問題 S3b~S3f 四輪修復）皆已驗收通過。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀本 BRIEF 全文；工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 使用者登入後，考完的每次成績會自動累積到「每個單字的錯誤率」，並能查看自己的成績歷史列表與依錯誤率排序的單字統計。

## 現況（可直接重用）
- `src/types/exam.ts` 已定義 `ExamResult`、`ExamQuestionRecord`、`WordStat`（`word`、`attempts`、`wrong`、`wrongRate`）型別。
- `src/pages/ExamResultPage.tsx` 目前已登入時會把該次成績寫入 `users/{uid}/examResults/{examId}`（S3 完成的部分），但**還沒有**把逐題結果累加到 `users/{uid}/wordStats/{word}`——這是本切片要補的。
- `src/services/firebase.ts` 匯出 `db`（Firestore 實例）。
- `src/services/auth.ts` 匯出 `onAuthStateChange`、`User` 型別。
- `src/components/SpeakButton.tsx` 可重用。
- 路由定義在 `src/App.tsx`（目前用 `BrowserRouter`，不要改回 `HashRouter`——之前花了四輪才修好登入問題，根因是 `HashRouter` 與 Firebase 登入衝突，絕對不要動這個路由選型）。

## 任務

1. **`wordStats` 累加寫入**：在 `ExamResultPage.tsx` 寫入 `examResults` 成功後（或同一個 effect 內一起做），對這次考試的每個 `ExamQuestionRecord`（依 `word` 分組，同一個字在同一次考試可能出現不只一次，要分別累加），把 `users/{uid}/wordStats/{word}` 的 `attempts`、`wrong` 用 Firestore 的 `increment()` 做原子累加（`attempts` 每次作答都 +1；`wrong` 只有在 `record.correct === false` 時 +1）；文件不存在時要能自動建立（`setDoc(..., { merge: true })` 搭配 `increment()` 即可）。
   - `wrongRate` 不建議存成欄位怕跟 `attempts`/`wrong` 不同步；改成在讀取顯示的頁面（任務 3）用 `attempts > 0 ? wrong / attempts : 0` 即時算出即可，`WordStat` 型別裡的 `wrongRate` 欄位可以保留但視為「顯示用的衍生值」，不必真的寫進 Firestore 文件。
   - 每個字各自累加即可，不需要用跨文件 transaction 保證多個字之間的原子性（`increment()` 本身對單一文件的單一欄位已經是原子操作，足夠這裡的需求）。

2. **成績歷史頁**：新增 `ExamHistoryPage`（路由例如 `/history`）
   - 讀取 `users/{uid}/examResults`，依 `date` 新到舊排序，列出：日期、模式（混合/純聽力）、頁數範圍、得分（score/questionCount）。
   - 每筆可以點進去看詳細逐題對錯（可以重用 `ExamResultPage` 的逐題清單呈現方式，或另外做一個簡化的詳細頁，你評估哪個實作量小就做哪個，不用兩種都做）。
   - 未登入時，這個頁面要顯示「登入後才能查看成績歷史」之類的提示，不要嘗試讀取 Firestore（`db` 沒有使用者資訊時不要發查詢）。

3. **單字錯誤率統計頁**：新增 `WordStatsPage`（路由例如 `/stats`）
   - 讀取 `users/{uid}/wordStats`，依錯誤率（`wrong/attempts`，`attempts` 為 0 的字不用顯示或排在最後）由高到低排序，列出：單字、錯誤率（百分比）、答錯次數/作答次數，每個字旁加 `SpeakButton`。
   - 未登入時同樣顯示「登入後才能查看單字統計」提示。

4. **入口**：在 `HomePage` 加入「成績歷史」「單字統計」兩個入口（可以做成兩個卡片，或跟現有「開始考試」卡片並列，你決定排版，維持現有頁面的視覺風格即可）。未登入時這兩個入口仍可以顯示，但點進去會看到上述「登入後才能查看」提示（不要整個隱藏入口，讓使用者知道有這個功能、需要登入才能用）。

5. `npm run lint`、`npm run build` 要過。

## 邊界（本切片不做）
- 不做錯題複習卷（S5，會重用 `wordStats` 排序結果出題，那是下一片的事）。
- 不做拼字填空題型、批次歷史/續作（M4）。
- 不改考試引擎本身（`src/services/exam.ts`、`ExamSetupPage`、`ExamRunPage`）的出題邏輯，只在 `ExamResultPage` 補寫入 `wordStats` 的部分。
- 不改路由選型（維持 `BrowserRouter`）、不改登入邏輯、不改 PWA/Service Worker 設定——這些都已經驗收通過，不要因為本切片而動到。

## 驗收（負責人操作）
1. 登入後考三次（可以是同一頁數範圍，讓同一批字重複出現，比較容易驗證累加有沒有生效）。
2. 進入「成績歷史」，看到三筆成績，日期新到舊排列，每筆看得出日期、模式、頁數範圍、得分。
3. 進入「單字統計」，看得到哪些字答錯比較多，錯誤率高的排在前面。
4. 未登入狀態下點「成績歷史」「單字統計」，看到「登入後才能查看」之類的提示，不會白畫面或報錯。
5. iPhone Safari、Android Chrome 各測一次（登入狀態下考一次、看兩個新頁面）。
6. `npm run lint`、`npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「等負責人驗收 S4，過了開 `BRIEF_S5_錯題複習卷.md`」。
2. 若有任何偏離本 BRIEF 的改動 → 記 `DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟（比照 S3 的白話驗收步驟風格）。
