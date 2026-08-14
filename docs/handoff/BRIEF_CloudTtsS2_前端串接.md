# BRIEF_CloudTtsS2_前端串接.md — Google Cloud TTS 切片2：前端串接

> 交接合約：規劃層 → 執行層，2026-08-14。
> 背景：切片1（`docs/handoff/REPORT_CloudTtsS1_後端Function.md`）已完成並經規劃層獨立驗證通過——`synthesizeSpeech` Cloud Function 已部署到 `gen-lang-client-0930375434` 專案的 `us-central1`，接受 `{ text, lang }`，回傳 `{ audioBase64 }`（MP3），已用 curl 等價測試證明能正常運作、也能正確擋下不合法輸入。這片要把它接進 App 前端，讓使用者真的能選「Google 雲端語音」並聽到效果。**這片驗收一定要在真實 iPhone 上測，是這片最大的風險點，不能只在桌機瀏覽器測過就當作沒問題。**

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 讀 `docs/handoff/REPORT_CloudTtsS1_後端Function.md` 了解 Cloud Function 的輸入輸出格式與部署細節。
3. 工作目錄為 `exam-vocab-batcher/`（App 本體）。**這片不碰 `functions/` 底下任何檔案**，後端已經在切片1做完並驗證通過，這片只是把它接起來用。

## 目標（一句話）
> 使用者在「發音設定」頁可以選「Google 雲端語音」，選了之後 App 裡任何地方點英文發音按鈕，都會呼叫已經部署好的 `synthesizeSpeech` Cloud Function 播放 Google 品質的語音；網路不通或呼叫失敗時要自動退回裝置原本的發音方式，不能整個發不出聲音。

## 現況（可直接重用）

- **已部署的 Cloud Function**（切片1完成，不用你再改）：
  - Callable function 名稱：`synthesizeSpeech`，region：`us-central1`。
  - 輸入：`{ text: string, lang: 'en-US' | 'en-GB' }`。
  - 成功回傳：`{ audioBase64: string }`（MP3 base64）。
  - 失敗時拋 `HttpsError`（例如 `invalid-argument`），前端用 Firebase SDK 呼叫時會變成一個帶 `code`/`message` 的 JS Error，直接 catch 起來處理即可。
  - `text` 上限 200 字元，這個 App 的單字/句子長度不會超過，不用特別處理超長文字的情況，但呼叫端還是要做好 try/catch，不要假設一定成功。

- **`exam-vocab-batcher/src/services/tts.ts`**（2026-08-14 上一輪「發音模式選擇」剛加過語音選擇邏輯，目前結構）：
  ```ts
  export function getVoicesAsync(): Promise<SpeechSynthesisVoice[]> { ... }

  export function speakEn(word: string): void {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const accent = getAccent();
    void getVoicesAsync().then((voices) => {
      // 挑選 SpeechSynthesisVoice、呼叫 speechSynthesis.speak(utterance)
    });
  }

  export function speakZh(text: string): void { ... }
  ```
  `speakEn` 對外簽名是 `speakEn(word: string): void`（fire-and-forget，呼叫端不用 `await`），這片要維持這個簽名不變。**這個檔案是全站唯一的發音出口**（`AGENTS.md` 明文規定），所有呼叫點（`SpeakButton`、`FlashCardPage.tsx:88,173`、`ExamRunPage.tsx:111`、`StoryPage.tsx:73`）都不用改，你只要在 `speakEn` 內部加雲端語音分支即可。

- **`exam-vocab-batcher/src/services/ttsPreferences.ts`**：目前有 `getAccent()`/`setAccent()`、`getPreferHighQuality()`/`setPreferHighQuality()`，都是讀寫 `localStorage`、預設值 `false`/`en-US` 的簡單 pattern，已經有防呆處理（`localStorage` 不可用時安全降級），這片新增的 `useCloudTts` 偏好要照同樣的寫法。

