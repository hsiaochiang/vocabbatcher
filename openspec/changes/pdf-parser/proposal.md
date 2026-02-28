## Why

VocabBatcher 的所有功能（批次錄音、練習測驗、逐字學習）都以結構化單字資料為基礎。目前尚無任何方式將原始 PDF 教材（`top2025.pdf`）轉換為 JSON 單字庫，因此整條產品鏈無法啟動。PDF Parser 是 M1（Data Ready）里程碑的唯一交付物，完成後才能進入 UI 原型與 App 開發。

## What Changes

- **新增** Python 3.11 CLI 工具 `pdf_parser`，將 `top2025.pdf` 解析為結構化 JSON
- **新增** 三階段輸出管線：
  - `vocab.raw.json`：逐頁原始解析結果
  - `vocab.cleaned.json`：去重、清雜訊、合併同 word+pos 的乾淨資料
  - `vocab.qa_report.json`：品質報告（parse_confidence 0–1、issues 陣列）
- **新增** 可替換的 regex parser 規則設計，方便日後適配不同 PDF 格式
- **新增** CLI 參數：`--input`、`--outdir`、`--min-frequency`、`--page-range`
- **新增** pytest 單元測試與 README

## Capabilities

### New Capabilities

- `pdf-extract`: PDF 文字抽取——使用 pdfplumber/pypdf 逐頁抽取文字並保留頁碼
- `vocab-parse`: 單字解析——從原始文字解析出 word、pos、zh_definition、frequency、source_page、ipa_us/ipa_uk 等欄位；parser 規則可替換
- `vocab-clean`: 資料清洗——去重（同 word+pos 合併）、trim、清雜訊、空值設為 null
- `qa-report`: 品質報告——產出 parse_confidence（0–1）與 issues 陣列，標記低信心或異常記錄

### Modified Capabilities

（無——目前沒有既有 specs）

## Non-goals

- 不支援 `top2025.pdf` 以外格式的自動適配（僅保留可替換 regex 的擴充點）
- 不提供 GUI；本工具為純 CLI
- 不做雲端上傳或與 App 的即時同步
- 不處理音訊或發音檔案；音標僅為文字欄位
- 不負責 JSON schema 版本遷移

## Roadmap Impact

- **直接推進 M1（Data Ready）**：本 change 完成後，M1 的 7 項驗收標準中至少可勾選：
  - ☑ vocab.cleaned.json 存在且可被 App 載入
  - ☑ 欄位完整度 ≥ 95%
  - ☑ qa_report 無 P0 issue
  - ☑ 去重後筆數與教材目錄吻合（±5%）
  - ☑ pytest 通過率 100%
- **階段轉換**：M1 完成後可進入 S2（UI/UX Review）
- **無 Breaking Change**，不影響既有程式碼（目前無程式碼）

## Impact

- **新增依賴**：`pdfplumber`（或 `pypdf`）、`pytest`
- **新增目錄**：`src/pdf_parser/`（CLI + parser 模組）、`tests/`
- **輸出檔案**：`output/vocab.raw.json`、`output/vocab.cleaned.json`、`output/vocab.qa_report.json`
- **系統需求**：Python 3.11+、Windows 可執行
