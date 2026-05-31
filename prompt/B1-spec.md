# B-1 開發規格書：ExamVocabBatcher Web App（M2 核心功能）

> 版本：1.0｜日期：2026-05-31
> 交付對象：GitHub Copilot Agent 模式
> 目標：從零建立可部署到 GitHub Pages 的 PWA，完成 M2 驗收標準

---

## 0. 閱讀本文件的方式

本文件是**完整的實作規格**，不是建議方向。Copilot 應按以下順序執行：

1. 先看「技術棧與專案結構」，建立骨架
2. 再看「資料層」，確認 TypeScript 型別
3. 再看「狀態管理」，建立 Context
4. 最後逐一實作「畫面規格」裡的每個 Screen

每完成一個 Screen，應確認：元件渲染正常、localStorage 讀寫正確、TTS 可觸發。

---

## 1. 技術棧

| 項目 | 選擇 | 說明 |
|------|------|------|
| 框架 | React 18 + TypeScript | |
| 建構工具 | Vite 5 | `npm create vite@latest` |
| CSS | Tailwind CSS v3 | 與 Stitch 設計稿一致 |
| 路由 | React Router v6 | `<HashRouter>` 模式（GitHub Pages 相容）|
| PWA | vite-plugin-pwa | Service Worker + manifest 自動產生 |
| 圖示字型 | Material Symbols Outlined | Google Fonts CDN |
| 文字字型 | Inter | Google Fonts CDN |
| TTS | Web Speech API（原生，不需套件）| |
| 狀態持久化 | localStorage | 不需 Redux，Context 即可 |
| 部署目標 | GitHub Pages（靜態）| `vite.config.ts` 設 `base` |

### 不使用的東西

- ❌ React Native / Expo（已決定走 Web）
- ❌ 任何後端 / API server
- ❌ Redux / Zustand（規模不需要）
- ❌ CSS-in-JS（用 Tailwind）

---

## 2. 專案初始化指令

```bash
npm create vite@latest exam-vocab-batcher -- --template react-ts
cd exam-vocab-batcher
npm install
npm install -D tailwindcss postcss autoprefixer
npm install react-router-dom
npm install -D vite-plugin-pwa
npx tailwindcss init -p
```

---

## 3. 設計系統（Design Tokens）

與 Stitch 設計稿完全一致，不自行創作顏色。

### tailwind.config.ts

```ts
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3c83f6',
        'bg-light': '#f5f7f8',
        'bg-dark': '#101722',
      },
      fontFamily: {
        display: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
      },
    },
  },
}
```

### index.html（`<head>` 必要內容）

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
  rel="stylesheet"
/>
<link
  href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
  rel="stylesheet"
/>
```

### 通用 CSS（src/index.css）

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Inter', sans-serif;
  min-height: 100dvh;
  background-color: #f5f7f8;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.icon-filled {
  font-variation-settings: 'FILL' 1;
}
```

---

## 4. 資料層

### 4-1 vocab.cleaned.json 的存放位置

```
public/
  data/
    vocab.cleaned.json   ← 從 output/vocab.cleaned.json 複製過來
```

App 用 `fetch('/data/vocab.cleaned.json')` 載入，這樣 Vite 和 GitHub Pages 都能直接 serve。

### 4-2 TypeScript 型別（src/types/vocab.ts）

```ts
export interface VocabEntry {
  word: string;
  pos: string | null;
  zh_definition: string | null;
  frequency: number | null;
  source_page: number[];
  ipa_us: string | null;
  ipa_uk: string | null;
  parse_confidence: number;
  issues: string[];
}
```

### 4-3 Batch 資料型別（src/types/batch.ts）

```ts
export interface Batch {
  id: string;              // nanoid() 或 Date.now().toString()
  name: string;            // 例如 "批次 #1"
  createdAt: string;       // ISO 8601
  lastAccessedAt: string;  // ISO 8601
  words: VocabEntry[];     // 勾選的單字（最多 25 筆）
  flashcardIndex: number;  // 上次翻到第幾張（0-based），預設 0
}
```

