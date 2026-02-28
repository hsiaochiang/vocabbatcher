# Skill: code-reviewer（程式碼審查員）

## 任務目標
在提交前做結構化的程式碼審查，擋掉安全性、效能、一致性問題。

## 依據
- `.github/copilot/rules/50-tech-stack.md`（技術棧約定）
- `.github/copilot/rules/60-testing.md`（測試策略）
- `.github/copilot/rules/10-style-guide.md`（UI 規範，若涉及前端）
- 本次變更的 diff

## 審查 Checklist

### 安全性
- [ ] 沒有硬編碼的密鑰 / token / 密碼
- [ ] 使用者輸入有做驗證與清理（sanitize）
- [ ] API 呼叫有做錯誤處理
- [ ] 檔案操作有做路徑驗證（避免 path traversal）
- [ ] 沒有暴露敏感資訊到 log / UI

### 效能
- [ ] 沒有不必要的重複渲染 / 重複計算
- [ ] 大量資料處理使用分頁 / 串流 / 批次
- [ ] 非同步操作有適當的 loading 狀態
- [ ] 沒有記憶體洩漏風險（event listener / subscription 有清理）

### 一致性
- [ ] 符合 `50-tech-stack.md` 的技術選型
- [ ] 命名風格一致（camelCase / PascalCase / snake_case）
- [ ] 錯誤處理模式一致（try-catch / Result type / error boundary）
- [ ] 目錄結構符合專案慣例

### 可維護性
- [ ] 函式職責單一（不超過 50 行為佳）
- [ ] 沒有重複程式碼（可抽取的已抽取）
- [ ] 關鍵邏輯有必要的註解
- [ ] 公開 API / 型別有適當的文件

### 測試
- [ ] 新增 / 修改的邏輯有對應測試
- [ ] 測試涵蓋 happy path + 主要 edge case
- [ ] 測試可獨立執行（不依賴外部狀態）

## 輸出（建議格式）
```markdown
## Code Review: <PR/commit 描述>
### 🔴 必修（Must Fix）
- [檔案:行號] 問題描述 → 建議修改

### 🟡 建議（Suggestion）
- [檔案:行號] 問題描述 → 建議修改

### 🟢 良好（Good）
- 值得肯定的做法
```

## 使用方式
- 告訴 Copilot：「請以 code-reviewer 角色審查這次變更」
- 可搭配 `git-steward` 在 commit 前執行
