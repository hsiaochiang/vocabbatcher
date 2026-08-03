# REPORT_M5S1_學測資料管線 — 執行結果

- 執行時間：2026-08-03 19:48 +08:00
- 狀態：完成（資料需負責人抽查後才可開 M5-S2）

## 改了什麼

- `0resource/topsat.md`：新增學測 Markdown 轉錄檔，共 1640 筆。單字、年份、Level、頁碼由 PDF 表格座標/文字層抽取；中文定義由 Tesseract `eng+chi_tra` OCR 逐頁回填，不保留個別出現年份。
- `src/pdf_parser/models.py`：`VocabEntry`、`CleanedEntry` 新增 `level: str | None`。
- `src/pdf_parser/cleaner.py`：`clean_entries()` 透傳 `level`，並用 `_trim_or_null()` 處理空字串。
- `src/pdf_parser/__main__.py`：Markdown pipeline 改為依 `--rule` 載入 `<rule>_md`，例如 `--rule topsat` 會載入 `src.pdf_parser.rules.topsat_md`。
- `src/pdf_parser/rules/topsat_md.py`：新增學測 Markdown parser，支援頻率章節、Level 欄位、表格列與印刷頁碼。
- `output/gsat/`：產出 `vocab.raw.json`、`vocab.cleaned.json`、`vocab.qa_report.json`。
- `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`：新增前端備用資料檔，內容與 `output/gsat/vocab.cleaned.json` SHA256 相同。
- `tests/test_topsat_md.py`、`tests/test_cleaner.py`：新增學測 parser 測試與 `level` 清洗測試。

## 資料正確性自我檢查

- 整體信心：中等。單字拼字、年份數量、Level、頁碼主要來自 PDF 表格座標與文字層，信心較高；中文定義來自 OCR，仍可能有錯字或漏字，必須由負責人抽查。
- QA 統計：Raw 1640 筆、Cleaned 1640 筆、去重 0、拒絕 0、低信心 1；詞性完整率 94.0%，中文定義完整率 98.7%。
- 已知 OCR 疑慮：98 筆缺詞性、22 筆缺中文定義；另有少數中文定義看起來明顯需人工核對，例如 `suffer`、`refer`、`unique`、`splendor` 等。
- 頁碼偏移：視覺核對 PDF 第 3 頁為印刷頁碼 1，PDF 第 81 頁為印刷頁碼 79，確認固定偏移為 2；`topsat.md` 與 JSON 內 `source_page` 已使用印刷頁碼。
- 出現次數：未把 PDF 目錄的「10~7」合併章節直接寫成同一 frequency，而是用每列年份標記數量計算精確出現次數後分節；`topsat_md.py` 仍支援 `10~7` 範圍標題，若遇到範圍會採下界 7 作為保守值。

## 抽樣清單（供負責人快速核對）

| 單字 | 詞性 | 中文定義 | Level | 出現次數 | 頁碼 |
|---|---|---|---|---:|---|
| passage | n. | 文章的一段;通道;(時間的) 流逝 | 第三級 | 10 | 1 |
| accord | v. | 符合;[n.] 協議 * 考題多出現 according to(根據) | 第五級 | 10 | 1 |
| researcher | n. | 研究員;調查者 | 第四級 | 10 | 1 |
| reduce | v. | 減少;降低 | 第三級 | 8 | 1 |
| various | adj. | 各種的;不同的 | 第三級 | 7 | 2 |
| advantage | n. | 優勢;利益 | 第三級 | 5 | 3 |
| construction | n. | 建設;建築 | 第四級 | 5 | 4 |
| recognize | v. | 辨認;認 | 第三級 | 5 | 3 |
| cruelly | adv. | 殘忍地;殘酪地 | 第三級 | 1 | 39 |
| cupboard | n. | 櫥櫃;壁櫥 | 第三級 | 1 | 39 |
| electricity | n. | 電力;電流 | 第三級 | 1 | 39 |
| rehearse | v. | 排練;演練 | 第六級 | 1 | 79 |
| reef | n. | 礁;暗礁 | 第六級 | 1 | 79 |
| splendor | n. | RE 5 | 第六級 | 1 | 79 |

> `splendor` 與 `cruelly` 的中文定義是刻意列入的疑慮樣本，請優先對照 PDF；若抽查發現同類 OCR 錯誤很多，建議先修 `topsat.md`，不要進 M5-S2。

## 是否偏離 BRIEF

無。`topsat.md` 的中文定義使用 OCR 轉錄，是因為 PDF 中文文字層無法由 PyMuPDF/pdfplumber 直接抽出；已在本報告揭露信心與疑慮。沒有改 `exam-vocab-batcher/src/`、沒有覆蓋會考資料、沒有把 `level` 加進 QA 信心分數。

## pytest 結果

- Baseline（改動前）：`python -m pytest tests/` → 54 passed
- 新增後：`python -m pytest tests/` → 66 passed

## ★ 負責人驗收步驟（白話、按順序）

1. 打開 `docs/handoff/REPORT_M5S1_學測資料管線.md`，先看上方抽樣清單。
2. 打開 `0resource/TopAcademy 學測高頻率單字表.pdf`，對照抽樣清單中的單字、詞性、中文定義、Level、出現次數、頁碼。
3. 再打開 `output/gsat/vocab.cleaned.json`，抽查至少 20~30 個字；請每個 Level（第三級、第四級、第五級、第六級）都抽幾個，不要只看同一頁。
4. 特別優先檢查 `suffer`、`refer`、`unique`、`splendor`、缺詞性或缺中文定義的字，因為這些最可能是 OCR 錯誤。
5. 打開 `output/gsat/vocab.qa_report.json`，確認總筆數 1640、低信心 1、詞性完整率 94.0%、中文定義完整率 98.7%。
6. 確認 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json` 存在，且不要動到 `exam-vocab-batcher/public/data/vocab.cleaned.json`（會考資料）。
7. 若抽查只發現少量錯字，可以先回報要修哪些字；若錯字很多，先不要開 M5-S2，應回頭修 `topsat.md` 或調整 OCR/人工校對流程。

## 遇到的問題 / 卡住的地方（若有）

- PDF 的中文定義無法由 PyMuPDF/pdfplumber 的文字層直接抽出；表格座標可抽到單字/年份/Level，但中文定義欄必須用 OCR。
- OCR 不是 100% 精準。本片已把資料管線做完並產出可抽查 JSON，但不建議在未人工抽查前直接把學測資料接進 App。
