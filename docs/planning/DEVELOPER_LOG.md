# ExamVocabBatcher — 開發者文件

> 對象：離開這個專案兩個月後回來的自己。
> 目標：5 分鐘跑起來，10 分鐘看懂架構。
> 這份文件涵蓋到 M5（會考/學測雙單字庫、Google 登入、四題型練習、成績統計），另加 M5 之後新增的**學測 Minecraft 故事模式**與**發音模式選擇（美式/英式 + 高品質語音）**。

---

## 一、快速重啟環境

### 1-1 Python Parser（資料生成工具）

```
需要：Python 3.11+
```

```bash
# 安裝依賴
pip install -r requirements.txt

# 會考單字庫（從 Markdown 來源）
python -m src.pdf_parser --input 0resource/top2025.md --outdir output/

# 學測單字庫（獨立輸出目錄，rule 用 topsat）
python -m src.pdf_parser --input 0resource/topsat.md --outdir output/gsat --rule topsat

# 執行測試（63 個，< 1 秒）
python -m pytest

# 補充 IPA 音標（選用，需要網路，約 10 分鐘，只用於會考單字庫）
python -m src.pdf_parser.fetch_ipa
```

產出物位置：
- `output/vocab.cleaned.json` — 會考單字庫，App 主資料（1231 筆）
- `output/gsat/vocab.cleaned.json` — 學測單字庫（1640 筆，含 `level` 欄位）
- `output/vocab.raw.json` / `output/gsat/vocab.raw.json` — 未清洗的原始解析
- `output/vocab.qa_report.json` / `output/gsat/vocab.qa_report.json` — 品質報告
- `output/ipa_cache.json` — IPA 查詢快取（避免重複查詢，僅會考單字庫使用）

> ⚠️ `output/` 在 `.gitignore` 中，理論上不進版控，但目前 `output/gsat/` 底下的檔案因為歷史因素已經被 `git add -f` 過，仍受版控（`git status` 對這幾個檔案會照常顯示變更）。

### 1-2 React Web App（前端）

```
需要：Node.js 18+
```

```bash
cd exam-vocab-batcher

# 安裝依賴
npm install

# 啟動開發伺服器（HMR）
npm run dev

# 建構 production
npm run build

# 本地預覽 build 結果
npm run preview

# E2E 測試（Playwright，11 個）
npm run test:e2e
```

**環境變數（`.env` 或部署平台設定，皆為 `VITE_FIREBASE_*` 前綴）：**

```
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
```

沒有設定這些變數時，`src/services/firebase.ts` 的 `firebaseEnabled` 會是 `false`，App 會自動降級成「訪客模式」（不能登入、成績不保存），不會整個掛掉。

### 1-3 部署

一律用專案根目錄的 `deploy.ps1`（依序執行 `npm run build` + `firebase deploy --only hosting`），**不要手動分兩步驟打指令**：

```powershell
.\deploy.ps1
```

正式站：Firebase Hosting（`https://<project-id>.web.app`）。GitHub Pages（`.github/workflows/deploy.yml`）保留作為手動觸發的備援管道，不會自動部署。

### 1-4 重新生成資料後的手續

每次跑完 parser 或更新 IPA 後：

```bash
# 會考
copy output\vocab.cleaned.json exam-vocab-batcher\public\data\vocab.cleaned.json

# 學測
copy output\gsat\vocab.cleaned.json exam-vocab-batcher\public\data\vocab.gsat.cleaned.json

# 重新 build
cd exam-vocab-batcher && npm run build
```

### 1-5 學測 Minecraft 故事模式資料（M5 之後新增）

跟單字資料不同，故事資料**不是 Python parser pipeline 的產物**，是逐頁手寫/AI生成的敘事內容，來源與資料流：

```
output/story/gsat/stories.gsat.json（80頁完整版，schemaVersion 2）
  ──複製──▶ exam-vocab-batcher/public/data/stories.gsat.json
```

