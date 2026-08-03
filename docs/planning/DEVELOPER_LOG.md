# ExamVocabBatcher — 開發者文件

> 對象：離開這個專案兩個月後回來的自己。
> 目標：5 分鐘跑起來，10 分鐘看懂架構。

---

## 一、快速重啟環境

### 1-1 Python Parser（資料生成工具）

```
需要：Python 3.11+
```

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行 parser（從 Markdown 來源）
python -m src.pdf_parser --input 0resource/top2025.md --outdir output/

# 執行測試（53 個，< 1 秒）
python -m pytest

# 補充 IPA 音標（選用，需要網路，約 10 分鐘）
python -m src.pdf_parser.fetch_ipa
```

產出物位置：
- `output/vocab.cleaned.json` — App 使用的主資料（1231 筆）
- `output/vocab.raw.json` — 未清洗的原始解析
- `output/vocab.qa_report.json` — 品質報告
- `output/ipa_cache.json` — IPA 查詢快取（避免重複查詢）

> ⚠️ `output/` 在 `.gitignore` 中，不進版控。

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
# → 打開 http://localhost:4173/vocabbatcher/
```

### 1-3 重新生成資料後的手續

每次跑完 parser 或更新 IPA 後：

```bash
# 1. 複製新資料到 App
copy output\vocab.cleaned.json exam-vocab-batcher\public\data\vocab.cleaned.json

# 2. 重新 build
cd exam-vocab-batcher && npm run build
```

---

## 二、Reference：主要模組

### 2-1 Python Parser（`src/pdf_parser/`）

| 模組 | 負責什麼 | 輸入 → 輸出 |
|------|---------|------------|
| `__main__.py` | CLI 入口，4 步驟 pipeline | CLI args → JSON files |
| `rules/top2025_md.py` | **主力**：Markdown 表格解析 | `top2025.md` → `ParseResult` |
| `rules/top2025.py` | 舊版：PDF 表格解析（只有 word+freq）| PDF pages → `VocabEntry[]` |
| `parser.py` | 呼叫 rule，整合結果 | rule output → `ParseResult(entries, rejected_count)` |
| `cleaner.py` | 去重、trim、min-freq 過濾、排序 | `VocabEntry[]` → `CleanedEntry[]` |
| `qa.py` | 計算 confidence、issues、QA report | `CleanedEntry[]` → `QAReport` |
| `models.py` | TypedDict 定義 | — |
| `fetch_ipa.py` | 獨立工具：dictionaryapi.dev API 查詢 | `vocab.cleaned.json` → 合併 IPA 欄位 |

**資料流：**
```
top2025.md
    ↓ parse_md_file()
VocabEntry[]  ← 1231 筆，含 word/pos/zh_definition/frequency/source_page
    ↓ clean_entries()
CleanedEntry[] ← 去重、排序、加 confidence/issues
    ↓ json.dump()
vocab.cleaned.json

    ↓ fetch_ipa.py（獨立執行）
vocab.cleaned.json ← 合併 ipa_us/ipa_uk
```

**特別容易忘記或搞錯的地方：**

1. **MD 檔案格式很重要**。頻率來自 `## ...出現次數：N` 的章節標題，不是表格欄位。如果改了標題格式，parser 會解析失敗。
2. **`--input` 自動偵測**。給 `.md` 走 MD pipeline，給 `.pdf` 走 PDF pipeline。不要混淆。
3. **fetch_ipa.py 有限速**（0.5 秒/次）。dictionaryapi.dev 需要 `User-Agent` header，沒給會 403。
4. **IPA 快取**在 `output/ipa_cache.json`。如果改了單字清單要刪除快取重跑嗎？不用——它會自動跳過已快取的字，只查新的。
5. **ParseResult**。`parse_pages()` 回傳 `ParseResult(entries=list, rejected_count=int)`，不是純 list。第一次看會搞混。

### 2-2 React Web App（`exam-vocab-batcher/src/`）

**型別（`types/`）**

| 檔案 | 內容 |
|------|------|
| `vocab.ts` | `VocabEntry` — 對應 vocab.cleaned.json 的每一筆 |
| `batch.ts` | `Batch` — id, name, createdAt, lastAccessedAt, words[], flashcardIndex |

**狀態管理（`store/AppContext.tsx`）**

全域狀態只有 `React.createContext` + `useState`，沒用 Redux。

| 狀態 | 來源 | 持久化 |
|------|------|--------|
| `allWords` | `fetch(BASE_URL + 'data/vocab.cleaned.json')` | 不持久化（每次載入） |
| `batches` | `localStorage.getItem('batches')` | ✅ JSON.stringify |
| `activeBatchId` | `localStorage.getItem('activeBatchId')` | ✅ |

主要方法：`createBatch(words)` → 建立 Batch 並存 localStorage、`deleteBatch(id)`、`updateBatch(id, patch)`。

**特別容易忘記或搞錯的地方：**

1. **`import.meta.env.BASE_URL`**。fetch 路徑要加 `BASE_URL` 前綴，否則 GitHub Pages 上找不到 JSON。
2. **HashRouter**。所有路由都是 `/#/` 開頭。直接在 `App.tsx` 看路由表。
3. **`flashcardIndex` 持久化**。每翻一張牌就 `updateBatch(id, { flashcardIndex: n })`，存進 localStorage。

