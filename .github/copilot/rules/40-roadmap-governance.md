# 40-roadmap-governance（Roadmap 治理與階段管理）

> 目的：確保 roadmap 即時反映專案狀態，階段轉換有據可查，上線決策有明確依據。

## Roadmap 結構（必要區段）
`docs/roadmap.md` 必須包含：
1. **專案範疇**（Scope + Non-goals）
2. **里程碑**（Milestones）— 每個里程碑有驗收標準 checklist
3. **開發階段**（Stages）— 對應到里程碑
4. **目前狀態**（Current / Next / Blockers）
5. **階段轉換記錄**

## 何時必須更新 Roadmap

| 觸發事件 | 更新內容 |
|---------|---------|
| 階段完成（S? → S?+1） | 更新 §4 目前狀態 + §5 轉換記錄 |
| 里程碑驗收通過 | 勾選 §2 對應 checklist |
| 範疇變更（新增/移除功能） | 更新 §1 Scope 或 Non-goals + 記錄決策 |
| 發現阻塞 | 更新 §4 Blockers |
| `#status` prompt 執行時 | 至少更新 §4 |
| `#opsx-archive` 時 | 檢查是否觸發里程碑完成 |

## 階段轉換條件

階段轉換**不可跳級**（除非在 decision-log 中記錄特殊原因）。

### 轉換到下一階段的門檻
| 轉換 | 條件 |
|------|------|
| → S2 | S1 workspace 健檢通過（`--verify-only`） |
| → S3 | Style Freeze 完成（`docs/uiux/` 有 ui-review 且標記 FROZEN） |
| → S4 | OpenSpec Change 的 spec + tasks 已建立且 validate 通過 |
| → S5 | 所有 tasks 完成 + verify 通過 |
| → S6 | Smoke test 全數通過 + 無 P0/P1 未修 bug |

### 里程碑上線門檻
一個里程碑可以「上線」（release）的條件：
1. 該里程碑的**所有驗收標準**（checkbox）全部勾選
2. **Smoke test 通過**（`docs/qa/` 有對應記錄）
3. **無 P0 bug**（`docs/bugs/` 中無未關閉的 P0）
4. **決策已記錄**（`docs/decision-log.md` 含上線決策）

## `#status` 更新範本

執行 `#status` 時，必須輸出以下格式並同步更新 `docs/roadmap.md` §4：

```markdown
## 📊 狀態更新 — {日期}

### Roadmap
- 階段：{S?} {名稱}
- 里程碑：{M?} {名稱}
- 進度：{完成項/總項} 驗收標準已滿足

### 里程碑驗收進度
- M1 資料就緒：{?}/7 ✅
- M2 核心可用：{?}/10 ✅
- M3 練習完整：{?}/9 ✅
- M4 品質收斂：{?}/7 ✅

### 下一步
- {具體行動} — `#prompt-name`

### 風險/阻塞
- {列出或「無」}
```

## 決策記錄觸發
以下情況**必須**同步記錄到 `docs/decision-log.md`：
- 里程碑驗收標準變更
- 階段跳級
- 功能移入/移出 Scope
- 上線時程變更
