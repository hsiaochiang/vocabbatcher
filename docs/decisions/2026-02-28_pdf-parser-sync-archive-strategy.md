# Decision: pdf-parser 規格同步與歸檔策略

- Date: 2026-02-28
- Scope: OpenSpec change lifecycle（`pdf-parser`）
- Related Commands: `/opsx:sync`, `/opsx:archive`

## Context

在 `pdf-parser` change 完成後，已先執行 `/opsx:sync "pdf-parser"`，將 delta specs 同步到 `openspec/specs/*`。之後執行 `/opsx:archive "pdf-parser"` 時，OpenSpec 仍嘗試再套用一次 delta，造成 requirement 重複衝突並中止。

實際錯誤訊息：
- `pdf-extract ADDED failed for header "### Requirement: 逐頁抽取 PDF 文字" - already exists`
- `Aborted. No files were changed.`

## Decision

在「已先完成 `/opsx:sync`」的情況下，archive 階段一律使用：

```bash
openspec archive "<change-name>" --yes --skip-specs
```

對 `pdf-parser` 已採用：

```bash
openspec archive "pdf-parser" --yes --skip-specs
```

並成功歸檔為：
- `openspec/changes/archive/2026-02-28-pdf-parser/`

## Why

- 避免重複套用 delta specs 造成衝突（idempotency 問題）
- 保持已同步完成的 `openspec/specs/*` 為單一真實來源（source of truth）
- 降低歸檔流程不必要失敗，確保 lifecycle 可穩定執行

## Impact

- `pdf-parser` 已成功從 active changes 移除（`openspec list --json` 為空）
- 主規格已保留於：
  - `openspec/specs/pdf-extract/spec.md`
  - `openspec/specs/vocab-parse/spec.md`
  - `openspec/specs/vocab-clean/spec.md`
  - `openspec/specs/qa-report/spec.md`
- 後續流程規則明確：
  - 若先 sync，再 archive 必須加 `--skip-specs`

## Evidence

- 指令結果：
  - `openspec archive "pdf-parser" --yes`（失敗，重複 requirement）
  - `openspec archive "pdf-parser" --yes --skip-specs`（成功）
- 狀態檢查：
  - `openspec list --json` -> `{"changes":[]}`
- 相關檔案：
  - `openspec/changes/archive/2026-02-28-pdf-parser/`
  - `openspec/specs/*/spec.md`
