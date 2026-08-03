# BRIEF_M4S1_拼字填空題型.md — M4 切片 1：拼字填空題型

> 交接合約：規劃層 → 執行層，2026-08-03。
> 對應 `docs/roadmap.md` M3 驗收標準「四題型：中→英、英→中、拼字填空、聽音選字」中唯一還沒做的一種；也是 `REQUIREMENTS.md` R6 的落地。
> 切片全景見 `docs/planning/STAGE_4_PLAN.md`（M4-S1，無相依，可獨立開工）。M4-S2（批次頁面收斂）依賴這片完成後，考試設定頁才有「拼字填空」可選。

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 考試（混合模式）作答時，除了原有的選擇題與聽力選字，會出現「看中文意思、打字拼出英文單字」的題目，並正確判分。

## 現況（可直接重用）
- `src/services/exam.ts` 目前有 `QUESTION_TYPES = ['zh_to_en', 'en_to_zh', 'listening']`（第 63 行），`generateExam()`／`generateReviewExam()` 都是從這個陣列隨機挑題型，混合模式（`mode: 'mixed'`）才會隨機挑，`listening` 模式固定只出聽力題。
- `buildQuestion(word, type, pool)`（第 42~61 行）目前所有題型都走「4 選項單選」的邏輯（`options: string[]` + `correctIndex: number`），拼字填空不是選擇題，這個函式需要能分流處理。
- `src/types/exam.ts` 的 `QuestionType`（第 1 行）、`ExamQuestionRecord`（第 3~7 行，含 `correct: boolean`）是共用型別，新增 `'spelling'` 這個 type 值即可，`ExamQuestionRecord` 結構不用改。
- `src/pages/ExamRunPage.tsx` 目前的作答 UI 是清一色的選項按鈕列表（第 110~151 行），`handleSelect(optionIndex)` 選完就 `setAnswered(true)`；拼字填空要換成文字輸入框 + 「送出答案」按鈕，判定邏輯要另外處理（不是比對 index，是比對輸入文字）。
- `src/pages/ExamResultPage.tsx`、`WordStatsPage.tsx` 都是靠 `ExamQuestionRecord.correct`（布林值）統計對錯，不吃 `options`／`correctIndex`，所以拼字填空只要正確寫入 `correct: boolean` 到 record，結果頁與統計頁不用改。

## 任務

1. **型別調整**：`src/types/exam.ts` 的 `QuestionType` 加入 `'spelling'`。

2. **出題邏輯（`src/services/exam.ts`）**：
   - `QUESTION_TYPES` 陣列加入 `'spelling'`，變成 `['zh_to_en', 'en_to_zh', 'listening', 'spelling']`；混合模式（`generateExam` 的 `mode === 'mixed'` 分支、`generateReviewExam`）隨機挑題型時自然就會抽到，不用額外寫機率邏輯。`mode === 'listening'` 這個分支維持固定回傳 `'listening'`，不受影響。
   - `ExamQuestion` 介面（第 6~11 行）目前 `options`／`correctIndex` 是必填，拼字填空不需要 4 選項，改成：`options` 允許空陣列 `[]`、`correctIndex` 可以固定填 `-1`（不使用），另外新增一個可選欄位 `correctAnswer?: string`，拼字填空題填入正確答案（`word.word`，即單字本身）。選擇題／聽力題不用填這個欄位。
   - `buildQuestion()` 內部依 `type` 分流：`type === 'spelling'` 時不呼叫 `pickDistractors`（不需要干擾選項），直接回傳 `{ word, type, options: [], correctIndex: -1, correctAnswer: word.word }`；其餘型別維持原本 4 選項邏輯不變。
   - 拼字填空判分規則（大小寫不敏感、去頭尾空白）寫成一個獨立、可匯出的函式，例如 `export function isSpellingCorrect(input: string, answer: string): boolean { return input.trim().toLowerCase() === answer.trim().toLowerCase(); }`，放在 `exam.ts` 裡靠近 `buildQuestion` 的位置。**這是本切片唯一寫判分邏輯的地方**，`ExamRunPage.tsx` 判分時要 import 這個函式來用，不要在頁面元件裡自己重寫一次比對邏輯（未來若有其他地方要判斷拼字對錯——例如複習卷或別的題型變體——都要重用這個函式，不得各自複製）。

