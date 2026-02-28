# Antigravity Vibe Coding Workspace 說明檔（UI/UX + Debug + OpenSpec）v5

> 目的：把你在 Vibe Coding 最耗時的兩件事（UI 一致性反覆調整、除錯反覆修錯檔/修了還錯）  
> 變成「可重複套用」的專案起始骨架：**rules（規範）+ workflows（流程）+ skills（角色分工）+ evidence（證據文件）**。

---

## 0. 這份文件包含什麼
1) 從無到有的建議流程（為什麼要先 Stitch，再產 Style Guide）  
2) bootstrap 生成的 repo 結構（檔案樹）  
3) 每個檔案的用途 / 使用情境 / 你要下的指令  
4) 如何確保 skills / workflows 真的有被正常啟用（可驗證方法）  
5) 最常用指令清單（Antigravity + OpenSpec）  
6) 專案起始執行事項（你尚未執行但建議先做）

---

## 1. 參考依據（資料來源）
- Antigravity Rules & Workflows 官方說明：https://antigravity.google/docs/rules-workflows
- OpenSpec（Spec-Driven Development 工具）：https://github.com/Fission-AI/OpenSpec
- Stitch（UI 溝通與匯出 HTML 的設計工具）：（依你實際使用版本/來源為準）

---

## 2. Repo 檔案樹（bootstrap 後的建議結構）

```
.
├─ tools/
│  └─ bootstrap_antigravity_workspace_v7.py
├─ .agent/
│  ├─ AGENTS.md
│  ├─ rules/
│  │  ├─ 00-instructions.zh-TW.md
│  │  ├─ 01-session-template.zh-TW.md
│  │  ├─ 10-style-guide.md
│  │  ├─ 20-ux-flow.md
│  │  ├─ 30-debug-contract.md
│  │  ├─ 35-quality-gate.md
│  │  ├─ 36-scope-guard.md
│  │  └─ 40-activation-proof.md
│  ├─ workflows/
│  │  ├─ preflight.md
│  │  ├─ ui-review.md
│  │  ├─ ux-review.md
│  │  ├─ bugfix.md
│  │  ├─ stitch-import.md
│  │  ├─ commit-push.md
│  │  ├─ log-decision.md
│  │  ├─ status.md
│  │  └─ session-close.md
│  ├─ skills/
│  │  ├─ ui-designer/SKILL.md
│  │  ├─ ux-fullstack-engineer/SKILL.md
│  │  ├─ debug-sheriff/SKILL.md
│  │  ├─ smoke-tester/SKILL.md
│  │  ├─ openspec-conductor/SKILL.md
│  │  ├─ scribe/SKILL.md
│  │  └─ git-steward/SKILL.md
│  └─ _bootstrap_backups/
│     └─ <timestamp>/
├─ design/
│  └─ stitch/
│     └─ stitch.html
├─ docs/
│  ├─ roadmap.md
│  ├─ decision-log.md
│  ├─ decisions/
│  │  └─ <date>_<slug>.md
│  ├─ runlog/
│  │  └─ <date>_README.md
│  ├─ uiux/
│  │  ├─ README.md
│  │  ├─ <date>_ui-review.md
│  │  └─ <date>_ux-review.md
│  ├─ bugs/
│  │  ├─ README.md
│  │  └─ <date>_<slug>.md
│  └─ qa/
│     ├─ README.md
│     └─ <date>_smoke.md
├─ experience/
│  └─ <YYYY-MM>/
│     └─ slides_<date>_talk-outline.md
├─ AGENTS.md
└─ instructions.md
```

---

## 3. 每個檔案的說明（用途 / 使用情境 / 指令）

### 3.1 Root：跨工具的「最短入口」
#### `AGENTS.md`
- **用途**：根目錄導引 stub（避免 OpenSpec/其他工具覆寫時影響 Antigravity 入口）
- **使用情境**：任何人打開 repo 根目錄先看到這個
- **你要做什麼**：不用手改；真正入口在 `.agent/AGENTS.md`

#### `instructions.md`
- **用途**：最小入口（導引到 `.agent/AGENTS.md`）
- **使用情境**：其他工具只會找根目錄 instructions 時
- **你要做什麼**：不用手改

---

### 3.2 `.agent/rules/`：你的「規格基準點」放這裡（Antigravity 會讀）
> rules 的重點：**不是「執行」它，而是 workflows/skills 在執行時必須遵守它**。

#### `00-instructions.zh-TW.md`
- **用途**：語言規範、可上網查、文件留痕、每次 implement 後要 commit/push（繁中 commit log）
- **使用情境**：每次開工、每次回報
- **關鍵指令**：搭配 `/preflight`、`/commit-push`

#### `01-session-template.zh-TW.md`
- **用途**：每次開工必貼模板，避免「以為有啟用但其實沒讀」
- **使用情境**：新 session / 新任務開始
- **關鍵指令**：照模板依序跑 `/preflight` → `/status`

