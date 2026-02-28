## ADDED Requirements

### Requirement: 去重合併

系統 SHALL 以 `(word.lower().strip(), pos.strip())` 為 key 進行去重。同 key 多筆記錄時，SHALL 保留 `parse_confidence` 最高的那筆，並合併所有 `source_page` 為陣列。

#### Scenario: 同 word+pos 出現多次

- **WHEN** `vocab.raw.json` 中有多筆 word="apple" 且 pos="n."
- **THEN** `vocab.cleaned.json` 中僅保留一筆，`source_page` 包含所有出現頁碼

#### Scenario: 不同 pos 視為不同記錄

- **WHEN** word="run" 分別出現 pos="v." 和 pos="n."
- **THEN** 系統保留兩筆獨立記錄

### Requirement: 資料清洗

系統 SHALL 對所有文字欄位執行 trim（去除前後空白），將空字串轉為 null。

#### Scenario: 欄位含前後空白

- **WHEN** word 值為 "  apple  "
- **THEN** 清洗後 word 值為 "apple"

#### Scenario: 欄位為空字串

- **WHEN** zh_definition 值為 ""
- **THEN** 清洗後 zh_definition 值為 null

### Requirement: 最低頻率門檻

系統 SHALL 支援 `--min-frequency` 參數，僅保留 frequency >= 門檻值的記錄。未指定時不做頻率過濾。

#### Scenario: 設定最低頻率

- **WHEN** 使用者指定 `--min-frequency 2`
- **THEN** `vocab.cleaned.json` 僅包含 frequency >= 2 的記錄（frequency 為 null 的記錄 SHALL 被保留）

### Requirement: 輸出 vocab.cleaned.json

系統 SHALL 將清洗後的記錄輸出為 `vocab.cleaned.json`，內容為 JSON 陣列，依 word 字母排序。

#### Scenario: 成功輸出 cleaned JSON

- **WHEN** 清洗流程完成
- **THEN** 系統在 `--outdir` 目錄產出 `vocab.cleaned.json`，記錄按 word 字母順序排列
