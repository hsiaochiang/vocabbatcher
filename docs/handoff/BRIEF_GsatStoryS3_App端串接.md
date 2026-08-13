# BRIEF_GsatStoryS3_App端串接.md — 學測 Minecraft 故事模式切片3：App 端串接

> 交接合約：規劃層 → 執行層，2026-08-13。
> 背景：學測 Minecraft 故事模式的內容資料已經備妥並通過品質審查——`output/story/gsat/stories.gsat.json`（80頁完整版，含第16~20頁規劃層手寫試行版 + 第1~15/21~80頁執行層重做版，過程與品質核對記錄見 `docs/planning/DECISIONS.md` 2026-08-13「學測故事模式切片2模板化生成不合格」與「切片2b 重做通過但密度超出上限」兩則條目）。這片要把這份資料真正接進 App：學生用「選課本頁碼」建立的批次，如果有對應的故事，批次頁要多一個「故事模式」入口，點進去能看到整頁故事（英文+中文對照），並能點擊發音。

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 讀 `docs/handoff/REPORT_GsatStoryS2b_剩餘75頁故事重做.md` 了解故事資料的來源與格式。
3. 工作目錄為 `exam-vocab-batcher/`（App 本體），資料檔案在專案根目錄的 `output/story/gsat/`。

## 目標（一句話）
> 學生用「選課本頁碼」快速建立學測批次時，若該頁有對應的 Minecraft 故事，批次頁會出現「故事模式」入口，點進去能讀到整頁故事（英文+中文對照），點英文句子或中文對照裡的英文單字都能聽發音。

## 現況（可直接重用）

- **故事資料**：`output/story/gsat/stories.gsat.json`，格式（`schemaVersion: 2`）：
  ```jsonc
  {
    "schemaVersion": 2,
    "stories": [
      {
        "id": "gsat-p13-minecraft",
        "source": "gsat",
        "page": 13,
        "theme": "minecraft",
        "wordList": ["wheat", "access", "..."],
        "generatedAt": "2026-08-13T00:00:00Z",
        "sentences": [
          {
            "index": 0,
            "text": "Steve found a wheat field near his shelter.",
            "zh": "Steve 在他的避難所附近發現了一片小麥（wheat）田。",
            "targetWords": ["wheat"]
          }
        ]
      }
    ]
  }
  ```
  中文 `zh` 欄位裡，`targetWords` 對應的每個英文單字都保證能在字串裡用全形或半形括號找到（例如「小麥（wheat）」），這個比對規則規劃層已經在資料產出時反覆驗證過，不用重新設計解析方式，直接拿 `targetWords` 逐一去 `zh` 字串裡找 `[（(]word[）)]` 這個 pattern 即可。
  **這份檔案有 80 頁的完整版，但不是全部批次都會對到——只有透過「選課本頁碼」按鈕建立的批次才會有對應故事，手動勾字的批次不會有。**

- **`Batch` 型別**：`exam-vocab-batcher/src/types/batch.ts`：
  ```ts
  export interface Batch {
    id: string;
    name: string;
    source: VocabSource;
    createdAt: string;
    lastAccessedAt: string;
    words: VocabEntry[];
    flashcardIndex: number;
  }
  ```
  目前沒有頁碼欄位。

- **批次建立流程**：`exam-vocab-batcher/src/pages/BatchBuilderPage.tsx` 的 `pageOptions`（依 `word.source_page` 分組）與 `handleCreatePageBatch`（頁碼快速建立按鈕的 click handler，內部呼叫 `createBatch(words, name)`）——這是負責人在這次 session 一開始就在看的「快速建立：選課本頁碼」那個畫面，`page` 這個頁碼數字在這個函式裡已經是已知變數。

- **批次的通用更新 hook**：`exam-vocab-batcher/src/store/AppContext.tsx` 的 `updateBatch(id, patch: Partial<Batch>)`——泛用 merge，可以直接拿來寫入新欄位，不用改函式簽名。**注意：`AppContext.tsx` 裡的 `setSource()` 今天稍早才修過一個 bug（重複點選同一來源會讓 App 卡在載入中，見 `DECISIONS.md` 2026-08-13「真正根因」條目），這段邏輯不要動，這片工作跟它無關，只是提醒你這個檔案裡有這段今天才修好的敏感邏輯，改動時眼睛看清楚別誤觸。**

- **`BatchHubPage`**（`exam-vocab-batcher/src/pages/BatchHubPage.tsx`）：批次進去後看到的功能格子頁，目前有「翻牌學習」「練習測驗」「學習統計」三格（`features` 陣列，約第68-105行），每格有 `available` 布林值控制是否可點擊，可以參考這個 pattern。

