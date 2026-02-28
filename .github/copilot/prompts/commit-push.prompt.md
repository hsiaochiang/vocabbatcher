---
agent: agent
description: "審查 + 提交 + 推送：先 review 再 commit/push（GitKraken MCP 自動化）"
---
請以 `git-steward` + `code-reviewer` 角色執行提交流程。
優先使用 GitKraken MCP 工具（`mcp_gitkraken_*`）執行 git 操作，若 MCP 不可用則 fallback 到終端指令。

**嚴格順序**：

### Step 1：查看變更（GitKraken MCP）
- 使用 `mcp_gitkraken_git_status` 查看目前工作區狀態
- 使用 `mcp_gitkraken_git_log_or_diff` 查看詳細 diff
- 依 `code-reviewer.md` checklist 審查
- 若有 🔴 必修項 → 停止，先修復

### Step 2：Review 結果呈現
- 列出變更檔案清單
- 列出 review 結果（必修/建議/良好）
- **等待我確認後才繼續**

### Step 3：Commit + Push（我確認後執行）
- 產出 commit message（繁體中文，含 What / Why / Impact / Evidence）
- 使用 `mcp_gitkraken_git_add_or_commit` 執行 stage + commit
- 使用 `mcp_gitkraken_git_push` 執行 push

### Fallback（MCP 不可用時）
- 改用終端執行 `git add` + `git commit` + `git push`

注意：
- 不得跳過 review 直接 commit
- commit message 必須使用繁體中文
