# 20-ux-flow（UX Flow Contract）

## 目標
- 盤點主要操作流程（happy path / edge cases）
- 每個流程都要有狀態設計：loading / empty / error / success
- 使用者永遠知道：我在哪、下一步是什麼、我做對了嗎

## 產出格式（建議）
- 流程清單：以「使用者目標」命名（例：建立專案、編輯提示詞、匯出、權限設定）
- 每個流程：
  - 前置條件 / 入口
  - 步驟（1..N）
  - 介面反應（按下按鈕後的反應、換頁、提示）
  - 錯誤處理與提示文字（含 retry）
  - 驗收條件（DoD）

## Navigation 架構
- 每個 flow 必須標注使用的 navigation 類型：Stack / Tab / Drawer / Modal
- 頁面層級關係需明確（從哪進、返回到哪）
- Deep link / 通知點擊的入口需標注

## 離線 / 網路狀態
- 明確定義離線策略：local-first / online-only / 混合
- 離線時的 UI 狀態：banner / toast / 功能降級範圍
- 重新上線時的同步行為（自動 / 手動 / 提示）

## 權限流程
- 需要裝置權限的功能（如麥克風、儲存、通知等），需定義：
  - 何時請求（首次使用時 / 啟動時）
  - 拒絕後的 UI 反應（功能降級 + 引導至設定）
  - 永久拒絕的處理

## App 生命週期
- 定義切換至背景時的行為（暫停 / 繼續 / 儲存進度）
- 定義從背景恢復時的行為（刷新 / 恢復 / 提示）
- 長時間背景後（被系統回收）的重新啟動行為

## 手勢規範
- 列出使用的手勢類型：swipe / long-press / pull-to-refresh / pinch 等
- 每個手勢需定義：觸發區域、行為、視覺回饋
- 手勢不可與系統手勢衝突（如邊緣滑動返回）

## 使用方式
- 依據本文件 + `skills/ux-fullstack-engineer.md` 產出 `docs/uiux/<date>_ux-review.md`
