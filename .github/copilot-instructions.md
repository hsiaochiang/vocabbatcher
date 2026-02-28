# GitHub Copilot 工作規範（自動載入）

> 本檔案在每次 Copilot 對話時自動載入。詳細規範請參閱 `.github/copilot/rules/` 與 `.github/copilot/skills/`。

## 基本輸出規則（強制）
- 回覆與說明：**一律使用正體中文**
- 可上網查適合的工具或套件（請附來源連結）
- 對使用者提供的文件：以中文為主；若必須用英文，請在備註區用中文說明

## 治理與留痕（強制）
- 討論結論必須寫入文件（`docs/roadmap.md` / `docs/decision-log.md` / `docs/runlog/` / `docs/uiux/` / `docs/bugs/` / `docs/qa/`）
- 維持 `docs/roadmap.md` 最新（回答「目前在哪個階段」）
- 每次 Implement 後：add/commit/push，commit log 使用**繁體中文**（含 What / Why / Impact / Evidence）

## Smallest Safe Change（最小安全修改）
- 僅做必要修改；可共用的要共用化
- 沒有證據不得宣稱「已修好」或「已符合」

## 品質門檻（Done Gate）
- UI 修改 → 必須更新 `docs/uiux/<date>_ui-review.md`
- UX 流程修改 → 必須更新 `docs/uiux/<date>_ux-review.md`
- Bug 修復 → 必須產出 `docs/bugs/<date>_<slug>.md` + `docs/qa/<date>_smoke.md`
- 未通過門檻不得宣稱 Done

## 範圍護欄
- 一次改動超過 5 個檔案 → 先記錄決策（`docs/decisions/`）
- 需要改動 Style Contract → 先記錄決策
- 同一問題第 3 次未收斂 → 換策略

## 流程導航（WOS Agent）
- 呼叫 `@WOS` 可自動偵測目前狀態並建議下一步
- WOS 會檢查：roadmap 階段、Change 狀態、git 狀態、今日 runlog
- 不確定該執行什麼時，優先呼叫 `@WOS`

## 開工流程（每次新任務）
1. 呼叫 `@WOS` 或執行 `#session-start`
2. 閱讀 `.github/copilot/rules/` 下所有規範
3. 確認目前階段（`docs/roadmap.md`）
4. 初始化當日 runlog（`docs/runlog/<date>_README.md`）
5. 檢查 Style Guide 狀態（PENDING/FROZEN）
6. 回報啟用證據：已讀規範清單、本次使用的角色、產出的證據位置

## 任務觸發（依任務類型讀取對應文件）
| 任務 | Prompt 觸發 | 必讀規範 | 使用角色 | 產出 |
|------|------------|---------|---------|------|
| 開工 | `#session-start` | 全部 rules | — | runlog 初始化 |
| UI 調整 | `#ui-review` | `rules/10-style-guide.md` | `skills/ui-designer.md` | `docs/uiux/<date>_ui-review.md` |
| UX 流程 | `#ux-review` | `rules/20-ux-flow.md` | `skills/ux-fullstack-engineer.md` | `docs/uiux/<date>_ux-review.md` |
| 修 Bug | — | `rules/30-debug-contract.md` | `skills/debug-sheriff.md` + `skills/smoke-tester.md` | `docs/bugs/` + `docs/qa/` |
| 新功能實作 | `#opsx-new` → `#opsx-ff` → `#opsx-apply` | `rules/50-tech-stack.md` + `rules/70-openspec-workflow.md` | `skills/openspec-conductor.md` | spec + runlog + smoke |
| 驗證 | `#opsx-verify` | `rules/35-quality-gate.md` | — | 驗證報告 |
| Code Review | `#code-review` | `rules/50-tech-stack.md` + `rules/60-testing.md` | `skills/code-reviewer.md` | review 記錄 |
| 冒煙測試 | `#smoke-test` | — | `skills/smoke-tester.md` | `docs/qa/<date>_smoke.md` |
| 提交推送 | `#commit-push` | — | `skills/git-steward.md` + `skills/code-reviewer.md` | commit + push |
| 狀態更新 | `#status` | — | — | roadmap + runlog 更新 |
| 記錄決策 | `#log-decision` | — | — | `docs/decision-log.md` + `docs/decisions/` |
| 歸檔 | `#opsx-archive` | — | — | change 歸檔 |
| Session 結束 | `#session-close` | — | `skills/scribe.md` | `experience/<YYYY-MM>/slides_<date>.md` |

## 證據結構
```
docs/
├─ roadmap.md              # 階段追蹤
├─ decision-log.md         # 決策留痕
├─ decisions/<date>_*.md   # 決策詳情
├─ runlog/<date>_*.md      # 每日進度
├─ uiux/<date>_*.md        # UI/UX 審查
├─ bugs/<date>_*.md        # Bug 修復
└─ qa/<date>_*.md          # Smoke 測試
```

## 啟用證據（每次回覆強制包含）
- 已讀入的規範清單
- 本次使用的角色
- 產出的證據位置（文件路徑）