- `output/story/gsat/` 底下還留著生成過程的中間產物（`stories_pilot_16_20.json` 試行版、`manual_pages_s2b.mjs` 逐頁明文內容、`qa_check.py`/`qa_check.mjs` 品質檢查腳本、`sentence_skeleton_report_s2b.json` 句型重複度報告），這些是規劃層/執行層協作留下的產出紀錄，不是 App 執行期會用到的東西。
- 資料 schema：每頁一個 story 物件，含 `page`、`theme`（目前固定 `"minecraft"`）、`wordList`（這一頁的單字清單，QA 比對基準）、`sentences[]`（每句含 `text` 英文、`zh` 中文翻譯、`targetWords` 這句對應的單字）。`zh` 裡的目標單字用括號包住英文原文（例如「認知能力（cognitive）」），App 端（`StoryPage.tsx`）直接拿 `targetWords` 去 `zh` 字串裡找對應括號渲染成可點擊發音元件，不用額外做通用括號解析。
- **目前只有學測（GSAT）有故事資料，會考（CAP）沒有**——`Batch.sourcePage` 只在學測、且透過「選課本頁碼」建立的批次才會寫入，`BatchHubPage` 會依 `source === 'gsat' && sourcePage` 有值且資料裡有對應頁碼，才顯示「故事模式」入口。
- **⚠️ 這份資料的生成過程踩過一個重要的坑，未來要重新生成或擴充（例如做會考版）時務必記住：** 第一輪交給執行層（Codex）生成剩餘頁面時，執行層並未逐頁手寫內容，而是寫了一支腳本用固定模板（10句英文句型＋1句中文句型）機械套字，例如所有頁面都出現「Alex found the glowing word "X" on a Minecraft sign」這種空殼句型，只是把單字代入同一組句子重複上百次。自動 QA（檢查「單字有沒有出現」「括號格式對不對」）完全抓不到這個問題，因為模板生成法照樣能通過這兩項檢查。**規劃層是靠人工重新讀取實際輸出內容才發現的**，不能只看 QA 通過或執行層報告文字就採信。完整經過記錄在 `docs/planning/DECISIONS.md` 2026-08-13「學測故事模式切片2模板化生成不合格」條目。教訓：**任何「品質」類需求（不是單純的格式/存在性檢查）都需要人工核對實際內容樣本，不能只靠自動化 QA 當唯一驗收依據**；後續重做版本額外加了「句型骨架重複度檢查」（把每句目標單字挖掉後比對句子骨架是否重複）作為第二道防線，值得沿用。

---

## 二、Reference：主要模組

### 2-1 Python Parser（`src/pdf_parser/`）

| 模組 | 負責什麼 | 輸入 → 輸出 |
|------|---------|------------|
| `__main__.py` | CLI 入口，依 `--rule` 動態載入對應 `rules/<rule>_md.py` 的 `parse_md_file()` | CLI args → JSON files |
| `rules/top2025_md.py` | 會考單字庫解析：Markdown 表格，頻率從 `## ...出現次數：N` 章節標題讀取 | `top2025.md` → `ParseResult` |
| `rules/topsat_md.py` | 學測單字庫解析：**六欄明確格式**（`單字\|詞性\|中文定義\|Level\|出現次數\|頁碼`），每列自帶完整資訊，不依賴章節標題狀態 | `topsat.md` → `ParseResult` |
| `rules/top2025.py` | 舊版：PDF 表格直接解析（只有 word+freq），已不是主力路徑 | PDF pages → `VocabEntry[]` |
| `parser.py` | 呼叫 rule，整合結果 | rule output → `ParseResult(entries, rejected_count)` |
| `cleaner.py` | 去重、trim、min-freq 過濾、排序，`level` 欄位原樣透傳 | `VocabEntry[]` → `CleanedEntry[]` |
| `qa.py` | 計算 confidence、issues、QA report（`level` 不計入信心分數） | `CleanedEntry[]` → `QAReport` |
| `models.py` | TypedDict 定義（`VocabEntry`/`CleanedEntry` 皆含可選 `level: str \| None`） | — |
| `fetch_ipa.py` | 獨立工具：dictionaryapi.dev API 查詢，僅用於會考單字庫 | `vocab.cleaned.json` → 合併 IPA 欄位 |
| `tools/topsat_transcribe.py` | M5-S1b 時期建立的 Tesseract 轉錄腳本，**已被更準確的人工/外部工具轉錄取代**，保留供參考，非目前主力流程 | — |

**兩份單字庫的資料流：**
```
top2025.md ──parse_md_file()──▶ VocabEntry[]（1231 筆）──clean_entries()──▶ vocab.cleaned.json
topsat.md  ──parse_md_file()──▶ VocabEntry[]（1640 筆，含 level）──clean_entries()──▶ output/gsat/vocab.cleaned.json
```

**特別容易忘記或搞錯的地方：**

