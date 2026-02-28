# GitHub Copilot Workspace Guide（正體中文）v1

> **適用對象**：GitHub Copilot（VS Code Chat / Agent mode）  
> **對應 Bootstrap**：`bootstrap_copilot_workspace_v1.py`  
> **核心理念**：把「按鈕/字級/間距/色彩」從逐頁人工微調，改成「有規範、可對照、可 Freeze」；把「修了還錯/改錯檔」改成可重現→定位→修復→驗證→防回歸的閉環，並強制留下證據。

---

## 0. 名詞對照

| 概念 | 說明 |
|------|------|
| **Rule（規範）** | 限制型文件：描述「什麼可做/不可做」。放在 `.github/copilot/rules/` |
| **Skill（角色）** | 角色型文件：描述「用什麼身份產出什麼」。放在 `.github/copilot/skills/` |
| **Evidence（證據）** | 任何修改都必須留痕的文件，放在 `docs/` 下的子資料夾 |
| **Style Contract** | UI 設計基準（字體/色彩/間距/按鈕/表單），來自 `rules/10-style-guide.md` |
| **Style Freeze** | 確認 UI 基準OK後凍結，避免後續反覆修改 UI |
| **Done Gate** | 每次「宣稱完成」前必須通過的門檻（UI review / UX review / Bug 證據 / Smoke test） |
| **Scope Guard** | 範圍護欄：超過觸發條件時先停下、先記錄決策、再動手 |
| **Smallest Safe Change** | 最小安全修改：只做必要修改，避免一次改太多引入新 bug |
| **Prompt** | 一鍵觸發的工作流檔案（`.prompt.md`），等效 Antigravity 的 slash command |
| **Agent** | 自訂子代理（`.agent.md`），具有專屬工具與職責限制 |
| **Change Lifecycle** | 一個 Change 從構想到歸檔的完整生命週期，見 `rules/70-openspec-workflow.md` |
| **WOS** | Wilson Operation System，自動導航 Agent，判斷目前狀態並建議下一步 |
| **MCP** | Model Context Protocol，讓 Copilot 直接呼叫外部工具（如 GitKraken） |

---

## 1. 檔案結構

```
<project-root>/
├─ .github/
│  ├─ copilot-instructions.md          ← Copilot 永久載入的主指令（每次對話必讀）
│  ├─ agents/                          ← 自訂 Agent（子代理）
│  │  └─ WOS.agent.md                  ← Wilson Operation System（流程自動導航）
│  └─ copilot/
│     ├─ rules/                        ← 詳細規範（按需讀取）
│     │  ├─ 10-style-guide.md          ← Style Contract（字體/色彩/間距/狀態）
│     │  ├─ 20-ux-flow.md              ← UX Flow Contract（操作流程/狀態設計）
│     │  ├─ 30-debug-contract.md       ← 除錯閉環（重現→定位→修復→驗證→防回歸）
│     │  ├─ 35-quality-gate.md         ← Done Gate（完成宣告門檻）
│     │  ├─ 36-scope-guard.md          ← 範圍護欄
│     │  ├─ 50-tech-stack.md           ← 技術棧約定（套件選型/版本）
│     │  ├─ 60-testing.md              ← 測試策略（金字塔/覆蓋率）
│     │  └─ 70-openspec-workflow.md     ← Change Lifecycle（完整流程定義）
│     ├─ prompts/                      ← 一鍵觸發工作流（等效 slash command）
│     │  ├─ session-start.prompt.md    ← #session-start 開工
│     │  ├─ opsx-explore.prompt.md     ← #opsx-explore 需求探索
│     │  ├─ opsx-new.prompt.md         ← #opsx-new 建立 Change
│     │  ├─ opsx-ff.prompt.md          ← #opsx-ff 快進 artifacts
│     │  ├─ opsx-validate.prompt.md    ← #opsx-validate 驗證完整性
│     │  ├─ opsx-apply.prompt.md       ← #opsx-apply 實作
│     │  ├─ opsx-verify.prompt.md      ← #opsx-verify 驗證實作
│     │  ├─ opsx-sync.prompt.md        ← #opsx-sync 同步 specs
│     │  ├─ opsx-archive.prompt.md     ← #opsx-archive 歸檔
│     │  ├─ ui-review.prompt.md        ← #ui-review UI 審查
│     │  ├─ ux-review.prompt.md        ← #ux-review UX 審查
│     │  ├─ smoke-test.prompt.md       ← #smoke-test 冒煙測試
│     │  ├─ code-review.prompt.md      ← #code-review 程式碼審查
│     │  ├─ status.prompt.md           ← #status 狀態更新
│     │  ├─ commit-push.prompt.md      ← #commit-push 審查+提交+推送
│     │  ├─ log-decision.prompt.md     ← #log-decision 記錄決策
│     │  └─ session-close.prompt.md    ← #session-close 收尾
│     ├─ skills/                       ← 角色分工（按需讀取）
│     │  ├─ ui-designer.md             ← UI 前端設計師
│     │  ├─ ux-fullstack-engineer.md   ← UX 全端工程師
│     │  ├─ debug-sheriff.md           ← 除錯警長
│     │  ├─ smoke-tester.md            ← 冒煙測試
│     │  ├─ openspec-conductor.md      ← OpenSpec 指揮官
│     │  ├─ scribe.md                  ← 記錄官（投影片素材整理）
│     │  ├─ git-steward.md             ← 版本控管管家
│     │  └─ code-reviewer.md           ← 程式碼審查員
│     └─ _backups/                     ← bootstrap 自動備份（每次覆寫前）
├─ openspec/                           ← OpenSpec 規格專案
│  ├─ config.yaml                      ← OpenSpec 設定（專案上下文 + artifact 規則）
│  ├─ specs/                            ← 主規格文件
│  └─ changes/                          ← 進行中的 Change
│     └─ archive/                      ← 已歸檔的 Change
├─ docs/
│  ├─ roadmap.md                       ← 階段追蹤（目前在哪/下一步是什麼）
│  ├─ decision-log.md                  ← 決策留痕（表格）
│  ├─ decisions/                       ← 決策詳情（每份一個 .md）
│  ├─ runlog/                          ← 每日進度（日期_README.md）
│  ├─ uiux/                            ← UI/UX 審查輸出
│  ├─ bugs/                            ← Bug 修復記錄
│  └─ qa/                              ← Smoke 測試結果
├─ design/
│  └─ stitch/                          ← Stitch 匯出的 HTML（若有）
├─ experience/                         ← Session 總結 / 投影片素材
└─ tools/
   └─ bootstrap_copilot_workspace.py   ← 本 Bootstrap 腳本
```

