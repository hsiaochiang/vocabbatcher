請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\BRIEF_S4_成績統計.md，這是你這次要做的完整施工規格（現況、任務、邊界、驗收標準、收工指令都在裡面），照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡。
2. 工作目錄是 exam-vocab-batcher/。
3. 重點任務：在 ExamResultPage.tsx 補上 wordStats 的原子累加寫入（用 Firestore increment()，attempts/wrong 分開累加，wrongRate 不存欄位、改成顯示時即時計算），新增成績歷史頁與單字錯誤率統計頁，並在 HomePage 加入這兩個入口。
4. 絕對不要改路由選型（維持 BrowserRouter）、不要動登入邏輯（src/services/auth.ts、firebase.ts）、不要動 PWA/Service Worker 設定（vite.config.ts 的 workbox 部分）——這些都已經驗收通過，之前花了四輪才修好登入問題，不要因為這次任務動到相關程式碼。
5. 不要改考試引擎出題邏輯本身（src/services/exam.ts、ExamSetupPage、ExamRunPage），只在 ExamResultPage 補寫入邏輯。
6. npm run lint、npm run build 要過。
7. 若有偏離本 BRIEF 的改動 → 記進 DECISIONS.md。
8. 收工前更新 PROGRESS.md：加一行本切片成果，「▶ 下一步」改為等負責人驗收 S4。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_S4_成績統計.md，內容依這個格式寫：

```markdown
# REPORT_S4_成績統計 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<具體改了哪些檔案：ExamResultPage 的 wordStats 寫入邏輯、新增的成績歷史頁/單字統計頁檔名與路由、
HomePage 新增的入口、型別檔案是否有調整>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF_S4 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。寫完這份報告代表你這次工作結束，不用再額外輸出總結。
