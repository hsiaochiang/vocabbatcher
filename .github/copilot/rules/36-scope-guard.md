# 36-scope-guard（範圍護欄 / Smallest Safe Change 強化）

## 目標
- 避免為了修一個 bug/調一個 UI，把其它頁面或流程一起弄壞（引入新 bug）
- 確保每次改動可回溯、可驗收、可快速回滾

## 觸發條件（遇到就先停、先記錄決策）
- 一次改動超過 5 個檔案
- 需要改動 tokens / Style Contract（10-style-guide）
- 沒有重現步驟卻想大改
- 同一問題第 3 次仍未收斂（代表需要換策略）

- 新增或升級 dependency（套件 / 函式庫）
- 新增或移除頁面路由（navigation route）
- 變更資料庫 schema 或本地儲存結構

## 拆解策略
- 先把「最短修復」做出來 → 先通過 smoke → 再做重構/美化
