# BRIEF_CloudTtsS1_後端Function.md — Google Cloud TTS 切片1：Cloud Function 後端

> 交接合約：規劃層 → 執行層，2026-08-14。
> 背景：負責人想要 App 的英文發音真正達到 Google Translate 的音質水準（尤其是上一輪「優先使用高品質語音」開關在 iPhone Safari 上完全無效，因為 iOS 沒有 Google 網路語音可選）。查證後確認 Google Translate 網頁用的是非官方、不穩定的隱藏端點，不能拿來當作正式功能基礎，唯一可靠的路是官方 **Google Cloud Text-to-Speech API**。負責人已經：① 把 Firebase 專案 `gen-lang-client-0930375434` 升級到 **Blaze 方案**（已綁卡確認完成）；② 啟用 **Cloud Text-to-Speech API**（已確認完成）。**這是本專案第一次引入後端（Cloud Function）**，之前完全是純前端靜態網站 + Firestore + Auth，沒有任何伺服器端程式碼，開工前請先理解這個架構轉變的意義。
>
> **這片只做後端，完全不碰 `exam-vocab-batcher/` 前端程式碼**——前端串接是下一片（切片2）的事，屆時會再開新 BRIEF。這片的唯一目標是證明「Blaze + API 啟用 + Cloud Function 呼叫 Google TTS」這條路真的能跑通，用可驗證的方式證明給規劃層看，不需要任何 UI。

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 工作目錄為專案根目錄 `D:\program\vocabbatcher`（這片要新增的是根目錄下的 `functions/`，不是 `exam-vocab-batcher/` 裡面）。

## 目標（一句話）
> 新增一個 Firebase Cloud Function `synthesizeSpeech`，接收 `{ text, lang }`，呼叫 Google Cloud Text-to-Speech API 合成語音，回傳 base64 編碼的 MP3，並且部署到正式環境、用可重現的方式證明它真的能跑（回傳的音檔真的能播放、聽起來是自然的英文發音）。

## 現況（可直接重用）

- **Firebase 專案設定**：`.firebaserc` 指向 `gen-lang-client-0930375434`（已升級 Blaze、已啟用 Cloud Text-to-Speech API，負責人已確認完成，不用你再檢查）。
- **`firebase.json`**（專案根目錄）：目前只有 `"firestore"` 與 `"hosting"` 兩個區塊，**沒有 `"functions"` 區塊**，`functions/` 目錄目前不存在，這片要從零建立。
- **`firestore.rules`**：目前只允許登入使用者讀寫自己 `users/{uid}` 底下的資料，其餘路徑預設全部拒絕（沒有明確規則的路徑，Firestore 預設就是拒絕存取，不用擔心這片新增的東西會意外對外開放）。**這片不需要用到 Firestore**（快取層是切片3的事），純粹是提醒你現有規則長怎樣。
- 這個專案的 App 本體（`exam-vocab-batcher/`）是 TypeScript + React，`package.json` 用 npm 管理依賴——這片的 `functions/` 也要用 TypeScript，跟主專案語言一致。

## 任務

1. **建立 `functions/` 目錄**（專案根目錄下，跟 `exam-vocab-batcher/` 同一層）：
   - 用 `firebase init functions`（或手動建立等價結構）建立標準 Firebase Functions TypeScript 專案骨架：`functions/package.json`、`functions/tsconfig.json`、`functions/src/index.ts`。
   - Node 版本用 20（`functions/package.json` 的 `engines.node` 設 `"20"`）。
   - 安裝依賴：`firebase-functions`（v2/Gen 2 API）、`firebase-admin`（可能用不到但通常會裝）、`@google-cloud/text-to-speech`。

2. **實作 `synthesizeSpeech` callable function**（`functions/src/index.ts` 或拆成模組，你自行決定檔案結構）：
   - 用 `firebase-functions/v2/https` 的 `onCall`（Gen 2 callable function）。
   - 輸入：`{ text: string, lang: 'en-US' | 'en-GB' }`。
   - **輸入驗證**：`lang` 必須是 `'en-US'` 或 `'en-GB'` 這兩個值之一，其他值要拋出明確錯誤（`HttpsError`，code 用 `invalid-argument`）；`text` 長度上限抓 200 字元，超過就拋錯（防止濫用，這個 App 只會拿來唸單字或短句子，正常使用不會超過這個長度）。
   - 用 `@google-cloud/text-to-speech` 的 Node SDK（`TextToSpeechClient`）呼叫 Google 的語音合成，`input: { text }`、`voice: { languageCode: lang }`（性別/音色你可以自行挑一個合理的預設，例如 `ssmlGender: 'NEUTRAL'` 或指定一個具體的標準音色名稱，只要是穩定、正常的英文發音即可）、`audioConfig: { audioEncoding: 'MP3' }`。
   - **不用手動管理 API 金鑰**——Cloud Function 執行環境的預設服務帳號應該已經有權限呼叫同專案內已啟用的 Google Cloud API。**如果實際部署後發現權限不夠（例如收到 permission denied），這是這片明確允許你自行排查解決的範圍**：可以到 IAM 頁面確認 Cloud Functions 用的服務帳號、視需要加上呼叫 Cloud Text-to-Speech API 所需的角色，這部分不確定的地方就照實際情況調整，不用等規劃層決定，但要在報告裡寫清楚你做了什麼調整、為什麼。
   - 回傳格式：`{ audioBase64: string }`（先不用加 `cached` 欄位，那是切片3快取層才有意義的欄位，這片沒有快取）。

