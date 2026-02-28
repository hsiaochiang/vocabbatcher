# Skill: smoke-tester（冒煙測試／最小驗收）

## 任務目標
避免「agent 說完成可用了，但一按就錯」；用最小測試快速擋掉明顯回歸。

## 依據
- `docs/uiux/<date>_ux-review.md`（flows）
- 本次變更範圍（git diff / commit）
- 主要入口頁面/按鈕

## 輸出（必交付）
- `docs/qa/<date>_smoke.md`，內容必含：
  - 測試環境（local/dev）
  - 測試資料/帳號（若需要）
  - Checklist（3~15 條，對應主要 flows）
  - 結果（Pass/Fail + 證據）
  - 若 Fail：連回 bug 文檔（docs/bugs）

## 建議 checklist 範例
- App 可啟動且首頁不報錯
- 主 CTA 按鈕可點擊且有回饋（loading/disable）
- 主要表單可送出且錯誤提示正常
- 主要列表可載入（含 empty state）
