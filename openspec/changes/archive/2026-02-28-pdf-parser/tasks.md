## 1. 專案初始化

- [x] 1.1 建立 `src/pdf_parser/` 目錄結構（`__init__.py`、`__main__.py`、`models.py`、`extractor.py`、`parser.py`、`cleaner.py`、`qa.py`、`rules/__init__.py`、`rules/top2025.py`）
  - 驗收：所有檔案存在，`python -m pdf_parser --help` 可執行
- [x] 1.2 建立 `requirements.txt`（pdfplumber、pytest）與 `README.md`
  - 驗收：`pip install -r requirements.txt` 成功
- [x] 1.3 建立 `tests/` 目錄與 `conftest.py`，準備測試 fixtures
  - 驗收：`pytest --collect-only` 無錯誤

## 2. 資料模型

- [x] 2.1 在 `models.py` 定義 `VocabEntry`、`CleanedEntry`、`QAReport` TypedDict
  - 驗收：可被其他模組 import，型別定義完整

## 3. PDF 抽取（pdf-extract）

- [x] 3.1 實作 `extractor.py`：使用 pdfplumber 逐頁抽取文字，支援 `--page-range`
  - 驗收：傳入 PDF 路徑回傳 `list[dict]`（含 page_number 與 text），頁碼範圍正確過濾
- [x] 3.2 實作表格優先策略：先嘗試 `extract_tables()`，失敗退回逐行文字
  - 驗收：表格頁回傳結構化列資料，非表格頁回傳純文字
- [x] 3.3 撰寫 `tests/test_extractor.py`：涵蓋成功抽取、頁碼範圍、檔案不存在
  - 驗收：pytest 3 個 scenario 全部 pass

## 4. 單字解析（vocab-parse）

- [x] 4.1 定義 `ParserRule` Protocol（`parse_line(line) -> VocabEntry | None`）於 `rules/__init__.py`
  - 驗收：Protocol 可被 mypy / IDE 辨識
- [x] 4.2 實作 `rules/top2025.py`：依據 PDF 實際格式撰寫 regex 規則
  - 驗收：對樣本行正確回傳 VocabEntry，無法解析的行回傳 None
- [x] 4.3 實作 `parser.py`：接受 rule_module 參數，逐行呼叫 `parse_line` 並產出 `vocab.raw.json`
  - 驗收：輸出 JSON 陣列，欄位完整，順序與原始頁面一致
- [x] 4.4 撰寫 `tests/test_parser.py`：涵蓋完整行解析、含音標行、無法解析行、自訂規則
  - 驗收：pytest 4 個 scenario 全部 pass

## 5. 資料清洗（vocab-clean）

- [x] 5.1 實作 `cleaner.py`：去重（word+pos key）、trim、空字串轉 null、合併 source_page
  - 驗收：同 word+pos 僅保留一筆，source_page 為陣列，文字已 trim
- [x] 5.2 實作 `--min-frequency` 過濾邏輯
  - 驗收：frequency < 門檻值的記錄被排除，null frequency 保留
- [x] 5.3 產出 `vocab.cleaned.json`（按 word 字母排序）
  - 驗收：輸出 JSON 內容按 word 排序，格式正確
- [x] 5.4 撰寫 `tests/test_cleaner.py`：涵蓋去重、trim、空字串轉 null、頻率過濾、排序
  - 驗收：pytest 5 個 scenario 全部 pass

## 6. 品質報告（qa-report）

- [x] 6.1 實作 `qa.py`：計算 parse_confidence（依欄位填充率與格式正確性評分）
  - 驗收：全欄位完整時 confidence >= 0.8，僅有 word 時 <= 0.3
- [x] 6.2 實作 issues 陣列產生（missing_pos、missing_definition、suspicious_word、low_confidence）
  - 驗收：各類 issue 正確標記
- [x] 6.3 產出 `vocab.qa_report.json`（含 total_raw/cleaned/duplicates_removed/low_confidence_count/field_completeness/issues_summary）
  - 驗收：所有統計欄位存在且數值正確
- [x] 6.4 撰寫 `tests/test_qa.py`：涵蓋 confidence 計算、issues 標記、報告完整性
  - 驗收：pytest 3 個 scenario 全部 pass

## 7. CLI 整合

- [x] 7.1 實作 `__main__.py`：argparse 整合 --input、--outdir、--min-frequency、--page-range、--rule
  - 驗收：`python -m pdf_parser --help` 顯示所有參數，`--input` 與 `--outdir` 為必填
- [x] 7.2 串接完整 pipeline：extract → parse → clean → qa_report
  - 驗收：執行 CLI 後 `--outdir` 目錄產出三個 JSON 檔案
- [x] 7.3 撰寫 `tests/test_cli.py`：涵蓋 CLI 參數解析與端到端執行
  - 驗收：pytest pass，三個輸出檔案內容正確

## 8. 文件與收尾

- [x] 8.1 撰寫 `README.md`：安裝步驟、使用方式、輸出格式說明、開發指引
  - 驗收：README 包含安裝、使用範例、輸出 schema 說明
- [x] 8.2 使用 `top2025.pdf` 執行端到端驗證，確認三個輸出檔案品質
  - 驗收：vocab.cleaned.json 筆數合理、qa_report 無 P0 issue、欄位完整度 >= 95%
