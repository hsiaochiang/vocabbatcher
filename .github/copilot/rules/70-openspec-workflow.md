# 70-openspec-workflow（Change Lifecycle 完整流程）

> 定義一個 Change 從構想到歸檔的完整生命週期，確保每個步驟都不遺漏。

## Change Lifecycle（建議順序）

```
Session Start → Explore（可選）→ New → FF → Validate
    → Apply → Verify → UI Review → UX Review → Smoke Test
    → Code Review → Commit-Push → Status
    → Sync → Archive → Log Decision → Session Close
```

## 各階段說明

### Phase 1：規劃
| 步驟 | 觸發 | 內建 Skill | 專案 Skill | 產出 |
|---|---|---|---|---|
| Session Start | `#session-start` | — | — | runlog 初始化 |
| Explore | `#opsx-explore` | `openspec-explore` | — | 需求釐清筆記 |
| New Change | `#opsx-new` | `openspec-new-change` | `openspec-conductor.md` | change 目錄 + proposal |
| Fast-Forward | `#opsx-ff` | `openspec-ff-change` | — | 所有 artifacts |
| Validate | `#opsx-validate` | — | — | 驗證報告 |

### Phase 2：實作
| 步驟 | 觸發 | 內建 Skill | 專案 Skill | 產出 |
|---|---|---|---|---|
| Apply | `#opsx-apply` | `openspec-apply-change` | — | 程式碼變更 |
| Verify | `#opsx-verify` | `openspec-verify-change` | — | 驗證結果 |

### Phase 3：品質閘
| 步驟 | 觸發 | 專案 Skill | 產出 |
|---|---|---|---|
| UI Review | `#ui-review` | `ui-designer.md` | `docs/uiux/<date>_ui-review.md` |
| UX Review | `#ux-review` | `ux-fullstack-engineer.md` | `docs/uiux/<date>_ux-review.md` |
| Smoke Test | `#smoke-test` | `smoke-tester.md` | `docs/qa/<date>_smoke.md` |
| Code Review | `#code-review` | `code-reviewer.md` | review 記錄 |

### Phase 4：提交與歸檔
| 步驟 | 觸發 | 專案 Skill | 產出 |
|---|---|---|---|
| Commit-Push | `#commit-push` | `git-steward.md` + `code-reviewer.md` | commit + push |
| Status | `#status` | — | roadmap + runlog 更新 |
| Sync Specs | `#opsx-sync` | — | main specs 同步 |
| Archive | `#opsx-archive` | — | change 歸檔 |
| Log Decision | `#log-decision` | — | `docs/decision-log.md` + `docs/decisions/` |
| Session Close | `#session-close` | `scribe.md` | `experience/` slides outline |

## 簡化流程（小型修改）

若 Change 很小（如 bugfix、微調 UI），可省略部分步驟：

```
New → FF → Apply → Verify → Smoke Test → Commit-Push → Archive
```

## 必須遵守
- Apply 前必須有 Validate 通過
- Commit-Push 前必須有 Code Review
- Archive 前必須有 Verify 通過
- 涉及 UI 修改 → 必須 UI Review（Done Gate）
- 涉及 UX 流程 → 必須 UX Review（Done Gate）
- 涉及 Bug 修復 → 必須 Smoke Test（Done Gate）
