請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\BRIEF_UIUX3_頁碼修正與單頁建立批次.md，這是你這次要做的完整施工規格（背景、3 項任務、邊界、驗收標準、收工指令都在裡面），照著做：

1. 開工先讀 PROGRESS.md 恢復脈絡，並讀 REPORT_UIUX2_頁次篩選與自動化驗證.md 了解上一片剛做的內容。
2. 這次工作範圍橫跨專案根目錄（Python pdf_parser pipeline）與 exam-vocab-batcher/（前端）。
3. 重點任務一（最優先，資料正確性問題）：修正 vocab.cleaned.json 的頁碼固定 2 頁偏移（exam-vocab-batcher/public/data/vocab.cleaned.json 與 output/vocab.cleaned.json 都要改），並嘗試修正 pipeline 原始碼避免未來重新解析又跑出一樣的偏移（若風險太高可以只做資料檔修正，記錄待辦）。
4. 重點任務二：把批次建立器改成「一頁一按鈕，按下即建立批次」，取代原本的頁次範圍輸入框；原有的頻率/詞性/搜尋進階篩選保留作為次要路徑。
5. 重點任務三：延續上一片的 Playwright 驗證習慣，寫測試涵蓋頁碼按鈕清單、單頁建立批次流程、進階篩選沒壞掉，把結果和截圖寫進報告。
6. 不要動考試出題邏輯、登入邏輯、Firestore 規則、路由選型、PWA 設定；不要重新解析整個 PDF。
7. npm run lint、npm run build 要過；若動了 Python pipeline，確認沒改壞既有測試。
8. 若有偏離本 BRIEF 的改動 → 記進 DECISIONS.md，包含 BRIEF 裡明確要求的「頁碼修正背景與影響範圍」記錄。
9. 收工前更新 PROGRESS.md：記錄這次修正成果，特別註明 S3 考試引擎頁數範圍過去可能存在頁碼落差這件事。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在專案根目錄新建（或覆寫）D:\program\vocabbatcher\REPORT_UIUX3_頁碼修正與單頁建立批次.md，內容依這個格式寫：

```markdown
# REPORT_UIUX3_頁碼修正與單頁建立批次 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<逐項對應 BRIEF 的 3 項任務：頁碼偏移修正（資料檔＋pipeline，或只有資料檔並說明原因）、
批次建立器改版的具體做法、Playwright 測試新增/調整了什麼>

## 頁碼偏移修正細節
<確認是哪條 pipeline 產生現有資料、修正前後的驗證方式、有沒有發現 source_page 減完出現 0 或負數的異常情況>

## Playwright 驗證結果
<逐項列出測了什麼、結果如何、截圖存放位置>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果（與 Python 測試，若有動 pipeline）
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟，
特別強調第 2 點「拿課本對照頁碼是否正確」是這次最重要的驗收點。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。寫完這份報告代表你這次工作結束，不用再額外輸出總結。
