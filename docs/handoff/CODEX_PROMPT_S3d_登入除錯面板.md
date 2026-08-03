請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\BRIEF_S3d_登入除錯面板.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡，並讀 REPORT_S3b_登入異常修復.md、REPORT_S3c_遷移至FirebaseHosting.md 了解前兩輪已排除的假設。
2. 工作目錄是 exam-vocab-batcher/。
3. 這片純粹是加「肉眼可見的除錯資訊」，不要猜測根因去改登入邏輯本身（signInWithRedirect、authDomain 等都不要動）。
4. 不要動 S3 考試引擎程式碼。
5. npm run lint、npm run build 要過。
6. 若有偏離本 BRIEF 的改動 → 記進 DECISIONS.md。
7. 收工前更新 PROGRESS.md：註明這是暫時除錯用途的改動，下一步是等負責人部署後在手機上回報畫面文字。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_S3d_登入除錯面板.md，內容依這個格式寫：

```markdown
# REPORT_S3d_登入除錯面板 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<具體改了哪些檔案，除錯區塊長什麼樣子、顯示哪些資訊、掛在畫面哪個位置>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## ★ 負責人接下來要做的事（白話、按順序）
<部署步驟——負責人已經做過一次 firebase deploy，這次應該只需要重複：
npm run build（在 exam-vocab-batcher/ 目錄）→ firebase deploy --only hosting（在專案根目錄）。
提醒負責人部署後用哪個網址測試（https://gen-lang-client-0930375434.firebaseapp.com），
以及要把除錯區塊顯示的完整文字截圖或抄下來，iPhone 和 Android 都要做一次。>

## ⚠️ 提醒事項
<提醒規劃層：這是暫時性除錯改動，問題解決後要記得移除或收斂，不可留在正式畫面上。>
```

寫完這份報告代表你這次工作結束，不用再額外輸出總結。
