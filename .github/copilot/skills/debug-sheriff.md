# Skill: debug-sheriff（除錯警長）

## 任務目標
把 bug 修復變成閉環：可重現→定位→修復→驗證→防回歸（並落檔留證據）。

## 依據（Evidence）
- `.github/copilot/rules/30-debug-contract.md`
- 錯誤訊息/stack trace/console log
- 相關頁面與程式碼（檔案路徑）

## 輸出（必交付）
- `docs/bugs/<date>_<slug>.md`，內容必含：
  1) Repro（最短重現步驟）
  2) Root Cause（含定位證據：log/diff）
  3) Fix（改了哪些檔案，為何是這裡）
  4) Verify（如何證明修好）
  5) Regression（防回歸：最小測試/檢查項）
- 需要時：交由 smoke-tester 產出 `docs/qa/<date>_smoke.md`

## 禁止事項
- 沒有重現步驟就大改
- 沒有驗證證據就結案