---

## 5. 狀態管理（src/store/）

### 5-1 AppContext（src/store/AppContext.tsx）

管理全域狀態，**讀寫都同步到 localStorage**。

```ts
interface AppState {
  allWords: VocabEntry[];          // 全部 1231 筆，載入後不變
  isLoading: boolean;
  batches: Batch[];
  activeBatchId: string | null;    // 最近一次操作的批次
}

interface AppContextValue extends AppState {
  createBatch: (words: VocabEntry[]) => Batch;
  deleteBatch: (id: string) => void;
  updateBatch: (id: string, patch: Partial<Batch>) => void;
  setActiveBatch: (id: string) => void;
}
```

**實作要求：**
- `allWords` 在 App 啟動時用 `fetch` 載入一次，存入 Context
- `batches` 從 `localStorage.getItem('batches')` 初始化（JSON.parse，若無則空陣列）
- 每次呼叫 `createBatch` / `deleteBatch` / `updateBatch`，都立刻寫入 `localStorage.setItem('batches', JSON.stringify(...))`
- `activeBatchId` 同樣存入 `localStorage.getItem('activeBatchId')`

---

## 6. TTS 服務（src/services/tts.ts）

**只實作單詞發音，不實作循環播放。**

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

**注意：**
- 呼叫前必須先 `cancel()`，避免前一個 utterance 卡住
- `rate: 0.9` 讓英文發音稍慢，學生較容易聽清楚
- 不需要 pause / resume（已知 Chrome Android bug，直接迴避）

---

## 7. 路由結構（src/App.tsx）

```tsx
<HashRouter>
  <Routes>
    <Route path="/"                          element={<HomePage />} />
    <Route path="/builder"                   element={<BatchBuilderPage />} />
    <Route path="/batch/:id"                 element={<BatchHubPage />} />
    <Route path="/batch/:id/flashcard"       element={<FlashCardPage />} />
  </Routes>
</HashRouter>
```

**使用 `<HashRouter>` 而非 `<BrowserRouter>`**，原因：GitHub Pages 不支援 SPA 的路徑重寫，HashRouter 的 `/#/` 路徑不需要 server 設定。

---

## 8. vite.config.ts

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  base: '/vocabbatcher/',   // ← GitHub Pages repo 名稱，視實際 repo 調整
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico'],
      manifest: {
        name: '會考單字練習',
        short_name: '會考單字',
        description: '國中會考英文單字練習 App',
        theme_color: '#3c83f6',
        background_color: '#f5f7f8',
        display: 'standalone',
        orientation: 'portrait',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,json}'],
        runtimeCaching: [
          {
            urlPattern: /\/data\/vocab\.cleaned\.json$/,
            handler: 'CacheFirst',
            options: { cacheName: 'vocab-data' },
          },
        ],
      },
    }),
  ],
})
```

---

## 9. 專案目錄結構

```
exam-vocab-batcher/
├── public/
│   ├── data/
│   │   └── vocab.cleaned.json      ← 複製自 output/vocab.cleaned.json
│   ├── icon-192.png
│   └── icon-512.png
├── src/
│   ├── types/
│   │   ├── vocab.ts
│   │   └── batch.ts
│   ├── store/
│   │   └── AppContext.tsx
│   ├── services/
│   │   └── tts.ts
│   ├── components/                 ← 可跨頁複用的元件
│   │   ├── Header.tsx
│   │   ├── WordCard.tsx            ← 單字清單的單一列
│   │   └── SelectionCounter.tsx    ← N/25 計數器
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── BatchBuilderPage.tsx
│   │   ├── BatchHubPage.tsx
│   │   └── FlashCardPage.tsx
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── tailwind.config.ts
├── vite.config.ts
└── package.json
```

---

## 10. 畫面規格

### Screen 1：首頁（HomePage）

**路由：** `/`
**對應設計稿：** `design/stitch/stitch_home_screen/_5/code.html`

**版面：**
```
[Header] 國中會考單字準備

