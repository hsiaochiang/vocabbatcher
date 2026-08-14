# BRIEF_TTSAccentSettings_發音模式選擇.md — 發音模式選擇（美式/英式 + 高品質語音選項）

> 交接合約：規劃層 → 執行層，2026-08-14。
> 背景：有使用者回報「App 的發音沒有 Google 準」，也提到其他網站可以選「美式」「英式」發音。規劃層追查程式碼後找到根本原因：`exam-vocab-batcher/src/services/tts.ts` 從頭到尾**從未指定要用哪個語音（`SpeechSynthesisVoice`）**，只設定了 `lang`，所以瀏覽器/裝置會自己隨便挑一個符合語言的預設語音——這通常才是「發音不準」的真正原因，不是 Web Speech API 本身不行，而是沒有主動挑一個好的語音來用。這片要做兩件事：① 讓使用者可以選美式或英式發音；② 修正語音選擇邏輯明確挑語音，並提供「優先使用高品質語音（需要網路）」的開關。完整設計討論見規劃層 plan 文件（已核准）。

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 工作目錄為 `exam-vocab-batcher/`（App 本體）。

## 目標（一句話）
> 使用者可以在一個新的「發音設定」頁面裡選擇美式或英式發音，並選擇性開啟「優先使用高品質語音」，設定會套用到全站所有發音功能（翻牌卡、練習測驗聽力題、故事模式、單字列表等），不用每個地方重選。

## 現況（可直接重用）

- **唯一的發音出口**：`exam-vocab-batcher/src/services/tts.ts`（17行）：
  ```ts
  export function speakEn(word: string): void {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }

  export function speakZh(text: string): void {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-TW';
    window.speechSynthesis.speak(utterance);
  }
  ```
  `AGENTS.md` 明文規定「語音一律經 `src/services/tts.ts`」——這條規則很重要，這片修改要維持這個唯一出口的架構，不要讓任何頁面繞過 `tts.ts` 自己呼叫 `speechSynthesis`。

- **呼叫方式不統一，這點會影響設計**：`WordCard.tsx:78`、`ExamResultPage.tsx:159`、`WordStatsPage.tsx:164`、`ExamHistoryPage.tsx:174`、`FlashCardPage.tsx:147,159`、`StoryPage.tsx:223` 是透過共用元件 `SpeakButton`（`src/components/SpeakButton.tsx`）呼叫；但 `FlashCardPage.tsx`（第88行自動播放中文、第173行手動播放中文按鈕）、`ExamRunPage.tsx`（第111行聽力題重播按鈕）、`StoryPage.tsx`（第73行逐句播放）是**直接呼叫** `speakEn`/`speakZh`，完全跳過 `SpeakButton`。**這代表偏好設定不能靠元件 props 一路往下傳，必須讓 `tts.ts` 自己去讀設定**，這樣不管從哪裡呼叫都會生效，不用逐一修改上面列的所有呼叫點。

- **既有的 localStorage 偏好模式可參考**：`src/store/AppContext.tsx` 裡 `source`（`vocabSource` key）的讀寫方式，是這個專案既有的「使用者選項存 localStorage」慣例，可以參考它的寫法風格，但**這次的偏好設定不要放進 `AppContext`**（見下方任務1說明原因）。

- **`VocabEntry` 型別**（`src/types/vocab.ts:13-24`）已經有 `ipa_us` 跟 `ipa_uk` 兩個欄位，`ipa_uk` 目前完全沒在畫面上用過（`FlashCardPage.tsx:142-146` 只顯示 `ipa_us`）。**這片不用處理 `ipa_uk` 的顯示**，音標文字顯示跟語音選擇是兩件獨立的事，只是告訴你資料庫已經有這個欄位存在，不用意外。

- **`Header` 元件**（`src/components/Header.tsx`）：通用標題列，支援 `title`、`onBack`、`rightSlot` 這幾個 prop，其他頁面（例如 `BatchHubPage.tsx`）已經示範過 `rightSlot` 放多個元件的寫法（`<div className="flex items-center gap-2">...</div>` 包起來）。

## 任務

