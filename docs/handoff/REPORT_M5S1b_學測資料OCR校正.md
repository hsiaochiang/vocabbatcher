# REPORT_M5S1b_學測資料OCR校正 — 執行結果

- 執行時間：2026-08-03 23:15 +08:00
- 狀態：完成（待負責人再次抽查資料正確性）

## 改了什麼

- 優先嘗試 PaddleOCR：已安裝 `paddleocr 3.7.0`、`paddlepaddle 3.3.1`，並成功下載 PP-OCRv5 模型；但本機 Windows CPU 推論固定失敗，錯誤為 `ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`，關閉相關旗標仍失敗。
- 依 BRIEF 備援條件改用 Tesseract 優化版：渲染 DPI 固定 300，裁切每筆單字的中文定義 cell 後 OCR；單字、Level、頁碼、出現次數仍用 PDF 表格層，不用 OCR 猜。
- 新增可重複執行腳本：`src/pdf_parser/tools/topsat_transcribe.py`。
- 實際重跑指令：
  `python src/pdf_parser/tools/topsat_transcribe.py --input "0resource/TopAcademy 學測高頻率單字表.pdf" --output 0resource/topsat.md --dpi 300 --engine tesseract --pos-fallback-md .codex-tmp/topsat_m5s1_old.md`
- 重新產出檔案：
  `0resource/topsat.md`
  `output/gsat/vocab.raw.json`
  `output/gsat/vocab.cleaned.json`
  `output/gsat/vocab.qa_report.json`
  `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`
- `output/gsat/vocab.cleaned.json` 與 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json` SHA256 相同：`5BC0CF82A64A614B32279A20637D120810516B042E285724F8F0393CC9F1100D`。

## 改善前 → 改善後對照

### QA 完整率

| 指標 | M5-S1 舊版 | M5-S1b 新版 |
|---|---:|---:|
| 詞性完整率 | 94.0%（缺 98） | 99.5%（缺 8） |
| 中文定義完整率 | 98.7%（缺 22） | 99.8%（缺 3） |
| 低信心筆數 | 1 | 0 |
| raw / cleaned | 1640 / 1640 | 1640 / 1640 |
| rejected lines | 0 | 0 |

新版仍缺詞性的 8 筆：`attach`、`bullying`、`evaluate`、`impress`、`landmark`、`layer`、`splash`、`terrify`。

新版仍缺中文定義的 3 筆：`fiber`、`glory`、`humidity`。

### 具體樣本

| 單字 | 改善前 zh_definition | 改善後 zh_definition |
|---|---|---|
| splendor | RE 5 | 壯麗;輝煌;壯觀 |
| cruelly | 殘忍地;殘酪地 | 殘忍地;殘酷地 |
| refer | BS (+to) | 提及;參考(+to) |
| suffer | WSs Bow | 遭受;忍受;患病 |
| unique | fad.) 獨特的;唯一的 | 獨特的;唯一的 |
| injury | 傷害;損作 | 傷害;損傷 |
| risk | 風險;危險;擔 ... 的風險 | 風險;危險;[v.] 擔...的風險 |
| preference | 偏愛偏好;優先選擇 | 偏愛;偏好;優先選擇 |
| passage | 文章的一段;通道;(時間的) 流逝 | 文章的一段;通道;(時間的) 流逝 |
| researcher | 研究員;調查者 | 研究員;調查者 |

## 是否偏離 BRIEF

有，已記錄在 `docs/planning/DECISIONS.md` 的「2026-08-03　M5-S1b OCR 方案改用 Tesseract 300 DPI 優化版（PaddleOCR 推論失敗）」條目。

偏離內容：原定優先使用 PaddleOCR，但本機 PaddleOCR 推論階段失敗；本版改用 Tesseract 300 DPI 裁切字義 cell 備援，並加入少量已目視確認的校正表。沒有改 `exam-vocab-batcher/src/`，沒有動會考資料。

## pytest 結果

通過：`python -m pytest tests/` → 66 passed。

## ★ 負責人驗收步驟（白話、按順序）

1. 打開 `docs/handoff/REPORT_M5S1b_學測資料OCR校正.md`，先看上面的 QA 表格，確認缺詞性從 98 降到 8、缺中文定義從 22 降到 3。
2. 打開 `output/gsat/vocab.cleaned.json`，搜尋 `splendor`、`cruelly`、`refer`、`suffer`、`unique`，確認這幾個上次錯得明顯的字已經變合理。
3. 打開 `0resource/TopAcademy 學測高頻率單字表.pdf`，抽查 20~30 個字；每個 Level（第三級、第四級、第五級、第六級）都抽幾個，不要只看同一頁。
4. 特別看新版仍缺資料的 11 個字：缺詞性 8 筆、缺中文定義 3 筆；若你很在意，可以回報要人工補哪幾筆。
5. 確認 `exam-vocab-batcher/public/data/vocab.cleaned.json`（會考資料）沒有被動到；本片只覆蓋學測資料 `vocab.gsat.cleaned.json`。
6. 如果抽查覺得整體已夠乾淨，這關通過後才開 M5-S2；若仍有你在意的錯字，先回報字詞清單，不要急著接進 App。

## 遇到的問題 / 卡住的地方（若有）

- PaddleOCR 安裝與模型下載成功，但在本機 Windows CPU 推論失敗，因此本版不能宣稱是 PaddleOCR 產物。
- Tesseract 300 DPI 裁切版大幅降低缺值與明顯錯字，但仍不是 100% 校對完成；建議負責人完成抽查後再接 M5-S2。
