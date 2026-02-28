# 30-debug-contract（Debug Contract）

## 除錯閉環（必走）
1) 重現：最短重現步驟（含環境、帳號、資料）
2) 定位：root cause 與定位證據（log / stack trace / diff）
3) 修復：改了哪些檔案、為何是這裡
4) 驗證：修復後如何驗證（步驟 + 證據）
5) 防回歸：補最小必要測試/檢查項（避免下次又壞）

## 禁止事項
- 沒有重現步驟，不得宣稱已修好
- 沒有驗證證據，不得結案

## 行動裝置偵錯（若適用）
- 重現步驟需標注測試裝置：模擬器 / 實機 + OS 版本
- 使用平台對應的 debug 工具（DevTools / 日誌檢視器 / 效能分析器）
- 若為裝置特定問題，需記錄裝置型號與 OS 版本

## 使用方式
- 依據本文件 + `skills/debug-sheriff.md` + `skills/smoke-tester.md`
- 產出 `docs/bugs/<date>_<slug>.md` + `docs/qa/<date>_smoke.md`
