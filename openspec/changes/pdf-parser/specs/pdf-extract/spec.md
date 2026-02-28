## ADDED Requirements

### Requirement: 逐頁抽取 PDF 文字

系統 SHALL 使用 pdfplumber 開啟指定的 PDF 檔案，逐頁抽取文字內容，並保留每頁的頁碼。

#### Scenario: 成功抽取完整 PDF

- **WHEN** 使用者提供有效的 PDF 檔案路徑
- **THEN** 系統回傳所有頁面的文字內容，每筆記錄包含 `page_number`（int）與 `text`（str）

#### Scenario: 指定頁碼範圍

- **WHEN** 使用者提供 `--page-range 5-20` 參數
- **THEN** 系統僅抽取第 5 頁至第 20 頁的文字內容

#### Scenario: PDF 檔案不存在

- **WHEN** 使用者提供不存在的檔案路徑
- **THEN** 系統 SHALL 拋出明確的錯誤訊息並以非零 exit code 結束

### Requirement: 表格優先抽取策略

系統 SHALL 優先嘗試使用 pdfplumber 的 `extract_tables()` 取得結構化表格資料。若該頁無法解析為表格，SHALL 退回為逐行文字抽取。

#### Scenario: 頁面含表格

- **WHEN** 某頁 PDF 包含可解析的表格
- **THEN** 系統使用 `extract_tables()` 回傳結構化列資料

#### Scenario: 頁面無表格

- **WHEN** 某頁 PDF 無法被解析為表格
- **THEN** 系統退回為逐行純文字抽取，以換行符分割