1. **新增 `exam-vocab-batcher/src/services/ttsPreferences.ts`**：
   ```ts
   export type Accent = 'en-US' | 'en-GB';

   export function getAccent(): Accent            // 讀 localStorage，key 自訂（例如 'ttsAccent'），預設 'en-US'
   export function setAccent(accent: Accent): void

   export function getPreferHighQuality(): boolean  // 讀 localStorage，key 自訂（例如 'ttsPreferQuality'），預設 false
   export function setPreferHighQuality(v: boolean): void
   ```
   **為什麼不放進 `AppContext`**：`tts.ts` 是純函式模組、不是 React 元件，沒辦法用 `useContext` 讀取 `AppContext` 的狀態；而且上面任務背景提到很多呼叫點是直接呼叫 `speakEn`/`speakZh`，不會經過任何會重新渲染的 React 元件樹。用一個獨立的 `localStorage` 讀寫模組，讓 `tts.ts` 內部直接呼叫 `getAccent()`/`getPreferHighQuality()`，才能保證所有呼叫點都自動套用最新設定，不用大改呼叫介面。

2. **修改 `tts.ts` 的語音選擇邏輯**：
   - 新增 `getVoicesAsync(): Promise<SpeechSynthesisVoice[]>`：若 `speechSynthesis.getVoices()` 已經有資料就直接回傳；否則掛一次性的 `voiceschanged` 監聽，並加一個時間上限（建議 300ms）保底逾時直接回傳當下的（可能是空的）清單，避免某些瀏覽器永遠不觸發事件時卡住。
   - `speakEn` 內部依 `getAccent()` 回傳的 accent，在語音清單裡找符合 `lang` 的語音：
     - 有找到符合的 → 若 `getPreferHighQuality()` 為真，且找到的語音裡有 `localService === false` 的，優先選那個；否則選第一個符合語言的。
     - 完全找不到符合語言的語音（例如裝置沒有英式語音）→ 退而求其次找任何 `lang` 以 `en` 開頭的語音；再找不到就維持現況（只設定 `utterance.lang`、不指定 `utterance.voice`）。**不能靜默失敗，一定要有聲音播出來，這是最重要的容錯要求。**
     - 把選到的語音（如果有）指定給 `utterance.voice`，同時仍然設定 `utterance.lang`（用 `getAccent()` 的值，取代現在寫死的 `'en-US'`）保底。
   - `speakEn` 會變成非同步流程（內部 `await getVoicesAsync()` 才真正呼叫 `.speak()`），但**對外的函式簽名不變**，呼叫端依然是 `speakEn(word)`，不用改成 `await speakEn(word)`（除非你評估後覺得改成 async 對呼叫端更好，需要在報告裡說明理由並確認所有呼叫點都相容）。
   - `speakZh` 可以選擇性共用同一套「`preferHighQuality` 時找 `localService === false` 的 `zh-TW` 語音」邏輯，這是加分項不是必做，沒做也不影響驗收。
   - **iOS Safari 使用者點擊觸發限制要特別小心**：這個非同步等待的邏輯，理論上有可能讓 `.speak()` 的呼叫脫離原本使用者點擊事件的呼叫堆疊，導致 iPad/iPhone 上發不出聲音。**這片如果有 iPad/iPhone 實機或模擬器可以測，一定要實測這個風險；如果沒有裝置可測，要在報告裡明講「這項風險沒有實機驗證」，不要假設沒問題。**

3. **新增 `exam-vocab-batcher/src/pages/SettingsPage.tsx`，路由 `/settings`**：
   - 頁面結構比照其他頁面：`Header`（`title="發音設定"`、`onBack` 返回上一頁）。
   - 「美式發音」／「英式發音」二選一控制項（單選鈕或分段按鈕皆可，你自行決定 UI 呈現方式），選了立刻呼叫 `setAccent()` 存起來。
   - 旁邊放一個「測試發音」按鈕，點下去呼叫 `speakEn('hello')`（用目前選的 accent），讓使用者不用離開設定頁就能立刻聽到差異。
   - 「優先使用高品質語音（需要網路）」開關（預設關閉，讀寫 `getPreferHighQuality`/`setPreferHighQuality`），旁邊加一行說明文字，例如：「部分裝置（例如 iPad）可能沒有更高品質的語音可選，這個設定在這些裝置上可能沒有效果。」
   - 頁面載入時呼叫 `getVoicesAsync()` 檢查一次目前裝置有沒有 `en-GB` 語音，如果完全沒有，英式選項要顯示提示文字或直接停用，不要讓使用者選了卻沒作用又不知道為什麼。

