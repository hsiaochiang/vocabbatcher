請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。注意 AGENTS.md 這次新增了兩點：一是 `.\deploy.ps1` 部署腳本，二是「UI/UX 類切片的自我驗證」規則（純視覺/互動修正要用 Playwright 自己先驗證一輪），本次任務就是實踐這條規則。

接著讀 D:\program\vocabbatcher\BRIEF_UIUX2_頁次篩選與自動化驗證.md，這是你這次要做的完整施工規格（背景、任務、邊界、驗收標準、收工指令都在裡面），照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡，並讀 REPORT_UIUX1_首頁動線與可用性修正.md 了解上一片已完成的內容。
2. 工作目錄是 exam-vocab-batcher/。
3. 重點任務一：把批次建立器（BatchBuilderPage.tsx）改成以「頁次範圍」為主要挑選方式，原有頻率/詞性/搜尋篩選降為次要。
4. 重點任務二：安裝 @playwright/test，針對不需要真實 Google 登入的頁面與流程寫自動化驗證腳本並實際跑過，把結果（含截圖）寫進收工報告。這不是要建立長期 CI 測試框架，是這次收工前的自我驗證工具。
5. 不要動考試出題邏輯、登入邏輯、Firestore 規則、路由選型、PWA 設定，這些都已經驗收通過。
6. npm run lint、npm run build 要過。
7. 若有偏離本 BRIEF 的改動 → 記進 DECISIONS.md。
8. 收工前更新 PROGRESS.md：加一行本次修正成果，包含 Playwright 驗證結果摘要。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_UIUX2_頁次篩選與自動化驗證.md，內容依這個格式寫：

```markdown
# REPORT_UIUX2_頁次篩選與自動化驗證 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<BatchBuilderPage 的頁次篩選具體改法（UI 版面、篩選邏輯）；Playwright 安裝與設定、
寫了哪些驗證腳本、放在哪個目錄>

## Playwright 驗證結果
<逐項列出測了什麼、結果如何（通過/發現問題並修正）、截圖存放位置>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟，包含
Playwright 驗證結果的白話摘要（不用負責人自己重跑）。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。寫完這份報告代表你這次工作結束，不用再額外輸出總結。
