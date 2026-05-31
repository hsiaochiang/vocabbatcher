# DEVELOPER_LOG.md 大綱草稿

> 對象：一兩個月後回來看這個專案的自己
> 框架：Reference（模組查閱）+ Explanation / ADR（決策記錄）
> 待確認後，交由 Copilot 撰寫正文

---

## 文件定位說明

這份文件假設讀者是自己，有程式背景，但已忘記這個專案的細節。
目標：5 分鐘內把環境跑起來，10 分鐘內能看懂整個架構。

---

## 一、快速重啟環境

### 1-1 Python Parser（資料生成工具）

```
需要：Python 3.11+
```

1. 安裝依賴：`pip install -r requirements.txt`
2. 執行 parser：`python -m src.pdf_parser --input 0resource/top2025.md --outdir output/`
3. 執行測試：`python -m pytest`
4. 補充 IPA（選用）：`python src/pdf_parser/fetch_ipa.py`
5. 產出物位置：`output/vocab.cleaned.json`（不進 git，見 `.gitignore`）

---

### 1-2 React Web App（前端）

```
需要：Node.js 18+
```

1. 進入目錄：`cd exam-vocab-batcher`
2. 安裝依賴：`npm install`
3. 啟動開發伺服器：`npm run dev`
4. 建構：`npm run build`
5. 本地預覽 build 結果：`npm run preview`
6. 部署到 GitHub Pages：`npm run deploy`（若有設定 gh-pages）

---

### 1-3 重新生成 vocab.cleaned.json 後的手續

1. 執行 parser，取得新的 `output/vocab.cleaned.json`
2. 手動複製到 `exam-vocab-batcher/public/data/vocab.cleaned.json`
3. 重新 build + deploy

---

## 二、Reference：主要模組與元件

### 2-1 Python Parser（`src/pdf_parser/`）

| 模組 | 負責什麼 |
|------|---------|
| `__main__.py` | CLI 入口，4 步驟 pipeline：extract → parse → clean → qa |
| `extractor.py` | 用 pdfplumber 抽取 PDF 頁面文字（備用，主資料已改用 MD）|
| `rules/top2025_md.py` | 主力：從 top2025.md Markdown 表格解析單字 |
| `rules/top2025.py` | 舊版：從 PDF 表格解析（只有 word + frequency，無中文）|
| `parser.py` | 呼叫 rule，整合 ParseResult（entries + rejected_count）|
| `cleaner.py` | 去重（word+pos key）、trim、min-frequency 過濾、排序 |
| `qa.py` | 計算 parse_confidence、issues 陣列、產生 QAReport |
| `models.py` | TypedDict：VocabEntry、CleanedEntry、QAReport |
| `fetch_ipa.py` | 獨立工具：呼叫 dictionaryapi.dev，補充 ipa_us/ipa_uk，有快取 |

**資料流：**
```
top2025.md → parse_md_file() → VocabEntry[] → clean_entries() → CleanedEntry[] → vocab.cleaned.json
                                                                               → vocab.qa_report.json
```

**關鍵欄位（CleanedEntry）：**
```
word, pos, zh_definition, frequency, source_page[],
ipa_us, ipa_uk, parse_confidence, issues[]
```

---

### 2-2 React Web App（`exam-vocab-batcher/src/`）

**型別（`types/`）**

| 檔案 | 內容 |
|------|------|
| `vocab.ts` | `VocabEntry` interface，對應 vocab.cleaned.json 每筆 |
| `batch.ts` | `Batch` interface：id, name, createdAt, lastAccessedAt, words[], flashcardIndex |

**狀態管理（`store/AppContext.tsx`）**

- 全域狀態：`allWords`（1231 筆，載入一次）、`batches`（localStorage 持久化）、`activeBatchId`
- 主要方法：`createBatch`、`deleteBatch`、`updateBatch`、`setActiveBatch`
- localStorage 鍵：`batches`、`activeBatchId`
- 資料載入：`fetch(BASE_URL + 'data/vocab.cleaned.json')`，每次啟動讀一次

**服務（`services/tts.ts`）**

- `speakEn(word)` → Web Speech API，`lang: 'en-US'`，`rate: 0.9`
- `speakZh(text)` → Web Speech API，`lang: 'zh-TW'`
- 每次呼叫前先 `speechSynthesis.cancel()`（避免重疊）

**頁面（`pages/`）**

