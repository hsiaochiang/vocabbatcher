---
agent: agent
description: "記錄決策：落檔到 decision-log 和 decisions/"
---
請執行決策記錄：

1. 確認本次決策的內容（若不清楚，請問我）
2. 在 `docs/decision-log.md` 新增一行：
   - Date | Decision | Why | Impact | Evidence
3. 若為重大決策（Style Freeze / 規範變更 / 架構調整），額外產出：
   - `docs/decisions/<今日日期>_<slug>.md`
   - 內容：背景 / 決策 / 原因 / 影響 / 替代方案 / 證據

完成後確認 decision-log.md 已更新。