- **`exam-vocab-batcher/src/services/firebase.ts`**：
  ```ts
  export const firebaseEnabled = Boolean(firebaseConfig.apiKey);
  export const app = firebaseEnabled ? initializeApp(firebaseConfig) : null;
  export const auth = app ? getAuth(app) : null;
  export const db = app ? getFirestore(app) : null;
  ```
  這片要仿照這個 pattern 新增 `export const functions = app ? getFunctions(app, 'us-central1') : null;`（`getFunctions` 從 `firebase/functions` 匯入，第二個參數指定 region 要跟切片1部署的 `us-central1` 一致，不指定的話 SDK 預設也是 `us-central1`，但明確寫出來比較不會出錯）。**`firebaseEnabled` 這個既有的降級機制要沿用**——沒有設定 Firebase 環境變數時，`functions` 會是 `null`，雲端語音模式就是不可用，不能讓 App 整個壞掉。

- **`exam-vocab-batcher/src/pages/SettingsPage.tsx`**：目前是「美式/英式」二選一 radio 按鈕組 + 「優先使用高品質語音」布林開關，UI 元件風格可以直接參考沿用（`aria-pressed` 的按鈕樣式、開關的 toggle 樣式）。

## 任務

1. **`ttsPreferences.ts` 新增雲端語音偏好**：
   - `getUseCloudTts(): boolean` / `setUseCloudTts(value: boolean): void`，localStorage key 自訂（例如 `ttsUseCloudTts`），**預設 `false`**（跟 `preferHighQuality` 一樣的 opt-in 模式，不要預設開啟）。

2. **`firebase.ts` 新增 `functions` export**：
   - `import { getFunctions } from 'firebase/functions';`
   - `export const functions = app ? getFunctions(app, 'us-central1') : null;`

3. **`tts.ts` 的 `speakEn` 新增雲端語音分支**：
   - 開頭判斷：如果 `getUseCloudTts()` 為真、且 `functions` 不是 `null`：
     - 呼叫 `httpsCallable(functions, 'synthesizeSpeech')({ text: word, lang: getAccent() })`。
     - 設定合理逾時（例如 5~8 秒），可以用 `Promise.race` 或等價方式，避免網路卡住讓使用者永遠等不到聲音也沒有任何反應。
     - 成功拿到 `audioBase64` 後，轉成可播放的音檔（例如組成 `data:audio/mp3;base64,...` 字串，用 `new Audio(url)` 播放，或轉成 `Blob` 用 `URL.createObjectURL`，你自行決定哪種寫法更乾淨）。
     - **任何失敗（呼叫拋錯、逾時、`functions` 是 `null`）都要自動退回目前既有的 Web Speech API 邏輯**（也就是現有的 `getVoicesAsync().then(...)` 那段），**絕對不能讓使用者點了按鈕完全沒有聲音、也沒有任何提示**，這是延續上一輪就定下的鐵律。
   - 如果 `getUseCloudTts()` 是假、或雲端呼叫失敗，走原本的 Web Speech API 路徑（現有邏輯不用大改，本來就會處理）。
   - 加一層簡單的**瀏覽器端快取**（`localStorage`，key 用 `${lang}::${word}` 之類的組合）：同一個字在同一台裝置重複播放時，先檢查快取有沒有存過 `audioBase64`，有的話直接播放、不用再呼叫 Cloud Function。這不是必要的效能優化，但實作起來不難，這片建議一起做（如果評估後覺得會拖慢這片、想留到之後再做也可以，在報告裡說明理由）。
   - `speakZh`（中文發音）**不用改**，這片只處理英文發音的雲端語音路徑。

4. **`SettingsPage.tsx` 改成三選一**：
   - 把現有「美式/英式」選擇器**保留**（口音選擇跟發音引擎是兩件獨立的事：不管用裝置語音還是雲端語音，都要知道使用者想要美式還是英式）。
   - 「優先使用高品質語音」跟新的「Google 雲端語音」**整理成一組三選一**（不要做成兩個各自獨立、可能同時開啟的開關），三個選項：
     1. **裝置預設語音**（現況，離線可用，不特別優先挑語音）
     2. **優先高品質裝置語音**（沿用現有 `preferHighQuality`，補充說明「使用瀏覽器/裝置內建的網路語音（如果有），iPad/iPhone 可能沒有效果」）
     3. **Google 雲端語音（最準，需要網路）**（新的 `useCloudTts`，說明文字強調「每次播放都需要連網，音質最接近 Google Translate，網路不通時會自動改用裝置預設發音」）
   - UI 呈現方式可以比照現有美式/英式選擇器的按鈕群組風格（單選、`aria-pressed`），底層還是兩個獨立的布林值沒關係，只是畫面上做成互斥選項，避免「兩個都開，不知道哪個生效」的困惑狀態。
   - 「測試發音」按鈕保留，選哪個模式就用哪個模式測試。

