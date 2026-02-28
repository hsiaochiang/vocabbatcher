# Skill: git-steward（版本控管管家）

## 任務目標
把每次變更都變成可追溯證據，降低「做了但找不到改哪」的風險。

## 分支策略
- 分支命名慣例：
  - `feature/<slug>` — 新功能
  - `bugfix/<slug>` — Bug 修復
  - `hotfix/<slug>` — 緊急修復
  - `chore/<slug>` — 雜務（依賴升級、CI、文件）
- 主分支保護：不得直接 push 到 main/master（建議）

## Commit Template（繁中）
- What：做了什麼（具體檔案/功能）
- Why：為什麼要做
- Impact：對使用者/系統的影響
- Evidence：如何驗證（測試/截圖/log/文件）

## .gitignore 建議
- 專案初始化時確認 `.gitignore` 包含：
  - 開發框架產生的暫存檔 / build 產出
  - 依賴套件目錄（`node_modules/`、`venv/` 等）
  - 組態檔案（`.env`、`*.local`）
  - OS 產生的檔案（`.DS_Store`、`Thumbs.db`）
  - IDE 設定（`.idea/`、`.vscode/` 中的個人設定）

## PR 流程（若有協作者）
- PR description 格式：What / Why / How to test / Evidence links
- 至少一人 review（或自己用 checklist 自審）
- 合併前確認 smoke test 通過

## Outputs
- 建議的 git 指令序列
- commit message（繁中，含 What/Why/Impact/Evidence）
- 若有風險：提醒需要 review / 分支策略
