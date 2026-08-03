# VocabBatcher

國中會考英文單字練習 App。學生可以從課本頁碼或進階篩選建立單字批次，透過翻牌學習、四題型考試、成績歷史與錯題複習，把 PDF 詞表變成可在手機與平板上使用的 PWA。

## 目前技術棧

- 前端：React 19 + Vite + Tailwind CSS
- App 型態：PWA，目標裝置為 iPad Safari 與 Android Chrome
- 語音：瀏覽器 Web Speech API，發音必須由使用者點擊觸發
- 帳號與雲端：Firebase Authentication（Google 登入）+ Cloud Firestore（成績與錯誤率）
- 部署：專案根目錄 `deploy.ps1` 會建置前端並部署 Firebase Hosting
- 資料來源：PDF/Markdown parser 產出的 `vocab.cleaned.json`

## 核心功能流程

1. 在批次建立器用課本頁碼快速建立批次，或用頻率、詞性、關鍵字手動篩選單字。
2. 進入批次 Hub 後，可翻牌學習、以該批次頁碼範圍進入練習測驗，或查看單字統計。
3. 翻牌學習支援英文與中文發音，並會保存進度，首頁可繼續上次批次。
4. 考試支援四題型：中→英、英→中、拼字填空、聽音選字；純聽力模式會固定出聽力題。
5. 登入 Google 帳號後，考試結果會寫入 Firestore，可在成績歷史、單字統計與錯題複習卷中使用。

## 開發環境

建議使用 Node.js 20 LTS 或更新版本。

```powershell
cd exam-vocab-batcher
npm install
npm run dev
```

常用檢查指令：

```powershell
cd exam-vocab-batcher
npm run lint
npm run build
npm run test:e2e
```

如果 Windows PowerShell 執行 `npm run ...` 遇到 `npm.ps1` 權限問題，可以改用：

```powershell
npm.cmd run lint
npm.cmd run build
```

## 部署

專案根目錄提供部署腳本：

```powershell
.\deploy.ps1
```

腳本會進入 `exam-vocab-batcher/` 執行 build，接著部署 Firebase Hosting。第一次部署前請先確認 Firebase CLI 已登入，且專案設定與 Firebase Hosting 目標正確。

## 專案文件地圖

- `AGENTS.md`：本專案的兩層協作規範與驗收方法。
- `docs/planning/`：需求、進度、決策、路線圖、使用手冊與開發紀錄。
- `docs/handoff/`：每個切片的 BRIEF、CODEX_PROMPT、REPORT 三件交接文件。
- `exam-vocab-batcher/`：React/Vite PWA 主程式。
- `src/pdf_parser/`：詞表解析相關程式。

更多架構細節請看 `docs/planning/DEVELOPER_LOG.md`；使用者操作說明請看 `docs/planning/USER_MANUAL.md`。
