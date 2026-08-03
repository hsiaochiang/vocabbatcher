# BRIEF_S3f_PWA排除登入路徑.md — M3 插入切片：PWA 離線快取排除 Firebase 登入保留路徑

> 交接合約：規劃層 → 執行層，2026-07-31。
> 背景：`BRIEF_S3e` 把路由從 `HashRouter` 換成 `BrowserRouter`，解決了一個真實存在的衝突，
> 但負責人重新部署驗收時，桌機／Android 仍然登入失敗（iPhone 這次有進步、跳出了 Google 帳號選擇畫面，
> 但整體仍不穩定）。規劃層再次用瀏覽器工具重現，這次直接檢查正式站實際部署的 `sw.js`（PWA 離線快取程式），
> 發現裡面有 `registerRoute(new NavigationRoute(createHandlerBoundToURL("index.html")))`——
> 這是 workbox 的 `NavigationRoute`，**預設會攔截網站所有的整頁導覽請求，一律改成回傳快取好的 `index.html`**。
> Google 登入流程需要跳轉到 Firebase 保留路徑 `/__/auth/handler`（和 `/__/auth/iframe`）去處理登入，
> 這個跳轉也被 Service Worker 攔截，回傳的是我們自己的 App 畫面而不是 Firebase 真正的登入處理頁面，
> 導致登入永遠無法正常完成。這正是 `BRIEF_S3b` 當初列出、後來被降低優先度的
> 「PWA Service Worker 快取干擾」假設，這次證實它才是主要根因（`BrowserRouter` 修復是必要但不足夠的一步，
> 兩個問題都要修，登入才會穩定）。
>
> 佐證方式：用 `curl` 直接打 `/__/auth/handler`，伺服器回應的是 Firebase 真正的登入處理頁
> （內容含 `fireauth.oauthhelper.widget.initialize()`）；但用真的瀏覽器（有 Service Worker 運作）打開同一個網址，
> 畫面卻變成本 App 自己的首頁——兩者一對照，證實問題出在 Service Worker 的攔截層，不是伺服器端設定。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀 `REPORT_S3b_登入異常修復.md`、`REPORT_S3c_遷移至FirebaseHosting.md`、`REPORT_S3e_改用BrowserRouter.md`，了解前三輪已排除/已完成的部分，避免重複工作。
3. 工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 讓 PWA 的 Service Worker 不要攔截 Firebase 登入保留路徑（`/__/auth/**`、`/__/firebase/**`），這些路徑要直接透過網路連到 Firebase，不要被離線快取的「SPA 導覽 fallback」機制搶走。

## 任務

1. **調整 `vite.config.ts` 的 `VitePWA` workbox 設定**：在 `workbox` 選項裡加上 `navigateFallbackDenylist`（vite-plugin-pwa／workbox-build 支援的設定，接受一組正規表示式），把 `/^\/__\//`（或更精確地寫 `/^\/__\/auth\//`、`/^\/__\/firebase\//`）排除在 SPA 導覽 fallback 之外，讓這些路徑的請求直接放行給網路，不被 Service Worker 的 `NavigationRoute` 攔截改回 `index.html`。
   - 請先查一下目前專案用的 `vite-plugin-pwa` 版本實際支援的設定名稱是 `navigateFallbackDenylist`（陣列或函式皆可），確認寫法跟版本相容，不要憑印象亂猜參數名稱。
2. **重新產生的 `sw.js` 要確認**：`registerRoute(new NavigationRoute(...))` 那行呼叫要帶有排除規則（通常是 `NavigationRoute(handler, { denylist: [...] })` 或等效寫法），確認建置後的 `dist/sw.js` 內容確實包含這個排除設定，不是只改了設定檔但沒真的反映到產出的 Service Worker 程式碼裡。
3. **不要整個關掉 PWA 離線快取功能**——單字庫、翻牌卡、考試等離線可用的需求（`R4` 斷網可用）要維持，只是排除 Firebase 登入這幾條保留路徑。
4. `npm run lint`、`npm run build` 要過。
5. **本機驗證方式**（因為本機 preview 不會是 Firebase Hosting 的網域，沒辦法真的觸發登入導向）：
   - 檢查 `dist/sw.js` 內容，確認排除規則確實存在（用文字比對或印出片段即可，不用真的跑登入）。
   - 若方便，可以寫一個簡單的臨時測試腳本（例如用 Node 直接讀 `dist/sw.js` 字串搜尋排除規則），驗證完後不需要留在專案裡當正式測試案例（這不是要新增自動化測試，只是本次驗證手段，不用寫成 test file）。

## 邊界（本切片不做）
- 不動 S3 考試引擎邏輯、不動 `BrowserRouter` 或 Firebase Hosting 部署設定（那些已經是對的）。
- 不關閉整個 PWA/Service Worker 功能。
- 不修改 `firebase.json` 的 SPA rewrite（那是 Hosting 端的設定，Firebase 官方文件已保證 `/__/auth/**` 等保留路徑在 Hosting 層級不受自訂 rewrite 影響，這次的問題是瀏覽器端 Service Worker 攔截，跟 Hosting rewrite 是兩層不同的機制）。

## 驗收（負責人操作，需先重新部署）
1. 負責人重新跑 `npm run build`（`exam-vocab-batcher/`）+ `firebase deploy --only hosting`（專案根目錄）。
2. **重要：因為 Service Worker 本身也會被快取**，負責人這次測試前，建議在瀏覽器對這個網站做一次「清除網站資料」或至少強制重新整理數次，確保拿到新版 Service Worker，否則可能還在用舊版快取邏輯，看起來像沒修好。
3. 打開 `https://gen-lang-client-0930375434.firebaseapp.com`，點「使用 Google 登入」，這次應該要能順利跳轉到 Google 帳號選擇畫面、完成登入、導回 App 後看到頭像。
4. 重新整理頁面，頭像仍在。
5. 關閉分頁、重新打開，仍是登入狀態。
6. iPhone Safari、Android Chrome、桌機瀏覽器都要重測（也都建議先清一次快取再測，避免舊 Service Worker 干擾判讀）。
7. 順手確認離線功能沒被破壞：可以的話，斷網後確認單字列表、批次、翻牌卡仍可使用（這是原本 R4 的驗收標準，不能因為這次修復而退步）。
8. `npm run lint`、`npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：記錄這次補上的第二個根因（Service Worker 攔截登入保留路徑）與修法。
2. 在 `DECISIONS.md` 補記：`BRIEF_S3b` 當初被降低優先度的「PWA Service Worker 快取干擾」假設，這次證實是登入問題的主要根因之一（與 `HashRouter` 問題並存，兩個都需要修）。
3. 收工報告請照 `CODEX_PROMPT_S3f_PWA排除登入路徑.md` 的格式寫，並提醒負責人「這次測試前記得先清除網站資料，避免舊版 Service Worker 干擾判讀」。
