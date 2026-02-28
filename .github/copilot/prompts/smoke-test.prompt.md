---
agent: agent
description: "冒煙測試：最小驗收 checklist"
---
請以 `smoke-tester` 角色執行冒煙測試。

步驟：
1. 讀取 `skills/smoke-tester.md`（角色說明）
2. 確認本次變更範圍（git diff 或手動說明）
3. 產出 `docs/qa/<今日日期>_smoke.md`

輸出內容必含：
- 測試環境
- 測試資料/帳號（若需要）
- Checklist（3~15 條，對應主要 flows）
- 結果（Pass / Fail + 證據）
- 若 Fail：連回 bug 文檔路徑
