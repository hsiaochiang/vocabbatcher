# REPORT_S3e_改用BrowserRouter — 執行結果

- 執行時間：2026-07-31 22:53 +08:00
- 狀態：完成

## 改了什麼

- `exam-vocab-batcher/src/App.tsx`
  - `import { HashRouter, ... }` 改成 `import { BrowserRouter, ... }`。
  - `<HashRouter>` / `</HashRouter>` 改成 `<BrowserRouter>` / `</BrowserRouter>`。
  - 沒有設定 `basename`，因為 Firebase Hosting 目前部署在根路徑。

- 全面搜尋結果
  - `exam-vocab-batcher/src/`、`public/`、`index.html` 內沒有 `#/`。
  - `exam-vocab-batcher/src/` 內沒有 `location.hash` 或 `window.location` 導頁邏輯。
  - 導頁仍使用 `react-router-dom` 的 `useNavigate()` 與 `<Route>`。

- `vite.config.ts`
  - 沒有調整。S3c 已把 Firebase Hosting 根路徑 `/` 設定好，本切片不需要再改部署/建置設定。

提醒規劃層：切換成 `BrowserRouter` 後，GitHub Pages 手動備援在子路徑 `/vocabbatcher/` 下若直接輸入或重新整理深層路徑，可能會 404。Firebase Hosting 已有 `firebase.json` SPA rewrite，不受影響。GitHub Pages 備援若未來還要長期保留，可另開切片加 `404.html` 轉址技巧；不在本切片做。

另提醒：`BRIEF_S3d_登入除錯面板.md` 已不需要執行，因為根因已找到。

## 是否偏離 BRIEF

無。

`DECISIONS.md` 已有 2026-07-31「登入問題真正根因確認：HashRouter 與 Firebase 登入網址片段衝突（推翻前兩輪假設）」條目，本次沒有重複新增。

## npm run lint / npm run build / 本機 preview 驗證結果

- `npm run lint`：通過（exit code 0）。
- `npm run build`：通過（exit code 0）。
- 本機 preview：用 `npm run preview -- --host 127.0.0.1 --port 4173` 驗證。
  - `http://127.0.0.1:4173/` 回應 200，載入 App root。
  - `http://127.0.0.1:4173/exam` 回應 200，直接開 `/exam` 可載入 App root。

備註：`npm run lint` 與 `npm run build` 仍出現既有 PowerShell/npm 全域路徑權限警告：
`Access to the path 'C:\Users\wilson_hsiao\AppData\Roaming\npm\node_modules\npm\bin\npm-cli.js' is denied.`
但兩個指令 exit code 都是 0，不影響驗證結果。

`npm run build` 另有既有 chunk size warning，不影響 build 成功。

## ★ 負責人接下來要做的事（白話、按順序）

1. 重新建置網站。

   在 PowerShell 執行：

   ```powershell
   cd D:\program\vocabbatcher\exam-vocab-batcher
   npm run build
   ```

2. 部署到 Firebase Hosting。

   在 PowerShell 執行：

   ```powershell
   cd D:\program\vocabbatcher
   firebase deploy --only hosting
   ```

3. 用新版本重測登入。

   請用這個網址測：

   ```text
   https://gen-lang-client-0930375434.firebaseapp.com
   ```

   注意：換成 `BrowserRouter` 後，網址不會再有 `#`。例如考試頁會是：

   ```text
   https://gen-lang-client-0930375434.firebaseapp.com/exam
   ```

   不是：

   ```text
   https://gen-lang-client-0930375434.firebaseapp.com/#/exam
   ```

4. iPhone Safari 驗收。

   - 打開 `https://gen-lang-client-0930375434.firebaseapp.com`。
   - 點「使用 Google 登入」。
   - 這次應該會看到 Google 帳號選擇畫面，這是最關鍵的差異。
   - 完成登入後，確認畫面出現頭像或名字。
   - 重新整理頁面，確認頭像或名字不消失。
   - 關掉分頁，重新打開網址，確認仍是登入狀態。

5. Android Chrome 驗收。

   - 重複 iPhone Safari 的同一套步驟。
   - 特別注意：之前 Android 上完全不會出現 Google 帳號選擇畫面；這次應該要出現。

6. 順手確認原本功能沒有壞。

   - 單字列表可以打開。
   - 可以建立批次。
   - 翻牌卡可以看。
   - 發音按鈕可以播放。
   - 考試流程可以進入、作答、看到結果。

7. 登入驗收通過後，回頭繼續 S3 驗收項 3~6。

## 遇到的問題 / 卡住的地方（若有）

沒有卡住。

歷史文件中仍有舊的 `HashRouter` / `/#/` 說明（例如 `DEVELOPER_LOG.md`、`docs/adr/ADR-003-hash-router.md`、早期 spec/prompt），那些不是執行中的 App 導頁邏輯，本切片未修改。若規劃層希望整理架構文件，可另開文件同步切片。
