請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\BRIEF_S3f_PWA排除登入路徑.md，這是你這次要做的完整施工規格（根因、任務、邊界、驗收標準、收工指令都在裡面），照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡，並讀 REPORT_S3b_登入異常修復.md、REPORT_S3c_遷移至FirebaseHosting.md、REPORT_S3e_改用BrowserRouter.md 了解前三輪已排除/已完成的部分。
2. 工作目錄是 exam-vocab-batcher/。
3. 在 vite.config.ts 的 VitePWA workbox 設定加上排除規則，讓 Service Worker 的 NavigationRoute 不要攔截 /__/auth/**、/__/firebase/** 這類 Firebase 登入保留路徑，改成直接放行給網路。先確認目前 vite-plugin-pwa 版本實際支援的設定名稱（例如 navigateFallbackDenylist）再動手，不要憑印象亂猜參數名稱。
4. 確認建置後 dist/sw.js 真的包含這個排除規則，不是只改了設定檔沒生效。
5. 不要整個關掉 PWA 離線快取功能，其他離線可用的需求要維持。
6. 不要動 S3 考試引擎邏輯、不要動 BrowserRouter 或 Firebase Hosting 部署設定。
7. npm run lint、npm run build 要過。
8. 若有偏離本 BRIEF 的改動 → 記進 DECISIONS.md，並補記一筆說明 BRIEF_S3b 當初列的「PWA Service Worker 快取干擾」假設這次證實是登入問題的主要根因之一。
9. 收工前更新 PROGRESS.md：記錄根因與修法，下一步是負責人重新部署、清除網站資料後在 iPhone/Android/桌機重測登入。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_S3f_PWA排除登入路徑.md，內容依這個格式寫：

```markdown
# REPORT_S3f_PWA排除登入路徑 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<具體改了 vite.config.ts 哪裡、用了什麼設定名稱與寫法、怎麼確認 dist/sw.js 真的反映這個排除規則
（例如貼出建置後 sw.js 裡 NavigationRoute 那段的實際內容片段）>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## ★ 負責人接下來要做的事（白話、按順序，務必包含清除快取的提醒）
<部署步驟：npm run build（exam-vocab-batcher/ 目錄）→ firebase deploy --only hosting（專案根目錄）→
提醒負責人這次測試前務必先在瀏覽器對這個網站清除網站資料（或至少強制重新整理數次），
避免舊版 Service Worker 還在運作、看起來像沒修好 → 用 https://gen-lang-client-0930375434.firebaseapp.com
在 iPhone Safari、Android Chrome、桌機瀏覽器重測登入（出現 Google 帳號選擇畫面 → 完成登入 → 出現頭像 →
重新整理不消失 → 關分頁重開還在）→ 順手確認斷網時單字列表/批次/翻牌卡仍可使用（離線功能沒被破壞）。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

寫完這份報告代表你這次工作結束，不用再額外輸出總結。
