---
agent: agent
description: "UI 審查：依 Style Guide 比對差異並產出修正計畫"
---
請以 `ui-designer` 角色執行 UI 審查。

步驟：
1. 讀取 `rules/10-style-guide.md`（Style Contract）
2. 讀取 `skills/ui-designer.md`（角色說明）
3. 對目標頁面/元件進行比對
4. 產出 `docs/uiux/<今日日期>_ui-review.md`

輸出內容必含：
- Findings（差異清單）：現況 vs 規範 + 引用章節
- Patch Plan（修正計畫）：可直接執行的修改清單
- Acceptance（驗收）：如何驗收
- Evidence（證據）：diff / 截圖 / runlog 位置

如果你不確定目標頁面，請先問我。
