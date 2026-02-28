## ADDED Requirements

### Requirement: 解析單字記錄

系統 SHALL 將每頁的原始文字解析為結構化單字記錄，每筆記錄包含以下欄位：
- `word`（str，必填）
- `pos`（str | null，詞性）
- `zh_definition`（str | null，中文釋義）
- `frequency`（int | null，出現頻率）
- `source_page`（int，必填，來源頁碼）
- `ipa_us`（str | null，美式音標）
- `ipa_uk`（str | null，英式音標）

#### Scenario: 成功解析完整單字行

- **WHEN** 原始文字行包含 word、pos、zh_definition
- **THEN** 系統正確填入對應欄位，缺少的選填欄位設為 null

#### Scenario: 解析含音標的行

- **WHEN** 原始文字行包含 IPA 音標
- **THEN** 系統 SHALL 將美式音標填入 `ipa_us`、英式音標填入 `ipa_uk`

#### Scenario: 無法解析的行

- **WHEN** 某行文字不符合任何已知的單字格式
- **THEN** 系統 SHALL 跳過該行，不產生記錄，但 SHALL 記錄為低信心項目

### Requirement: 可替換的 Parser 規則

系統 SHALL 採用 Strategy Pattern 設計 parser 規則。每個規則模組 SHALL 實作 `parse_line(line: str) -> VocabEntry | None` 介面。

#### Scenario: 使用預設規則

- **WHEN** 使用者未指定 `--rule` 參數
- **THEN** 系統 SHALL 使用 `rules.top2025` 模組進行解析

#### Scenario: 指定自訂規則

- **WHEN** 使用者指定 `--rule custom_rule` 參數
- **THEN** 系統 SHALL 載入 `rules.custom_rule` 模組進行解析

### Requirement: 輸出 vocab.raw.json

系統 SHALL 將逐頁解析結果輸出為 `vocab.raw.json`，內容為所有解析記錄的 JSON 陣列，保持原始順序。

#### Scenario: 成功輸出 raw JSON

- **WHEN** 解析完成
- **THEN** 系統在 `--outdir` 目錄產出 `vocab.raw.json`，包含所有成功解析的記錄