| 頁面 | 路由 | 功能摘要 |
|------|------|---------|
| `HomePage.tsx` | `/#/` | 繼續上次、歷史批次列表、建立新批次按鈕 |
| `BatchBuilderPage.tsx` | `/#/builder` | 搜尋 + 頻率 + 詞性篩選，勾選 ≤25 字，建立批次 |
| `BatchHubPage.tsx` | `/#/batch/:id` | 進度卡片，4 功能入口（翻牌可用，其餘「即將推出」）|
| `FlashCardPage.tsx` | `/#/batch/:id/flashcard` | 3D 翻牌，TTS，進度保存（flashcardIndex 持久化）|

**共用元件（`components/`）**

| 元件 | 用途 |
|------|------|
| `Header.tsx` | 通用 Header，含返回按鈕、title、右側 slot |
| `WordCard.tsx` | 批次建立器的單一單字列（含勾選、disabled 狀態）|
| `SelectionCounter.tsx` | N/25 計數器，選滿時文字變色 |
| `Toast.tsx` | 短暫提示訊息（例如「最多只能選 25 個單字」）|

**路由：** `HashRouter`（`/#/` 前綴），原因見 ADR-03

**PWA 設定（`vite.config.ts`）**

- `base: '/vocabbatcher/'`（GitHub Pages repo 路徑）
- Service Worker：`autoUpdate` 模式
- `vocab.cleaned.json` 使用 `CacheFirst`（離線可用）
- Manifest：`display: standalone`、`orientation: portrait`

---

## 三、ADR（架構與技術決策記錄）

### ADR-01：資料來源從 PDF 改為 Markdown（top2025.md）

**決定：** Parser 的主力輸入從 `top2025.pdf` 改為 `0resource/top2025.md`

**為什麼：**
- `top2025.pdf` 的表格只有「英文單字 + 出現年份」，完全沒有 `pos` 和 `zh_definition`
- 解析後 vocab.cleaned.json 裡的 pos/zh_definition 全是 null，App 完全無法使用
- 手動將 PDF 轉為 Markdown 後，表格多了詞性和中文定義欄位

**評估過的替代方案：**
- 串接 DictCN 或 MoeDict API 自動補充中文 → 速率限制、品質不穩定
- 繼續用 PDF parser 加強 regex → PDF 本身格式就沒有這些欄位，無法解決
- 直接用現成字典 JSON（BNC/COCA + cedict）→ 會考出題分佈和這份 top2025 不同

**後果：**
- Markdown 需要維護（若未來有新版 top2025 要手動轉換）
- 舊 `top2025.py` 規則保留但不再是主力
- PDF 頁碼透過另一個腳本（`word_page_map.json`）補回 MD 的第四欄

---

### ADR-02：平台從 React Native + Expo 改為 Web PWA

**決定：** 放棄 React Native，改為 React + Vite + vite-plugin-pwa，部署到 GitHub Pages

**為什麼：**
- 這是個人/少數人用的工具，不需要上架 App Store / Google Play
- 不需要 Android Studio / Xcode 編譯環境，門檻低
- Web Speech API 足夠處理單詞發音需求
- GitHub Pages 免費，零維護成本

**評估過的替代方案：**
- React Native + Expo → 需要編譯環境、TTS 實作複雜、部署繁瑣
- Capacitor（Web 轉原生）→ 比直接 PWA 複雜，優勢不明顯
- Flutter → 學習成本高，與現有技術棧不符

**後果：**
- iOS Safari Add to Home Screen 步驟需手動操作（非 Chrome 那種自動提示）
- 後台持續播放受瀏覽器限制（不過這個 App 設計上不需要後台播放）

---

### ADR-03：路由使用 HashRouter 而非 BrowserRouter

**決定：** `react-router-dom` 使用 `HashRouter`（URL 格式：`/#/batch/123`）

**為什麼：**
- GitHub Pages 是純靜態 host，不支援 SPA 的 URL rewrite（404 fallback）
- BrowserRouter 在 GitHub Pages 上，重新整理或直接輸入子路徑會得到 404

**評估過的替代方案：**
- 自訂 404.html + redirect hack（GitHub Pages workaround）→ 可行但脆弱、不優雅
- 換 Cloudflare Pages 或 Netlify → 支援 SPA redirect，但增加部署複雜度
- 保持 BrowserRouter 並只用首頁路由 → 犧牲深層連結功能

**後果：**
- URL 有 `/#/` 前綴，稍微不美觀
- `import.meta.env.BASE_URL` 要搭配 `vite.config.ts` 的 `base: '/vocabbatcher/'` 使用