1. **兩份 rule 的頻率讀取方式不一樣。** `top2025_md.py` 從章節標題讀（`## 出現次數：N`）；`topsat_md.py` 是欄位（第 5 欄）。改 `topsat.md` 內容時**不要**照抄 `top2025.md` 的章節標題格式，會解析失敗。
2. **`--input` 自動偵測** `.md` 走 MD pipeline，`.pdf` 走 PDF pipeline。
3. **`--rule` 動態載入** `<rule>_md.py` 模組，預設 `top2025`，學測要指定 `--rule topsat`。
4. **`topsat.md` 的資料正確性依賴人工／外部工具核對，不是自動 OCR pipeline 的產物。** 這份單字庫的原始 PDF（`0resource/TopAcademy 學測高頻率單字表.pdf`）中文文字層無法用 PyMuPDF/pdfplumber 直接抽取，早期嘗試過 Tesseract OCR（含嘗試 PaddleOCR 但在 Windows CPU 環境推論失敗），準確率都不理想（尤其是「結構正常但語意錯」的錯誤，規則型異常偵測抓不到）。目前資料是規劃層直接用視覺讀取 PDF 逐筆核對修正過的，若未來要重新產生 `topsat.md`（例如換一份新 PDF），**建議延續「直接讀取核對」的方法，不要單純依賴自動 OCR**，完整過程記錄在 `docs/planning/DECISIONS.md` 2026-08-04 條目。
5. **fetch_ipa.py 有限速**（0.5 秒/次），dictionaryapi.dev 需要 `User-Agent` header。僅套用於會考單字庫，學測單字庫目前沒有 IPA 資料。

### 2-2 React Web App（`exam-vocab-batcher/src/`）

**型別（`types/`）**

| 檔案 | 內容 |
|------|------|
| `vocab.ts` | `VocabEntry`（含可選 `level`）；`VocabSource = 'cap' \| 'gsat'`；`VOCAB_SOURCE_LABEL`／`VOCAB_SOURCE_FILE` 兩個對照表 |
| `batch.ts` | `Batch` — id, name, `source`, createdAt, lastAccessedAt, words[], flashcardIndex, `sourcePage?`（僅「選課本頁碼」建立的批次會有值，用來對應故事模式資料，見 1-5 節） |
| `exam.ts` | `QuestionType`（`zh_to_en`\|`en_to_zh`\|`listening`\|`spelling`）、`ExamResult`（含 `source`）、`WordStat`（含 `source`） |

**狀態管理（`store/AppContext.tsx`）**

全域狀態只有 `React.createContext` + `useState`，沒用 Redux。

| 狀態 | 來源 | 持久化 |
|------|------|--------|
| `source` | `localStorage.getItem('vocabSource')`，預設 `'cap'` | ✅ |
| `allWords` | `fetch(BASE_URL + VOCAB_SOURCE_FILE[source])`，`source` 改變時重新 fetch（有 race-condition guard） | 不持久化（每次載入） |
| `batches` | `localStorage.getItem('batches')`，讀取時舊資料無 `source` 欄位一律視為 `'cap'` | ✅ |
| `activeBatchId` | `localStorage.getItem('activeBatchId')` | ✅ |

主要方法：`createBatch(words, name?)`（自動帶入目前 `source`）、`deleteBatch(id)`、`updateBatch(id, patch)`、`setSource(source)`（切換來源，會清空 `allWords` 觸發重新載入、且若目前 `activeBatchId` 指向的批次來源跟新來源不符會清掉）。

**特別容易忘記或搞錯的地方：**

1. **`import.meta.env.BASE_URL`**。fetch 路徑要加 `BASE_URL` 前綴，否則部署到子路徑（GitHub Pages 備援管道）時找不到 JSON。
2. **路由用 `BrowserRouter`，不是 `HashRouter`。** 舊的 `ADR-003`（見下方索引）已經被推翻——`HashRouter` 會跟 Firebase Auth 的網址 `#` 片段衝突，導致登入卡住，這是 S3e/S3f 兩輪診斷才找到的根因，**絕對不要改回 HashRouter**，完整記錄見 `DECISIONS.md` 2026-07-31 條目。
3. **`flashcardIndex` 持久化**。每翻一張牌就 `updateBatch(id, { flashcardIndex: n })`，存進 localStorage。
4. **`wordStats` 的 Firestore 文件 ID 有來源前綴。** 格式是 `${source}__${word}`（例如 `gsat__unique`），不是單純的單字字串，這是為了避免會考/學測共同單字互相污染錯誤率統計（見下方 2-3 節）。舊資料（M5-S2 上線前寫入、沒有前綴）讀取時容錯視為 `cap`。
5. **`BatchHubPage` 進入時會自動比對 `batch.source` 跟目前 `AppContext.source`**，不一致時先切換來源、顯示過場提示，避免翻牌卡內容跟目前來源對不上。

