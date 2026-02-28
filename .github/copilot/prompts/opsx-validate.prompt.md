---
agent: agent
description: "OpenSpec：驗證 Change 完整性（自動呼叫 openspec validate）"
---
請對目前進行中的 Change 執行嚴格驗證。

### Step 1：找出目前 Change
- 讀取 `openspec/changes/` 目錄，找出進行中的 change（排除 `archive/`）
- 若無進行中 Change → 告知並停止

### Step 2：執行 OpenSpec CLI 驗證
在終端執行：
```
openspec validate "<change-name>" --strict
```
捕獲輸出結果。

### Step 3：補充檢查（CLI 無法覆蓋的部分）
1. 檢查所有 artifacts 是否完整（proposal / spec / delta-spec / tasks）
2. 檢查 tasks 是否可執行（每個 task 有明確的驗收條件）
3. 檢查 spec 與 delta-spec 是否一致
4. 檢查是否違反 `rules/36-scope-guard.md`（範圍護欄）

### Step 4：輸出驗證報告
```markdown
## 驗證報告：<change-name>

### CLI 驗證
- 結果：PASS / FAIL
- 輸出：（CLI 原始輸出）

### 補充檢查
| 項目 | 狀態 | 說明 |
|---|---|---|
| Artifacts 完整性 | ✅/❌ | ... |
| Tasks 可執行性 | ✅/❌ | ... |
| Spec 一致性 | ✅/❌ | ... |
| 範圍護欄 | ✅/❌ | ... |

### 結論：PASS / WARN / FAIL
```

若有問題，說明需要修正什麼再繼續。
通過後提示進行 `#opsx-apply`。