4. **`App.tsx` 新增 `/settings` 路由**，比照現有路由的寫法加一行。

5. **`HomePage.tsx` 的 `Header` 加設定入口**：目前 `rightSlot` 只有 `<UserBadge />`，改成同時放一個設定圖示按鈕（點擊導向 `/settings`）與 `<UserBadge />`，兩個元件並排（可參考 `BatchHubPage.tsx` 的 `rightSlot` 多元件寫法）。

6. `npm run lint`、`npm run build` 要過。

7. **Playwright 自我驗證**（比照本專案 2026-08-03 起的 UI/UX 切片慣例，`AGENTS.md` 有寫這條規則）：
   - 進 `/settings`，切換美式/英式，點測試發音按鈕沒有報錯。
   - 開關「優先高品質語音」沒有報錯。
   - 重新整理頁面，確認設定有持久化（沒有跳回預設值）。
   - 從首頁進入任一批次的翻牌卡或故事模式，點發音按鈕沒有報錯（不需要驗證實際發出的語音內容，Playwright 測不出聲音品質，只要確認功能沒壞掉、沒有 JS 錯誤）。
   - 截圖存下來（暫時性驗證用，跑完可留可不留）。

## 邊界（本切片不做）

- **不改任何一個目前呼叫 `speakEn`/`speakZh` 的頁面元件**（`WordCard`、`ExamResultPage`、`WordStatsPage`、`ExamHistoryPage`、`FlashCardPage`、`ExamRunPage`、`StoryPage`、`SpeakButton`）——這是這次設計刻意換來的好處：偏好設定讓 `tts.ts` 內部自己讀，呼叫介面不變，全站自動生效，不用逐頁修改。如果你發現非改不可，要在報告裡說明為什麼設計上的假設不成立。
- **不顯示 `ipa_uk` 音標文字**——那是另一個範圍的事，這片只處理語音播放，不處理文字顯示。
- **不做多國語言以外的口音**（例如澳洲腔）——固定只有美式/英式兩個選項。
- **不改 `App.tsx` 的 `BrowserRouter`／`basename` 設定**——2026-08-13 才修好的部署 bug（`DECISIONS.md` 2026-08-13 條目），這片只是新增一行路由，不要動到 Router 本身的設定。
- **不改 `vite.config.ts` 的 PWA/Workbox 快取規則**——這片不涉及任何新的資料檔案，跟快取無關。
- **「優先高品質語音」預設要關閉，不是開啟**——這是規劃層已經想清楚的取捨（離線優先精神 vs 音質），不要自己決定改成預設開啟。

## 驗收（負責人操作）

1. 打開 App，首頁右上角應該會多一個設定圖示，點下去進入「發音設定」頁。
2. 切換「美式發音」／「英式發音」，點「測試發音」按鈕，聽聽看有沒有差異（如果裝置本身兩種語音聽起來很像也算正常）。
3. 回到任一批次，進翻牌學習或故事模式，點發音按鈕，確認會照你剛才選的口音播放。
4. 回設定頁，打開「優先使用高品質語音」，在電腦的 Chrome 瀏覽器上測試看看發音品質有沒有變得比較清楚自然；如果是在 iPad 上測，這個開關可能沒有明顯效果，這是正常的（裝置限制，不是壞掉）。
5. 重新整理頁面，確認剛才選的設定還在（不會跳回預設值）。

## 收工指令（執行層收工必做）

1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「發音模式選擇待負責人實機驗收（尤其 iPad 上的使用者點擊觸發限制與高品質語音開關效果）」。
2. 若有任何偏離本 BRIEF 的改動 → 記 `docs/planning/DECISIONS.md`（例如「優先高品質語音」預設關閉這個決策，如果報告裡有更多相關的實測發現，可以在 DECISIONS.md 補充細節，不用重複規劃層已經寫過的取捨說明，但如果實測結果推翻了某個假設要記錄）。
3. 給負責人「現在你能做什麼」＋上面「驗收（負責人操作）」的白話操作步驟。
4. **完成以上所有事項、且 `npm run lint`、`npm run build` 都通過後，將本次變更 commit（不用 push，等負責人實機驗收過再由規劃層決定要不要部署）。** commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。commit 前確認 `git status` 沒有不該提交的檔案。
