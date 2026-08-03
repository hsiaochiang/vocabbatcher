# REPORT_M4S1_拼字填空題型 — 執行結果

- 執行時間：2026-08-03 16:16 +08:00
- 狀態：完成

## 改了什麼

- `src/types/exam.ts`：`QuestionType` 加入 `spelling`。
- `src/services/exam.ts`：`QUESTION_TYPES` 加入 `spelling`；`ExamQuestion` 新增可選 `correctAnswer`；`buildQuestion()` 對拼字題回傳 `options: []`、`correctIndex: -1`、`correctAnswer: word.word`，不再挑干擾選項；新增並匯出 `isSpellingCorrect(input, answer)`，集中處理大小寫不敏感與去頭尾空白的拼字判分。
- `src/pages/ExamRunPage.tsx`：拼字題顯示中文意思、輸入框與「送出答案」按鈕；送出後呼叫 `isSpellingCorrect()` 判分，顯示答對/拼錯與正確拼法；`handleNext()` 改讀本題已算好的 `answerCorrect` 寫入 record，避免拼字題沿用 `correctIndex`。
- `src/pages/ExamResultPage.tsx`、`src/pages/ExamHistoryPage.tsx`：補上 `spelling: '拼字'` 題型標籤，讓新增型別後 build 與結果顯示都正常；沒有改成績儲存或統計邏輯。

## 是否偏離 BRIEF

有。BRIEF 原本說不用改 `ExamResultPage.tsx`，但新增 `spelling` 型別後，結果頁與成績歷史的題型標籤必須補齊，否則 TypeScript build 會失敗或畫面無法正確顯示題型名稱。已記錄在 `docs/planning/DECISIONS.md` 的「2026-08-03　M4-S1 相容修正：結果頁與歷史頁補上拼字題型標籤」。

## npm run lint / npm run build 結果

- `npm.cmd run lint`：通過
- `npm.cmd run build`：通過

## ★ 負責人驗收步驟（白話、按順序）

1. 打開 App，進「開始考試」。
2. 選「混合模式」，不要選「純聽力」。
3. 設定頁數範圍與題數後，按「開始考試」。
4. 多做幾題，看到「請拼出正確的英文單字」時，確認畫面上方是中文意思，下方是可以打字的輸入框。
5. 遇到拼字題時，故意輸入正確答案一次；可以試著把字母改成大寫，或前後多打一兩個空白，確認仍會判定答對。
6. 再遇到拼字題時，故意拼錯一次，確認畫面會顯示「拼錯了」以及「正確拼法」。
7. 確認同一份混合模式考卷裡，拼字題會和原本的選擇題、聽力題交錯出現，不是整份考卷都變成拼字題。
8. 考完後看結果頁，確認分數與每題對錯正常顯示，拼字題會標成「拼字」。
9. 若有登入，再進「單字統計」確認剛剛拼字題的對錯有算進統計，畫面不要出現空白或錯誤。
10. 用 iPhone Safari 與 Android Chrome 各測一次，確認拼字輸入框點得到、手機鍵盤輸入順暢。

## 遇到的問題 / 卡住的地方（若有）

沒有未解決卡點。既有 Playwright e2e 會覆寫 UIUX 截圖，為避免產生與本切片無關的圖片差異，本次依 BRIEF 執行 `npm.cmd run lint` 與 `npm.cmd run build` 驗證。
