## Context

VocabBatcher 目前沒有任何程式碼。原始教材為 `top2025.pdf`，內含國中會考英文單字表，每頁以表格或清單格式列出單字、詞性、中文釋義、音標等資訊。本 Change 需從零開始建構一個 Python CLI 工具，將 PDF 解析為結構化 JSON，作為整個產品鏈的數據基礎。

**限制條件**：
- Python 3.11+、Windows 執行環境
- PDF 格式只需支援 `top2025.pdf`（但 parser 規則需可替換）
- 不依賴 OCR（PDF 為文字型）

## Goals / Non-Goals

**Goals:**
- 建立完整的三階段 pipeline：Extract → Parse & Clean → QA Report
- 輸出三個 JSON 檔案（raw / cleaned / qa_report）
- 提供 CLI 介面與常用參數
- parser 規則可替換，方便日後適配不同格式
- pytest 測試覆蓋核心邏輯

**Non-Goals:**
- 不建立 GUI
- 不處理非 `top2025.pdf` 格式（但保留擴展點）
- 不做 JSON schema migration
- 不處理音訊檔案

## Decisions

### D1：PDF 抽取工具 — 選用 pdfplumber

| 方案 | 優點 | 缺點 |
|------|------|------|
| **pdfplumber** ✅ | 表格解析能力強、可取得字元座標、API 直覺 | 相依 pdfminer.six |
| pypdf | 輕量、純 Python | 表格解析弱、難處理複雜排版 |
| pdfminer.six | 底層控制力高 | API 複雜、上手成本高 |

**決定**：優先使用 pdfplumber。若 PDF 內容以表格為主，pdfplumber 的 `extract_tables()` 可直接取出結構化資料。若遇到純文字段落，退回逐行 regex 解析。

### D2：模組架構 — 三層分離

```
src/pdf_parser/
├── __init__.py
├── __main__.py          # CLI 入口 (argparse)
├── extractor.py         # 第一層：PDF → raw text per page
├── parser.py            # 第二層：raw text → structured records
├── cleaner.py           # 第三層：records → deduplicated + cleaned
├── qa.py                # QA 報告產生
├── rules/               # 可替換 regex 規則
│   ├── __init__.py
│   └── top2025.py       # top2025.pdf 專用規則
└── models.py            # dataclass / TypedDict 定義
```

**理由**：三層分離讓每層可獨立測試，`rules/` 目錄讓 parser 規則可插拔替換。

### D3：Parser 規則設計 — Strategy Pattern

- 每個規則模組匯出一個 `ParserRule` Protocol（或 ABC），定義 `parse_line(line: str) -> VocabEntry | None`
- `parser.py` 接受 `rule_module` 參數，預設為 `rules.top2025`
- CLI 加 `--rule` 參數可選擇不同規則模組（未來擴展用）

### D4：資料模型

```python
class VocabEntry(TypedDict):
    word: str
    pos: str | None           # 詞性
    zh_definition: str | None # 中文釋義
    frequency: int | None     # 出現頻率
    source_page: int          # 來源頁碼
    ipa_us: str | None        # 美式音標
    ipa_uk: str | None        # 英式音標

class CleanedEntry(VocabEntry):
    parse_confidence: float   # 0.0 ~ 1.0
    issues: list[str]         # 問題標記

class QAReport(TypedDict):
    total_raw: int
    total_cleaned: int
    duplicates_removed: int
    low_confidence_count: int  # confidence < 0.5
    field_completeness: dict[str, float]  # 各欄位填充率
    issues_summary: list[dict]
```

### D5：去重策略

- Key = `(word.lower().strip(), pos.strip())`
- 同 key 多筆時，保留 `parse_confidence` 最高的那筆
- 合併 `source_page` 為 list（記錄所有出現頁碼）

### D6：CLI 設計

```
python -m pdf_parser --input top2025.pdf --outdir output/
python -m pdf_parser --input top2025.pdf --outdir output/ --min-frequency 2 --page-range 1-50
```

使用 `argparse`，不引入額外 CLI 框架（保持最小依賴）。

## Risks / Trade-offs

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| PDF 排版格式不規則（跨欄、分頁斷行） | regex 解析失敗率上升 | 先用 `extract_tables()` 嘗試表格解析；失敗再退回逐行 regex；qa_report 標記低信心記錄 |
| 音標欄位可能缺失或格式不一致 | ipa_us/ipa_uk 填充率低 | 設為 nullable，qa_report 統計填充率 |
| pdfplumber 版本升級可能破壞 API | 建構失敗 | 鎖定版本於 `requirements.txt`（pin major.minor） |
| 首次看到實際 PDF 內容時規則可能需大幅調整 | 開發時間增加 | 第一步先人工檢視 PDF 前 5 頁，確認格式後再撰寫 regex |

## Open Questions

1. `top2025.pdf` 的實際排版是表格式還是純文字清單？→ 需開發時先人工檢視確認
2. frequency 欄位在 PDF 中的表示方式為何？→ 可能需從上下文推斷
3. 是否需要 `--encoding` 參數？→ pdfplumber 預設 UTF-8，暫不加