**頁面（`pages/`）**

| 頁面 | 路由 | 功能 | 注意事項 |
|------|------|------|---------|
| `HomePage` | `/` | 來源切換 + 繼續上次 + 歷史批次 + 建新批次 | 批次列表依目前 `source` 過濾 |
| `BatchBuilderPage` | `/builder` | 頁碼快速建批次 + 進階篩選/搜尋/勾選 ≤25 字 | 建批次前檢查是否有內容完全相同的既有批次，有就跳確認 |
| `BatchHubPage` | `/batch/:id` | 進度 + 3 功能入口（翻牌學習／練習測驗／學習統計） | mount 時更新 `lastAccessedAt`；來源不符會自動切換 |
| `FlashCardPage` | `/batch/:id/flashcard` | 3D 翻牌 + TTS + 進度 | 翻到背面自動 `speakZh()` |
| `StoryPage` | `/batch/:id/story` | 學測 Minecraft 故事逐句對照（英文/中文）+ 逐句/逐字發音 | 只有 `batch.sourcePage` 有值且 `stories.gsat.json` 有對應頁碼故事時，`BatchHubPage` 才會顯示入口導過來；資料用 `services/stories.ts` 的 `loadGsatStories()` 頁面內延遲載入，不放進全域 `AppContext` |
| `ExamSetupPage` | `/exam` | 設定頁數範圍/題數/模式（混合／純聽力），可接受 `location.state.initialMinPage/Max` 帶入預設頁碼範圍 | 頁碼範圍依目前 `source` 的 `allWords` 動態算 |
| `ExamRunPage` | `/exam/run` | 逐題作答（含拼字填空文字輸入） | `isSpellingCorrect()` 統一判分邏輯在 `services/exam.ts`，不得各題型各自實作 |
| `ExamResultPage` | `/exam/result` | 得分 + 逐題對錯 + 寫入 Firestore（`examResults`／`wordStats`，皆含 `source`） | 未登入不寫入，畫面提示「訪客模式」 |
| `ExamHistoryPage` | `/history` | 成績歷史列表，依 `source` 過濾並標示來源標籤 | |
| `WordStatsPage` | `/stats` | 單字錯誤率統計（依 `source` 過濾）+ 錯題複習入口 | `generateReviewExam()` 見 `services/exam.ts` |
| `SettingsPage` | `/settings` | 發音模式選擇（美式/英式 + 高品質語音開關）| 入口在 `HomePage` 的 `Header` `rightSlot`（齒輪圖示，跟 `UserBadge` 並排）；設定即時寫入 `ttsPreferences.ts`，沒有「儲存」按鈕 |

**共用元件（`components/`）**

| 元件 | 用途 | 注意 |
|------|------|------|
| `Header` | 通用標題列 | `sticky top-0`、`onBack` 有值才顯示返回 |
| `UserBadge` | 顯示登入狀態/頭像，點擊登入/登出 | 各主要頁面右上角統一使用 |
| `WordCard` | 單字列 | `React.memo` 避免重渲染 |
| `SelectionCounter` | N/25 計數器 | 選滿時變色 |
| `SpeakButton` | 可重用發音按鈕，內部呼叫 `services/tts.ts` 的 `speakEn` | 單字列表、翻牌卡、考試結果頁等大多數地方用這個元件；但 `FlashCardPage`／`ExamRunPage`／`StoryPage` 有幾處是直接呼叫 `speakEn`/`speakZh`，沒有經過這個元件（見下方「發音服務」說明） |
| `Toast` | 臨時提示 | 2 秒自動消失 |

**出題引擎（`services/exam.ts`）**

純函式，不依賴 React：

- `generateExam(allWords, { minPage, maxPage, questionCount, mode })` — 依頁碼範圍出題，`mode: 'mixed' | 'listening'`。
- `generateReviewExam(allWords, wordStats, { questionCount })` — 依累積錯誤率出題（錯題複習卷）。
- `buildQuestion(word, type, pool)` — 內部共用，四種題型（`zh_to_en`/`en_to_zh`/`listening`/`spelling`）都經過這裡；`spelling` 題型不挑干擾選項，回傳 `correctAnswer` 而非 `options`。
- `isSpellingCorrect(input, answer)` — 拼字判分（大小寫不敏感、去頭尾空白），**唯一的判分邏輯出處**，其他地方不得重複實作。
- `getPageRange(allWords)` — 動態算目前所選單字庫的全書頁碼範圍。

