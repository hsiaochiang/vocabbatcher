# BRIEF_M5S1b_學測資料OCR校正.md — M5 修正切片：提高學測資料中文定義的 OCR 辨識率

> 交接合約：規劃層 → 執行層，2026-08-03。
> 背景：`BRIEF_M5S1_學測資料管線.md` 已完成（`docs/handoff/REPORT_M5S1_學測資料管線.md`），負責人抽查 `output/gsat/vocab.cleaned.json` 後發現中文定義有明顯 OCR 誤判，例如：
> - `splendor` 的 `zh_definition` 被辨識成 `"RE 5"`（完全錯誤，正確應該是類似「光輝；壯麗」這類意思，實際請以 PDF 印刷內容為準）。
> - `cruelly` 的 `zh_definition` 被辨識成 `"殘忍地;殘酪地"`（「殘酪地」應為「殘酷地」的誤判，「酪」「酷」兩字形近）。
> - QA 報告顯示 98 筆缺詞性、22 筆缺中文定義，這些都可能還有其他未被抽樣抓到的錯字。
>
> 負責人的判斷是：這份 PDF 是**印刷體、不是手寫或低品質掃描**，理論上辨識率應該非常高，目前的結果不合理地差，需要用更好的工具重做一次。規劃層查過 2026-08 當前的公開資訊：**PaddleOCR** 在中文（含繁體）印刷體辨識上的準確率明顯優於 Tesseract，PP-OCRv5 版本比前代再提升約 13 個百分點；另外，**Tesseract 是用 300 DPI 訓練的，渲染解析度不到 300 就會明顯掉準確率**——上一片執行層用的 OCR 腳本是臨時寫的、沒有存檔，也沒記錄實際用了多少 DPI，這本身就是一個問題，這片要一併修正。

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 讀 `docs/handoff/REPORT_M5S1_學測資料管線.md` 了解上一片做了什麼、用什麼方法、哪裡有疑慮。
3. 工作目錄為專案根目錄（Python `src/pdf_parser/` pipeline）。

## 目標（一句話）
> 用更準確的 OCR 工具（PaddleOCR）加上足夠的渲染解析度（≥300 DPI），重新產出 `0resource/topsat.md` 與 `output/gsat/*.json`，讓中文定義的錯字大幅減少，並把這次的轉錄流程存成可重複執行的腳本，不要再用完即丟。

## 現況（可直接重用）

- `src/pdf_parser/models.py`、`src/pdf_parser/cleaner.py`、`src/pdf_parser/rules/topsat_md.py`、`src/pdf_parser/__main__.py`（`--rule topsat` 的動態載入機制）**都已經在 M5-S1 做好，這片原則上不用改這些檔案**——只要新產出的 `topsat.md` 維持跟上一片一樣的表格格式（章節標題、`| 單字 | 詞性 | 中文定義 | Level | 頁碼 |` 欄位順序），`topsat_md.py` 應該可以直接吃，不需要跟著改解析規則。如果你發現新流程產出的格式非得調整不可，才動 `topsat_md.py`，並在報告裡說明為什麼。
- `src/pdf_parser/ocr_extractor.py`：專案裡已經有一套為同類 PDF（PMingLiU 字型 ToUnicode CMap 幾乎空白，中文文字層無法直接抽取）調校過的 **PyMuPDF + EasyOCR 混合策略**，含 OCR 常見誤判的後處理修正（`_fix_bracket()`、`_dedup_definition()` 等）。這是當初為會考版 PDF 寫的，你可以參考它的整體架構（英文單字/座標用 PyMuPDF 抓、中文定義才動用 OCR），但實際辨識引擎這次要改用 PaddleOCR（見下方任務說明），不是照抄 EasyOCR。
- `0resource/topsat.md`（M5-S1 產出的版本）可以當作這次重跑後的比對基準——同一個單字、同一個章節位置，新舊兩個版本的中文定義有沒有變得更準確，是這片最主要的驗收依據。

## 任務

1. **改用 PaddleOCR 重新辨識中文定義**：
   - 安裝 `paddleocr`（`pip install paddleocr`，需要 `paddlepaddle` 框架，CPU 版即可，不用 GPU）。
   - 初始化時指定繁體中文模型（`lang='chinese_cht'`，或視你安裝的 PaddleOCR 版本 API 使用對應的 PP-OCRv5 繁中識別模型），不要用簡體中文模型辨識繁體字。
   - 渲染 PDF 頁面成圖片時，**DPI 至少 300**（可以用 PyMuPDF 的 `page.get_pixmap(dpi=300)` 或等價方式），這是這次修正的關鍵之一——如果你能確認上一片用的 DPI 低於這個值，請在報告裡記錄實際差異；如果無從得知上一片的 DPI（腳本沒留下），至少確保**這次**用 300 以上。
   - 英文單字、Level、出現次數、頁碼這些欄位，如果能靠 PyMuPDF 直接抽取文字層（不需要 OCR）就繼续沿用直接抽取（比 OCR 更準、更快），只有中文定義欄位才動用 PaddleOCR——這跟 `ocr_extractor.py` 當初的分工邏輯一致。
   - 如果你發現 PaddleOCR 在你的執行環境裡因為某些原因（例如安裝失敗、模型下載受阻）真的無法使用，退而求其次可以嘗試優化現有 Tesseract 流程（提高 DPI、加影像前處理如二值化/去噪），但這是次選方案，**必須在報告裡明確說明為什麼没有用 PaddleOCR、比較過的辨識率差異**，不能悄悄降級成同樣的做法又不說明。

