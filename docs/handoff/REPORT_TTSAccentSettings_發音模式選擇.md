# REPORT_TTSAccentSettings_發音模式選擇 — 執行結果

- 執行時間：2026-08-14
- 狀態：完成，待負責人實機驗收

## 改了什麼

- 新增 `exam-vocab-batcher/src/services/ttsPreferences.ts`：儲存 `en-US` / `en-GB` 發音模式與「優先使用高品質語音」偏好；預設美式，且高品質語音預設關閉。
- 修改 `exam-vocab-batcher/src/services/tts.ts`：新增 `getVoicesAsync()`，處理 `speechSynthesis.getVoices()` 初次可能為空的狀況；`speakEn()` 維持原本 `speakEn(word: string): void` 介面，但內部會讀取偏好並挑選符合口音的 `SpeechSynthesisVoice`。找不到指定口音時會退回任何英文語音，再不行就只設定 `lang` 照常播放。
- 新增 `exam-vocab-batcher/src/pages/SettingsPage.tsx`：提供「美式發音 / 英式發音」二選一、「測試發音」按鈕、「優先使用高品質語音」開關，並在頁面載入時偵測裝置是否有 `en-GB` 語音；沒有偵測到時會停用英式選項並提示。
- 修改 `exam-vocab-batcher/src/App.tsx`：新增 `/settings` 路由，未改 `BrowserRouter` / `basename`。
- 修改 `exam-vocab-batcher/src/pages/HomePage.tsx`：首頁右上角新增設定圖示入口，和原本的 Google 登入元件並排。
- 新增 `exam-vocab-batcher/e2e/tts-accent-settings.spec.ts`：驗證設定頁與既有故事模式發音按鈕。
- 更新首頁相關既有截圖，並新增兩張本切片驗證截圖。

## Playwright 自我驗證結果

- `npx.cmd playwright test tts-accent-settings`：2 passed。
- `npm.cmd run test:e2e`：15 passed。

驗證內容：
- 從首頁右上角進 `/settings`。
- 切換美式 / 英式發音，點「測試發音」沒有 JS 錯誤。
- 開啟「優先使用高品質語音」沒有 JS 錯誤。
- 重新整理後，英式發音與高品質語音設定仍保留。
- 套用設定後，從學測第 16 頁故事模式點既有發音按鈕沒有 JS 錯誤，且 mock 語音可確認走到 `en-GB` 與高品質語音選擇邏輯。

截圖：
- `exam-vocab-batcher/e2e/screenshots/tts-settings-persisted.png`
- `exam-vocab-batcher/e2e/screenshots/tts-story-button-after-settings.png`

## iOS Safari 使用者點擊觸發風險

本次沒有 iPad / iPhone 實機或模擬器可驗證。

這片的 `speakEn()` 內部會等待 `getVoicesAsync()` 後才呼叫 `speechSynthesis.speak()`；桌機 Chromium 的 Playwright 驗證通過，但 iOS Safari 對「必須由使用者點擊直接觸發語音」的限制比較嚴格，仍需負責人在 iPad / iPhone 上實測：
- 設定頁「測試發音」是否能發聲。
- 翻牌卡 / 故事模式的發音按鈕是否能發聲。
- 「優先使用高品質語音」開關是否有效果。

## 是否偏離 BRIEF

無。

補充：未修改任何現有 `speakEn` / `speakZh` / `SpeakButton` 呼叫點；偏好設定由 `tts.ts` 內部讀取，符合 BRIEF 邊界。

## lint / build 結果

- `npm.cmd run lint`：通過。
- `npm.cmd run build`：通過。Vite 仍有既有 chunk size warning，未影響 build。

## ★ 負責人驗收步驟（白話、按順序）

1. 打開 App，首頁右上角應該會多一個齒輪設定圖示。
2. 點齒輪進入「發音設定」頁。
3. 切換「美式發音」和「英式發音」，每次切換後點「測試發音」，聽聽看有沒有差異。
4. 回到任一批次，進翻牌學習或故事模式，點發音按鈕，確認會發聲。
5. 回設定頁，打開「優先使用高品質語音」，在電腦 Chrome 上測試發音是否更清楚自然。
6. 在 iPad / iPhone 上也測一次設定頁與翻牌卡 / 故事模式發音，特別確認點按後能不能發聲。
7. 重新整理頁面，再回設定頁，確認剛才選的發音模式與高品質語音開關還在。

## 遇到的問題 / 卡住的地方（若有）

- 沒有產品實作阻塞。
- 本機無法驗證 iOS Safari 真實發音限制與語音品質差異，需負責人實機驗收。