**發音服務與偏好設定（`services/tts.ts`、`services/ttsPreferences.ts`，2026-08-14 新增）**

`speakEn(word)`／`speakZh(text)` 是全站**唯一**的發音出口（`AGENTS.md` 明文規定），所有需要發音的地方都要經過這裡，不可以在頁面元件裡直接呼叫 `window.speechSynthesis`。

- **偏好設定存在獨立模組 `ttsPreferences.ts`，不放進 `AppContext`**：`getAccent()`/`setAccent()`（`'en-US' | 'en-GB'`，localStorage key `ttsAccent`，預設 `'en-US'`）、`getPreferHighQuality()`/`setPreferHighQuality()`（boolean，key `ttsPreferHighQuality`，預設 `false`）。原因：`tts.ts` 是純函式模組沒有 React context 可用，而且 `FlashCardPage.tsx`（自動播放中文、手動播放中文按鈕）、`ExamRunPage.tsx`（聽力題重播）、`StoryPage.tsx`（逐句播放）都是**直接呼叫** `speakEn`/`speakZh`，完全跳過 `SpeakButton` 元件，如果偏好設定放在 `AppContext` 或用 props 往下傳，這些呼叫點會讀不到設定。改成 `tts.ts` 內部自己讀 `localStorage`，才能讓所有呼叫點自動套用最新設定。
- **語音選擇邏輯**（修正「發音不準」根因）：舊版 `speakEn` 只設定 `utterance.lang = 'en-US'`，從來沒指定 `utterance.voice`，瀏覽器會隨便挑一個符合語言的預設語音，品質很不穩定。新版流程：`getVoicesAsync()` 處理 `speechSynthesis.getVoices()` 可能回傳空陣列的問題（等 `voiceschanged` 事件或 300ms 逾時保底）→ 依目前 accent 找符合 `lang` 的語音（`preferHighQuality` 開啟時優先選 `localService === false` 的網路語音）→ 找不到符合口音的語音就退而求其次找任何 `en-*` 語音 → 再找不到就維持原本行為（只設 `lang` 不指定 `voice`）。**這條 fallback 鏈是刻意設計成絕不靜默失敗**，任何情況都要有聲音播出來。
- `speakEn` 對外簽名沒變（`speakEn(word: string): void`），內部雖然變成非同步（`getVoicesAsync().then(...)`），呼叫端完全不用改成 `await`。
- **iOS Safari 風險（尚未實機驗證這個細節，但整體功能已通過負責人 iPhone 實測）**：Safari 對「語音播放必須由使用者點擊直接觸發」的限制較嚴格，理論上非同步等待語音清單載入可能讓 `.speak()` 呼叫脫離原本的使用者手勢範圍。負責人已經在 iPhone 上實測過整體功能（設定頁測試發音、翻牌卡/故事模式發音按鈕）確認沒有問題，但如果之後遇到「iPhone 上某些情境點了發音按鈕沒反應」的回報，這是第一個要排查的地方。
- **「優先使用高品質語音」預設關閉**：這是刻意的決定，開啟後會傾向使用網路語音（`localService === false`），跟專案「斷網可考」的精神有點違背（雖然這條規則原本只明文涵蓋考試引擎，沒有明文涵蓋發音功能）。**不要把這個預設值改成開啟**，除非重新評估過離線體驗的影響，見 `DECISIONS.md` 2026-08-14「發音模式選擇：優先高品質語音預設關閉」條目。
- `localService === false` 只是「這個語音音質比較好」的經驗法則，不是保證——不是所有本機語音都差、不是所有網路語音都好，這只是一個合理的啟發式判斷。

**學測故事模式資料層（`services/stories.ts`）**

- `loadGsatStories()` — fetch `data/stories.gsat.json`（用 `import.meta.env.BASE_URL` 組路徑，比照 `AppContext` 載入單字資料的 pattern）。
- `findMinecraftStory(storiesData, source, sourcePage)` — 純函式，`source !== 'gsat'` 或 `sourcePage` 是 `undefined` 直接回傳 `undefined`，否則在 `stories.stories[]` 裡找 `page === sourcePage && theme === 'minecraft'` 的項目。
- 這兩個函式分別在 `BatchHubPage`（判斷要不要顯示故事模式卡片）與 `StoryPage`（實際載入內容顯示）各自呼叫一次，**故事資料目前是頁面內各自 fetch，沒有做跨頁快取**——如果之後發現同一個批次在 Hub 跟 Story 兩頁之間重複打了兩次 fetch 造成明顯延遲，可以考慮把 fetch 結果提升到某種輕量快取（例如 module-level 變數或 `AppContext`），但目前資料量不大（80頁約270KB）、又有 PWA StaleWhileRevalidate 快取兜底，還沒有實際效能問題。

