# REPORT_S3f_PWA排除登入路徑 — 執行結果

- 執行時間：2026-07-31 23:12 +08:00
- 狀態：完成

## 改了什麼

修改 `exam-vocab-batcher/vite.config.ts` 的 `VitePWA({ workbox })` 設定，在既有 `globPatterns` 與 `runtimeCaching` 之間新增：

```ts
navigateFallbackDenylist: [/^\/__\/auth\//, /^\/__\/firebase\//],
```

使用的設定名稱是 `navigateFallbackDenylist`。已從本機安裝的 `workbox-build` 型別與 schema 確認：

- `node_modules/workbox-build/build/types.d.ts` 有 `navigateFallbackDenylist?: Array<RegExp>`。
- `node_modules/workbox-build/build/templates/sw-template.js` 會把它輸出成 `NavigationRoute(..., { denylist: [...] })`。
- `node_modules/workbox-routing/NavigationRoute.d.ts` 確認 `NavigationRoute` 接受 `denylist?: RegExp[]`。

建置後已確認 `dist/sw.js` 真的反映排除規則。實際片段如下：

```js
e.registerRoute(new e.NavigationRoute(e.createHandlerBoundToURL("index.html"),{denylist:[/^\/__\/auth\//,/^\/__\/firebase\//]}))
```

這表示 Firebase Auth 保留路徑 `/__/auth/**` 和 Firebase 保留路徑 `/__/firebase/**` 不會再被 SPA navigation fallback 攔截成 `index.html`。

沒有關閉 PWA，也沒有移除既有離線快取；`data/vocab.cleaned.json` 仍維持 `CacheFirst`。

## 是否偏離 BRIEF

無。

已依 BRIEF 在 `DECISIONS.md` 補記 2026-07-31「登入問題第二根因確認：PWA Service Worker 攔截 Firebase 登入保留路徑」，說明 `BRIEF_S3b` 當初的 PWA 快取干擾假設這次證實是主要根因之一，且與 S3e 的 `HashRouter` 衝突並存。

## npm run lint / npm run build 結果

- `npm run lint`：通過（exit code 0）。
- `npm run build`：通過（exit code 0）。

備註：兩個指令仍出現既有 PowerShell/npm 全域路徑權限警告：
`Access to the path 'C:\Users\wilson_hsiao\AppData\Roaming\npm\node_modules\npm\bin\npm-cli.js' is denied.`
但 exit code 都是 0，不影響驗證結果。

`npm run build` 另有既有 chunk size warning，不影響 build 成功。

## ★ 負責人接下來要做的事（白話、按順序，務必包含清除快取的提醒）

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

3. 測試前先清除這個網站的舊快取。

   這一步很重要，因為 Service Worker 本身也會被瀏覽器保留。如果沒清掉，手機可能還在跑舊版 Service Worker，看起來會像沒修好。

   請對這個網站清除網站資料：

   ```text
   https://gen-lang-client-0930375434.firebaseapp.com
   ```

   如果一時找不到清除網站資料的位置，至少先強制重新整理數次，再重開瀏覽器分頁測試。手機上建議直接清除該網站資料後再測，判讀最乾淨。

4. 用桌機瀏覽器重測登入。

   - 打開 `https://gen-lang-client-0930375434.firebaseapp.com`。
   - 點「使用 Google 登入」。
   - 應該要看到 Google 帳號選擇畫面。
   - 完成登入後，確認畫面出現頭像或名字。
   - 重新整理頁面，確認頭像或名字不消失。
   - 關掉分頁，重新打開網址，確認仍是登入狀態。

5. 用 iPhone Safari 重測登入。

   - 先清除這個網站的網站資料。
   - 打開 `https://gen-lang-client-0930375434.firebaseapp.com`。
   - 點「使用 Google 登入」。
   - 確認出現 Google 帳號選擇畫面。
   - 完成登入後確認出現頭像或名字。
   - 重新整理不消失。
   - 關分頁重開仍在。

6. 用 Android Chrome 重測登入。

   - 先清除這個網站的網站資料。
   - 打開 `https://gen-lang-client-0930375434.firebaseapp.com`。
   - 點「使用 Google 登入」。
   - 確認出現 Google 帳號選擇畫面。
   - 完成登入後確認出現頭像或名字。
   - 重新整理不消失。
   - 關分頁重開仍在。

7. 順手確認離線功能沒有被破壞。

   可以的話，登入測完後再確認：

   - 單字列表可以打開。
   - 批次可以打開。
   - 翻牌卡可以使用。
   - 斷網後，上面幾個已載入過的學習功能仍可使用。

8. 登入驗收通過後，回頭繼續 S3 驗收項 3~6。

## 遇到的問題 / 卡住的地方（若有）

沒有卡住。

本機無法直接驗證 Firebase Hosting 登入 redirect，因為本機 preview 不是 Firebase Hosting 網域；本次以 `dist/sw.js` 產物檢查確認 Service Worker denylist 已生成。真正登入驗收仍需負責人部署後在正式網址上測。
