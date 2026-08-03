# BRIEF_M5S2_App端來源切換.md — M5 切片 2：會考／學測單字庫來源切換

> 交接合約：規劃層 → 執行層，2026-08-04。
> 前置：M5-S1／M5-S1b（學測資料管線與 OCR 校正）已完成，`exam-vocab-batcher/public/data/vocab.gsat.cleaned.json` 詞性/中文定義完整率已達 100%，負責人已確認資料品質可以接進 App。
> 對應 `docs/planning/REQUIREMENTS.md` R13、`docs/planning/STAGE_5_PLAN.md` M5-S2。這是 M5 最後一片，做完 M5 就全部完成。

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 讀 `docs/handoff/REPORT_M5S1_學測資料管線.md`、`docs/handoff/REPORT_M5S1b_學測資料OCR校正.md` 了解學測資料的來源與格式。
3. 工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 使用者能在 App 裡選擇「會考」或「學測」單字庫，選定後，搜尋、批次建立、翻牌學習、考試出題、頁碼範圍、批次歷史、成績與錯誤率統計，全部只在所選單字庫內運作，兩份資料完全不互相污染。

## 現況（可直接重用）
- `src/store/AppContext.tsx`：`allWords` 目前寫死 `fetch(... + 'data/vocab.cleaned.json')`（第 51 行）。`batches`／`activeBatchId` 存在 `localStorage`（`batches`、`activeBatchId` 兩個 key）。
- `src/types/vocab.ts`：`VocabEntry` 介面（word/pos/zh_definition/frequency/source_page/ipa_us/ipa_uk/parse_confidence/issues），會考、學測兩份資料格式完全相同（`level` 欄位學測才有值，會考該欄位不存在也沒關係，`VocabEntry` 目前沒有 `level` 欄位，是否要加供 App 顯示由你決定，非必要）。
- `src/types/batch.ts`：`Batch` 介面目前沒有任何「這批是哪個來源建的」欄位。
- `src/services/exam.ts` 的 `generateExam()`／`getPageRange()` 都是純函式，吃 `allWords: VocabEntry[]` 當參數，只要 `AppContext` 給的 `allWords` 已經是所選來源的資料，這兩個函式完全不用改。
- `src/pages/ExamResultPage.tsx`（第 62~72 行）寫入 Firestore `users/{uid}/wordStats/{record.word}`（**文件 ID 直接是單字字串，沒有來源區分**）；`src/pages/WordStatsPage.tsx`（第 42~70 行）讀取整個 `wordStats` collection。`firestore.rules` 用 `match /{subcollection=**}` 萬用字元涵蓋所有子集合層級與文件 ID，**這片不需要改 `firestore.rules`**，不管你怎麼調整文件路徑/ID 命名都已經被涵蓋。

## ⚠️ 這片最重要的資料正確性風險（務必處理，不是選配）

`wordStats` 目前的 Firestore 文件 ID 就是單字字串本身（例如 `unique`），**沒有任何來源區分**。會考、學測兩份單字庫很可能有共同的高頻字（例如 `unique`、`various` 這類基礎字兩份詞表都會收錄）。如果不處理，使用者在學測單字庫答錯 `unique`，錯誤率會跟會考單字庫的 `unique` 混在一起計算，完全違背「兩份單字庫完全獨立」的需求（`REQUIREMENTS.md` R13）。

**這片必須把 `wordStats` 與 `examResults` 依來源區分**，具體做法建議（你可以評酌其他等價做法，只要能達到「兩個來源的統計互不污染」這個目的即可）：
- `wordStats` 文件 ID 改成 `${source}__${word}`（例如 `cap__unique`、`gsat__unique`），文件內容裡也存一個 `source` 欄位方便查詢/除錯。
- `examResults` 文件內容加一個 `source` 欄位（文件 ID 本身可以維持 `crypto.randomUUID()` 不用改）。
- `WordStatsPage.tsx` 讀取時只顯示/計算目前所選來源的 `wordStats`（用文件 ID 前綴或 `source` 欄位過濾）。
- `ExamHistoryPage.tsx` 讀取時比照處理，並在畫面上標示每筆成績是哪個來源（例如小標籤「會考」／「學測」），避免使用者混淆。
- 因為既有使用者（M5-S2 上線前）已經有一批沒有來源前綴的舊 `wordStats`／`examResults` 資料，這些舊資料視為屬於「會考」（`cap`，這是既有唯一來源），過渡處理方式由你決定（例如讀取時「找不到 source 前綴/欄位」就當作 `cap`），不用做資料遷移腳本，只要新寫入的資料都正確帶 `source` 即可。

