# STAGE_5_PLAN.md — M5「學測單字庫」切片拆分

> 規劃層產出（2026-08-03）。對應 `REQUIREMENTS.md` R13、`DECISIONS.md` 2026-08-03「新增 M5：學測高頻率單字庫」條目。
> 每個切片一份 `BRIEF_M5S#_*.md` 交執行層（Codex CLI），做完一片、負責人親自操作驗收，才開下一片。

## 目標（一句話）
> 把 `TopAcademy 學測高頻率單字表.pdf` 轉成跟會考版完全獨立的第二份單字庫，使用者能在 App 裡切換「會考」／「學測」，兩份資料、頁碼、批次互不混用。

## 規劃時的盤點發現（寫在這裡避免重工）

- **現有會考單字庫的正式資料來源不是直接解析 PDF**：因為原始 PDF 文字抽取有排版/字型問題（見 `src/pdf_parser/ocr_extractor.py` 的說明），實際生產資料是靠一份手動/半自動轉出的 `0resource/top2025.md`（表格式 Markdown，依「出現次數」分章節），由 `src/pdf_parser/rules/top2025_md.py` 解析。這條路徑比較可靠，M5-S1 建議比照辦理，不要硬解 PDF。
- **學測 PDF 排版比會考版複雜**：規劃層已讀過 `0resource/TopAcademy 學測高頻率單字表.pdf` 的內容，除了「出現次數」分章節外，還有 **Level（第三/四/五/六級）**分級，且部分章節（出現次數 1、2）底下又依 Level 再分小節；不能直接套用 `top2025_md.py` 既有的章節解析規則，需要新寫一份規則。
- **負責人已拍板（2026-08-03）**：會考、學測兩份單字庫完全獨立，不合併；學測資料保留 `level` 欄位，不保留個別出現年份（例如「05 07 09」這種逐年出現標記）。
- **`VocabEntry`／`CleanedEntry`（`src/pdf_parser/models.py`）目前沒有 `level` 欄位**，`clean_entries()`（`src/pdf_parser/cleaner.py`）用固定欄位建構物件，新增欄位要三處同步改：`models.py` 型別、`cleaner.py` 建構邏輯、新的 Markdown 解析規則。這個欄位對會考資料要是可選（`None`），不影響既有會考 pipeline 與既有 pytest 測試。
- **輸出檔名规劃**：學測用 `gsat`（學測＝ General Scholastic Ability Test，台灣學測慣用英文簡稱）當識別前綴，避免跟會考既有檔案（`vocab.raw.json`／`vocab.cleaned.json`／`vocab.qa_report.json`，不動、不改名）搞混：
  - Python pipeline 輸出到獨立子目錄 `output/gsat/`（沿用現有 `write_raw_json`／`write_cleaned_json`／`write_qa_report` 的固定檔名，只是目錄不同，不用改這三個函式）。
  - 前端資料檔複製為 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`（會考既有的 `vocab.cleaned.json` 檔名與內容不動）。

## 切片與相依順序

| 切片 | 名稱 | 內容（對應驗收標準） | 相依 | 狀態 |
|---|---|---|---|---|
| M5-S1 | 學測資料管線 | `TopAcademy 學測高頻率單字表.pdf` → 人工/半自動轉出 `0resource/topsat.md`（比照 `top2025.md` 格式，另加 `level` 欄位）→ 新解析規則 `src/pdf_parser/rules/topsat_md.py` → `output/gsat/vocab.cleaned.json` → 複製到 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`。**只做資料，不動 App 前端邏輯**，讓負責人先肉眼核對資料正確性（單字、詞性、中文定義、Level、出現次數）。 | 無 | ✅ 已完成（2026-08-03，`REPORT_M5S1_學測資料管線.md`） |
| M5-S1b | 學測資料 OCR 辨識率校正 | 負責人抽查發現中文定義有 OCR 誤判（例如 `splendor`→「RE 5」、`cruelly`→「殘酪地」）。本片建立可重複執行的 `topsat_transcribe.py`，嘗試 PaddleOCR 但因本機 Windows CPU 推論錯誤改採 Tesseract 300 DPI 裁切字義 cell 備援，重新產出 `topsat.md` 與 `output/gsat/*.json`；QA 缺詞性 98→8、缺中文定義 22→3、低信心 1→0。 | M5-S1 | ✅ 已完成（2026-08-03，`REPORT_M5S1b_學測資料OCR校正.md`；待負責人抽查） |
| M5-S2 | App 端會考/學測來源切換 | App 新增單字庫來源選擇（例如首頁或設定入口，選「會考」／「學測」），`AppContext` 依所選來源載入對應 `vocab.*.cleaned.json`；批次建立器、翻牌卡、考試出題、頁碼範圍、批次歷史，全部依目前所選來源運作，互不混用；已建立的批次要記住是用哪個來源建的（避免使用者切換來源後、舊批次的字對不上目前載入的單字庫）。 | M5-S1b（要有乾淨且經負責人驗收過的學測資料才能接） | ☐ |

## 跨切片一致性（執行層務必遵守）

- `level` 欄位只在 `VocabEntry`／`CleanedEntry`（Python）與對應的前端 `VocabEntry`（TS，M5-S2 才會用到）新增，會考資料這個欄位一律是 `None`／不存在，不得因為新增欄位而動到既有會考資料或既有 pytest 測試的預期輸出。
- M5-S1 沿用 `top2025_md.py` 的「Markdown 表格 → parser」架構模式（`_FREQ_HEADER_RE`、`_TABLE_ROW_RE` 等正則比對邏輯），但因為章節結構不同（多了 Level 子分節），不要硬改 `top2025_md.py` 本體去相容兩種格式，另開一份 `topsat_md.py`，避免改壞會考既有 pipeline。
- M5-S2 串接「來源切換」時，**不修改**既有會考資料流的任何路徑（`vocab.cleaned.json`、`AppContext` 對會考資料的既有處理邏輯保留原樣，切換邏輯用「依目前選的來源決定要 fetch 哪個檔案」的方式疊加，不要把兩份資料的型別/邏輯混在一起判斷）。
- 兩片都要遵守既有地雷：不動 `BrowserRouter`、不動 Workbox `navigateFallbackDenylist`、不動 Firestore 安全規則。

## 驗收軌道 B（負責人把關，白話清單）

1. M5-S1：規劃層／執行層會給你一份 `topsat.md`（或直接看 `output/gsat/vocab.cleaned.json`）與抽樣清單，請你對照手上的學測 PDF，抽查至少 20~30 個單字（含每個 Level 至少抽幾個），確認單字拼字、詞性、中文定義、Level、出現次數都跟 PDF 上印的一致。這一步過了才能開 M5-S2。
2. M5-S2：App 裡有地方可以選「會考」或「學測」；選學測後，建立批次、翻牌學習、練習測驗（含拼字填空）都只會出現學測單字庫裡的字；切回會考，一切恢復原本熟悉的內容，兩邊互不干擾。

## 待記錄的需求變更

- 若 M5-S1 執行過程中發現學測 PDF 有排版問題導致部分章節無法可靠解析（比照當初會考版遇過的狀況），要在報告裡明確列出哪些章節/單字有疑慮，讓負責人決定要人工修正 `topsat.md` 還是接受目前的信心水準，不要在資料有疑慮的情況下悄悄放行到 M5-S2。