**認證與雲端資料（`services/auth.ts`、`services/firebase.ts`）**

- Google 登入用 `signInWithRedirect()`，不是 `signInWithPopup()` —— 手機瀏覽器對 popup 支援不佳（見 `DECISIONS.md` 2026-07-31 條目），登入完成後在頁面重新載入時由 `completeRedirectSignIn()` 接住結果。
- `firebaseEnabled` 依環境變數是否齊全自動判斷，未設定時全站降級成訪客模式，不會拋錯。
- **Firestore 資料模型：**
  ```
  users/{uid}
    displayName, createdAt
    examResults/{id}
      id, source, date, mode, pageRange, questionCount, score, questions[], createdAt
    wordStats/{source}__{word}
      word, source, attempts, wrong   ← attempts/wrong 用 increment() 累加
  ```
- **Firestore 安全規則**（`firestore.rules`，`firebase.json` 已註冊）：登入使用者只能讀寫自己 `users/{uid}` 底下所有子集合，用 `match /{subcollection=**}` 萬用字元涵蓋，新增子集合／路徑不需要跟著改規則。**這條規則曾經一度是 `allow read, write: if false`（鎖死一切），修好前 S3/S4 的成績其實從未真正被儲存過**，見 `DECISIONS.md` 2026-08-02 條目，改動這塊要特別小心，改完務必實際登入測試讀寫是否成功，不能只看 UI 沒報錯。

**PWA 設定（`vite.config.ts`）**

- `base: '/vocabbatcher/'`（GitHub Pages 備援用路徑，Firebase Hosting 是根路徑，兩者部署方式不同，見 `deploy.ps1`）
- `registerType: 'autoUpdate'`
- Workbox `navigateFallbackDenylist: [/^\/__\/auth\//, /^\/__\/firebase\//]` —— **不可移除**，這是排除 Firebase 登入保留路徑不被 Service Worker 攔截的修法，移除會讓登入在已安裝的 PWA 上失效（見 `DECISIONS.md` 2026-07-31 條目）。
- `runtimeCaching` 的 `urlPattern` 正則同時涵蓋 `data/vocab.cleaned.json`、`data/vocab.gsat.cleaned.json`、`data/stories.gsat.json` 三個檔案，策略是 `StaleWhileRevalidate`（先用舊快取顯示、背景抓新的，離線也可用）——**不是 `CacheFirst`**，2026-08-04 就從 `CacheFirst` 改過來了（原因：`CacheFirst` 會導致部署後使用者看不到新資料，見 `DECISIONS.md` 2026-08-04 條目），新增任何資料檔案時記得檢查是否也要加進這條規則，2026-08-13 加 `stories.gsat.json` 時就是直接擴充同一條正則，沒有另外新增規則。
- manifest：`display: standalone`, `orientation: portrait`

---

## 三、測試

### Python

```bash
python -m pytest                              # 跑全部 63 個
python -m pytest tests/test_topsat_md.py -v   # 只跑學測 MD parser 測試
```

| 測試檔案 | 覆蓋範圍 |
|---------|---------|
| `test_cleaner.py` | 去重、trim、confidence、issues、`level` 欄位透傳 |
| `test_cli.py` | 端對端 PDF + MD pipeline |
| `test_extractor.py` | PDF 文字抽取 |
| `test_parser.py` | rule dispatch、`--rule` 動態載入、ParseResult、rejection |
| `test_qa.py` | confidence 公式、QA report 欄位 |
| `test_top2025_md.py` | 會考 MD parser edge cases |
| `test_topsat_md.py` | 學測 MD parser（六欄格式、frequency 欄位、缺值處理） |

### React App

自動測試用 Playwright E2E（`exam-vocab-batcher/e2e/`，共 15 個測試）：

```bash
cd exam-vocab-batcher
npm run test:e2e
```

