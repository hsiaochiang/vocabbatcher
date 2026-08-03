請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_M5S2_App端來源切換.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡，並讀 D:\program\vocabbatcher\docs\handoff\REPORT_M5S1_學測資料管線.md、REPORT_M5S1b_學測資料OCR校正.md 了解學測資料的來源與格式。
2. 工作目錄是 exam-vocab-batcher/。
3. 重點任務：
   - `src/types/vocab.ts` 新增 `VocabSource = 'cap' | 'gsat'`；`src/store/AppContext.tsx` 新增 `source` state（預設 `localStorage` 讀取，沒有則 `'cap'`）與 `setSource()`，`allWords` 依 `source` fetch `data/vocab.cleaned.json`（cap）或 `data/vocab.gsat.cleaned.json`（gsat）。
   - `src/types/batch.ts` 的 `Batch` 新增 `source` 欄位，`createBatch()` 建立時帶入目前 source；`HomePage.tsx` 的「繼續上次」與「歷史批次」都只顯示目前 source 的批次；舊批次沒有 source 欄位時容錯視為 `'cap'`。
   - **重點風險（務必處理）**：`ExamResultPage.tsx` 寫入 Firestore 的 `wordStats` 文件 ID 目前直接是單字字串（`users/{uid}/wordStats/{word}`），沒有來源區分，會考/學測共同的高頻字（例如 `unique`）會互相污染錯誤率統計。改成 `${source}__${word}` 當文件 ID，`examResults` 文件加 `source` 欄位；`WordStatsPage.tsx`、`ExamHistoryPage.tsx` 讀取時依目前 source 過濾/標示，舊資料（無 source 標記）容錯視為 `cap`，不用寫遷移腳本。`firestore.rules` 已用萬用字元涵蓋所有子集合，不用改。
   - `HomePage.tsx` 加清楚的來源切換 UI（例如「會考」／「學測」兩個分頁按鈕）。
4. 邊界（不要碰）：不改 `exam.ts` 的出題演算法本身（純函式，傳對 `allWords` 即可）；不做跨來源混合批次；不改 `firestore.rules`；不改 M5-S1/S1b 已產出的資料檔內容；不動 `BrowserRouter`、不動 Workbox `navigateFallbackDenylist`。
5. `npm run lint`、`npm run build` 要過；延續 Playwright 自我驗證習慣，測試涵蓋「切來源→批次只看得到對應來源單字→翻牌/考試只出現對應來源單字」。
6. 若有偏離本 BRIEF 的改動（尤其是 wordStats/examResults 來源隔離的實作方式）→ 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
7. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：標記 M5「學測單字庫」全部完成，「▶ 下一步」改為「M5 全部完成，等負責人驗收，過了 M1~M5 全部里程碑都完成」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建（或覆寫）REPORT_M5S2_App端來源切換.md，內容依這個格式寫：

```markdown
# REPORT_M5S2_App端來源切換 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<逐項對應 BRIEF 的任務：來源型別與切換機制、批次記住來源、成績/統計隔離的具體實作方式、
來源切換 UI、新增/調整的測試>

## wordStats/examResults 來源隔離實作細節
<文件 ID 或欄位設計、舊資料容錯處理方式、有沒有實際驗證過兩個來源的統計不會互相污染
（例如同一個字在兩邊都答錯，確認統計分開）>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## Playwright 測試結果
<跑了什麼、通過與否>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit 並 push

寫完報告檔後，確認 `npm run lint`、`npm run build` 都通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案，然後：

1. `git add` 這次改動的檔案（含 `docs/handoff/REPORT_M5S2_App端來源切換.md`、`docs/planning/PROGRESS.md`，若有動 `DECISIONS.md` 也一併加入）。
2. `git commit`，commit message 用一句話講清楚這片做了什麼（例如「功能: 新增會考/學測單字庫來源切換」），可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。
3. `git push` 到 `origin main`。
4. push 完成後在報告檔（或對負責人的回覆）中註明 commit hash 與 push 是否成功；若 push 失敗（例如遠端有新 commit、需要先 pull），不要用 force push，把卡住的狀況寫清楚讓規劃層或負責人決定怎麼處理。

完成 commit 並 push（或記錄清楚卡住原因）後，這次工作才算真正結束，不用再額外輸出總結。