- **`FlashCardPage`**（`exam-vocab-batcher/src/pages/FlashCardPage.tsx`）：現有的單字翻牌頁面，可以參考它的整體頁面結構（`Header` + 進度條 + 內容區 + 底部固定按鈕列）與如何用 `useParams` 拿 `batch.id`、用 `batches.find()` 找到對應批次，但**故事頁不是翻牌邏輯，不要共用 `flashcardIndex` 這類翻牌專屬狀態，另開一頁獨立元件**。

- **`SpeakButton` / `speakEn` / `speakZh`**（`exam-vocab-batcher/src/components/SpeakButton.tsx`、`src/services/tts.ts`）：`speakEn(text: string)` 本來就接受任意字串，不是只能唸單字，`SpeakButton` 元件也一樣，**這片直接重用，不用改**。

- **PWA 快取設定**：`exam-vocab-batcher/vite.config.ts` 裡的 `runtimeCaching` 規則（約第31-41行），目前 `urlPattern` 是 `/\/data\/vocab(\.gsat)?\.cleaned\.json$/` → `StaleWhileRevalidate`，只匹配 `vocab.cleaned.json` 跟 `vocab.gsat.cleaned.json` 這兩個檔案。**這個正則要擴大涵蓋 `stories.gsat.json`，否則故事資料不會被離線快取、也不會有背景更新機制**——2026-08-04 曾經因為快取規則沒涵蓋到 `vocab.gsat.cleaned.json`（規則一開始只寫會考那份）導致部署後學測資料看不到更新，這個坑不要再踩一次（見 `DECISIONS.md` 2026-08-04 條目）。

## 任務

1. **`Batch` 型別新增 `sourcePage` 欄位**（`exam-vocab-batcher/src/types/batch.ts`）：
   - 新增 `sourcePage?: number;`（optional，不影響既有 localStorage 存的舊批次資料，讀出來時這個欄位自然是 `undefined`）。

2. **`BatchBuilderPage.handleCreatePageBatch` 建立批次時打上頁碼標籤**：
   - 建立完批次（`createBatch(...)`）後，緊接著呼叫 `updateBatch(batch.id, { sourcePage: page })`（`page` 是這個函式裡已經有的頁碼變數）。
   - **手動勾字建立的批次（`handleCreate` 那個路徑）不要打這個標籤**——維持 `sourcePage` 是 `undefined`，這樣故事分頁才會正確地只在頁碼批次上出現。

3. **載入故事資料**：
   - 仿照 `AppContext.tsx` 裡載入 `vocab.gsat.cleaned.json` 的既有 fetch pattern（用 `import.meta.env.BASE_URL` 組路徑，同源請求），寫一個 fetch `data/stories.gsat.json` 的邏輯。
   - 這個資料只有進到故事頁才需要，建議**在 `StoryPage`（見任務5）內部用 `useEffect` 做 page-local fetch**，不用一開始就載入到全域 `AppContext`（大部分使用者可能整個 session 都不會點進故事模式，不用一開始就多下載一份資料），除非你評估後覺得放進 `AppContext` 更合理，可以自行決定，但要在報告裡說明理由。
   - 找故事的邏輯：`story = batch.sourcePage != null ? storiesData.stories.find(s => s.page === batch.sourcePage && s.theme === 'minecraft') : undefined`——`sourcePage` 有值、且資料裡真的有對應頁碼的故事，兩個條件都成立才算有故事。

4. **`BatchHubPage` 新增「故事模式」入口**：
   - 在 `features` 陣列裡新增第4格，只有在該批次符合上面「有故事」的條件時才顯示（可以用跟現有 `available` 類似的方式處理，或直接不把這個格子塞進陣列——你自行判斷哪種寫法比較乾淨）。
   - 點擊導向新路由 `/batch/:id/story`。
   - 沒有對應故事的批次（例如手動勾字批次、或頁碼對到資料裡沒涵蓋的頁面）**完全不顯示這格，不要顯示灰色不可點擊的格子**——沒有故事對這些批次來說是正常狀態，不是「功能還沒做完」，不需要用 disabled 樣式暗示使用者這裡缺了什麼。

