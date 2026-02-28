# Change Lifecycle 指令手冊

> 本文件為 VocabBatcher 專案的 OpenSpec 工作流程指令參考。
> 涵蓋從建立 Change 到歸檔的完整生命週期。

---

## 快速入口

| 情境 | 指令 |
|------|------|
| 不確定該做什麼 | `@WOS` |
| 開始新 Session | `#session-start` |
| 新功能 / 修改 | `/opsx:new "change-name"` |
| 快速起步 | `/opsx:new` → `/opsx:ff` → `/opsx:apply` |
| 探索想法 | `/opsx:explore` |
| 繼續未完成工作 | `/opsx:continue "change-name"` |

---

## Phase 0：啟動 Session

| # | 指令 | 用途 |
|---|------|------|
| 0 | `@WOS` | 自動偵測目前狀態，建議下一步（任何時候不確定就呼叫它） |
| 0 | `#session-start` | 初始化當日 runlog、確認 roadmap 階段 |

---

## Phase 1：規劃（Spec → Artifacts）

| # | 指令 | 用途 | 產出 |
|---|------|------|------|
| 1 | `/opsx:explore` | 思考模式——探索想法、釐清需求（不寫程式） | 需求筆記 |
| 2 | `/opsx:new "change-name"` | 建立新 Change，產出第一個 artifact（proposal） | `openspec/changes/<name>/proposal.md` |
| 3 | `/opsx:continue "change-name"` | 逐步產出下一個 artifact（design → specs → tasks） | 依序產出每個 artifact |
| 3' | `/opsx:ff "change-name"` | 一次快轉產出所有剩餘 artifacts（替代多次 continue） | proposal + design + specs + tasks |
| 4 | `openspec validate "change-name" --type change --json` | 驗證 artifacts 完整性與格式 | PASS / FAIL |

---

## Phase 2：實作（Code）

| # | 指令 | 用途 | 產出 |
|---|------|------|------|
| 5 | `/opsx:apply "change-name"` | 依 tasks.md 逐一實作所有程式碼 + 測試 | 原始碼 + 測試 |
| 6 | `/opsx:verify "change-name"` | 三維驗證（完整性 / 正確性 / 一致性） | 驗證報告 |

---

## Phase 3：品質閘（Quality Gate）

| # | 指令 | 用途 | 產出 | 何時需要 |
|---|------|------|------|----------|
| 7 | `#smoke-test` | 冒煙測試 | `docs/qa/<date>_smoke.md` | Bug 修復、功能上線 |
| 8 | `#ui-review` | UI 視覺審查 | `docs/uiux/<date>_ui-review.md` | 涉及 UI 修改時 |
| 9 | `#ux-review` | UX 流程審查 | `docs/uiux/<date>_ux-review.md` | 涉及 UX 流程時 |
| 10 | `#code-review` | 程式碼審查 | review 記錄 | commit 前必做 |

---

## Phase 4：提交與歸檔

| # | 指令 | 用途 | 產出 |
|---|------|------|------|
| 11 | `#commit-push` | Code review → git commit → push（commit log 用繁中） | git commit + push |
| 12 | `#status` | 更新 roadmap 階段與 runlog 進度 | `docs/roadmap.md` + `docs/runlog/` |
| 13 | `/opsx:sync "change-name"` | 將 delta specs 同步回 main specs | `openspec/specs/` 更新 |
| 14 | `/opsx:archive "change-name"` | 歸檔完成的 Change | 移至 `openspec/changes/archive/` |
| 15 | `#log-decision` | 記錄本次重要決策 | `docs/decision-log.md` + `docs/decisions/` |
| 16 | `#session-close` | Session 結束，產出收尾摘要 | `experience/<YYYY-MM>/slides_<date>.md` |

---

## 常用路徑

### 簡化路徑（小型修改 / Bugfix）

```
/opsx:new → /opsx:ff → /opsx:apply → /opsx:verify → #smoke-test → #commit-push → /opsx:archive
```

### 完整路徑（功能開發）

```
@WOS → #session-start → /opsx:explore → /opsx:new → /opsx:ff
  → openspec validate → /opsx:apply → /opsx:verify
  → #smoke-test → #ui-review → #ux-review → #code-review
  → #commit-push → #status → /opsx:sync → /opsx:archive
  → #log-decision → #session-close
```

---

## OpenSpec CLI 輔助指令

| 指令 | 用途 |
|------|------|
| `openspec list --json` | 列出所有 active changes |
| `openspec status --change "name" --json` | 查看特定 change 的 artifact 狀態 |
| `openspec validate "name" --type change --json` | 驗證 change artifacts 完整性 |
| `openspec instructions apply --change "name" --json` | 查看實作任務清單與進度 |

---

## 強制規則

| 規則 | 條件 |
|------|------|
| `/opsx:apply` 前 | 必須 `openspec validate` 通過 |
| `#commit-push` 前 | 必須 `#code-review` |
| `/opsx:archive` 前 | 必須 `/opsx:verify` 通過 |
| UI 修改 | 必須 `#ui-review` |
| UX 流程修改 | 必須 `#ux-review` |
| Bug 修復 | 必須 `#smoke-test` |

---

## 治理規範速查

| 規範檔 | 編號 | 涵蓋範圍 |
|--------|------|----------|
| `10-style-guide.md` | 10 | UI 風格合約（字型、色彩、間距） |
| `20-ux-flow.md` | 20 | UX 流程合約（導航、狀態處理） |
| `30-debug-contract.md` | 30 | Debug 合約（重現→診斷→修復→驗證） |
| `35-quality-gate.md` | 35 | Done Gate 品質門檻 |
| `36-scope-guard.md` | 36 | 範圍護欄（≥5 檔案需決策記錄） |
| `40-roadmap-governance.md` | 40 | 里程碑與階段治理 |
| `50-tech-stack.md` | 50 | 技術堆疊合約 |
| `60-testing.md` | 60 | 測試策略（核心邏輯 ≥70%） |
| `70-openspec-workflow.md` | 70 | Change Lifecycle 完整流程 |

> 規範路徑：`.github/copilot/rules/<file>`

---

## 證據結構

```
docs/
├─ roadmap.md              # 階段追蹤
├─ decision-log.md         # 決策留痕
├─ workflow-guide.md       # 本文件
├─ decisions/<date>_*.md   # 決策詳情
├─ runlog/<date>_*.md      # 每日進度
├─ uiux/<date>_*.md        # UI/UX 審查
├─ bugs/<date>_*.md        # Bug 修復
└─ qa/<date>_*.md          # Smoke 測試
```