[Section: 繼續上次]           ← 只在有 activeBatchId 時顯示
  批次名稱 + 已學 N/M 張
  進度條
  [按鈕：繼續]

[Section: 歷史批次]
  每筆：批次名稱 / 建立日期 / 單字數
  → 點擊進入 BatchHub

[底部固定按鈕：＋ 建立新批次]  ← 導向 /builder
```

**行為：**
- 進入頁面時，從 AppContext 讀取 `batches` 列表
- `batches` 按 `lastAccessedAt` 降序排列（最新的在前）
- `activeBatchId` 對應的批次，顯示在「繼續上次」區塊
- 若沒有任何批次，顯示空狀態：「還沒有批次，點下方按鈕開始」
- 「繼續」按鈕：`navigate('/batch/:id')`
- 歷史批次列點擊：`navigate('/batch/:id')` 並 `setActiveBatch(id)`

---

### Screen 2：批次建立器（BatchBuilderPage）

**路由：** `/builder`
**對應設計稿：** `design/stitch/stitch_home_screen/_1/code.html`

**版面：**
```
[Header] 批次建立器 ← 返回

[篩選列] 頻率▾  詞性▾  頁碼▾     ← 水平捲動的 chip 列

[勾選計數器]  已選 N / 25       ← sticky，滾動時保持可見

[單字清單]                       ← 虛擬捲動或直接 map（1231 筆）
  每筆：
    ☐ / ☑  word  [pos]
            zh_definition
            頻率 N 次

[底部固定按鈕：建立批次（N 字）]  ← N=0 時 disabled
```

**篩選邏輯（所有篩選條件 AND 運算）：**

| 篩選項 | 選項 | 說明 |
|--------|------|------|
| 頻率 | 全部 / 高（≥8）/ 中（4–7）/ 低（≤3）| 按 frequency 欄位 |
| 詞性 | 全部 / n. / v. / adj. / adv. / 其他 | 按 pos 欄位 |
| 搜尋 | 文字輸入框 | 英文單字模糊比對（word.includes）|

**勾選邏輯：**
- 已選 < 25：可勾選
- 已選 = 25：未勾選的項目顯示 disabled（不可點、文字變灰）
- 已選 = 25 時點擊未勾選項目：顯示 toast 提示「最多只能選 25 個單字」
- 點「建立批次」：
  1. 建立新 Batch（nanoid 或 timestamp id）
  2. 名稱自動命名：`批次 #${batches.length + 1}`
  3. 呼叫 `createBatch(selectedWords)`
  4. `navigate('/batch/:newId')`

**效能注意：**
- 1231 筆 `map` 可以直接渲染（不需要虛擬捲動），但要用 `React.memo` 包住 `WordCard` 避免不必要的重渲
- 篩選結果以 `useMemo` 計算

---

### Screen 3：批次 Hub（BatchHubPage）

**路由：** `/batch/:id`
**對應設計稿：** `design/stitch/stitch_home_screen/_3/code.html`

**版面：**
```
[Header] 批次名稱  ← 返回

[進度卡片]
  整體進度 N%（已完成翻牌張數 / 總字數）
  進度條

[2×2 功能卡片格]
  ┌────────────────┬────────────────┐
  │  🃏 翻牌學習   │  🔊 錄音播放   │
  │  （可用）      │  （即將推出）  │
  ├────────────────┼────────────────┤
  │  ✏️ 練習測驗   │  📊 學習統計   │
  │  （即將推出）  │  （即將推出）  │
  └────────────────┴────────────────┘
```

**行為：**
- 進入頁面時，呼叫 `updateBatch(id, { lastAccessedAt: new Date().toISOString() })`
- 「翻牌學習」卡片：點擊 → `navigate('/batch/:id/flashcard')`
- 「即將推出」卡片：點擊無反應或顯示 toast「即將推出」，卡片外觀 opacity-50

**進度計算：**
`progress = batch.flashcardIndex / batch.words.length`（0 到 1）

---

### Screen 4：翻牌卡（FlashCardPage）

