# 50-tech-stack（技術棧約定）

## 目標
- 統一技術選型，避免同一功能重複引入不同套件
- 新增 dependency 需有決策記錄

## 技術棧清單（依專案填入）

### 語言 / 框架
- （請填入：例如 TypeScript、Python、React Native + Expo、Next.js 等）

### 狀態管理
- （請填入：例如 Zustand、Redux Toolkit、Pinia 等）

### 資料儲存
- 本地：（請填入：例如 AsyncStorage、SQLite、MMKV 等）
- 遠端：（請填入：例如 Supabase、Firebase、自建 API 等）

### UI 元件庫
- （請填入：例如 NativeBase、Tamagui、shadcn/ui 等）

### 測試工具
- 單元測試：（請填入：例如 Jest、Vitest 等）
- 整合 / E2E：（請填入：例如 Detox、Maestro、Playwright 等）

### 其他工具
- 音檔處理：（請填入）
- 多語系：（請填入）
- CI/CD：（請填入）

## 新增 Dependency 規則
- 引入新套件前，先確認沒有現有套件能解決
- 新增套件需記錄決策到 `docs/decisions/`，內容包含：
  - 套件名稱與版本
  - 為什麼選這個（vs 替代方案）
  - 對 bundle size / 啟動速度的影響評估
  - 授權條款（license）確認

## Node / Python 版本
- （請填入：例如 Node ≥ 18、Python ≥ 3.11）

## 使用方式
- 專案初始化時填入本文件
- 每次新增 dependency 時對照並更新
- Style Freeze 後，此文件連同 `10-style-guide.md` 一起凍結
