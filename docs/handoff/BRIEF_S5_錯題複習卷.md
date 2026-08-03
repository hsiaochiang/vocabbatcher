# BRIEF_S5_錯題複習卷.md — M3 切片 5：錯題複習卷

> 交接合約：規劃層 → 執行層，2026-08-02。
> 對應需求：`REQUIREMENTS.md` R12。切片全景見 `STAGE_3_PLAN.md`。
> 前置：S1~S4 皆已驗收通過（含登入問題 S3b~S3f 四輪修復、S4 Firestore 安全規則修復）。
> 這是 M3「考試與追蹤」的最後一片，做完 M3 就全部完成。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 使用者在「單字統計」頁按「錯題複習」，系統依照累積錯誤率最高的單字，自動產生一份選擇題考卷。

## 現況（可直接重用）
- `src/services/exam.ts` 的 `generateExam()` 已能依候選單字池出題（4 選項、混合/純聽力模式）；`buildQuestion()` 內部邏輯可重用，只是候選池的篩選方式要換成「依錯誤率優先」而不是「依頁數範圍」。
- `src/pages/WordStatsPage.tsx` 已讀取並算好 `WordStat[]`（依 `wrongRate` 由高到低排序），本切片可以直接在這個頁面加按鈕，不用重新查一次 Firestore。
- `src/pages/ExamRunPage.tsx`、`ExamResultPage.tsx` 的 state 介面（`questions`、`minPage`、`maxPage`、`mode`）不用改介面本身，用既有的 `ExamQuestion[]` 格式帶過去即可。
- `AppContext` 的 `allWords: VocabEntry[]` 可用來把 `WordStat.word`（字串）對應回完整的 `VocabEntry`（含 `zh_definition`、`source_page` 等出題需要的欄位）。

## 任務

1. **出題邏輯**：在 `src/services/exam.ts` 新增一個函式（例如 `generateReviewExam(allWords, wordStats, questionCount)`），做法：
   - 篩出 `wordStats` 中 `wrong > 0` 的項目，依 `wrongRate`（或直接沿用呼叫端已排序好的順序）由高到低取前 N 個（N = `questionCount`，字數不足就取全部，比照 `generateExam` 現有「不足就取全部」的處理方式）。
   - 用這些字的 `word` 字串去 `allWords` 裡找到對應的完整 `VocabEntry`（找不到的字跳過，可能是單字庫更新過）。
   - 干擾選項（錯誤選項）一樣從整個 `allWords`（或至少扣掉本次已入選的字）隨機選，不要求干擾項也要是「錯題」。
   - 題型固定或隨機用 `mixed` 邏輯（中→英/英→中/聽力交互），不需要额外做「純聽力」的複習模式，除非你覺得順手加上也無妨（不強制）。
   - 這個函式獨立於 `generateExam`，可以抽取共用的 `buildQuestion`／`shuffle` 內部函式，不要複製貼上重複程式碼。

2. **入口與觸發**：在 `WordStatsPage.tsx` 加一個「錯題複習」按鈕（例如頁面頂部或底部固定按鈕，比照其他頁面現有的按鈕風格）。
   - 只有在使用者已登入、且 `wordStats` 裡至少有一筆 `wrong > 0` 的資料時才能按（沒有錯題資料時，按鈕可以顯示但disabled，或不顯示，你決定，只要清楚讓人知道「還沒有錯題可以複習」）。
   - 按下後呼叫 `generateReviewExam()`，拿到題目後導向 `/exam/run`，把結果用跟 `ExamSetupPage` 一樣的 state 格式（`questions`、`minPage`、`maxPage`、`mode`）帶過去；`minPage`/`maxPage` 可以用這次入選單字的 `source_page` 實際範圍算出（不用等於全書範圍）。
   - 若你覺得有必要讓使用者事後分辨「這次是不是錯題複習卷」（例如在結果頁/成績歷史多顯示一個標籤），可以在 `ExamResult`/`ExamResultState` 型別加一個可選欄位（例如 `source?: 'review'`），但這不是強制要求，簡單起見也可以不加，只要功能本身正確運作即可，不要為了這個小細節過度設計。

3. `npm run lint`、`npm run build` 要過。

## 邊界（本切片不做）
- 不做「複習卷專屬的設定頁」（頁數範圍、題數自訂）——直接按「錯題複習」就出題即可，題數可以固定一個合理預設值（例如跟 `ExamSetupPage` 一樣給 10 題，或跟目前錯題數量對齊，你決定即可，不用刻意做設定介面）。
- 不改考試作答頁 `ExamRunPage`、結果頁 `ExamResultPage` 的既有邏輯（除非任務 2 提到的可選標籤功能你決定要加，才做最小幅度調整）。
- 不改路由選型、登入邏輯、PWA 設定、Firestore 安全規則——這些都已經驗收通過，不要動到。

## 驗收（負責人操作）
1. 登入後先考幾次、故意答錯幾題，讓「單字統計」頁有錯誤率資料。
2. 進「單字統計」頁，按「錯題複習」。
3. 確認出現的考卷主要都是剛剛答錯過的字（不用 100% 全部是，但「大多是」剛剛錯過的字）。
4. 作答完畢，正常看到得分與結果頁，跟一般考試流程一樣。
5. 完全沒有錯題資料時（例如全新帳號沒考過），確認「錯題複習」按鈕行為合理（disabled 或有提示），不會讓使用者按下去卻得到空白或報錯的畫面。
6. iPhone Safari、Android Chrome 各測一次。
7. `npm run lint`、`npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：加一行本切片成果；標記 M3「考試與追蹤」全部五片（S1~S5）皆完成，「▶ 下一步」改為「等負責人驗收 S5，過了 M3 全部完成，可以規劃 M4」。
2. 若有偏離本 BRIEF 的改動 → 記 `DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟。
