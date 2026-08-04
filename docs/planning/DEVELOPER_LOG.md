# ExamVocabBatcher — 開發者文件

> 對象：離開這個專案兩個月後回來的自己。
> 目標：5 分鐘跑起來，10 分鐘看懂架構。
> 這份文件涵蓋到 M5（會考/學測雙單字庫、Google 登入、四題型練習、成績統計）。

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
| `batch.ts` | `Batch` — id, name, `source`, createdAt, lastAccessedAt, words[], flashcardIndex |
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
| `ExamSetupPage` | `/exam` | 設定頁數範圍/題數/模式（混合／純聽力），可接受 `location.state.initialMinPage/Max` 帶入預設頁碼範圍 | 頁碼範圍依目前 `source` 的 `allWords` 動態算 |
| `ExamRunPage` | `/exam/run` | 逐題作答（含拼字填空文字輸入） | `isSpellingCorrect()` 統一判分邏輯在 `services/exam.ts`，不得各題型各自實作 |
| `ExamResultPage` | `/exam/result` | 得分 + 逐題對錯 + 寫入 Firestore（`examResults`／`wordStats`，皆含 `source`） | 未登入不寫入，畫面提示「訪客模式」 |
| `ExamHistoryPage` | `/history` | 成績歷史列表，依 `source` 過濾並標示來源標籤 | |
| `WordStatsPage` | `/stats` | 單字錯誤率統計（依 `source` 過濾）+ 錯題複習入口 | `generateReviewExam()` 見 `services/exam.ts` |

**共用元件（`components/`）**

| 元件 | 用途 | 注意 |
|------|------|------|
| `Header` | 通用標題列 | `sticky top-0`、`onBack` 有值才顯示返回 |
| `UserBadge` | 顯示登入狀態/頭像，點擊登入/登出 | 各主要頁面右上角統一使用 |
| `WordCard` | 單字列 | `React.memo` 避免重渲染 |
| `SelectionCounter` | N/25 計數器 | 選滿時變色 |
| `SpeakButton` | 可重用發音按鈕 | 單字列表、翻牌卡、考試結果頁皆用同一個元件 |
| `Toast` | 臨時提示 | 2 秒自動消失 |

**出題引擎（`services/exam.ts`）**

純函式，不依賴 React：

- `generateExam(allWords, { minPage, maxPage, questionCount, mode })` — 依頁碼範圍出題，`mode: 'mixed' | 'listening'`。
- `generateReviewExam(allWords, wordStats, { questionCount })` — 依累積錯誤率出題（錯題複習卷）。
- `buildQuestion(word, type, pool)` — 內部共用，四種題型（`zh_to_en`/`en_to_zh`/`listening`/`spelling`）都經過這裡；`spelling` 題型不挑干擾選項，回傳 `correctAnswer` 而非 `options`。
- `isSpellingCorrect(input, answer)` — 拼字判分（大小寫不敏感、去頭尾空白），**唯一的判分邏輯出處**，其他地方不得重複實作。
- `getPageRange(allWords)` — 動態算目前所選單字庫的全書頁碼範圍。

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
- `data/vocab.cleaned.json`、`data/vocab.gsat.cleaned.json` 皆走 `CacheFirst`（離線可用）。
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

自動測試用 Playwright E2E（`exam-vocab-batcher/e2e/`，共 11 個測試）：

```bash
cd exam-vocab-batcher
npm run test:e2e
```

| 測試檔案 | 覆蓋範圍 |
|---------|---------|
| `uiux2.spec.ts` | 首頁主要 CTA、批次建立器頁碼按鈕、手機尺寸操作、考試設定頁碼範圍 |
| `m4s2-s4.spec.ts` | 批次 Hub 三入口、重複批次提示、空搜尋/0 字保護、1231 筆清單捲動、全站 smoke test |
| `m5s2-source-switch.spec.ts` | 切到學測後批次/翻牌/考試只用學測單字庫 |

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
| `USER_MANUAL.md`／`DEVELOPER_LOG.md` 只到 M5 | 後續新里程碑要記得同步更新 | 見 `AGENTS.md`「★ 成果文件交付閘」 |

### 已解決但值得記住的坑（避免重蹈覆轍）

| 問題 | 根因 | 修法 | 記錄 |
|------|------|------|------|
| Google 登入在手機上卡住 | `HashRouter` 網址 `#` 片段與 Firebase Auth redirect 衝突 + PWA Service Worker 攔截 `/__/auth/` 保留路徑 | 改用 `BrowserRouter` + Workbox `navigateFallbackDenylist` 排除保留路徑 | `DECISIONS.md` 2026-07-31 兩筆 |
| 成績/統計從未真正儲存 | Firestore 安全規則預設 `allow read, write: if false` | 改為登入使用者只能讀寫自己 `users/{uid}` 底下資料 | `DECISIONS.md` 2026-08-02 |
| 頁碼跟課本印刷頁碼差 2 頁 | `top2025.md` 保留的是 PDF 內部頁碼，不是印刷頁碼 | 資料減 2 + `PRINTED_PAGE_OFFSET` 常數化 | `DECISIONS.md` 2026-08-03 |
| 學測資料 OCR 品質不佳（含語意錯誤但結構正常，規則抓不到） | 自動 OCR（Tesseract／PaddleOCR）辨識準確率不夠，尤其小字表格 | 改用人工／視覺直接讀取 PDF 核對整份資料，不依賴自動 OCR | `DECISIONS.md` 2026-08-04 |

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