---

## 2. 各檔案用途

### 2.1 `.github/copilot-instructions.md`（永久載入）
- Copilot 在 VS Code 中使用時，**每次對話都會自動載入此檔案**
- 內容包含：基本輸出規則、治理與留痕要求、品質門檻摘要、開工流程、任務觸發表
- **不應過長**（建議 <2000 字），詳細規範放在 `rules/` 和 `skills/`

### 2.2 `rules/`（規範，按需讀取）
| 檔案 | 職責 |
|------|------|
| `10-style-guide.md` | UI 設計基準：字體、色彩、間距、按鈕/表單狀態、Freeze 機制 |
| `20-ux-flow.md` | UX 流程設計：happy path + edge case、狀態設計、驗收條件 |
| `30-debug-contract.md` | 除錯閉環：重現→定位→修復→驗證→防回歸 |
| `35-quality-gate.md` | Done Gate：缺什麼證據就不能宣稱 Done |
| `36-scope-guard.md` | 範圍護欄：觸發條件觸及時先停下 |
| `50-tech-stack.md` | 技術棧約定：套件選型、版本、新增 dependency 規則 |
| `60-testing.md` | 測試策略：金字塔、覆蓋率、命名慣例、何時寫測試 |
| `70-openspec-workflow.md` | Change Lifecycle：完整流程定義、階段門檻、必須遯守規則 |

### 2.3 `prompts/`（一鍵觸發工作流）
在 Copilot Chat 中輸入 `#prompt-name` 即可觸發對應工作流，等效 Antigravity 的 slash command。