3. **`firebase.json` 新增 `functions` 設定區塊**，指向 `functions/`，`runtime` 設 `nodejs20`，`predeploy` 記得跑 TypeScript build（`npm --prefix functions run build` 或等價寫法）。

4. **部署並驗證**：
   - `firebase deploy --only functions`。
   - **用可重現、規劃層事後能看懂的方式證明這個 function 真的能用**，具體怎麼測你自行決定最合理的方式（例如：寫一支暫時性的本機 Node 測試腳本，用 Firebase Admin SDK 或直接 HTTPS POST 呼叫已部署的 callable function、把回傳的 base64 存成一個 `.mp3` 檔案），並且**你要實際確認這個 mp3 檔案是有效的音檔**（例如檔案大小明顯不是 0、用某種方式確認它是合法的 MP3 格式），不能只憑「API 回應 200」就當作成功。
   - 測試至少 2 個情境：① 正常情況（例如 `{ text: 'enhance', lang: 'en-US' }`），② 至少一個錯誤情境（例如 `lang` 傳一個不合法的值），確認錯誤處理有正確擋下來，不是整個 function 掛掉。
   - 把測試腳本（如果有寫）跟測試結果、實際產生的 mp3 檔案路徑，都記在報告裡。**如果你有辦法讓規劃層事後也能重跑同一個驗證腳本，請把腳本留在專案裡（例如 `functions/test/manual-test.ts` 或你覺得合理的位置），並在報告裡說明怎麼重跑。**

## 邊界（本切片不做）

- **完全不碰 `exam-vocab-batcher/` 底下任何檔案**——前端整合（`tts.ts`、`ttsPreferences.ts`、`SettingsPage.tsx`）是切片2的事，這片只要 Cloud Function 本身能正常運作即可，不用讓 App 真的用上它。
- **不做 Firestore 快取層**——那是切片3的事，這片每次呼叫都直接打 Google TTS API，不用擔心重複計費的問題（這個階段呼叫次數很少，用量遠低於免費額度）。
- **不改 `firestore.rules` 的既有內容**（`users/{uid}` 那段）——這片沒有新增任何 Firestore collection，不需要動安全規則。
- **不把 functions 部署塞進現有 `deploy.ps1`**——那支腳本是給前端用的，這片獨立用 `firebase deploy --only functions`（或你可以新增一支獨立的 `deploy-functions.ps1`，包成腳本方便未來重跑，這個可以做，但不要動 `deploy.ps1` 本身）。
- **不用做多種音色/情感語音的選擇**——固定用一個合理的預設音色即可，音色挑選/客製化不在這片範圍。

## 驗收（負責人操作）

這片沒有 UI，負責人不需要在 App 裡操作任何東西。驗收方式：
1. 看執行層報告裡附的測試結果，確認有成功呼叫 `synthesizeSpeech` 並產生出一個聽起來正常的英文發音 mp3 檔案（負責人可以要求執行層把這個檔案的路徑或內容想辦法讓自己聽到，或規劃層事後幫忙播放確認）。
2. 確認 Google Cloud Console 的帳單頁面顯示的用量微乎其微（不強制要求，僅供安心）。
3. 確認以上都沒問題，才會進入切片2（前端串接，屆時負責人要用 iPhone 實測）。

## 收工指令（執行層收工必做）

1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「Google Cloud TTS 切片1（後端 Function）已完成待規劃層驗證，驗證通過後開切片2（前端串接，含 iPhone 實測）」。
2. 若有任何偏離本 BRIEF 的改動（尤其是 IAM 權限調整、音色選擇、測試方式）→ 記 `docs/planning/DECISIONS.md`。
3. 給規劃層「現在可以怎麼驗證」＋測試腳本位置與重跑方式＋實際測試結果摘要。
4. **完成以上所有事項後，將本次變更 commit（不用 push，等規劃層確認這片真的可靠再決定）。** commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。commit 前確認 `git status` 沒有不該提交的檔案（特別注意 `functions/node_modules/`、任何測試產生的 mp3 檔案是否該進 `.gitignore`，通常這些不該進版控）。