## 任務

### 1. 定義來源型別與切換機制

- `src/types/vocab.ts` 新增 `export type VocabSource = 'cap' | 'gsat';`（`cap` = 會考，取自 Comprehensive Assessment Program；`gsat` = 學測，沿用 M5-S1 資料檔命名的 `gsat` 慣例，跟 `output/gsat/` 目錄一致）。
- `src/store/AppContext.tsx`：
  - 新增 `source: VocabSource` state，預設從 `localStorage`（例如 key `vocabSource`）讀取，沒有就預設 `'cap'`（維持現有使用者的既有體驗不變）。
  - 新增 `setSource(source: VocabSource)` 方法，寫入 state 與 `localStorage`。
  - `allWords` 的載入邏輯改成依 `source` 決定要 fetch 哪個檔案：`'cap'` → `data/vocab.cleaned.json`（現況不變），`'gsat'` → `data/vocab.gsat.cleaned.json`（M5-S1 已產出）。**`source` 改變時要重新 fetch 對應資料**（`useEffect` 依賴要包含 `source`），並在切換期間比照現有 `isLoading` 邏輯處理載入中狀態。
  - `AppContextValue` 介面新增 `source`、`setSource` 到回傳值。

### 2. 批次記住來源，畫面只顯示目前來源的批次

- `src/types/batch.ts`：`Batch` 介面新增 `source: VocabSource`。
- `src/store/AppContext.tsx` 的 `createBatch()`：建立時帶入目前的 `source`（同一個 provider 內可以直接讀 state）。
- 既有 `localStorage` 裡舊批次沒有 `source` 欄位，讀取時（`loadFromLS`）沒有這個欄位就視為 `'cap'`，不用寫遷移腳本，讀取當下容錯即可（例如 `batch.source ?? 'cap'` 在需要用到的地方處理，或在載入時統一補上預設值都可以，你選一種一致的做法）。
- `src/pages/HomePage.tsx`：「繼續上次」卡片與「歷史批次」列表都只顯示 `batch.source === source`（目前所選來源）的批次，不要讓學測模式下看到會考的批次（反之亦然）——這是避免使用者對「歷史批次」列表感到混淆的關鍵。
- `src/pages/BatchHubPage.tsx`：進入某個 batch id 的頁面時，如果該 batch 的 `source` 跟目前 `AppContext` 的 `source` 不一致（例如使用者直接照網址進入、或透過瀏覽器上一頁回到舊網址），要怎麼處理你可以自行決定合理的方式（例如自動把目前 `source` 切換成該批次的來源，或顯示提示），只要不要讓使用者看到「翻牌卡的字」跟「目前選的來源」對不上即可。

### 3. 成績與統計依來源隔離（見上方⚠️風險說明，這是本片重點）

- `src/pages/ExamResultPage.tsx`：`wordStats` 文件 ID 改用來源前綴（`${source}__${record.word}`），`examResults` 文件加 `source` 欄位；`source` 從 `useApp()` 的 `AppContext` 取得目前值。
- `src/pages/WordStatsPage.tsx`：只讀取/顯示目前 `source` 對應的 `wordStats`（用文件 ID 前綴或 `source` 欄位過濾，讀完整個 collection 後在前端 filter 即可，不用改 Firestore 查詢語法，資料量不大）。
- `src/pages/ExamHistoryPage.tsx`：讀取後過濾/標示 `source`；每筆成績列旁邊加一個小標籤顯示「會考」或「學測」（畫面上要能一眼分辨，尤其如果之後畫面同時顯示兩種來源的舊資料時不會混淆——但**功能邏輯上這片只需要正確標示與（可選）過濾，不強制要求做「只看目前來源」的篩選開關**，如果你覺得順手可以加，不強制）。
- `src/services/exam.ts` 的 `generateReviewExam()`（錯題複習卷）目前吃 `wordStats: WordStat[]` 做候選池，呼叫端（`WordStatsPage.tsx`）已經在上一步把 `wordStats` 過濾成只剩目前來源，所以 `generateReviewExam()` 本身不用改。

### 4. 來源切換 UI

