# BRIEF_S3e_改用BrowserRouter.md — M3 插入切片：把路由系統從 HashRouter 換成 BrowserRouter

> 交接合約：規劃層 → 執行層，2026-07-31。
> 背景：`BRIEF_S3b`、`BRIEF_S3c` 依序排除了「S3 程式碼回歸」與「跨網域第三方儲存限制」，
> 規劃層直接用瀏覽器工具重現問題，抓到瀏覽器主控台的實際錯誤：
> `No routes matched location "/id=I0_...&_gfid=...&parent=...&pfname=&rpctoken=..."`。
> 這行警告來自本專案自己的 React Router（`src/App.tsx` 用 `HashRouter`），
> 代表 Firebase Auth 內部用來傳遞登入流程狀態的網址 `#` 片段，被 `HashRouter` 誤判成路由變更、
> 嘗試匹配畫面失敗，導致整個 `signInWithRedirect()` 流程在還沒跳出 Google 帳號選擇畫面前就被打斷。
> 這個衝突跟部署在哪裡（GitHub Pages / Firebase Hosting）、裝置是 iPhone/Android/桌機都無關，
> 是純粧端路由函式庫與 Firebase 登入機制的衝突，因此三次環境調整都沒修好。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀 `REPORT_S3b_登入異常修復.md`、`REPORT_S3c_遷移至FirebaseHosting.md` 了解前兩輪已排除的假設，避免走回頭路。
3. 工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 把 `src/App.tsx` 的路由從 `HashRouter` 換成 `BrowserRouter`，讓網址的 `#` 片段不再被 App 佔用，Google 登入的 `signInWithRedirect()` 流程才能正常跑到底、正確回傳登入結果。

## 任務

1. **`src/App.tsx`**：`import { HashRouter, ... } from 'react-router-dom'` 改成 `import { BrowserRouter, ... } from 'react-router-dom'`，`<HashRouter>` 換成 `<BrowserRouter>`（`basename` 不用特別設定，因為 Firebase Hosting 部署在根路徑）。
2. **檢查專案內所有寫死 `#/` 開頭路徑的地方**（例如任何手動組字串導頁的程式碼、`window.location.hash` 相關邏輯），改成一般路徑格式（`/exam`、`/batch/:id` 等，不帶 `#`）。用 `grep` 全面搜尋 `#/`、`location.hash` 確認沒有漏改的地方。
3. **確認路由用的都是 `react-router-dom` 的 `<Link>`／`useNavigate()`／`<Route path="...">`**，不要有寫死 `window.location.href = '#/xxx'` 這種繞過路由系統的寫法（若有要一併改掉，否則會跟 `BrowserRouter` 不相容）。
4. **Vite 的 `base` 設定**（`vite.config.ts` 裡的 `appBase`）已經在 S3c 支援 Firebase Hosting 根路徑 `/`，這次不用改；但如果 GitHub Pages 備援那套（子路徑 `/vocabbatcher/`）之後有人打開，`BrowserRouter` 在子路徑 + 靜態檔案（無伺服器端 rewrite）下，直接輸入深層網址會 404——這是 GitHub Pages 備援本來就有的已知限制（Firebase Hosting 有設定 SPA rewrite，不受影響），不用特別處理，但要在報告裡提醒規劃層這件事，讓規劃層決定要不要之後幫 GitHub Pages 備援加 `404.html` 轉址技巧（不在本切片做）。
5. `npm run lint`、`npm run build` 要過。
6. 本機驗證：`npm run build` 後用 `npm run preview` 起本機伺服器，確認根路徑、`/exam`、直接刷新 `/exam` 分頁都能正常載入（`BrowserRouter` 在本機 preview 若沒有 SPA fallback，直接刷新非根路徑可能 404，這是本機 preview 工具本身的限制，不代表正式環境有問題——正式環境 Firebase Hosting 已有 SPA rewrite；報告裡註明這點即可，不用為了本機驗證特別加設定）。

## 邊界（本切片不做）
- 不動 S3 考試引擎邏輯本身、不動 Firebase Hosting／GitHub Actions 部署設定（那些在 S3c 已經是對的）。
- 不處理 GitHub Pages 備援的 404 深層連結問題（記錄起來即可，留給規劃層之後決定）。

## 驗收（負責人操作，需先重新部署）
1. 負責人重新跑 `npm run build`（在 `exam-vocab-batcher/`）+ `firebase deploy --only hosting`（在專案根目錄）部署到 Firebase Hosting。
2. 打開 `https://gen-lang-client-0930375434.firebaseapp.com`（注意：換成 `BrowserRouter` 後網址不會再有 `#`，例如「開始考試」頁會是 `.../exam` 不是 `.../#/exam`，這是正常的）。
3. 點「使用 Google 登入」→ 應該會看到 Google 帳號選擇畫面（這是這次修復要解決的核心：之前 Android 上這個畫面完全不會出現）→ 完成登入 → 畫面出現頭像。
4. 重新整理頁面，頭像仍在。
5. 關閉分頁、重新打開，仍顯示已登入。
6. 順手確認原本功能（單字列表、批次、翻牌卡、發音按鈕、考試流程）在新的網址格式下依然正常運作（因為網址從 `#/xxx` 變成 `/xxx`，理論上不影響功能，但要實際點過一輪確認）。
7. iPhone Safari、Android Chrome 都要重測。
8. `npm run lint`、`npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：記錄根因（HashRouter 與 Firebase 登入的 `#` 片段衝突）與修法（改用 BrowserRouter）。
2. 若有偏離本 BRIEF 的改動 → 記 `DECISIONS.md`（這次的根因判定應該也記一筆到 `DECISIONS.md`，說明前兩輪的假設已被推翻）。
3. 收工報告請照 `CODEX_PROMPT_S3e_改用BrowserRouter.md` 的格式寫，並提醒規劃層：`BRIEF_S3d_登入除錯面板.md` 這片如果還沒執行就不用做了（根因已經找到，不需要除錯面板）。
