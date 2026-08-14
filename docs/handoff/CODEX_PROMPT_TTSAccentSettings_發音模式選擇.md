請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_TTSAccentSettings_發音模式選擇.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡。
2. 工作目錄為 `exam-vocab-batcher/`（App 本體）。
3. 重點任務：
   - 新增 `exam-vocab-batcher/src/services/ttsPreferences.ts`：`getAccent()`/`setAccent()`（`'en-US' | 'en-GB'`，localStorage 存，預設 `'en-US'`）、`getPreferHighQuality()`/`setPreferHighQuality()`（boolean，localStorage 存，**預設 false，這是刻意的決定，不要改成預設開啟**）。**不要放進 `AppContext`**——`tts.ts` 是純函式模組沒有 React context，且很多呼叫點（`FlashCardPage.tsx:88,173`、`ExamRunPage.tsx:111`、`StoryPage.tsx:73`）直接呼叫 `speakEn`/`speakZh`，完全跳過 `SpeakButton` 元件，所以偏好設定必須讓 `tts.ts` 內部自己讀 localStorage，不能靠 props 往下傳，這樣才能保證全部呼叫點自動套用最新設定。
   - 修改 `exam-vocab-batcher/src/services/tts.ts`：新增 `getVoicesAsync()`（處理 `speechSynthesis.getVoices()` 可能回傳空陣列、要等 `voiceschanged` 事件的怪癖，加時間上限如300ms保底）；`speakEn` 依 `getAccent()` 選語言、在語音清單裡找符合的語音（`preferHighQuality` 開啟時優先選 `localService === false` 的），找不到符合語言的就退而求其次找任何 `en-*` 開頭的語音，再找不到就維持現況只設 `lang` 不指定 `voice`——**不能靜默失敗，一定要有聲音播出來**。`speakEn` 對外簽名維持 `speakEn(word: string): void`，呼叫端不用改。**iOS Safari 的「必須使用者點擊觸發」限制要特別注意**，如果有裝置可測就實測，沒有的話要在報告裡明講沒有實機驗證這項風險。
   - 新增 `exam-vocab-batcher/src/pages/SettingsPage.tsx`，路由 `/settings`：美式/英式二選一 + 「測試發音」按鈕（呼叫 `speakEn('hello')`）+ 「優先使用高品質語音（需要網路）」開關（預設關閉，附一行 iPad 可能沒效果的說明文字）+ 頁面載入時偵測裝置有沒有 `en-GB` 語音，沒有的話英式選項要提示或停用。
   - `App.tsx` 新增 `/settings` 路由；`HomePage.tsx` 的 `Header` `rightSlot` 加一個設定圖示入口（跟現有 `<UserBadge />` 並排，不要取代它）。
4. 邊界（不要碰）：不改任何目前呼叫 `speakEn`/`speakZh`/`SpeakButton` 的頁面元件（偏好設定是 `tts.ts` 內部自己讀取，呼叫介面不變）；不處理 `ipa_uk` 音標文字顯示；不做美式/英式以外的口音；不改 `App.tsx` 的 `BrowserRouter`/`basename`（2026-08-13 才修好的部署 bug）；不改 `vite.config.ts` 的 PWA 快取規則（這片不涉及新資料檔）；「優先高品質語音」預設必須是關閉。
5. `npm run lint`、`npm run build` 要過。
6. **Playwright 自我驗證**：`/settings` 頁切換美式/英式、點測試發音、開關高品質語音都不報錯；重新整理確認設定有持久化；從批次頁進翻牌卡或故事模式點發音按鈕不報錯（測功能沒壞掉，不用驗證實際語音品質）。
7. 若有偏離本 BRIEF 的改動 → 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
8. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果，「▶ 下一步」改為「發音模式選擇待負責人實機驗收（尤其 iPad 上的使用者點擊觸發限制與高品質語音開關效果）」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建 REPORT_TTSAccentSettings_發音模式選擇.md，內容依這個格式寫：

```markdown
# REPORT_TTSAccentSettings_發音模式選擇 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<逐項對應 BRIEF 的任務，具體改了哪些檔案>

## Playwright 自我驗證結果
<驗證了什麼、截圖有沒有留、結果如何>

## iOS Safari 使用者點擊觸發風險
<有沒有實機/模擬器驗證？結果如何？如果沒驗證，明講沒驗證，不要假設沒問題>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## lint / build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit（不用 push）

寫完報告檔後，確認 `npm run lint`、`npm run build` 都通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案，然後 `git add` 這次改動的檔案，`git commit`（commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫）。**這次不用 `git push`**，等負責人實機驗收過再由規劃層決定要不要部署。

完成 commit 後，這次工作才算真正結束，不用再額外輸出總結。