| Prompt | 功能 | 對應 Antigravity |
|--------|------|---|
| `#session-start` | 開工流程（讀規範、確認階段、初始化 runlog） | `/preflight` |
| `#opsx-explore` | 需求探索與問題釐清 | — |
| `#opsx-new` | 建立新 Change | `/opsx-new` |
| `#opsx-ff` | 快進生成所有 artifacts | `/opsx-ff` |
| `#opsx-validate` | 驗證 Change 完整性（自動呼叫 `openspec validate --strict`） | `openspec validate` |
| `#opsx-apply` | 實作 Change 中的 tasks | `/opsx-apply` |
| `#opsx-verify` | 驗證實作結果 | `/opsx-verify` |
| `#opsx-sync` | 同步 delta specs 到 main specs | `/opsx-sync` |
| `#opsx-archive` | 歸檔已完成的 Change | `/opsx-archive` |
| `#ui-review` | UI 審查 | `/ui-review` |
| `#ux-review` | UX 審查 | `/ux-review` |
| `#smoke-test` | 冒煙測試 | — |
| `#code-review` | 程式碼審查 | — |
| `#status` | 狀態更新（roadmap + runlog） | `/status` |
| `#commit-push` | 審查 + 提交 + 推送（GitKraken MCP 自動化） | `/commit-push` |
| `#log-decision` | 記錄決策 | `/log-decision` |
| `#session-close` | Session 收尾（slides outline） | `/session-close` |

### 2.4 `agents/`（自訂 Agent）
| 檔案 | 功能 | 使用方式 |
|------|------|---|
| `WOS.agent.md` | 流程自動導航：偵測目前狀態、建議下一步 | Chat 中選擇 `@WOS` |

WOS 會自動檢查：
- `docs/roadmap.md` → 目前大階段
- `openspec/changes/` → 進行中的 Change 及其 artifacts 狀態
- `docs/runlog/` → 今日是否已開工
- `git status` → 是否有未提交變更

然後輸出狀態報告 + 建議的下一步 `#prompt-name`。

### 2.5 `skills/`（角色，按需讀取）
| 檔案 | 角色 | 產出 |
|------|------|------|
| `ui-designer.md` | UI 前端設計師 | `docs/uiux/<date>_ui-review.md` |
| `ux-fullstack-engineer.md` | UX 全端工程師 | `docs/uiux/<date>_ux-review.md` |
| `debug-sheriff.md` | 除錯警長 | `docs/bugs/<date>_<slug>.md` |
| `smoke-tester.md` | 冒煙測試 | `docs/qa/<date>_smoke.md` |
| `openspec-conductor.md` | OpenSpec 指掮官 | roadmap + runlog（對接內建 OpenSpec skills） |
| `scribe.md` | 記錄官 | `experience/<YYYY-MM>/slides_<date>.md` |
| `git-steward.md` | 版本控管管家 | commit message（繁中） |
| `code-reviewer.md` | 程式碼審查員 | review 記錄（必修/建議/良好） |

