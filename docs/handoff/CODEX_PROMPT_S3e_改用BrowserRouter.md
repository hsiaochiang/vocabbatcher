請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\BRIEF_S3e_改用BrowserRouter.md，這是你這次要做的完整施工規格（根因、任務、邊界、驗收標準、收工指令都在裡面），照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡，並讀 REPORT_S3b_登入異常修復.md、REPORT_S3c_遷移至FirebaseHosting.md 了解前兩輪已排除的假設，避免走回頭路。
2. 工作目錄是 exam-vocab-batcher/。
3. 把 src/App.tsx 的 HashRouter 換成 BrowserRouter，並全面搜尋專案內有沒有寫死 #/ 開頭路徑或依賴 window.location.hash 的地方，一併改掉。
4. 不要動 S3 考試引擎邏輯、不要動 Firebase Hosting/GitHub Actions 部署設定（那些已經是對的）。
5. npm run lint、npm run build 要過。本機用 npm run preview 驗證根路徑與 /exam 能正常載入。
6. 若有偏離本 BRIEF 的改動 → 記進 DECISIONS.md，並記一筆說明前兩輪的假設（第三方儲存空間限制、部署網域問題）已被推翻，真正根因是 HashRouter 與 Firebase 登入 URL hash 片段的衝突。
7. 收工前更新 PROGRESS.md：記錄根因與修法，下一步是負責人重新部署並在 iPhone/Android 重測登入。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_S3e_改用BrowserRouter.md，內容依這個格式寫：

```markdown
# REPORT_S3e_改用BrowserRouter — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<具體改了哪些檔案：App.tsx 的 Router 換法、有沒有找到其他寫死 #/ 或 location.hash 的地方並修正、
vite.config.ts 是否需要調整（應該不需要，S3c 已設定根路徑）>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build / 本機 preview 驗證結果
<過 / 不過；本機 preview 根路徑、/exam 路徑分別看到什麼>

## ★ 負責人接下來要做的事（白話、按順序）
<部署步驟：npm run build（exam-vocab-batcher/ 目錄）→ firebase deploy --only hosting（專案根目錄）→
用 https://gen-lang-client-0930375434.firebaseapp.com 在 iPhone Safari、Android Chrome 重測登入
（這次應該會看到 Google 帳號選擇畫面才對，這是最關鍵的差異，之前 Android 上這個畫面完全不會出現）→
出現頭像 → 重新整理不消失 → 關分頁重開還在 → 順手確認單字列表/批次/翻牌卡/發音/考試流程正常。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

寫完這份報告代表你這次工作結束，不用再額外輸出總結。