**路由：** `/batch/:id/flashcard`
**對應設計稿：** `design/stitch/stitch_home_screen/_4/code.html`

**版面：**
```
[Header] 翻牌學習  ← 返回

[進度列]
  已看 N / M 張   M%

[翻牌卡區域]（主要空間，垂直置中）
  ┌─────────────────────────────┐
  │                             │
  │   [正面]                    │
  │   英文單字（大字）           │
  │   音標（ipa_us）            │
  │   [🔊] 播放發音按鈕         │
  │   ──────────────────────    │
  │   「點擊翻面」提示           │
  │                             │
  └─────────────────────────────┘

  翻面後：
  ┌─────────────────────────────┐
  │   [背面]                    │
  │   word（小字，上方）         │
  │   zh_definition（大字）      │
  │   [pos]（標籤）             │
  │   [🔊 中] 播放中文發音按鈕  │
  │                             │
  └─────────────────────────────┘

[下方操作按鈕]
  [← 上一張]  [翻面]  [下一張 →]
```

**翻牌動畫：**
```css
.card-inner {
  transition: transform 0.4s;
  transform-style: preserve-3d;
}
.card-inner.flipped {
  transform: rotateY(180deg);
}
.card-front, .card-back {
  backface-visibility: hidden;
  position: absolute;
  inset: 0;
}
.card-back {
  transform: rotateY(180deg);
}
```

**TTS 行為：**
- 正面「🔊」按鈕 → `speakEn(word)`
- 翻到背面時**自動**呼叫 `speakZh(zh_definition)` 一次
- 背面「🔊 中」按鈕 → 再次呼叫 `speakZh(zh_definition)`
- `zh_definition` 為 null 時：隱藏中文發音按鈕

**翻頁邏輯：**
- 「下一張」：index + 1，同時呼叫 `updateBatch(id, { flashcardIndex: newIndex })`（持久化）
- 「上一張」：index - 1（index = 0 時 disabled）
- 「下一張」index = words.length 時：顯示「這輪結束！」，按鈕文字改「重新開始」，點擊 → index 歸 0

**ipa_us 為 null 時：** 不顯示音標列，只顯示 word，TTS 按鈕仍保留

---

## 11. 共用元件

### Header.tsx

```tsx
interface HeaderProps {
  title: string;
  onBack?: () => void;      // 有值才顯示返回按鈕
  rightSlot?: ReactNode;    // 右側選填內容
}
```

樣式：sticky top-0，背景模糊（backdrop-blur），底部邊框

### WordCard.tsx

```tsx
interface WordCardProps {
  entry: VocabEntry;
  selected: boolean;
  disabled: boolean;        // 已選 25，這張沒被選
  onToggle: () => void;
}
```

### SelectionCounter.tsx

```tsx
interface SelectionCounterProps {
  count: number;
  max: number;              // 25
}
// 顯示：已選 N / 25，count === max 時文字變 primary 色並加警示 icon
```

---

## 12. 驗收標準（M2）

全部驗收前，先執行：
```bash
npm run build
npm run preview
```
用手機瀏覽器開 preview URL，模擬 PWA 使用情境。

| # | 驗收項目 | 通過條件 |
|---|---------|---------|
| 1 | 資料載入 | 首頁/批次建立器可看到 1231 筆單字 |
| 2 | 篩選 | 選「高頻率」後，清單只剩 frequency ≥ 8 的字 |
| 3 | 搜尋 | 輸入 "app" 後，清單顯示含 "app" 的字 |
| 4 | 勾選上限 | 選滿 25 字後，未選字變灰且無法新增 |
| 5 | 計數器 | 每次勾選 / 取消勾選，計數器即時更新 |
| 6 | 建立批次 | 點「建立批次」，自動跳轉 BatchHub，首頁歷史出現新批次 |
| 7 | 重整後資料保留 | 重整頁面後，批次資料不遺失（localStorage）|
| 8 | 翻牌卡翻面 | 點卡片或「翻面」按鈕，卡片有 3D 翻轉動畫 |
| 9 | 翻面自動唸中文 | 翻到背面時自動播放中文發音 |
| 10 | 手動播放發音 | 點「🔊」按鈕可播放英文；點「🔊 中」可播放中文 |
| 11 | 翻牌進度保存 | 翻到第 N 張後，離開再回來，從第 N 張繼續 |
| 12 | 首屏速度 | Chrome DevTools → Lighthouse → PWA 評分 ≥ 70 |
| 13 | 離線可用 | 開啟 DevTools → Network → Offline，仍可進入首頁與批次 |
| 14 | Add to Home Screen | Android Chrome 跳出安裝提示，加入後可全螢幕開啟 |

