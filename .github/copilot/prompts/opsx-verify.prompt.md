---
agent: agent
description: "OpenSpec：驗證實作是否符合 Change artifacts"
---
請使用 `openspec-verify-change` skill 驗證實作結果。

檢查項目：
1. 每個 task 的驗收條件是否滿足
2. 實作是否與 spec / delta-spec 一致
3. 是否有未處理的邊界情況
4. Done Gate（`rules/35-quality-gate.md`）是否通過

若涉及：
- UI 修改 → 提示需要 `#ui-review`
- UX 流程 → 提示需要 `#ux-review`
- Bug 修復 → 提示需要 `#smoke-test`

完成後提示進入品質閘階段。
