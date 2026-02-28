---
agent: agent
description: "程式碼審查：安全性、效能、一致性檢查"
---
請以 `code-reviewer` 角色執行程式碼審查。

步驟：
1. 讀取 `rules/50-tech-stack.md` + `rules/60-testing.md`
2. 讀取 `skills/code-reviewer.md`（角色說明 + checklist）
3. 檢視本次變更的 diff
4. 依 checklist 逐項檢查：安全性 / 效能 / 一致性 / 可維護性 / 測試

輸出格式：
- 🔴 必修（Must Fix）
- 🟡 建議（Suggestion）
- 🟢 良好（Good）

審查通過後提示可進行 `#commit-push`。