---

## 13. GitHub Pages 部署步驟

```bash
# 1. 安裝 gh-pages 工具
npm install -D gh-pages

# 2. package.json 新增 scripts
"scripts": {
  "deploy": "npm run build && gh-pages -d dist"
}

# 3. 部署
npm run deploy
```

`vite.config.ts` 的 `base` 設為 `'/vocabbatcher/'`（替換成你的 GitHub repo 名稱）。

---

## 14. 這份規格不包含的部分（留給 B-2）

- 循環發音（批次連續播放 25 字）
- 四題型練習（中→英、英→中、拼字填空、聽音選字）
- 即時判分 + 結果頁
- 錯題重練
- 批次統計（正確率 / 錯題分布）

---

## 15. 給 Copilot 的驗收指示

完成所有功能後，請在專案資料夾裡產出一份 `VERIFICATION.md`，
依照以下格式記錄測試過程。

撰寫時請假設讀者是完全不懂程式的使用者，只用過基本電腦操作——
不要出現任何程式術語，所有步驟要白話到「點哪裡、看到什麼、再點哪裡」
這種程度。不要只寫「功能正常」，要寫你實際做了什麼、看到了什麼。

```
# 功能驗收報告

## 本次完成的功能總覽
| 功能名稱 | 完成狀態 | 說明 |
|---------|---------|------|
| （功能1） | ✅ 完成 / ⚠️ 部分完成 / ❌ 未完成 | 一句話說明 |

---

## 逐項驗收（使用者角度）

### 功能 1：〔名稱〕

**這個功能是做什麼的：**
（白話說明，一到兩句）

**我測試的步驟：**
1. 我打開了 ___
2. 我點了 ___
3. 我輸入了 ___（如果有的話）

**我看到的結果：**
（描述畫面出現了什麼、發生了什麼事）

**測試結論：** ✅ 符合預期 / ⚠️ 有點出入 / ❌ 沒有正確運作

**你自己驗收的方法：**
1. 打開 ___
2. 找到 ___ 然後點它
3. 你應該會看到 ___
4. 如果看到的是這樣，代表這個功能完成了 ✅

---

## 測試時發現的注意事項
（有沒有什麼邊緣情況、小問題、或使用時要注意的地方）

## 這次還沒處理的部分
（列出哪些項目留到下一輪，以及原因）

## 驗收結果彙整
| 驗收項目 | 結果 |
|---------|------|
| 1. 資料載入 1231 筆 | ✅ / ❌ |
| 2. 篩選高頻率 | ✅ / ❌ |
| 3. 搜尋 | ✅ / ❌ |
| 4. 勾選上限 25 字 | ✅ / ❌ |
| 5. 計數器即時更新 | ✅ / ❌ |
| 6. 建立批次並跳轉 | ✅ / ❌ |
| 7. 重整後資料保留 | ✅ / ❌ |
| 8. 翻牌卡翻面動畫 | ✅ / ❌ |
| 9. 翻面自動唸中文 | ✅ / ❌ |
| 10. 手動播放發音 | ✅ / ❌ |
| 11. 翻牌進度保存 | ✅ / ❌ |
| 12. Lighthouse PWA ≥ 70 | ✅ / ❌ |
| 13. 離線可用 | ✅ / ❌ |
| 14. Add to Home Screen | ✅ / ❌ |
```
