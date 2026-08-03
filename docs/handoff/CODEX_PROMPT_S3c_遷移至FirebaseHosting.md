請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\BRIEF_S3c_遷移至FirebaseHosting.md，這是你這次要做的完整施工規格（開場指令、目標、執行層/負責人分工、任務、邊界、驗收標準、收工指令都在裡面），照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡，並讀 REPORT_S3b_登入異常修復.md 了解前一輪診斷結果。
2. 工作目錄是 exam-vocab-batcher/。
3. 嚴格遵守 BRIEF 裡「哪些事執行層做得到、哪些需要負責人親自操作」的分工：不要嘗試執行 firebase login、firebase init、firebase deploy 或任何需要負責人 Google 帳號授權的指令，這些做不到、也不應該嘗試。你只準備設定檔與程式碼調整。
4. 現有 GitHub Pages 部署（.github/workflows/deploy.yml）不要刪除，改成只能手動觸發（拿掉 push 觸發），當備援。
5. 不要動 S3 考試引擎或登入程式碼邏輯本身，這次只動部署/建置設定（vite.config.ts、firebase.json、.firebaserc 佔位檔、GitHub Actions workflow、PWA 設定裡跟路徑有關的部分）。
6. npm run build 要過；用本機靜態伺服器確認頁面能載入、路由能動（不用測登入，因為本機網域不是 Firebase Hosting 網域）。
7. 若修法偏離本 BRIEF → 記進 DECISIONS.md。
8. 收工前更新 PROGRESS.md：記錄完成狀態，「▶ 下一步」寫成負責人要做的手動步驟白話版。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_S3c_遷移至FirebaseHosting.md，內容依這個格式寫：

```markdown
# REPORT_S3c_遷移至FirebaseHosting — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<具體改了哪些檔案：vite.config.ts base 設定、新增的 firebase.json 內容摘要、.firebaserc 佔位內容、
新的 GitHub Actions workflow 檔名與內容摘要、deploy.yml 的觸發方式改動、PWA 設定調整了哪裡>

## 是否偏離 BRIEF
<有的話，簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run build / 本機靜態伺服器驗證結果
<過 / 不過，不過的話貼關鍵錯誤訊息；本機驗證看到什麼畫面、路由是否正常>

## ★ 負責人要做的操作清單（最重要，白話、按順序、可直接照做）
<把 BRIEF 裡「負責人事後要親自做的事」5 個步驟，展開成實際可以複製貼上的指令、
或清楚的畫面操作路徑（例如「打開 Firebase Console → 選你的專案 → 左側選 Authentication → ...」）。
每一步都要讓負責人不用懂 Firebase 術語也能照做。最後要包含：完成部署後怎麼確認新網址、
怎麼在 iPhone/Android 上重新測試登入（出現頭像、重新整理不消失、關分頁重開還在）。>

## GitHub Secrets 清單（若有新增 workflow 需要）
<列出負責人需要去 GitHub repo Settings → Secrets and variables → Actions 新增哪些 Secret，
每個 Secret 名稱、用途、去哪裡取得值，一項一項列清楚。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，「負責人要做的操作清單」與「GitHub Secrets 清單」這兩段例外，要直接用負責人看得懂的白話寫，因為規劃層會原封不動或稍加整理後轉交給負責人。其餘段落可以寫技術細節。寫完這份報告代表你這次工作結束，不用再額外輸出總結。