- 在 `HomePage.tsx` 加一個清楚可見的來源切換元件（例如頂部兩個分頁式按鈕「會考」／「學測」，仿照專案裡其他地方的 Chip／Tab 視覺風格，`BatchBuilderPage.tsx` 裡的 `Chip` 元件可以參考但不用強制重用同一個元件）。
- 切換來源後，畫面上依賴 `allWords`／`batches` 的內容（首頁的「歷史批次」、批次建立器的單字清單等）都要正確反映新來源，不需要整頁重新整理（`AppContext` state 變了、React 重新 render 即可）。
- 切換來源時，如果目前有「進行中」的狀態（例如剛好在 `BatchBuilderPage` 選了幾個字還沒建立批次），你可以決定要不要清空這些暫存的勾選狀態（建議清空，避免跨來源的單字混進同一個批次），但這不是本片的核心驗收點，簡單處理即可。

### 5. 測試

- `npm run lint`、`npm run build` 要過。
- 延續專案既有的 Playwright 自我驗證習慣（`AGENTS.md`「專案技術要點」），新增/調整 e2e 測試涵蓋：切換到學測後批次建立器只看得到學測單字、建立學測批次後翻牌卡與考試出題只出現學測單字、切回會考後看不到學測批次。

## 邊界（本切片不做）

- 不改 `src/services/exam.ts` 既有的出題演算法邏輯（`buildQuestion`／`pickDistractors`／`isSpellingCorrect` 等），這些函式已經是純函式，只要傳入正確來源的 `allWords` 即可正常運作。
- 不做「兩個來源的字混在同一批次」的功能——批次建立器在同一時間只操作目前所選來源的單字庫，不提供跨來源勾選。
- 不改 `firestore.rules`（已用萬用字元涵蓋，見上方說明）。
- 不改 M5-S1/S1b 已經產出的資料檔本身（`vocab.gsat.cleaned.json`、`vocab.cleaned.json`），這片只是「讀取」這兩份資料，不修改內容。
- 不動 `BrowserRouter`（不可改回 `HashRouter`）、不動 `vite.config.ts` 的 Workbox `navigateFallbackDenylist`——這兩個都是先前登入問題的根因修復，絕對不要碰。
- 舊資料（M5-S2 上線前寫入、沒有來源標記的 `wordStats`／`examResults`）不用寫遷移腳本，比照上方「過渡處理」用讀取時容錯（視為 `cap`）即可，不用要求 100% 完美回溯。

## 驗收（負責人操作）

1. 打開 App，首頁應該能看到「會考」／「學測」的來源切換。
2. 切到「學測」，進「建立新批次」，確認清單裡看到的字是學測單字庫的內容（例如可以搜尋幾個你知道只在學測版才有 Level 標記的字，確認畫面上有出現）。
3. 用學測單字庫建立一個批次，進翻牌學習，確認卡片內容是學測單字。
4. 進「練習測驗」，確認出的題目只在剛剛學測批次/學測單字庫範圍內（拼字題、選擇題都是學測的字）。
5. 切回「會考」，確認首頁「歷史批次」看不到剛剛建的學測批次；再進批次建立器確認又是熟悉的會考單字庫內容。
6. 若有登入：在學測模式考幾題（含故意答錯），切到會考模式也考幾題答錯同一個字（例如都考到 `unique`），進「單字統計」確認兩邊的錯誤率是分開計算、不會互相加總或覆蓋。
7. 「成績歷史」列表裡能分辨每筆是會考還是學測的成績。
8. iPhone Safari、Android Chrome 各測一次「切換來源→建批次→翻牌→考試」的流程。
9. `npm run lint`、`npm run build` 通過。

## 收工指令（執行層收工必做）

1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果；標記 M5「學測單字庫」全部完成（S1、S1b、S2）；「▶ 下一步」改為「M5 全部完成，等負責人驗收，過了 M1~M5 全部里程碑都完成」。
2. 若有任何偏離本 BRIEF 的改動（尤其是 `wordStats`/`examResults` 來源隔離的具體實作方式）→ 記 `docs/planning/DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟。
4. **完成以上所有事項、且 `npm run lint`／`npm run build` 都通過後，將本次變更 commit 並 push 到遠端（`origin main`）。** commit message 用一句話講清楚這片做了什麼（例如「功能: 新增會考/學測單字庫來源切換」），可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。push 前務必確認 `git status` 沒有不該提交的檔案。若 push 失敗，不要 force push，把卡住的狀況寫清楚在報告裡。
