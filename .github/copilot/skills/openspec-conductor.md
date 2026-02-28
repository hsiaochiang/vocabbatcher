# Skill: openspec-conductor（OpenSpec 指揮官）

## 任務目標
用 OpenSpec 把需求→規格→任務→實作走完；每一步都可驗收、可留證據。

## 依據
- OpenSpec 專案內 `specs/` 與 `tasks/`（依版本）
- `docs/roadmap.md`（目前階段）
- `docs/runlog/<date>_README.md`（當日進度）

## 安裝與初始化
```bash
# 全域安裝
# npm install -g <openspec-package>
# 或使用 npx 免安裝：npx <openspec-package> init

# 在專案根目錄初始化
cd <project-root>
openspec init
```
> 安裝指令依版本而異，請以官方文件為準。

## 工作流程（對應 Prompt 觸發）

完整 Change Lifecycle 請參閱 `rules/70-openspec-workflow.md`

| 階段 | Prompt | 內建 Skill |
|---|---|---|
| 需求探索 | `#opsx-explore` | `openspec-explore` |
| 建立 Change | `#opsx-new` | `openspec-new-change` |
| 快進 Artifacts | `#opsx-ff` | `openspec-ff-change` |
| 驗證完整性 | `#opsx-validate` | — |
| 實作 | `#opsx-apply` | `openspec-apply-change` |
| 驗證實作 | `#opsx-verify` | `openspec-verify-change` |
| 同步 Specs | `#opsx-sync` | `openspec-sync-specs` |
| 歸檔 | `#opsx-archive` | `openspec-archive-change` |

## Artifact 對應
| OpenSpec 產出 | 對應證據位置 |
|---|---|
| `specs/*.md` | docs/roadmap.md（階段更新） |
| `tasks/*.md` | docs/runlog/（每日進度） |
| 規格變更 | docs/decisions/（決策留痕） |
| 實作完成 | docs/qa/（smoke test） |

## 版本管理
- Spec 版本命名建議：`v1.0`、`v1.1`、`v2.0`（重大變更升主版號）
- 每次 spec 變更必須記錄決策（docs/decisions/）
- 在 `docs/roadmap.md` 記錄當前使用的 OpenSpec 版本號

## 輸出（必交付）
- 下一步該做什麼（包含要下的指令/動作）
- 規格缺口清單（缺一不可的驗收點）
- evidence 應落檔的位置（runlog / decision / bugs / qa）
