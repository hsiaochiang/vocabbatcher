# REPORT_S3b_登入異常修復 — 執行結果

- 執行時間：2026-07-31 10:54 +08:00
- 狀態：部分完成（已定位根因；依 BRIEF 邊界，需規劃層/負責人決定登入架構修法後才能實作）

## 根因

實際根因判定為：正式站目前部署在 GitHub Pages project site（`https://hsiaochiang.github.io/vocabbatcher/`），Firebase config 的 `authDomain` 使用 Firebase 預設網域（`*.firebaseapp.com`）。Firebase Web SDK 的 `signInWithRedirect()` 會依賴 auth helper 網域與 App 網域之間的瀏覽器儲存/iframe 溝通；Safari 16.1+ 與 Chrome M115+ 等現代瀏覽器封鎖第三方儲存時，導回 App 後可能讀不到 redirect pending state，因此 `getRedirectResult()` 會回到 `null` 或無法讓 `onAuthStateChanged()` 恢復使用者。

這也解釋負責人看到的現象：Google 帳號流程看似完成，但導回 App 後仍是未登入狀態；因為目前 `UserBadge.tsx` 只有在 `getRedirectResult()` 拋例外時才顯示紅字，若 SDK 因 pending state 遺失而回傳 `null`，畫面就會靜默停在「使用 Google 登入」按鈕。

本次也排除/降低下列假設優先度：

- S3 程式碼回歸：`src/services/auth.ts`、`src/services/firebase.ts`、`src/components/UserBadge.tsx` 自 S2 修復 commit `7d44332` 後未再變動。
- Firebase Authorized domains 完全漏設：若完全漏設，通常會在 OAuth 流程中出現 `unauthorized-domain` 類錯誤；而 S2 稍早三平台曾驗收通過，較不像單純漏設。不過 Firebase Console 仍需由有權限者最後確認 `hsiaochiang.github.io` 是否在 Authorized domains。
- Service Worker 單獨造成：PWA 目前會 precache `index.html` 與 JS，可能讓舊版頁面殘留，但它無法解決 Firebase redirect 在跨網域 auth helper 下的第三方儲存限制。清除網站資料可能短暫改善，但不是穩定修法。

參考依據：Firebase 官方文件「在禁止第三方儲存空間存取的瀏覽器上使用 signInWithRedirect 的最佳做法」說明，自 Chrome M115+、Safari 16.1+ 等環境起，若不是 Firebase Hosting 同網域或未採取 proxy/self-host/popup/自建 provider 流程等方案，`signInWithRedirect()` 無法保證在正式環境正常運作。

## 改了什麼

未改動產品程式碼。

原因：`BRIEF_S3b_登入異常修復.md` 明確規定「不重新設計登入方式；若診斷後認定 signInWithRedirect 本身在此情境不可行，先停下回報，不要自行換方案」。目前根因已落在部署/登入架構限制，直接改成 popup、Google Identity Services，或切換 authDomain/Hosting 都會偏離 S2 既有實作假設，需先由規劃層/負責人拍板。

已更新文件：

- `PROGRESS.md`：記錄根因，下一步改為等規劃層/負責人決定登入架構修法。
- `DECISIONS.md`：新增「待確認」決策，列出可選修法方向。
- `REPORT_S3b_登入異常修復.md`：本報告。

建議下一步方案，依穩定度排序：

1. 改部署到 Firebase Hosting，讓 App 與 Firebase Auth helper 使用同一套 Firebase Hosting/custom domain 設定。這最符合 Firebase 官方建議，對 `signInWithRedirect()` 最穩。
2. 若一定要保留現有網域，改到能反向代理 `/__/auth/` 的 hosting（GitHub Pages 做不到透明 reverse proxy）。
3. 若一定要留在 GitHub Pages，重新評估登入流程，例如回到 `signInWithPopup()` 並針對手機瀏覽器做實測，或改用 Google Identity Services + `signInWithCredential()`。這會是登入流程重設計。

## 是否偏離 BRIEF 或原始需求

尚未實作偏離。已在 `DECISIONS.md` 新增 2026-07-31「待確認：Google redirect 登入需調整部署或登入架構」，因為後續可行修法會偏離 S2「改用 signInWithRedirect 後沿用」的實作假設。

## npm run lint / npm run build 結果

- `npm run lint`：過（exit code 0）。PowerShell 額外印出一則全域 npm 路徑權限警告：`Access to the path 'C:\Users\wilson_hsiao\AppData\Roaming\npm\node_modules\npm\bin\npm-cli.js' is denied.`，但 ESLint 指令本身成功結束。
- `npm run build`：過（exit code 0）。同樣有上述 PowerShell/npm 權限警告；Vite 另有 chunk size warning，但 build 成功。

## 負責人驗收步驟（白話）

這次還不能請負責人重新驗收「登入已修好」，因為目前是卡在正式站登入架構限制，需要先選修法。

請負責人先做的確認：

1. 到 Firebase Console → Authentication → Settings → Authorized domains，確認有 `hsiaochiang.github.io`。
2. 決定正式站是否可以從 GitHub Pages 改到 Firebase Hosting。
3. 若可以改到 Firebase Hosting：下一片讓執行層調整部署與 authDomain，修好後再請負責人用 iPhone Safari、Android Chrome 重新測「登入 → 出現頭像 → 重新整理後頭像仍在 → 關分頁再開仍在」。
4. 若不能改部署：需由規劃層另開方案，評估 popup 或 Google Identity Services，不能直接沿用目前 redirect 寫法期待穩定。

本次沒有在正式畫面留下暫時除錯文字。

## 遇到的問題 / 卡住的地方（若有）

卡住點不是單一 React/Firebase 呼叫 bug，而是目前 hosting 與 Firebase redirect 登入機制不相容：

- GitHub Pages project site 無法透明代理根路徑 `/__/auth/` 到 Firebase auth helper。
- Firebase `authDomain` 不支援帶 `/vocabbatcher/` 這種 project site 子路徑。
- 直接改登入方式違反本 BRIEF 邊界，需先由規劃層/負責人決定。