5. `npm run lint`、`npm run build` 要過。

6. **Playwright 自我驗證**（基本功能不報錯即可，音質差異這種東西測不出來）：
   - 進 `/settings`，切換三個發音模式選項，點測試發音沒有 JS 錯誤（雲端語音在測試環境呼叫可能會失敗，這是預期的——**只要確認失敗時有自動退回、沒有整頁報錯或卡死**即可，不強求測試環境真的能連到 Cloud Function）。
   - 重新整理頁面，確認三選一的選擇有持久化。
   - 從批次頁進翻牌卡/故事模式點發音按鈕不報錯。
   - 截圖存下來（暫時性驗證用，跑完可留可不留）。

7. **這片一定要在真實 iPhone 上實測**（規劃層/負責人會做，但如果你有辦法提供一個可以讓負責人直接測試的網址或方式，例如部署到 Firebase Hosting 預覽頻道，在報告裡說明怎麼做——不強制要求你自己部署預覽頻道，這通常是規劃層在收尾階段做的事，但如果你評估後方便直接做，可以做）：
   - 設定頁選「Google 雲端語音」，點「測試發音」，確認 iPhone 上真的有聲音（這是最大的未知風險：網路請求 + 等待回應後才播放，可能超出 iOS Safari「必須緊接著使用者點擊」的限制）。
   - 進批次翻牌卡/故事模式點發音按鈕，確認有聲音。
   - 關閉網路（或用飛航模式）測試，確認會自動退回裝置預設發音，不會完全沒反應。

## 邊界（本切片不做）

- **不碰 `functions/` 底下任何檔案**——後端邏輯已經在切片1做完並驗證通過，這片純粹是前端呼叫既有的 Function，不需要也不應該修改後端程式碼。
- **不做 Firestore 快取層**——那是切片3的事，這片頂多做瀏覽器端 `localStorage` 快取（見任務3），不涉及伺服器端快取。
- **不改 `App.tsx` 的 `BrowserRouter`／`basename` 設定**——2026-08-13 才修好的部署 bug，這片不涉及路由改動。
- **不改 `AppContext.tsx` 裡 `setSource()` 的邏輯**——2026-08-13 才修好的「重複點選同一來源卡住」bug，這片不涉及來源切換邏輯。
- **`speakZh` 不動**——這片只處理英文發音的雲端語音選項，中文發音維持現況。
- **不用做「優先高品質語音」跟「Google 雲端語音」以外的第四種模式**——固定三選一，不要自己發揮加更多選項。

## 驗收（負責人操作）

1. 打開 App（規劃層會提供測試網址，可能是本機預覽或 Firebase Hosting 預覽頻道），進「發音設定」頁。
2. 選「Google 雲端語音」，點「測試發音」，聽聽看是不是比裝置預設的發音更清楚自然。
3. 回到任一批次，進翻牌學習或故事模式，點發音按鈕，確認會用 Google 雲端語音播放。
4. **在 iPhone 上重複步驟2、3**——這是這片最重要的驗收項目。
5. 在 iPhone 上開飛航模式，再點一次發音按鈕，確認還是有聲音（會自動改用裝置預設發音），不會完全沒反應。
6. 重新整理頁面，確認「Google 雲端語音」的選擇還在。

## 收工指令（執行層收工必做）

1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「Google Cloud TTS 切片2（前端串接）已完成待負責人 iPhone 實機驗收，通過後開切片3（Firestore 快取層）」。
2. 若有任何偏離本 BRIEF 的改動（尤其是逾時秒數、快取要不要做、UI 呈現方式）→ 記 `docs/planning/DECISIONS.md`。
3. 給規劃層「現在可以怎麼測」＋操作步驟，明確標出哪些是規劃層/負責人一定要在真實 iPhone 上測的項目。
4. **完成以上所有事項、且 `npm run lint`、`npm run build` 都通過後，將本次變更 commit（不用 push，等 iPhone 實測通過再由規劃層決定要不要部署）。** commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。commit 前確認 `git status` 沒有不該提交的檔案。