**頁面（`pages/`）**

| 頁面 | 路由 | 功能 | 注意事項 |
|------|------|------|---------|
| `HomePage` | `/#/` | 繼續上次 + 歷史批次 + 建新批次 | `batches` 按 `lastAccessedAt` 降序 |
| `BatchBuilderPage` | `/#/builder` | 篩選 + 搜尋 + 勾選 ≤25 字 | `WordCard` 用 `React.memo` 包 |
| `BatchHubPage` | `/#/batch/:id` | 進度 + 4 功能入口 | mount 時更新 `lastAccessedAt` |
| `FlashCardPage` | `/#/batch/:id/flashcard` | 3D 翻牌 + TTS + 進度 | 翻到背面自動 `speakZh()` |

**共用元件（`components/`）**

| 元件 | 用途 | 注意 |
|------|------|------|
| `Header` | 通用標題列 | `sticky top-0`、`onBack` 有值才顯示返回 |
| `WordCard` | 單字列 | `React.memo` 避免重渲染 |
| `SelectionCounter` | N/25 計數器 | 選滿時變色 |
| `Toast` | 臨時提示 | 2 秒自動消失 |

**TTS 服務（`services/tts.ts`）**

- `speakEn(word)` → `lang: 'en-US'`, `rate: 0.9`
- `speakZh(text)` → `lang: 'zh-TW'`
- 每次呼叫前先 `cancel()`（避免重疊）
- 不做循環播放（Chrome Android 的 pause bug，見 ADR-04）

**PWA 設定**

在 `vite.config.ts`：
- `base: '/vocabbatcher/'`
- `registerType: 'autoUpdate'`
- `vocab.cleaned.json` → `CacheFirst`（離線可用）
- manifest：`display: standalone`, `orientation: portrait`

---

## 三、測試

### Python

```bash
python -m pytest                    # 跑全部 53 個
python -m pytest tests/test_top2025_md.py -v  # 只跑 MD parser 測試
```

| 測試檔案 | 測試數 | 覆蓋範圍 |
|---------|--------|---------|
| `test_cleaner.py` | 7 | 去重、trim、confidence、issues |
| `test_cli.py` | 5 | 端對端 PDF + MD pipeline |
| `test_extractor.py` | 7 | PDF 文字抽取 |
| `test_parser.py` | 7 | rule dispatch、ParseResult、rejection |
| `test_qa.py` | 9 | confidence 公式、QA report 欄位 |
| `test_top2025_md.py` | 14 | MD parser edge cases |

### React App

目前無自動測試。驗收用 `npm run build` + 手動檢查。

---

## 四、還沒做完的事 / 已知問題

### 待開發（B-2 / M3）

| 功能 | 說明 |
|------|------|
| 四題型練習 | 中→英、英→中、拼字填空、聽音選字 |
| 即時判分 + 結果頁 | 練習完立即顯示分數 |
| 錯題重練 | 只重複練答錯的字 |
| 批次統計 | 正確率、錯題分布 |
| 循環播放 TTS | 25 字連續播放（受 Chrome Android bug 限制，見 ADR-04）|

### 已知技術債

| 問題 | 影響 | 備註 |
|------|------|------|
| UK IPA 覆蓋率低（30.6%） | App 只顯示 US IPA | dictionaryapi.dev 對 UK 覆蓋本來就差 |
| top2025.md 手動維護 | 若有新版需重新轉換 | 原始 PDF 無 pos/zh_def |
| React App 無自動測試 | 全靠手動驗收 | 可加 Playwright e2e |
| `output/` 不進版控 | 需手動複製到 App | 可用 npm script 自動化 |

---

## 五、架構決策索引（ADR）

| 編號 | 標題 | 一句話摘要 |
|------|------|-----------|
| [ADR-001](docs/adr/ADR-001-markdown-as-primary-source.md) | 資料來源從 PDF 改為 Markdown | PDF 無 pos/zh_def，改用手動整理的 MD 表格 |
| [ADR-002](docs/adr/ADR-002-web-pwa-over-react-native.md) | 平台從 React Native 改為 Web PWA | 不需要 App Store、零部署成本、Web Speech API 足夠 |
| [ADR-003](docs/adr/ADR-003-hash-router.md) | 路由使用 HashRouter | GitHub Pages 不支援 SPA URL rewrite |
| [ADR-004](docs/adr/ADR-004-tts-single-word-only.md) | TTS 只做單詞發音 | Chrome Android pause bug，不做循環播放 |
| [ADR-005](docs/adr/ADR-005-tailwind-v4-vite-plugin.md) | CSS 使用 Tailwind v4 + @tailwindcss/vite | 不用 PostCSS，設定更簡潔 |
| [ADR-006](docs/adr/ADR-006-context-localstorage.md) | 狀態管理使用 Context + localStorage | 規模不需要 Redux/Zustand |
| [ADR-007](docs/adr/ADR-007-ipa-batch-prefetch.md) | IPA 一次性批次補充 | 不在 runtime 查 API，結果存入 JSON |
