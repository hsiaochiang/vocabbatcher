請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_M5S1b_學測資料OCR校正.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡，並讀 D:\program\vocabbatcher\docs\handoff\REPORT_M5S1_學測資料管線.md 了解上一片用了什麼方法、負責人抽查發現哪些錯字（例如 `splendor`→「RE 5」、`cruelly`→「殘酪地」）。
2. 工作目錄為專案根目錄（Python `src/pdf_parser/` pipeline，這片完全不碰 `exam-vocab-batcher/src/`）。
3. 重點任務：
   - 改用 **PaddleOCR**（`pip install paddleocr`，繁體中文用 `lang='chinese_cht'` 或對應 PP-OCRv5 繁中模型）取代上一片用的 Tesseract，重新辨識中文定義；渲染 PDF 頁面 **DPI 至少 300**（Tesseract 準確率門檻是 300 DPI，這是上一片可能沒注意到的關鍵因素）。英文單字/Level/出現次數/頁碼優先用 PyMuPDF 直接抽取文字層，只有中文定義才動用 OCR，比照 `src/pdf_parser/ocr_extractor.py` 當初的分工邏輯（但辨識引擎這次換成 PaddleOCR，不是抄 EasyOCR）。
   - 把這次的轉錄流程存成**可重複執行的腳本**（例如 `src/pdf_parser/tools/topsat_transcribe.py`），不要再像上一片一樣寫完即丟；腳本要能重跑，參數至少含輸入 PDF 路徑、輸出 Markdown 路徑、DPI。
   - 若 PaddleOCR 環境裡真的裝不起來，可以退而求其次優化 Tesseract（提高 DPI、影像前處理），但要在報告裡明確說明原因與辨識率比較，不能悄悄用回原本做法卻不說明。
   - 重新產出 `0resource/topsat.md`（覆蓋舊版）、`output/gsat/vocab.raw.json`／`vocab.cleaned.json`／`vocab.qa_report.json`，複製新的 `vocab.cleaned.json` 覆蓋 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`。
   - 逐項比對新舊版本的 QA 完整率與具體樣本（`splendor`、`cruelly` 等），把「改善前 → 改善後」的對照寫進報告。
4. 邊界（不要碰）：不改 `top2025_md.py`、`0resource/top2025.md`、既有會考 `output/vocab.*.json`、`exam-vocab-batcher/public/data/vocab.cleaned.json`；不改任何 `exam-vocab-batcher/src/` 檔案；不用把新腳本做成取代 `ocr_extractor.py` 的通用工具；不強求 100% 零錯字，合理改善即可。
5. `python -m pytest tests/` 全部通過（含既有測試與上一片新增的測試，若因資料變化需調整斷言可以調整，不要刪測試）。
6. 若有偏離本 BRIEF 的改動（尤其是最終選用的 OCR 方案、DPI 設定）→ 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
7. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果（含改善前後對照重點數字），「▶ 下一步」改為「M5-S1b 待負責人再次抽查資料正確性，過了才開 M5-S2」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建（或覆寫）REPORT_M5S1b_學測資料OCR校正.md，內容依這個格式寫：

```markdown
# REPORT_M5S1b_學測資料OCR校正 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<用了什麼 OCR 方案（PaddleOCR 或退回 Tesseract 優化版，含理由）、DPI 設定、新腳本的位置與用法、
重新產出的檔案清單>

## 改善前 → 改善後對照

### QA 完整率
<舊版 vs 新版：pos 完整率、zh_definition 完整率、低信心筆數>

### 具體樣本
<至少列出 splendor、cruelly 兩個上次抓到的錯字，改善前後的 zh_definition 值；
再抽 5~10 個上次缺詞性/缺定義的字看有沒有補上>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## pytest 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit 並 push

寫完報告檔後，確認 `python -m pytest tests/` 全部通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案（特別注意 PaddleOCR 下載的模型快取檔不該進 git，必要時補 `.gitignore`），然後：

1. `git add` 這次改動的檔案（含 `0resource/topsat.md`、新腳本、`src/pdf_parser/` 若有調整、`output/gsat/`、`exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`、測試調整、`docs/handoff/REPORT_M5S1b_學測資料OCR校正.md`、`docs/planning/PROGRESS.md`，若有動 `DECISIONS.md` 也一併加入）。
2. `git commit`，commit message 用一句話講清楚這片做了什麼（例如「修復: 學測資料改用 PaddleOCR 提高辨識率」），可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。
3. `git push` 到 `origin main`。
4. push 完成後在報告檔（或對負責人的回覆）中註明 commit hash 與 push 是否成功；若 push 失敗，不要用 force push，把卡住的狀況寫清楚讓規劃層或負責人決定怎麼處理。

完成 commit 並 push（或記錄清楚卡住原因）後，這次工作才算真正結束，不用再額外輸出總結。