---

### ADR-04：TTS 使用 Web Speech API，只做單詞發音（不做循環播放）

**決定：** TTS 用瀏覽器原生 `speechSynthesis`，每次只播一個字，不實作 25 字循環連播

**為什麼：**
- Chrome Android 的 `pause()` / `resume()` 有已知 bug（Chromium issue #335907，開放超過 10 年）
- 在 Android 上用 pause+setTimeout 實作間隔靜音，實際上會截斷 utterance
- 15 秒以上的連續 utterance 在 Chrome Desktop 也會被自動截斷
- 循環播放的複雜實作（utterance chaining）= 更多邊界情況和 bug

**評估過的替代方案：**
- utterance chaining + setTimeout（繞過 pause bug）→ 可行，但 Android 測試成本高
- expo-speech（React Native 方案）→ 已放棄 React Native
- 預先合成 MP3（Web Audio API）→ 合成品質差、需要後端或複雜 JS

**後果：**
- 循環發音列入 B-2+ 待辦，若日後要加，需要實機 Android 測試
- 翻牌卡翻到背面自動播中文（一次），這樣設計反而更自然

---

### ADR-05：CSS 框架使用 Tailwind v4 + @tailwindcss/vite（非傳統 PostCSS 整合）

**決定：** 使用 `@tailwindcss/vite` v4（Tailwind CSS v4 的 Vite 原生整合），不用 `postcss`

**為什麼：**
- Tailwind v4 推出了 Vite 專屬 plugin，不需要 `postcss.config.js`
- 建構速度更快，設定更簡潔

**注意：** v4 的設定方式和 v3 不同：
- v3：`tailwind.config.js` + `postcss.config.js`
- v4：直接在 `vite.config.ts` 加 `tailwindcss()` plugin，CSS 直接 `@import "tailwindcss"`

**後果：**
- 網路上大多數 Tailwind 教學是 v3 語法，搜尋時要注意版本
- 不能直接套用 v3 的 `content: []` 設定方式

---

### ADR-06：狀態管理使用 React Context + localStorage（不用 Redux/Zustand）

**決定：** 全域狀態只用 `React.createContext` + `useState`，持久化用 `localStorage`

**為什麼：**
- 專案規模小，4 個頁面，狀態只有「1231 字清單」和「批次列表」
- 引入 Redux/Zustand 會增加 boilerplate 和學習成本，得不償失

**評估過的替代方案：**
- Zustand → 更輕量但仍是外部依賴
- React Query → 適合 server state，不適合純本地狀態
- IndexedDB → 更強但 API 複雜，localStorage 對這個資料量完全足夠

**後果：**
- 若未來要做帳號同步或更複雜的狀態，Context 架構需要重構
- localStorage 大小上限約 5–10MB，存幾百個批次沒問題

---

### ADR-07：IPA 音標資料從 dictionaryapi.dev 一次性批次補充，結果存入 JSON

**決定：** 不在 App runtime 呼叫字典 API，而是一次性批次查詢後合併進 `vocab.cleaned.json`

**為什麼：**
- 1231 個字如果每次使用時即時查，有 rate limit 問題，且需要網路
- 一次性補充後存進 JSON，App 載入時資料就已包含 IPA
- 快取存在 `output/ipa_cache.json`，重跑時不需要重新查詢

**注意：**
- 覆蓋率：US 音標 93.7%（1154/1231），UK 音標 30.6%（377/1231）
- 60 個字完全沒有 IPA（主要是功能詞和專有名詞）
- 來源工具：`src/pdf_parser/fetch_ipa.py`

---

## 四、目前狀態與下一步

### 已完成

| 里程碑 | 內容 | 驗收文件 |
|--------|------|---------|
| M1 Data Ready | PDF Parser + vocab.cleaned.json | `VERIFICATION.md`（根目錄）|
| M2 Core Usable | React PWA + 翻牌卡 + TTS | `exam-vocab-batcher/VERIFICATION.md` |

### 待開發（B-2 / M3）

- 四題型練習（中→英、英→中、拼字填空、聽音選字）
- 即時判分 + 結果頁
- 錯題重練
- 批次歷史統計
- AsyncStorage（已是 localStorage）持久化練習紀錄

### 已知技術債

- 循環播放 TTS（放棄原因見 ADR-04）
- UK IPA 覆蓋率低（30.6%）
- top2025.md 若有新版需手動重新轉換和執行 parser
