# REPORT_CloudTtsS2_前端串接 — 執行結果

- 執行時間：2026-08-14
- 狀態：完成，待負責人 iPhone 實機驗收

## 改了什麼

- `exam-vocab-batcher/src/services/ttsPreferences.ts` 新增 `getUseCloudTts()` / `setUseCloudTts()`，用 `localStorage` 儲存「Google 雲端語音」偏好，預設關閉。
- `exam-vocab-batcher/src/services/firebase.ts` 新增 `functions = app ? getFunctions(app, 'us-central1') : null`，沿用既有 Firebase 未設定時安全降級的 pattern。
- `exam-vocab-batcher/src/services/tts.ts` 的 `speakEn(word: string): void` 對外介面維持不變：
  - 使用者選「Google 雲端語音」且 Firebase Functions 可用時，呼叫 `synthesizeSpeech` callable function。
  - 呼叫參數為 `{ text: word, lang: getAccent() }`，支援 `en-US` / `en-GB`。
  - 雲端呼叫逾時設定為 7 秒。
  - 成功時用 MP3 base64 建立 `Audio` 播放。
  - 任何失敗、逾時、回傳格式異常、文字超過 200 字，都自動退回原本 Web Speech API 發音。
  - 新增瀏覽器端 `localStorage` 快取，key 含口音與文字；同一台裝置同一個字第二次播放會先讀快取。
- `exam-vocab-batcher/src/pages/SettingsPage.tsx` 保留美式 / 英式口音選擇，將原本「優先使用高品質語音」開關改成互斥三選一：
  - 裝置預設語音
  - 優先高品質裝置語音
  - Google 雲端語音（最準，需要網路）
- `exam-vocab-batcher/e2e/tts-accent-settings.spec.ts` 更新為三選一驗證，並新增雲端失敗時退回裝置語音的測試；故事模式與翻牌卡既有發音按鈕都納入驗證。
- 更新 / 新增本切片 Playwright 截圖：
  - `exam-vocab-batcher/e2e/screenshots/tts-settings-persisted.png`
  - `exam-vocab-batcher/e2e/screenshots/tts-story-button-after-settings.png`
  - `exam-vocab-batcher/e2e/screenshots/tts-flashcard-button-after-settings.png`

## Playwright 自我驗證結果

- `npx.cmd playwright test tts-accent-settings.spec.ts`：3 passed。
- `npm.cmd run test:e2e`：16 passed。

驗證內容：
- 進 `/settings`，切換美式 / 英式口音。
- 切換三種發音引擎，點「測試發音」沒有 JS 錯誤。
- 測試環境攔截雲端 Function 呼叫並使其失敗，確認會自動退回 Web Speech mock，沒有整頁報錯或卡死。
- 重新整理後，英式口音與 Google 雲端語音選擇仍保留。
- 從學測第 16 頁故事模式點既有發音按鈕，不報錯且退回裝置英文語音。
- 從學測第 16 頁翻牌卡點既有發音按鈕，不報錯且退回裝置英文語音。

## lint / build 結果

- `npm.cmd run lint`：通過。
- `npm.cmd run build`：通過。Vite 仍有既有 chunk size warning，未影響 build。

## 是否偏離 BRIEF

無。

補充：
- 逾時秒數採 7 秒，符合 BRIEF 建議的 5~8 秒範圍。
- 有實作 BRIEF 建議的瀏覽器端 `localStorage` 快取。
- 未修改 `functions/`。
- 未修改 `App.tsx` 的 `BrowserRouter` / `basename`。
- 未修改 `AppContext.tsx` 的 `setSource()`。
- `speakZh()` 保持原樣。

## iPhone 實機驗收風險

本機與 Playwright 只能確認流程不報錯、偏好有保存、雲端失敗會退回裝置語音；不能證明 iPhone Safari 真的會在「點擊後等待網路回應再播放」的情境下允許發聲。

這片一定要請負責人在真實 iPhone 上驗收：
1. 進「發音設定」頁，選「Google 雲端語音」。
2. 點「測試發音」，確認真的有聲音。
3. 選美式 / 英式各測一次，確認口音設定仍生效。
4. 進任一批次的翻牌卡，點英文發音按鈕，確認有聲音。
5. 進故事模式，點句子或單字發音按鈕，確認有聲音。
6. 開飛航模式或斷網，再點發音按鈕，確認會退回裝置預設發音，不會完全沒反應。
7. 重新整理頁面後回設定頁，確認「Google 雲端語音」選項還在。

建議驗收方式：先由規劃層部署 Firebase Hosting preview channel，讓負責人用 iPhone Safari 直接測；通過後再決定是否進切片3（Firestore 快取層）或正式部署。

## 遇到的問題 / 卡住的地方（若有）

- 沒有產品實作阻塞。
- `npx.cmd playwright test e2e\tts-accent-settings.spec.ts` 第一次因 Playwright 檔名參數未匹配到測試檔而回報 `No tests found`；改用 `npx.cmd playwright test tts-accent-settings.spec.ts` 後正常執行並通過。
- 本機無法驗證 iPhone Safari 的實際播放限制，需負責人實機驗收。