#### `10-style-guide.md`
- **用途**：Style Contract（字體/顏色/間距/按鈕/狀態）+ Freeze 規則（避免 UI 返工）
- **使用情境**：任何 UI 調整前、任何「看起來不像同一套系統」的問題
- **你要怎麼用（重點）**：
  1) 先有 Stitch HTML（`design/stitch/stitch.html`）
  2) 再用 `/stitch-import` 或重新跑 bootstrap 生成可用 tokens
  3) 用 `/ui-review` 盤點差異並產出修正清單
  4) UI 確認後用 `/log-decision` 記錄「Style Freeze」
- **關鍵指令**：`/stitch-import`、`/ui-review`、`/log-decision`

> 你之前問：「要下什麼指令才能執行 10-style-guide？」  
> 答案是：它本身不執行；你要用 `/ui-review` 讓 ui-designer skill 依它進行審查與輸出差異清單。

#### `20-ux-flow.md`
- **用途**：UX Flow Contract（流程/狀態/DoD），避免「功能做了但流程缺一段」
- **使用情境**：要開始寫功能前、或 UI/流程常被打回
- **關鍵指令**：`/ux-review`

#### `30-debug-contract.md`
- **用途**：除錯閉環（重現→定位→修復→驗證→防回歸）
- **使用情境**：任何 bug、或按一下就錯
- **關鍵指令**：`/bugfix`

#### `35-quality-gate.md`
- **用途**：Done Gate（沒有 evidence/驗收/Smoke 就不能說 Done）
- **使用情境**：你最常遇到的「說完成但一按就錯」
- **關鍵指令**：`/bugfix`（必產出 `docs/qa/<date>_smoke.md`）

#### `36-scope-guard.md`
- **用途**：範圍護欄（一次改太多就先 /log-decision 拆解）
- **使用情境**：同一問題改到第 3 輪仍未收斂、或一次要改超多檔
- **關鍵指令**：`/log-decision`、`/status`

#### `40-activation-proof.md`
- **用途**：每次回覆都要列出「啟用證據」（避免空口回報）
- **使用情境**：任何回報/交付
- **關鍵指令**：`/status`（應包含啟用證據）

---

### 3.3 `.agent/skills/`：七個核心 skill（角色分工）
> skills 的重點：把「輸出格式」固定，讓你可以直接交付給 coding agent 實作，而不是只有口頭建議。

#### `ui-designer/SKILL.md`（UI 前端設計師）
- **用途**：對照 Style Guide + Stitch evidence，輸出差異清單與可執行修正計畫
- **輸出**：`docs/uiux/<date>_ui-review.md`
- **搭配 workflow**：`/ui-review`

#### `ux-fullstack-engineer/SKILL.md`（UX 全端工程師）
- **用途**：盤點流程、定義每個流程的狀態與 DoD
- **輸出**：`docs/uiux/<date>_ux-review.md`
- **搭配 workflow**：`/ux-review`

#### `debug-sheriff/SKILL.md`（除錯警長）
- **用途**：用閉環方式修 bug，強制留下重現/定位/驗證/防回歸證據
- **輸出**：`docs/bugs/<date>_<slug>.md`
- **搭配 workflow**：`/bugfix`

#### `smoke-tester/SKILL.md`（新增：冒煙測試）
- **用途**：最小 smoke checklist（點得到、走得通、不會立刻報錯）
- **輸出**：`docs/qa/<date>_smoke.md`
- **搭配 workflow**：`/bugfix`（Done Gate）

#### `openspec-conductor/SKILL.md`（OpenSpec 指揮官）
- **用途**：引導 spec→tasks→implement 節奏，避免先寫 code 造成返工
- **輸出**：下一步指令與 evidence 落點（寫入 runlog/roadmap）
- **搭配 workflow**：可搭配 `/status`（回報進度）

#### `scribe/SKILL.md`（記錄官／投影片素材整理）
- **用途**：每次 session 結束，把成果整理成可投影片化素材
- **輸出**：`experience/<YYYY-MM>/slides_<date>_talk-outline.md`
- **搭配 workflow**：`/session-close`

#### `git-steward/SKILL.md`（版本控管管家）
- **用途**：繁中 commit log + add/commit/push 指令建議（含 Evidence）
- **輸出**：commit message 與指令
- **搭配 workflow**：`/commit-push`

---

### 3.4 `.agent/workflows/`：你實際會天天用的 workflow
> 你要求固定命名：**/ui-review /ux-review /bugfix**（已固定）。其餘為輔助流程。

#### `/preflight`
- **用途**：開工前健檢（檔案齊全、description 不空、初始化 runlog）
- **輸出**：`docs/runlog/<date>_README.md`
- **搭配指令**：終端機可加跑 `python tools/bootstrap_antigravity_workspace_v7.py --verify-only`

#### `/stitch-import`
- **用途**：匯入 Stitch HTML，更新 `10-style-guide.md`（讓 style 可落地）
- **使用情境**：你先去 Stitch 溝通並匯出 HTML 後
- **實際動作**：重新跑 bootstrap（因為 tokens 由檔案生成）

