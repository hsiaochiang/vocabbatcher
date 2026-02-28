---
agent: agent
description: "OpenSpec：實作 Change 中的 tasks"
---
請使用 `openspec-apply-change` skill 實作目前進行中 Change 的 tasks。

遵守規則：
- 參照 `rules/50-tech-stack.md` 技術棧約定
- 遵守 `rules/36-scope-guard.md` 範圍護欄
- 最小安全修改原則（Smallest Safe Change）
- 每完成一個 task 就更新狀態
- 在 `docs/runlog/` 記錄進度

完成後提示我進行 `#opsx-verify` 驗證實作結果。
