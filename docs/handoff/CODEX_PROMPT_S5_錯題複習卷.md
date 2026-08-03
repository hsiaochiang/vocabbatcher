請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\BRIEF_S5_錯題複習卷.md，這是你這次要做的完整施工規格（現況、任務、邊界、驗收標準、收工指令都在裡面），照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡。
2. 工作目錄是 exam-vocab-batcher/。
3. 重點任務：在 exam.ts 新增依錯誤率出題的函式（重用 generateExam 的內部邏輯，不要複製貼上重複程式碼），在 WordStatsPage.tsx 加「錯題複習」按鈕觸發出題並導向 /exam/run。
4. 不要改路由選型、登入邏輯、PWA 設定、Firestore 安全規則，這些都已經驗收通過。
5. npm run lint、npm run build 要過。
6. 若有偏離本 BRIEF 的改動 → 記進 DECISIONS.md。
7. 收工前更新 PROGRESS.md：加一行本切片成果，標記 M3 五片全部完成、待負責人驗收 S5。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_S5_錯題複習卷.md，內容依這個格式寫：

```markdown
# REPORT_S5_錯題複習卷 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<具體改了哪些檔案：exam.ts 新增的函式與介面、WordStatsPage 新增的按鈕與觸發邏輯、
有沒有加「複習卷標籤」這個可選功能>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF_S5 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。寫完這份報告代表你這次工作結束，不用再額外輸出總結。