#### `/ui-review`
- **用途**：UI 一致性盤點（對照 10-style-guide）
- **輸出**：`docs/uiux/<date>_ui-review.md`

#### `/ux-review`
- **用途**：流程盤點與狀態補齊（對照 20-ux-flow）
- **輸出**：`docs/uiux/<date>_ux-review.md`

#### `/bugfix`
- **用途**：除錯閉環 + Done Gate（必產 smoke evidence）
- **輸出**：
  - `docs/bugs/<date>_<slug>.md`
  - `docs/qa/<date>_smoke.md`

#### `/log-decision`
- **用途**：決策留痕（含 Style Freeze / 規範變更 / 重大取捨）
- **輸出**：
  - `docs/decision-log.md`（表格摘要）
  - `docs/decisions/<date>_<slug>.md`（詳細）

#### `/status`
- **用途**：進度回報（階段/下一步/阻塞/證據位置）並更新 roadmap/runlog
- **輸出**：更新 `docs/roadmap.md`、`docs/runlog/<date>_README.md`
- **強制**：必含「啟用證據」（40-activation-proof）

#### `/commit-push`
- **用途**：標準化 git add/commit/push（繁中 commit log）
- **輸出**：commit log 建議

#### `/session-close`
- **用途**：收尾整理成投影片素材
- **輸出**：`experience/<YYYY-MM>/slides_<date>_talk-outline.md`

---

### 3.5 `docs/`：你與主管/客戶報告最需要的文件
#### `docs/roadmap.md`
- **用途**：回答「目前在哪個階段？」
- **更新時機**：每次 `/status`

#### `docs/decision-log.md` + `docs/decisions/*`
- **用途**：所有取捨、Freeze、規範變更有憑有據（可稽核）
- **更新時機**：每次 `/log-decision`

#### `docs/runlog/*`
- **用途**：日誌（每日目標/進度/阻塞/證據），避免你因為一個 bug 迷失主線
- **更新時機**：每次 `/preflight`、`/status`

#### `docs/bugs/*` + `docs/qa/*`
- **用途**：處理「反覆除錯」的證據鏈（重現→修→驗證→防回歸）
- **更新時機**：每次 `/bugfix`

---

## 4. 如何確保 skills / workflows 被「正常啟用」（驗證方式）
### 4.1 Antigravity（建議的 Smoke Test）
1) 新 session 開始：先貼 `01-session-template.zh-TW.md` 的模板  
2) 你應該看到對方先輸出【啟用證據】（rules/workflows/skills 清單）  
3) 然後依序跑：`/preflight` → `/status`  
4) UI 任務：跑 `/stitch-import`（需要 HTML）→ `/ui-review` → 必須落檔 `docs/uiux/<date>_ui-review.md`

### 4.2 若你同時使用 Codex / Copilot / Gemini Code Assist
- 你要的不是「他會寫 code」，而是「他會遵守規範」  
- 建議在你的指令開頭加入固定句型：
  - 「請先讀 `.agent/AGENTS.md` 與 `.agent/rules/*`，並輸出啟用證據」
  - 「本次交付必須落檔到 docs/…（指定路徑）」
  - 「未通過 35-quality-gate 不得宣稱 Done」

---

## 5. 指令清單（你最常用的）
### 5.1 Antigravity slash commands（你建立的）
- `/preflight`
- `/stitch-import`
- `/ui-review`
- `/ux-review`
- `/bugfix`
- `/log-decision`
- `/status`
- `/commit-push`
- `/session-close`

### 5.2 OpenSpec（依你版本/實際安裝為準）
- 你可建立一個「openspec-conductor」去提醒每一步應下的命令與 evidence 落點  
- 建議節奏：spec → tasks → implement（每步都更新 runlog/roadmap）

---

## 6. 專案起始執行事項
### 6.1 初始化治理骨架（一次性）
1) 把 `bootstrap_antigravity_workspace_v7.py` 放到 `tools/`
2) 先跑一次（不帶 Stitch 也可）：
```bash
python tools/bootstrap_antigravity_workspace_v7.py
```
3) 再跑健檢：
```bash
python tools/bootstrap_antigravity_workspace_v7.py --verify-only
```

### 6.2 Stitch → Style Guide（從無到有的正確順序）
1) 先在 Stitch 溝通完成並匯出 HTML
2) 放到 repo：`design/stitch/stitch.html`
3) 重新跑 bootstrap（或在 Antigravity 用 `/stitch-import` 觸發重跑）：
```bash
python tools/bootstrap_antigravity_workspace_v7.py --stitch-html design/stitch/stitch.html
```
4) 跑 `/ui-review` → 產出 `docs/uiux/<date>_ui-review.md`
5) UI 確認後用 `/log-decision` 記錄 Style Freeze

### 6.3 第一次 commit（建立「可回溯的起點」）
```bash
git add -A
git commit -m "建立 Antigravity workspace 骨架（rules/workflows/skills + evidence docs）"
git push
```

---

## 7. 參考資料（來源連結）
- https://antigravity.google/docs/rules-workflows
- https://github.com/Fission-AI/OpenSpec