### 2.6 `docs/`（證據結構）
- **roadmap.md**：當前階段、下一步、阻塞因素
- **decision-log.md**：結構化表格（日期/決策/原因/影響/證據）
- **decisions/**：重大決策詳情（特別是 Style Freeze、規範變更）
- **runlog/**：每日進度記錄
- **uiux/**：UI/UX 審查輸出
- **bugs/**：Bug 修復記錄（重現/定位/修復/驗證/防回歸）
- **qa/**：Smoke 測試清單與結果

---

## 3. 如何使用（工作流程）

### 3.1 初次建置
```bash
cd <project-root>

# 複製 bootstrap script 到 tools/
mkdir -p tools
cp <path-to>/bootstrap_copilot_workspace_v1.py tools/bootstrap_copilot_workspace.py

# 執行 bootstrap（預設 overwrite，會自動備份）
python tools/bootstrap_copilot_workspace.py

# （可選）匯入 Stitch HTML 以凍結 Style Guide
python tools/bootstrap_copilot_workspace.py --stitch-html design/stitch/stitch.html
```

### 3.2 健檢
```bash
python tools/bootstrap_copilot_workspace.py --verify-only
```

### 3.3 每次開新任務時（Session Start）
在 Copilot Chat 輸入：
```
#session-start
```
或呼叫 `@WOS` 自動判斷目前狀態。

Copilot 會：
1. 讀取 `rules/` 下所有規範
2. 確認目前階段（`docs/roadmap.md`）
3. 初始化當日 runlog
4. 檢查進行中的 Change
5. 回報啟用證據

### 3.4 Change Lifecycle（完整流程）
一個 Change 從構想到歸檔的建議順序：

```
#session-start → #opsx-explore（可選）
  → #opsx-new → #opsx-ff → #opsx-validate
  → #opsx-apply → #opsx-verify
  → #ui-review（涉及 UI）→ #ux-review（涉及 UX）→ #smoke-test（涉及 bug）
  → #code-review → #commit-push → #status
  → #opsx-sync → #opsx-archive → #log-decision
  → #session-close
```

簡化流程（小型修改）：
```
#opsx-new → #opsx-ff → #opsx-apply → #opsx-verify → #smoke-test → #commit-push → #opsx-archive
```

> 詳細規則見 `rules/70-openspec-workflow.md`

### 3.5 做 UI 審查
```
#ui-review
```
會自動讀取 `rules/10-style-guide.md` 並以 `ui-designer` 角色執行，產出 `docs/uiux/<date>_ui-review.md`。

### 3.6 做 UX 審查
```
#ux-review
```
會自動讀取 `rules/20-ux-flow.md` 並以 `ux-fullstack-engineer` 角色執行。

### 3.7 修 Bug
> 請以 `debug-sheriff` 的角色，讀取 `rules/30-debug-contract.md`，修復以下 bug：[描述]

### 3.8 提交推送（GitKraken MCP 自動化）
```
#commit-push
```
會先執行 Code Review，確認後透過 GitKraken MCP 自動化執行 `git add` → `commit` → `push`。
MCP 不可用時自動 fallback 到終端指令。

### 3.9 Session 結束時
```
#session-close
```
會以 `scribe` 角色整理本次成果到 `experience/`。

---

## 4. 啟用驗證方式

Copilot 每次回覆時，應在回覆末尾包含啟用證據：

```
---
### ✅ 啟用證據
- 已讀規範：10-style-guide, 30-debug-contract
- 使用角色：debug-sheriff, smoke-tester
- 證據位置：docs/bugs/2025-01-15_login-crash.md, docs/qa/2025-01-15_smoke.md
```

如果 Copilot 沒有提供啟用證據，表示規範未被正確讀取。請明確要求：
> 請先讀取 `.github/copilot-instructions.md`，然後重新回覆。

---

## 5. 與 Antigravity 的對照

| 概念 | Antigravity | GitHub Copilot |
|------|-----------|---------------|
| 主進入點 | `.agent/AGENTS.md` | `.github/copilot-instructions.md` |
| 規範 | `.agent/rules/*.md`（有 frontmatter） | `.github/copilot/rules/*.md`（純 Markdown） |
| 角色 | `.agent/skills/*.md`（有 frontmatter） | `.github/copilot/skills/*.md`（純 Markdown） |
| Slash Command | `.agent/workflows/*.md` | `.github/copilot/prompts/*.prompt.md`（`#` 觸發） |
| 流程導航 | 手動呼叫 | `@WOS` Agent（自動偵測 lifecycle 狀態） |
| Git 操作 | 終端指令 | GitKraken MCP 自動化（fallback 終端） |
| OpenSpec Validate | 終端執行 | `#opsx-validate` 自動呼叫 CLI |
| 證據 | `docs/` | `docs/`（相同） |
| 健檢 | `bootstrap --verify-only` | `bootstrap --verify-only`（相同） |

### Slash Command 對照表
| Antigravity | Copilot | 說明 |
|---|---|---|
| `/preflight` | `#session-start` | 開工流程 |
| `/opsx-new` | `#opsx-new` | 建立新 Change |
| `/opsx-ff` | `#opsx-ff` | 快進 artifacts |
| `openspec validate --strict` | `#opsx-validate` | 驗證 Change |
| `/opsx-apply` | `#opsx-apply` | 實作 tasks |
| `/opsx-verify` | `#opsx-verify` | 驗證實作 |
| `/ui-review` | `#ui-review` | UI 審查 |
| `/ux-review` | `#ux-review` | UX 審查 |
| `/status` | `#status` | 狀態更新 |
| `/commit-push` | `#commit-push` | 審查+提交+推送 |
| `/opsx-sync` | `#opsx-sync` | 同步 specs |
| `/opsx-archive` | `#opsx-archive` | 歸檔 Change |
| `/log-decision` | `#log-decision` | 記錄決策 |
| `/session-close` | `#session-close` | Session 收尾 |
| — | `#opsx-explore` | 需求探索（新增） |
| — | `#smoke-test` | 冒煙測試（新增） |
| — | `#code-review` | 程式碼審查（新增） |

### 主要差異說明
1. **Prompt Files 取代 slash command**：在 Chat 輸入 `#prompt-name` 即可觸發，體驗與 Antigravity 相同
2. **WOS Agent 自動導航**：呼叫 `@WOS` 即可自動判斷目前 lifecycle 狀態並建議下一步
3. **GitKraken MCP**：`#commit-push` 透過 MCP 直接呼叫 git 操作，不需切到終端
4. **永久載入**：Copilot 會自動載入 `copilot-instructions.md`，不需要手動切換

---

## 6. CLI 參數一覽

| 參數 | 說明 | 預設值 |
|------|------|-------|
| `--root` | repo 根目錄 | 自動偵測（`tools/` → 上一層） |
| `--stitch-html` | Stitch HTML 檔案路徑 | — |
| `--mode` | `overwrite` / `safe` | `overwrite` |
| `--no-backup` | 不備份（不建議） | `false` |
| `--verify-only` | 只做健檢（不寫檔） | `false` |
| `--project-name` | 專案名稱（用於 `openspec/config.yaml`） | repo 資料夾名稱 |

---

## 7. 建議的專案建置順序

1. **S0**：用 Stitch 建立 UI 基準 HTML（可選；行動 App 可用 Figma 替代）
2. **S1**：跑 Bootstrap 建置 workspace 結構
3. **S1.5**：安裝 OpenSpec 並初始化規格專案
4. **S2**：UI/UX 盤點 + Style Freeze
5. **S3**：用 OpenSpec 寫規格、拆 tasks
6. **S4**：Implement（最小安全修改 + 留痕）
7. **S5**：Bugfix 收斂 + Smoke 驗證
8. **S6**：整理素材（投影片/分享）

### S1.5 OpenSpec 安裝與初始化

```bash
# 1) 安裝 OpenSpec（全域）
npm install -g @anthropic/openspec-conductor
# 或使用 npx 免安裝：npx @anthropic/openspec-conductor init

# 2) 在專案根目錄初始化
cd <project-root>
openspec init

# 3) 產出的目錄結構
# openspec/
#   ├─ config.yaml    ← 設定檔（專案上下文 + artifact 規則）
#   ├─ specs/         ← 主規格文件
#   └─ changes/       ← 進行中的 Change
#       └─ archive/   ← 已歸檔的 Change

# 4) 常用指令（透過 Prompt 觸發）
# #opsx-new          ← 建立新 Change
# #opsx-ff           ← 快進生成 artifacts
# #opsx-validate     ← 驗證（自動呼叫 openspec validate --strict）
# #opsx-apply        ← 實作 tasks
# #opsx-verify       ← 驗證實作
# #opsx-sync         ← 同步 specs
# #opsx-archive      ← 歸檔 Change
```

> **注意**：OpenSpec 的安裝指令可能因版本而異，請以官方文件為準。  
> 安裝後建議在 `docs/roadmap.md` 記錄 OpenSpec 版本號。
> `openspec/config.yaml` 已預填專案上下文與 artifact 規則。

---

## 8. MCP 整合（Model Context Protocol）

本專案透過 MCP 讓 Copilot 直接操作外部工具，減少手動切換終端的需要。

### 8.1 GitKraken MCP（Git 自動化）
`#commit-push` prompt 會優先使用 GitKraken MCP 工具：

| MCP 工具 | 用途 | 對應 git 指令 |
|---|---|---|
| `mcp_gitkraken_git_status` | 查看工作區狀態 | `git status` |
| `mcp_gitkraken_git_log_or_diff` | 查看 diff | `git diff` |
| `mcp_gitkraken_git_add_or_commit` | Stage + Commit | `git add` + `git commit` |
| `mcp_gitkraken_git_push` | 推送 | `git push` |
| `mcp_gitkraken_git_branch` | 分支操作 | `git branch` / `git checkout -b` |
| `mcp_gitkraken_git_blame` | 查看行歷史 | `git blame` |

若 MCP 不可用，會自動 fallback 到終端指令。

### 8.2 OpenSpec CLI（透過終端自動呼叫）
`#opsx-validate` prompt 會在終端自動執行：
```bash
openspec validate "<change-name>" --strict
```
目前 OpenSpec 尚未提供 MCP server，因此透過終端呼叫 CLI。若未來提供 MCP，可直接替換。

---

## 9. 共用到其他專案

本 workspace 結構設計為**專案無關（project-agnostic）**，可用於任何專案：
1. 將 `bootstrap_copilot_workspace_v1.py` + 本 Guide 複製到新專案的根目錄或 `tools/`
2. 執行 `python bootstrap_copilot_workspace_v1.py --root <new-project-root> --project-name <name>`
3. （可選）用 `--stitch-html` 匯入該專案的 Stitch HTML

生成的所有規範和角色內容都是泛用的（不綁定特定專案名稱或技術棧），可直接使用或依需求調整。
