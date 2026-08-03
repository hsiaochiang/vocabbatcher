請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_M5S1_學測資料管線.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡。
2. 工作目錄為專案根目錄（Python `src/pdf_parser/` pipeline，這片完全不碰 `exam-vocab-batcher/src/`）。
3. 重點任務：
   - 讀 `0resource/TopAcademy 學測高頻率單字表.pdf`，比照會考版 `0resource/top2025.md` 的做法，轉錄成 `0resource/topsat.md`（表格式 Markdown，含單字/詞性/中文定義/Level/頁碼，不含個別出現年份）。**這是精確度最關鍵的步驟，請盡可能交叉核對，在報告裡誠實記錄信心程度與疑慮處。**
   - `src/pdf_parser/models.py` 的 `VocabEntry`、`CleanedEntry` 新增 `level: str | None`；`src/pdf_parser/cleaner.py` 的 `clean_entries()` 同步透傳這個欄位（比照其他字串欄位用 `_trim_or_null()` 處理）。
   - 新增 `src/pdf_parser/rules/topsat_md.py`，架構比照 `top2025_md.py` 但因應學測版章節/Level 結構不同重新設計章節與表格正則；務必自行核對學測 PDF 有沒有跟會考版一樣的「PDF 內部頁碼 vs 課本印刷頁碼」固定偏移，不能假設偏移量一樣，核對方式與結論要寫進報告。
   - 用 CLI 或等價方式跑出 `output/gsat/vocab.raw.json`／`vocab.cleaned.json`／`vocab.qa_report.json`，複製 `vocab.cleaned.json` 到 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`（新檔名，絕對不要覆蓋既有的 `vocab.cleaned.json`）。
   - 新增 `tests/test_topsat_md.py`，涵蓋章節/Level/表格/頁碼解析。
4. 邊界（不要碰）：不改任何 `exam-vocab-batcher/src/` 底下的 `.tsx`/`.ts` 檔案；不改 `top2025_md.py`、`0resource/top2025.md`、既有會考 `output/vocab.*.json`、`exam-vocab-batcher/public/data/vocab.cleaned.json`；不把 `level` 加進 `qa.py` 的信心分數計算；不做會考/學測合併邏輯。
5. `python -m pytest tests/` 全部通過（含既有會考測試，確認沒有因新增 `level` 欄位壞掉）。
6. 若有偏離本 BRIEF 的改動（尤其章節解析邏輯、頁碼偏移判斷）→ 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
7. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果，「▶ 下一步」改為「M5-S1 待負責人抽查資料正確性，過了才開 M5-S2」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建（或覆寫）REPORT_M5S1_學測資料管線.md，內容依這個格式寫：

```markdown
# REPORT_M5S1_學測資料管線 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<逐項對應 BRIEF 的任務：topsat.md 轉錄、models.py/cleaner.py 的 level 欄位、topsat_md.py 解析規則、
輸出檔案位置、測試檔案>

## 資料正確性自我檢查
<轉錄 topsat.md 時的信心程度、有沒有發現排版模糊或不確定的地方；頁碼偏移的核對方式與結論
（有沒有固定偏移、偏移量多少，或無法確認）；出現次數範圍章節（如「10~7」）的處理邏輯>

## 抽樣清單（供負責人快速核對，10~15 個字）
<列出單字、詞性、中文定義、Level、出現次數、頁碼，方便負責人不用自己開 JSON 檔就能對照 PDF>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## pytest 結果
<過 / 不過，含跑了幾項、有沒有既有測試被影響>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」跟「抽樣清單」那兩段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit 並 push

寫完報告檔後，確認 `python -m pytest tests/` 全部通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案，然後：

1. `git add` 這次改動的檔案（含 `0resource/topsat.md`、`src/pdf_parser/` 的改動、`output/gsat/`、`exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`、`tests/test_topsat_md.py`、`docs/handoff/REPORT_M5S1_學測資料管線.md`、`docs/planning/PROGRESS.md`，若有動 `DECISIONS.md` 也一併加入）。
2. `git commit`，commit message 用一句話講清楚這片做了什麼（例如「功能: 新增學測單字庫資料管線」），可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。
3. `git push` 到 `origin main`。
4. push 完成後在報告檔（或對負責人的回覆）中註明 commit hash 與 push 是否成功；若 push 失敗，不要用 force push，把卡住的狀況寫清楚讓規劃層或負責人決定怎麼處理。

完成 commit 並 push（或記錄清楚卡住原因）後，這次工作才算真正結束，不用再額外輸出總結。