3. **作答 UI（`src/pages/ExamRunPage.tsx`）**：
   - 目前 `question.type === 'listening'` / `'zh_to_en'` / 其餘 三分支決定題目呈現方式（第 89~107 行）與 `questionLabel`（第 70~75 行），這裡要加第四種：`type === 'spelling'` 時，題目卡片顯示 `question.word.zh_definition`（比照 `zh_to_en` 的呈現，因為都是「看中文猜英文」的方向），`questionLabel` 改成類似「請拼出正確的英文單字」。
   - 下方作答區（第 110~151 行的選項按鈕列表）在 `type === 'spelling'` 時要整組換成：一個文字輸入框（`<input type="text">`，用既有 Tailwind 風格比照其他輸入框樣式，注意 touch target 高度不要小於 44dp）+ 送出按鈕（或沿用底部固定的「下一題」按鈕改當送出鍵，兩種做法你選一種較不重工的）。使用者打字送出後，用 `isSpellingCorrect()` 判斷對錯，比照原本 `handleSelect` 的行為切到「已作答」狀態（`setAnswered(true)`），並且要讓使用者看到「答對了 / 正解是 XXX」的回饋（參考現有選擇題答錯時「正確答案標綠、選錯的標紅」的視覺邏輯，拼字題至少要清楚顯示正確拼法，讓使用者知道自己哪裡錯）。
   - `handleNext()`（第 50~68 行）寫入 `records` 時，`correct` 欄位對拼字題要用 `isSpellingCorrect()` 的結果，不是 `selected === question.correctIndex`（拼字題 `correctIndex` 固定是 -1，不能拿來比）。這裡建議把「本題是否正確」抽成一個小函式或 state（例如加一個 `isCorrect: boolean` state，在送出當下就算好，`handleSelect`／拼字送出都寫入同一個 state），`handleNext()` 統一讀這個 state 寫入 record，不要各自判斷一次。
   - 手機鍵盤：`<input>` 建議加 `autoCapitalize="off"` `autoCorrect="off"` `spellCheck={false}`，避免手機自動大寫首字母或自動更正干擾拼字作答（不影響判分，因為判分本身不分大小寫，但會讓使用者體驗更好、不會誤以為輸入被竄改）。

4. `npm run lint`、`npm run build` 要過。

## 邊界（本切片不做）
- 不改考試設定頁 `ExamSetupPage.tsx` 的模式選擇 UI（`mixed`／`listening` 兩個既有選項不變，拼字題只在 `mixed` 模式下才可能出現，這是自然結果，不用特別加開關）。
- 不改 `ExamResultPage.tsx`、`WordStatsPage.tsx`——這兩頁只讀 `ExamQuestionRecord.correct`，本切片產生的 record 格式跟既有的相容，不需要跟著改。
- 不動路由選型（`BrowserRouter`，絕對不要改回 `HashRouter`，這是 S3e 花了一整輪診斷才修好的登入根因）、不動 `vite.config.ts` 的 Workbox `navigateFallbackDenylist`（S3f 修好的登入攔截問題）、不動 Firestore 安全規則（S4 修好的鎖死問題，本切片不涉及新的 Firestore 讀寫，不需要碰規則）。
- 不做「拼字題專屬統計」（例如額外區分拼字題錯誤率跟選擇題錯誤率），沿用現有 `WordStat` 的統計方式即可，不用擴充欄位。

## 驗收（負責人操作）
1. 進「開始考試」，選「混合模式」（不是純聽力模式），設定好頁數範圍後開始作答。
2. 多作答幾題，確認會出現「請拼出正確的英文單字」這種題目，畫面顯示中文意思，下方是可以打字的輸入框。
3. 故意打對一次、打錯一次（含刻意打大寫或前後多打空白），確認：
   - 拼對（不論大小寫、前後空白）都判定答對。
   - 拼錯會清楚顯示正確答案是什麼。
4. 確認拼字題跟原本的選擇題、聽力題會混在同一份考卷裡交錯出現，不是全部都變成拼字題。
5. 考完看結果頁與「單字統計」頁，確認拼字題的對錯有正確計入成績與統計（不會顯示異常或缺漏）。
6. iPhone Safari、Android Chrome 各測一次，確認手機鍵盤打字順暢、輸入框不會太小點不到。
7. `npm run lint`、`npm run build` 通過。

## 收工指令（執行層收工必做）
1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「M4-S1 待負責人驗收，過了可以開 M4-S2（批次頁面收斂）」。
2. 若有任何偏離本 BRIEF 的改動 → 記 `docs/planning/DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟。
4. **完成以上所有事項、且 `npm run lint`／`npm run build` 都通過後，將本次變更 commit 並 push 到遠端（`origin main`）。** commit message 用一句話講清楚這片做了什麼（例如「功能: 新增拼字填空題型」），照專案既有的 commit message 慣例（可以 `git log` 看最近幾筆的風格）。push 前務必確認 `git status` 沒有不該提交的檔案（例如暫時性的除錯輸出）。
