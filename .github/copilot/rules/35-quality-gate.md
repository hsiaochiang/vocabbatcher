# 35-quality-gate（完成宣告門檻 / Done Gate）

> 目的：處理常遇到的狀況：agent 說「完成可用了」，但一按就錯。

## Done Gate（缺一不可）
- UI 相關修改：
  - 必須更新 `docs/uiux/<date>_ui-review.md`（差異→修正→驗收→證據）
- UX 流程修改：
  - 必須更新 `docs/uiux/<date>_ux-review.md`（flow/狀態/DoD）
- Bug 修復：
  - 必須產出 `docs/bugs/<date>_<slug>.md`（重現/定位/修復/驗證/防回歸）
  - 必須產出 `docs/qa/<date>_smoke.md`（最小 smoke checklist + 結果）

- 功能實作：
  - 必須有對應的規格（spec）或需求描述
  - 必須通過基本 smoke test（主要 happy path 可用）
  - 若有 OpenSpec tasks，需更新 task 狀態
- 效能相關：
  - 批次操作 / 檔案生成 / 大量資料處理需確認不造成 UI 凍結（ANR / 無回應）
  - 若有明顯效能疑慮，需記錄測試結果（操作時間 / 記憶體用量）

## 里程碑驗收門檻（Milestone Release Gate）
- 上線前必須滿足 `docs/roadmap.md` §2 中該里程碑的**所有**驗收標準
- 必須有對應的 smoke test 記錄（`docs/qa/`）
- 無未關閉的 P0 bug（`docs/bugs/`）
- 已記錄上線決策（`docs/decision-log.md`）
- 詳見 `rules/40-roadmap-governance.md`

## 若未通過 Done Gate
- 不得宣稱 Done
- 必須補齊 evidence 後再回報