2. **把 OCR 轉錄流程存成可重複執行的腳本**：
   - 新增一個腳本檔案（例如 `src/pdf_parser/tools/topsat_transcribe.py`，或你覺得更符合專案慣例的位置），把「讀 PDF → 判斷用直接抽取還是 OCR → 產出 `topsat.md`」的邏輯寫成一個可以重新執行、有清楚參數（至少包含輸入 PDF 路徑、輸出 Markdown 路徑、DPI）的腳本，而不是一次性的互動式操作。
   - 這樣做的原因：這份資料未來如果 TopAcademy 更新 PDF 版本、或發現還有殘留錯字要重跑，負責人跟未來的執行層都能直接重新執行同一份腳本，不用再靠臨時操作復現流程。
   - 腳本不需要整合進 `python -m src.pdf_parser` 這個既有 CLI 的參數體系（那個 CLI 目前設計是「輸入是 Markdown 或 PDF，直接跑完整 pipeline」），這個新腳本可以是獨立的前置轉錄工具，產出 `.md` 之後再交給既有 CLI（`--rule topsat`）處理，兩者分工清楚即可。

3. **重新產出並比對**：
   - 用新腳本重新產出 `0resource/topsat.md`（覆蓋上一片的版本，git 歷史會保留舊版可比對）。
   - 重跑既有 CLI 流程產出新的 `output/gsat/vocab.raw.json`／`vocab.cleaned.json`／`vocab.qa_report.json`，並複製新的 `vocab.cleaned.json` 覆蓋 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`。
   - **逐項比對新舊兩版 QA 報告**（詞性完整率、中文定義完整率、低信心筆數），以及上一片報告裡明確列為疑慮的樣本（`splendor`、`cruelly`、缺詞性/缺定義的 98+22 筆挑幾筆代表性的），確認新版本有沒有改善，把「改善前 → 改善後」的具體對照寫進報告。

4. `python -m pytest tests/` 全部通過（既有測試與 M5-S1 新增的 `test_topsat_md.py`、`test_cleaner.py` 相關案例都要過；如果你發現這些測試因為資料內容變化而需要調整斷言，可以調整，但不要因為省事而刪測試）。

## 邊界（本切片不做）

- 不改 `src/pdf_parser/rules/top2025_md.py`、`0resource/top2025.md`、既有會考 `output/vocab.*.json`、`exam-vocab-batcher/public/data/vocab.cleaned.json`——這片完全不碰會考資料。
- 不改 App 前端邏輯（`exam-vocab-batcher/src/` 底下任何 `.tsx`／`.ts` 都不動），M5-S2 才會處理 App 端串接。
- 不用把這個新的 OCR 腳本做成通用工具去取代 `ocr_extractor.py`（那是會考版專用、已經穩定運作的東西），這片的腳本只服務學測資料轉錄。
- 不強求 100% 零錯字——OCR 再好的工具也可能有極少數辨識錯誤，這片的目標是「大幅改善、明顯優於上一版」，不是「保證完美」；如果重跑後仍有零星錯字，如實在報告裡列出來，讓負責人決定要不要人工逐一修正剩下的幾筆。

## 驗收（負責人操作）

1. 看報告裡「改善前 → 改善後」的對照表，確認 `splendor`、`cruelly` 這兩個上次抓到的錯字，這次是否已經修正為看起來合理的中文定義。
2. 打開新版 `output/gsat/vocab.qa_report.json`，確認詞性完整率、中文定義完整率有沒有比上一版（94.0%／98.7%）進步，或至少缺值的筆數有明顯減少。
3. 抽查 20~30 個字（延續上次的抽查方式，每個 Level 都抽幾個），確認整體正確率有感提升。
4. 確認 `exam-vocab-batcher/public/data/vocab.cleaned.json`（會考資料）沒有被動到。
5. 若這次抽查已經覺得夠乾淨（不用到 100% 零錯，合理即可），**這一步過了就可以開 M5-S2**；若還有你在意的錯字，跟規劃層說要修哪幾筆，可以小幅再修正，不用整片重做。

## 收工指令（執行層收工必做）

1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果（含改善前後對照的重點數字）；「▶ 下一步」改為「M5-S1b 待負責人再次抽查資料正確性，過了才開 M5-S2」。
2. 若有任何偏離本 BRIEF 的改動（尤其是最終選用的 OCR 方案、DPI 設定、有沒有退回 Tesseract）→ 記 `docs/planning/DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟＋改善前後對照表。
4. **完成以上所有事項、且 `python -m pytest tests/` 全部通過後，將本次變更 commit 並 push 到遠端（`origin main`）。** commit message 用一句話講清楚這片做了什麼（例如「修復: 學測資料改用 PaddleOCR 提高辨識率」），可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。push 前務必確認 `git status` 沒有不該提交的檔案（例如下載下來的 PaddleOCR 模型快取檔，那些通常不該進 git，記得確認 `.gitignore` 有沒有需要補充的規則）。若 push 失敗，不要 force push，把卡住的狀況寫清楚在報告裡。
