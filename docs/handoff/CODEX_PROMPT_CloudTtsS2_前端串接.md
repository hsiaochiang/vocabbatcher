請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_CloudTtsS2_前端串接.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡，並讀 D:\program\vocabbatcher\docs\handoff\REPORT_CloudTtsS1_後端Function.md 了解已部署的 `synthesizeSpeech` Cloud Function 的輸入輸出格式（`{text, lang}` → `{audioBase64}`，region `us-central1`）。
2. 工作目錄為 `exam-vocab-batcher/`。**不碰 `functions/` 底下任何檔案**，後端已在切片1完成並驗證通過。
3. 重點任務：
   - `exam-vocab-batcher/src/services/ttsPreferences.ts` 新增 `getUseCloudTts()`/`setUseCloudTts()`（localStorage，**預設 false**）。
   - `exam-vocab-batcher/src/services/firebase.ts` 新增 `export const functions = app ? getFunctions(app, 'us-central1') : null;`（`getFunctions` 來自 `firebase/functions`），沿用既有 `firebaseEnabled`/`app` 降級模式。
   - `exam-vocab-batcher/src/services/tts.ts` 的 `speakEn` 開頭新增雲端語音分支：`getUseCloudTts()` 為真且 `functions` 非 null 時，呼叫 `httpsCallable(functions, 'synthesizeSpeech')({ text: word, lang: getAccent() })`，設定5~8秒逾時，成功則把 `audioBase64` 轉成可播放音檔播放；**任何失敗（拋錯/逾時/functions為null）都要自動退回現有 Web Speech API 邏輯，絕對不能完全沒聲音**。可加 `localStorage` 瀏覽器端快取（key 如 `${lang}::${word}`）減少重複呼叫，非強制但建議做。`speakEn` 對外簽名維持不變，`speakZh` 不動。
   - `exam-vocab-batcher/src/pages/SettingsPage.tsx` 把「優先使用高品質語音」跟新的「Google 雲端語音」**整理成互斥的三選一**（裝置預設語音／優先高品質裝置語音／Google雲端語音），不要做成兩個可能同時開啟的獨立開關；美式/英式選擇器保留不動。底層仍是兩個獨立布林值沒關係，只是 UI 上做成單選。
4. 邊界（不要碰）：不改 `functions/`；不做 Firestore 快取（切片3的事，這片頂多做瀏覽器端 localStorage 快取）；不改 `App.tsx` 的 `BrowserRouter`/`basename`（2026-08-13 修好的部署bug）；不改 `AppContext.tsx` 的 `setSource()`（2026-08-13 修好的卡住bug）；`speakZh` 不動；固定三選一，不要加更多模式。
5. `npm run lint`、`npm run build` 要過。
6. **Playwright 自我驗證**：`/settings` 切換三個模式點測試發音不報錯（雲端語音在測試環境失敗是預期的，只要確認有自動退回、不整頁報錯即可）；重新整理確認持久化；批次頁翻牌卡/故事模式發音按鈕不報錯。
7. **這片核心風險是 iOS Safari 上「等網路回應後才播放」是否還算在使用者點擊觸發的範圍內**，這個一定要規劃層/負責人在真實 iPhone 上測，你不用自己想辦法測 iPhone，但如果方便的話可以在報告裡建議怎麼讓負責人快速測到（例如提示可以用預覽頻道部署）。
8. 若有偏離本 BRIEF 的改動（尤其逾時秒數、快取要不要做、UI 呈現方式）→ 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
9. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果，「▶ 下一步」改為「Google Cloud TTS 切片2（前端串接）已完成待負責人 iPhone 實機驗收，通過後開切片3（Firestore 快取層）」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建 REPORT_CloudTtsS2_前端串接.md，內容依這個格式寫：

```markdown
# REPORT_CloudTtsS2_前端串接 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<逐項對應 BRIEF 的任務，具體改了哪些檔案>

## Playwright 自我驗證結果
<驗證了什麼、截圖有沒有留、結果如何>

## iOS Safari 風險（尚待負責人 iPhone 實測）
<你有沒有辦法提供更方便的測試方式（例如預覽頻道）>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## lint / build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟，明確標出哪些一定要在 iPhone 上測。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit（不用 push）

寫完報告檔後，確認 `npm run lint`、`npm run build` 都通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案，然後 `git add` 這次改動的檔案，`git commit`（commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫）。**這次不用 `git push`**，等 iPhone 實測通過再由規劃層決定要不要部署。

完成 commit 後，這次工作才算真正結束，不用再額外輸出總結。
