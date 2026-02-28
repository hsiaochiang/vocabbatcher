## ADDED Requirements

### Requirement: 產出品質報告

系統 SHALL 產出 `vocab.qa_report.json`，包含以下統計資訊：
- `total_raw`：原始解析筆數
- `total_cleaned`：清洗後筆數
- `duplicates_removed`：去重移除筆數
- `low_confidence_count`：parse_confidence < 0.5 的筆數
- `field_completeness`：各欄位填充率（0.0–1.0）
- `issues_summary`：所有 issue 的彙總清單

#### Scenario: 成功產出 QA 報告

- **WHEN** 資料清洗流程完成
- **THEN** 系統在 `--outdir` 目錄產出 `vocab.qa_report.json`，包含上述所有統計欄位

#### Scenario: 無低信心記錄

- **WHEN** 所有記錄的 parse_confidence >= 0.5
- **THEN** `low_confidence_count` SHALL 為 0

### Requirement: parse_confidence 計算

系統 SHALL 為每筆記錄計算 `parse_confidence`（0.0–1.0），依據已填充的欄位數量與欄位格式正確性評分。

#### Scenario: 所有欄位完整

- **WHEN** 一筆記錄的 word、pos、zh_definition、frequency、ipa_us、ipa_uk 全部有值
- **THEN** parse_confidence SHALL >= 0.8

#### Scenario: 僅有 word

- **WHEN** 一筆記錄僅有 word 有值，其餘欄位為 null
- **THEN** parse_confidence SHALL <= 0.3

### Requirement: issues 陣列

每筆記錄 SHALL 包含 `issues` 陣列，列出該記錄的潛在問題。常見 issue 類型包含：
- `missing_pos`：缺少詞性
- `missing_definition`：缺少中文釋義
- `suspicious_word`：word 包含非英文字母字元
- `low_confidence`：parse_confidence < 0.5

#### Scenario: 記錄缺少詞性

- **WHEN** 一筆記錄的 pos 為 null
- **THEN** issues 陣列 SHALL 包含 `"missing_pos"`

#### Scenario: word 含特殊字元

- **WHEN** word 值為 "apple123"
- **THEN** issues 陣列 SHALL 包含 `"suspicious_word"`