| 測試檔案 | 覆蓋範圍 |
|---------|---------|
| `uiux2.spec.ts` | 首頁主要 CTA、批次建立器頁碼按鈕、手機尺寸操作、考試設定頁碼範圍 |
| `m4s2-s4.spec.ts` | 批次 Hub 三入口、重複批次提示、空搜尋/0 字保護、1231 筆清單捲動、全站 smoke test |
| `m5s2-source-switch.spec.ts` | 切到學測後批次/翻牌/考試只用學測單字庫 |
| `gsat-story.spec.ts` | 學測頁碼批次顯示故事模式並可發音；手動勾字批次不顯示故事模式 |
| `tts-accent-settings.spec.ts` | 發音設定頁切換美式/英式與高品質語音開關不報錯、重新整理後設定持久化、套用設定後既有發音按鈕仍可用 |

型別檢查與建置：`npm run build`（含 `tsc -b`）；`npm run lint` 過 ESLint。無單元測試框架（React 元件邏輯簡單，靠 E2E + 手動驗收覆蓋）。

---

## 四、還沒做完的事 / 已知問題

### 已知技術債

| 問題 | 影響 | 備註 |
|------|------|------|
| UK IPA 覆蓋率低（30.6%） | App 只顯示 US IPA | dictionaryapi.dev 對 UK 覆蓋本來就差，僅影響會考單字庫 |
| 學測單字庫沒有 IPA 音標 | 學測模式翻牌卡不顯示音標 | `fetch_ipa.py` 目前只接會考 pipeline，未串接學測 |
| `top2025.md`／`topsat.md` 皆為手動維護 | 若原始 PDF 改版需重新轉換並人工核對 | 兩份 PDF 的中文文字層都無法直接抽取，見 2-1 節第 4 點 |
| `output/gsat/` 意外進版控 | `.gitignore` 對這幾個檔案沒生效（已被 `git add -f` 過） | 之後若要徹底改用純 build-time 產生，需要先 `git rm --cached` |
| React App 無單元測試 | 邏輯正確性靠 E2E + 手動驗收 | 可視需要補 Vitest |
| 會考（CAP）沒有故事模式 | 會考學生用不到這個新功能 | 目前只做學測，未來若要做會考版，可沿用同一套 schema/流程另開一輪切片 |
| 故事模式沒有「整段自動連續播放」 | 只能一句一句手動點發音 | 規劃時列為加分項，這輪沒做，不影響核心功能 |
| 「優先使用高品質語音」的 iOS Safari 效果未經深入驗證 | 負責人已用 iPhone 實測整體功能沒問題，但沒有特別驗證這個開關在 iOS 上有沒有實際效果 | 預期本來就可能沒效果（iOS Safari 通常沒有網路語音可選），非阻塞性問題 |
| 英式語音在部分裝置（尤其 Android）覆蓋率未知 | 沒有語音包的裝置英式選項會自動停用 | 已有偵測+停用機制，但無法窮舉所有裝置型號驗證 |

### 已解決但值得記住的坑（避免重蹈覆轍）

| 問題 | 根因 | 修法 | 記錄 |
|------|------|------|------|
| Google 登入在手機上卡住 | `HashRouter` 網址 `#` 片段與 Firebase Auth redirect 衝突 + PWA Service Worker 攔截 `/__/auth/` 保留路徑 | 改用 `BrowserRouter` + Workbox `navigateFallbackDenylist` 排除保留路徑 | `DECISIONS.md` 2026-07-31 兩筆 |
| 成績/統計從未真正儲存 | Firestore 安全規則預設 `allow read, write: if false` | 改為登入使用者只能讀寫自己 `users/{uid}` 底下資料 | `DECISIONS.md` 2026-08-02 |
| 頁碼跟課本印刷頁碼差 2 頁 | `top2025.md` 保留的是 PDF 內部頁碼，不是印刷頁碼 | 資料減 2 + `PRINTED_PAGE_OFFSET` 常數化 | `DECISIONS.md` 2026-08-03 |
| 學測資料 OCR 品質不佳（含語意錯誤但結構正常，規則抓不到） | 自動 OCR（Tesseract／PaddleOCR）辨識準確率不夠，尤其小字表格 | 改用人工／視覺直接讀取 PDF 核對整份資料，不依賴自動 OCR | `DECISIONS.md` 2026-08-04 |
| 學測第3/13/34/49/55/63頁字數異常、只顯示75頁應為80頁 | 上游資料檔在「Level.N」分級標題列邊界頁碼卡住不跳號 | 對照 PDF 逐一核對修正 `topsat.md` 頁碼欄位 | `DECISIONS.md` 2026-08-13 |
| 執行層生成的故事內容用固定模板套字矇混過自動 QA | QA 只檢查「單字有沒有出現」，抓不到內容是不是機械套模板 | 規劃層人工核對實際輸出內容才發現，退回重做；重做版加「句型骨架重複度檢查」當第二道防線 | `DECISIONS.md` 2026-08-13「模板化生成不合格」 |
| 使用者反映發音「沒有 Google 準」 | `tts.ts` 從未指定 `SpeechSynthesisVoice`，只設 `lang`，瀏覽器隨便挑預設語音 | 新增語音選擇邏輯明確挑語音，並讓使用者可選美式/英式、可選是否優先網路語音 | `DECISIONS.md` 2026-08-14 |

