請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_M4S1_拼字填空題型.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡。
2. 工作目錄是 exam-vocab-batcher/。
3. 重點任務：
   - `src/types/exam.ts` 的 `QuestionType` 加入 `'spelling'`。
   - `src/services/exam.ts`：`QUESTION_TYPES` 加入 `'spelling'`；`ExamQuestion` 介面新增可選欄位 `correctAnswer?: string`；`buildQuestion()` 對 `spelling` 型別不挑干擾選項、直接回傳 `correctAnswer: word.word`；新增可匯出的 `isSpellingCorrect(input, answer)` 判分函式（大小寫不敏感、去頭尾空白）——這是唯一寫判分邏輯的地方，其他地方不得重複實作。
   - `src/pages/ExamRunPage.tsx`：`spelling` 題型顯示中文意思＋文字輸入框作答（取代選項按鈕列表），送出後用 `isSpellingCorrect()` 判斷對錯並給視覺回饋（顯示正確拼法），`handleNext()` 寫入 record 時要用這個判斷結果，不能沿用 `selected === question.correctIndex`（拼字題 correctIndex 固定 -1）。
4. 邊界（不要碰）：`ExamSetupPage.tsx` 模式選擇 UI、`ExamResultPage.tsx`、`WordStatsPage.tsx` 都不用改；不要把路由改回 `HashRouter`；不要動 `vite.config.ts` 的 Workbox `navigateFallbackDenylist`；不要動 Firestore 安全規則。
5. `npm run lint`、`npm run build` 要過。
6. 若有偏離本 BRIEF 的改動 → 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
7. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果，「▶ 下一步」改為「M4-S1 待負責人驗收，過了可以開 M4-S2」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建（或覆寫）REPORT_M4S1_拼字填空題型.md，內容依這個格式寫：

```markdown
# REPORT_M4S1_拼字填空題型 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<逐項對應 BRIEF 的任務：QuestionType 型別、exam.ts 的出題與判分邏輯、ExamRunPage.tsx 的作答 UI 改動>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit 並 push

寫完報告檔後，確認 `npm run lint`、`npm run build` 都通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案，然後：

1. `git add` 這次改動的檔案（含 `docs/handoff/REPORT_M4S1_拼字填空題型.md`、`docs/planning/PROGRESS.md`，若有動 `DECISIONS.md` 也一併加入）。
2. `git commit`，commit message 用一句話講清楚這片做了什麼（例如「功能: 新增拼字填空題型」），可以先 `git log --oneline -10` 看最近幾筆訊息的風格再照著寫。
3. `git push` 到 `origin main`。
4. push 完成後在報告檔（或對負責人的回覆）中註明 commit hash 與 push 是否成功；若 push 失敗（例如遠端有新 commit、需要先 pull），不要用 force push，把卡住的狀況寫清楚讓規劃層或負責人決定怎麼處理。

完成 commit 並 push（或記錄清楚卡住原因）後，這次工作才算真正結束，不用再額外輸出總結。
