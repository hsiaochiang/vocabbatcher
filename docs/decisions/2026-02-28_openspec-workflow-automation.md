# 決策：OpenSpec 工作流自動化 — Prompt Files + Lifecycle Rule

> 日期：2026-02-28

## 背景
從 Antigravity 遷移到 GitHub Copilot 後，原本的 `/opsx-*` slash commands 失去了對應觸發方式。
目前所有操作需要手動用自然語言描述，效率低且容易遺漏步驟。

## 決策
1. 建立 `.github/copilot/prompts/` 下的 prompt files（等效 slash command）
2. 新增 `rules/70-openspec-workflow.md` 定義完整 Change Lifecycle
3. 更新 `openspec-conductor.md` 對接內建 OpenSpec skills
4. 更新 `copilot-instructions.md` 任務觸發表加入 prompt 參考
5. 補充 `openspec/config.yaml` 專案上下文

## 影響
- 新增 ~18 個 prompt files（小檔案，只有觸發指令）
- 新增 1 個 rule 檔案
- 修改 3 個現有檔案
- 不影響任何程式碼或現有規範內容

## 預期效果
- 每個流程步驟可一鍵觸發（`#prompt-name`）
- 完整 Change Lifecycle 有文件記錄
- 流程步驟強制串聯（review → commit → push）
- 減少遺漏關鍵步驟的風險

## 新增 Prompt 清單
| Prompt | 對應動作 |
|---|---|
| `session-start` | 開工流程（preflight） |
| `opsx-explore` | 需求探索 |
| `opsx-new` | 建立新 Change |
| `opsx-ff` | 快進 artifact 生成 |
| `opsx-validate` | 驗證 Change 完整性 |
| `opsx-apply` | 實作 Change |
| `opsx-verify` | 驗證實作結果 |
| `opsx-sync` | 同步 specs |
| `opsx-archive` | 歸檔 Change |
| `ui-review` | UI 審查 |
| `ux-review` | UX 審查 |
| `smoke-test` | 冒煙測試 |
| `code-review` | 程式碼審查 |
| `status` | 狀態更新 |
| `commit-push` | 審查 + 提交 + 推送 |
| `log-decision` | 記錄決策 |
| `session-close` | Session 收尾 |