5. **新增 `StoryPage` 元件與路由**：
   - 新檔案 `exam-vocab-batcher/src/pages/StoryPage.tsx`，路由 `/batch/:id/story`（在 `App.tsx` 的路由設定裡加一行，比照其他 `/batch/:id/...` 路由的寫法）。
   - 內容：`Header`（比照其他頁面，含 `onBack`、`UserBadge`）+ 句子列表，逐句顯示：
     - 英文 `text`：目標單字（`targetWords`）用粗體標出，句子旁邊放一顆 `SpeakButton`，把整句 `text` 傳進去。
     - 中文 `zh`：括號內符合 `targetWords` 的英文單字渲染成可點擊的元件（例如小按鈕或有底色的文字），點下去呼叫 `speakEn(word)`（只唸這個單字，不是整句），其餘中文文字正常顯示。
   - 找不到批次、或批次沒有對應故事（正常來說不會發生，因為 `BatchHubPage` 已經做過條件判斷才會導到這頁，但防禦性地處理一下——例如使用者用瀏覽器網址列直接打進這個路由）時，顯示簡單的「找不到故事內容」訊息＋返回按鈕，不用做複雜的錯誤處理。
   - 「整段自動連續播放」是加分項，不是這片必做，有餘力可以做，沒有也沒關係。

6. **複製故事資料進 App 正式資料夾**：
   - 把 `output/story/gsat/stories.gsat.json` 複製到 `exam-vocab-batcher/public/data/stories.gsat.json`。

7. **PWA 快取規則擴大**（`exam-vocab-batcher/vite.config.ts`）：
   - 把 `runtimeCaching` 的 `urlPattern` 正則擴大成同時匹配 `stories.gsat.json`（例如改成 `/\/data\/(vocab(\.gsat)?\.cleaned|stories\.gsat)\.json$/` 或你覺得更清楚的寫法都可以，只要三個檔案都能被同一條規則涵蓋，策略維持 `StaleWhileRevalidate`）。

8. **`npm run lint`、`npm run build` 要過。**

9. **Playwright 自我驗證**（比照本專案 2026-08-03 起的 UI/UX 切片慣例，`AGENTS.md` 有寫這條規則）：
   - 用學測來源、透過「選課本頁碼」建立一個有故事的頁碼批次（例如第16頁，一定有故事），進批次頁確認出現「故事模式」格子，點進去確認句子列表正確顯示、點發音按鈕沒有報錯。
   - 用手動勾字建立一個批次，確認批次頁**不會**出現「故事模式」格子。
   - 截圖存下來（暫時性驗證用，跑完可留可不留）。
   - 這個驗證過程與結果要寫進收工報告。

## 邊界（本切片不做）

- **不做會考（CAP）的故事模式**——這次規劃只做學測，`stories.cap.json` 未來如果要做會是另一個切片。
- **不改 `App.tsx` 的 `BrowserRouter` 設定**——今天稍早才修好 `basename` 的部署 bug（`DECISIONS.md` 2026-08-13「修復 GitHub Pages 備援管道...」條目），跟這片無關，不要碰。
- **不改 `AppContext.tsx` 裡 `setSource()` 的邏輯**——今天稍早才修好「重複點選同一來源卡住」的 bug（`DECISIONS.md` 2026-08-13「真正根因」條目），這片工作只需要用到 `updateBatch`，不要動到 `setSource`。
- **不做「整段自動連續播放」以外的額外互動**（例如朗讀速度調整、故事主題切換）——這些不在這片範圍，之後有需要再開新切片。
- **不改 `vocab.gsat.cleaned.json`、`0resource/` 底下任何資料檔**——這片只讀單字資料，不寫入它。
- **不用申請或呼叫任何外部 AI API**——故事內容已經是現成資料，這片純粹是把靜態 JSON 接進 UI。

## 驗收（負責人操作）

1. 打開 App，切到「學測」來源，點「建立新批次」，用「選課本頁碼」按鈕選第16頁（或任何第16~20頁其中一頁，這幾頁保證有故事）建立批次。
2. 進到批次頁，確認看到「故事模式」這個新格子（跟翻牌學習、練習測驗、學習統計並排）。
3. 點進故事模式，確認能看到整頁故事，英文、中文對照都有，點英文句子旁的喇叭圖示能聽到整句發音，點中文句子裡括號的英文單字能聽到那個單字的發音。
4. 回到首頁，這次改用手動勾字的方式（進階篩選/搜尋自己選字）建立一個批次，進批次頁確認**沒有**「故事模式」這格。
5. 都正常的話，這片就算過關。

## 收工指令（執行層收工必做）

1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「學測 Minecraft 故事模式全部完成，待負責人在自己裝置上實際操作驗收」。
2. 若有任何偏離本 BRIEF 的改動 → 記 `docs/planning/DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋上面「驗收（負責人操作）」的白話操作步驟。
4. **完成以上所有事項、且 `npm run lint`、`npm run build` 都通過後，將本次變更 commit（不用 push，等負責人實機驗收過再由規劃層決定要不要部署）。** commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。commit 前確認 `git status` 沒有不該提交的檔案。
