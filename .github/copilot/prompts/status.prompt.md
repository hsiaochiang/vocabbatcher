---
agent: agent
description: "狀態更新：同步 roadmap（含里程碑驗收進度）與 runlog"
---
請先讀取 `rules/40-roadmap-governance.md` 了解狀態更新規範，然後執行狀態更新：

1. 讀取 `docs/roadmap.md`，確認目前階段與里程碑
2. 讀取 `openspec/changes/` 查看進行中的 Changes
3. 檢查 `docs/bugs/` 是否有未關閉的 P0/P1 bug
4. 更新 `docs/roadmap.md` §4 目前狀態：
   - Current 階段
   - Next 步驟
   - Blockers（阻塞因素）
   - Evidence（證據連結）
5. 更新 `docs/runlog/<今日日期>_README.md`
6. 輸出 `rules/40-roadmap-governance.md` 中定義的狀態更新範本格式，包含：
   - Roadmap 階段
   - 里程碑驗收進度（M1~M4 各幾項已完成）
   - 下一步建議
   - 風險/阻塞

若偵測到里程碑驗收全部勾選，主動提醒可以上線。
