# Decision Log（決策紀錄）

> 所有取捨與規格變更都要留痕（尤其是 Style Freeze / 規範變更）。

| Date | Decision | Why | Impact | Evidence |
|---|---|---|---|---|
| 2026-02-28 | 建立 Prompt Files + Lifecycle Rule 自動化 OpenSpec 工作流 | 從 Antigravity 遷移後缺少 slash command 等效觸發方式 | 新增 17 個 prompt files + 1 rule + 更新 3 檔 | docs/decisions/2026-02-28_openspec-workflow-automation.md |
| 2026-02-28 | WOS Agent + GitKraken MCP + OpenSpec Validate 整合 | 提升自動化程度，減少手動操作 | 新增 WOS agent + 更新 commit-push/validate prompts | .github/agents/WOS.agent.md |
| 2026-02-28 | 建立獨立 GitHub repo `copilot-workspace-template` | Bootstrap 腳本 + Guide 需跨專案共用並可拉取更新 | 所有專案可 `git pull` 取得最新模板；VocabBatcher 的 `0resource/` 為本機備份 | https://github.com/hsiaochiang/copilot-workspace-template |
| 2026-02-28 | 建立 Roadmap 治理規範 + 里程碑驗收機制 | 需明確定義專案範疇、分階段上線標準、及時更新機制 | 新增 rule 40 + 重寫 roadmap（4 里程碑 M1-M4）+ 更新 WOS/quality-gate/status prompt | docs/roadmap.md, .github/copilot/rules/40-roadmap-governance.md |
