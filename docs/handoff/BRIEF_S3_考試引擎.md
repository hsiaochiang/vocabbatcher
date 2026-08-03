# BRIEF_S3_考試引擎.md — M3 切片 3：考試引擎

> 交接合約：規劃層 → 執行層，2026-07-31。
> 對應需求：`REQUIREMENTS.md` R10。切片全景見 `STAGE_3_PLAN.md`。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀本 BRIEF 全文；工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 使用者能設定頁數範圍與題數，考一份中→英/英→中交互出題、含聽力題的選擇題考卷，逐題作答後看到得分與逐題對錯。

## 現況（S1、S2 已完成，可直接重用）
- `src/services/tts.ts`：`speakEn` / `speakZh`。
- `src/components/SpeakButton.tsx`：可重用發音按鈕。
- `src/services/auth.ts` / `src/services/firebase.ts`：登入狀態、Firestore 存取（`db`、`onAuthStateChange`）。
- `src/types/exam.ts`：已定義 `ExamResult`、`ExamQuestionRecord`、`QuestionType`、`WordStat` 型別。
- `src/types/vocab.ts` 的 `VocabEntry` 有 `source_page: number[]`，可依此篩選頁數範圍。
- `AppContext` 的 `allWords: VocabEntry[]` 已載入全部單字庫。

## 資料模型澄清（本 BRIEF 對 STAGE_3_PLAN.md 的補充說明，請以此為準）
- `users/{uid}/examResults/{examId}` 的**原始寫入**由本切片（S3）負責：使用者登入且考完一次考試時，寫入一筆完整的 `ExamResult` 文件（日期、模式、頁數範圍、題數、得分、逐題紀錄）。
- `users/{uid}/wordStats/{word}` 的**累積統計**（attempts/wrong/wrongRate 加總、成績歷史頁、錯誤率排序頁）留給 **S4** 處理，本切片不做。
- 未登入使用者：可以正常考試，但畫面需提示「訪客模式，成績不會保存」，且不寫入 Firestore（`db` 為 null 或使用者未登入時直接略過寫入）。

## 任務

1. **出題引擎**：新增 `src/services/exam.ts`
   - `generateExam(allWords, options)`：輸入頁數範圍 `[minPage, maxPage]`、題數、模式（`'mixed' | 'listening'`），從 `allWords` 篩出 `source_page` 落在範圍內的單字，去重後隨機抽取（若可用單字數小於題數，取全部並回傳實際題數）。
   - 每題隨機決定 `QuestionType`：`mixed` 模式從 `zh_to_en` / `en_to_zh` / `listening` 交互出題；`listening` 模式全部為 `listening`。
   - 每題產生 4 個選項（1 正確 + 3 干擾項，從候選池隨機選，避免與正確答案重複）。
   - 此檔案供 **S5** 重用（僅需替換候選字池為高錯誤率優先），介面設計時保留彈性。

2. **考試設定頁**：新增 `ExamSetupPage`（路由 `/exam`）
   - 輸入頁數範圍（最小頁~最大頁，可由 `allWords` 的 `source_page` 算出全域範圍當預設上下限）。
   - 輸入題數（例如 5/10/20 快速選項 + 自訂）。
   - 選擇模式：混合（中英交互＋聽力）／純聽力。
   - 按「開始考試」導向作答頁，把 `generateExam()` 的結果透過 route state 或暫存 context 帶過去。

3. **作答頁**：新增 `ExamRunPage`（路由 `/exam/run`）
   - 逐題顯示：`zh_to_en`（顯示中文，4 個英文選項）、`en_to_zh`（顯示英文單字，4 個中文選項）、`listening`（顯示播放按鈕唸英文，4 個中文選項；可重複播放）。
   - 聽力題發音一律呼叫 `speakEn()`（經 `tts.ts`），不得另建 `SpeechSynthesisUtterance`。
   - 使用者選答後標記對/錯並記錄，進下一題；全部作答完畢導向結果頁。

4. **結果頁**：新增 `ExamResultPage`（路由 `/exam/result`）
   - 顯示總分（答對題數/總題數）與逐題清單（單字、題型、對/錯），每個單字旁加 `SpeakButton`（重用 S1）。
   - 若使用者**已登入**：呼叫 Firestore，在 `users/{uid}/examResults/{examId}` 寫入一筆 `ExamResult`。
   - 若使用者**未登入**：畫面上明顯提示「訪客模式，成績不會保存」，不寫入 Firestore。

5. **入口**：在 `HomePage` 加入「開始考試」按鈕/入口，導向 `/exam`。

## 邊界（本切片不做）
- 不做拼字填空題型（M4）。
- 不做成績歷史頁、累積錯誤率統計頁（S4）。
- 不做錯題複習卷（S5）。
- 不做 `wordStats` 的累加寫入（S4）。

## 驗收（負責人操作）
1. 開「開始考試」，選第 10~20 頁、10 題、混合模式，作答完畢後看到分數與逐題對錯清單；題型有中英交錯出現。
2. 聽力題會播放英文發音，可重複點擊重播；選項是中文。
3. 未登入狀態下也能完整考完一次，畫面有「成績不會保存」提示。
4. 已登入狀態下考完一次，不出現任何錯誤（Firestore 寫入成功，不需負責人自行查看 Firestore 後台）。
5. iPhone Safari、iPad Safari、Android Chrome 三平台皆能正常作答與播放聽力題。
6. `npm run lint` 與 `npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「等負責人驗收 S3，過了開 `BRIEF_S4_成績統計.md`」。
2. 若有任何偏離本 BRIEF 的改動 → 記 `DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟。