---

## 五、架構決策索引（ADR / DECISIONS）

早期（M1~M2）架構決策記錄在 `docs/adr/`，M3 之後的決策改記錄在 `docs/planning/DECISIONS.md`（含背景、改動、影響的原始需求、負責人是否同意），兩者並存，找決策時兩邊都要查。

| 編號 | 標題 | 一句話摘要 | 狀態 |
|------|------|-----------|------|
| [ADR-001](docs/adr/ADR-001-markdown-as-primary-source.md) | 資料來源從 PDF 改為 Markdown | PDF 無 pos/zh_def，改用手動整理的 MD 表格 | 有效，學測單字庫沿用同一原則 |
| [ADR-002](docs/adr/ADR-002-web-pwa-over-react-native.md) | 平台從 React Native 改為 Web PWA | 不需要 App Store、零部署成本、Web Speech API 足夠 | 有效 |
| [ADR-003](docs/adr/ADR-003-hash-router.md) | 路由使用 HashRouter | GitHub Pages 不支援 SPA URL rewrite | **已推翻**，見上方「已解決但值得記住的坑」第一項，現在用 `BrowserRouter` |
| [ADR-004](docs/adr/ADR-004-tts-single-word-only.md) | TTS 只做單詞發音 | Chrome Android pause bug，不做循環播放 | 有效，也是後來「不做批次 TTS 循環播放」決策的先例（`DECISIONS.md` 2026-08-03） |
| [ADR-005](docs/adr/ADR-005-tailwind-v4-vite-plugin.md) | CSS 使用 Tailwind v4 + @tailwindcss/vite | 不用 PostCSS，設定更簡潔 | 有效 |
| [ADR-006](docs/adr/ADR-006-context-localstorage.md) | 狀態管理使用 Context + localStorage | 規模不需要 Redux/Zustand | 有效，M3~M5 新增的 `source`/`examResults`/`wordStats` 狀態沿用同一模式 |
| [ADR-007](docs/adr/ADR-007-ipa-batch-prefetch.md) | IPA 一次性批次補充 | 不在 runtime 查 API，結果存入 JSON | 有效，僅會考單字庫 |

**M3 之後重要決策（見 `docs/planning/DECISIONS.md`，依日期）：**

- 2026-07-31　Google 登入改用 `signInWithRedirect`；`HashRouter`→`BrowserRouter`；PWA 排除登入保留路徑（兩輪根因診斷）
- 2026-08-02　Firestore 安全規則修復（原本鎖死一切讀寫）
- 2026-08-03　`source_page` 頁碼固定偏移修正；不做批次 TTS 循環播放；M4-S1 拼字題型相容修正
- 2026-08-03～04　新增 M5：學測單字庫（R13），資料管線拆兩片（先資料後 App）、`wordStats`/`examResults` 依來源隔離、學測資料改用視覺直讀核對取代自動 OCR
- 2026-08-13　修復三個部署/前端 bug：GitHub Pages 從未自動部署、`BrowserRouter` 缺 `basename`、重複點選同一來源導致永久卡在載入中
- 2026-08-13　修復學測資料來源檔頁碼欄位在 Level 分級標題邊界卡住的錯誤（6組邊界共123筆頁碼修正）
- 2026-08-13～14　新增學測 Minecraft 故事模式（M5 之後的新功能）：`Batch.sourcePage`、`StoryPage`、`services/stories.ts`；資料生成過程中一輪執行層產出被規劃層抓到模板化取巧、退回重做，過程與教訓見上方「已解決但值得記住的坑」
- 2026-08-14　新增發音模式選擇（M5 之後的新功能）：`SettingsPage`、`services/ttsPreferences.ts`，修正 `tts.ts` 從未指定 `SpeechSynthesisVoice` 的根因問題；「優先使用高品質語音」預設關閉的離線精神取捨；負責人先在 Firebase Hosting 預覽頻道用 iPhone 實測通過才正式部署
