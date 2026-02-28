from __future__ import annotations

"""
tools/bootstrap_copilot_workspace.py

目標（解決兩個最耗時的痛點 — GitHub Copilot 版）
1) UI/UX 一致性：把「按鈕/字級/間距/色彩」從逐頁人工微調，改成「有規範、可對照、可 Freeze」。
2) 反覆除錯：把「修了還錯/改錯檔」改成「可重現→定位→修復→驗證→防回歸」的閉環，並強制留下證據。

核心策略（從無到有的正確順序）
- 先 Stitch 產出 UI 基準（HTML）→ 產出 Style Contract → UI/UX 盤點 → Style Freeze → 才開始大量寫 code。

輸出（repo 內會生成）
- .github/copilot-instructions.md（Copilot 永久載入的主指令）
- .github/agents/WOS.agent.md（流程自動導航 Agent）
- .github/copilot/rules/（詳細規範文件，含 70-openspec-workflow.md）
- .github/copilot/skills/（角色分工文件）
- .github/copilot/prompts/（17 個一鍵觸發工作流）
- openspec/config.yaml（OpenSpec 設定）
- docs/（證據與追蹤）：roadmap / decision-log / runlog / uiux / bugs / qa

⚠️預設行為
- **預設 = overwrite（完整覆蓋重建）**
- 覆寫前會自動備份到：`.github/copilot/_backups/<timestamp>/`

用法
  # 1) 建議：先匯入 Stitch HTML（可選但強烈建議）
  python tools/bootstrap_copilot_workspace.py --stitch-html design/stitch/stitch.html

  # 2) 只做健檢（不寫檔）
  python tools/bootstrap_copilot_workspace.py --verify-only

  # 3) 指定專案名稱（用於 openspec config.yaml）
  python tools/bootstrap_copilot_workspace.py --project-name MyProject

參數
  --root           repo root（預設：本檔位於 tools/ 時，使用上一層）
  --stitch-html    Stitch 匯出的 html 路徑（可選）
  --mode           overwrite|safe（預設 overwrite）
  --no-backup      關閉自動備份（不建議）
  --verify-only    只做 workspace 健檢（不寫檔）
  --project-name   專案名稱（用於 openspec config，預設取 repo 資料夾名稱）
"""

import argparse
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------
# FS helpers
# ---------------------------

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def today_str() -> str:
    return date.today().isoformat()

def ts_str() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def _copy2(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)

def _should_overwrite(mode: str) -> bool:
    return mode == "overwrite"

def backup_paths(root: Path, rel_paths: List[str], backup_root: Path) -> None:
    for rel in rel_paths:
        p = root / rel
        if p.exists() and p.is_file():
            _copy2(p, backup_root / rel)

def backup_tree(root: Path, rel_dir: str, backup_root: Path) -> None:
    p = root / rel_dir
    if not p.exists():
        return
    for fp in p.rglob("*"):
        if "_backups" in fp.parts:
            continue
        if fp.is_file():
            rel = fp.relative_to(root)
            _copy2(fp, backup_root / rel.as_posix())

def write_text(root: Path, rel: str, content: str, mode: str, backup_root: Optional[Path]) -> str:
    p = root / rel
    ensure_dir(p.parent)
    if p.exists() and not _should_overwrite(mode):
        return "SKIP"
    if p.exists() and backup_root:
        _copy2(p, backup_root / rel)
    p.write_text(content, encoding="utf-8")
    return "WRITE"

def copy_file(root: Path, src: Path, rel_dst: str, mode: str, backup_root: Optional[Path]) -> str:
    dst = root / rel_dst
    ensure_dir(dst.parent)
    if dst.exists() and not _should_overwrite(mode):
        return "SKIP"
    if dst.exists() and backup_root:
        _copy2(dst, backup_root / rel_dst)
    dst.write_bytes(src.read_bytes())
    return "WRITE"


# ---------------------------
# Stitch token extraction (best-effort)
# ---------------------------

COLOR_PAIR_RE = re.compile(r'"([^"]+)"\s*:\s*"?(#[0-9A-Fa-f]{3,8})"?')
FONT_ARRAY_RE = re.compile(r'("?[a-zA-Z0-9_-]+"?)\s*:\s*\[([^\]]+)\]')
QUOTED_STR_RE = re.compile(r'"([^"]+)"|\'([^\']+)\'')

def _scan_js_object(text: str, start: int) -> Optional[str]:
    i = text.find("{", start)
    if i == -1:
        return None
    depth = 0
    in_str: Optional[str] = None
    esc = False
    for j in range(i, len(text)):
        ch = text[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            continue
        else:
            if ch in ("'", '"'):
                in_str = ch
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[i : j + 1]
    return None

def _extract_quoted_strings(s: str) -> List[str]:
    out: List[str] = []
    for m in QUOTED_STR_RE.finditer(s):
        val = m.group(1) or m.group(2)
        if val:
            out.append(val)
    return out

@dataclass
class StitchTokens:
    colors: Dict[str, str]
    fonts: Dict[str, List[str]]

def extract_tokens_from_stitch_html(html_path: Path) -> StitchTokens:
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    idx = text.find("tailwind.config")
    colors: Dict[str, str] = {}
    fonts: Dict[str, List[str]] = {}

    if idx != -1:
        obj = _scan_js_object(text, idx)
        if obj:
            for name, hexv in COLOR_PAIR_RE.findall(obj):
                if len(name) < 2:
                    continue
                colors[name.strip()] = hexv.strip()
            for key, arr in FONT_ARRAY_RE.findall(obj):
                family_key = key.strip().strip('"').strip("'")
                items = _extract_quoted_strings(arr)
                if items:
                    fonts[family_key] = items

    return StitchTokens(colors=colors, fonts=fonts)


# ---------------------------
# Render: copilot-instructions.md (main entry, always loaded)
# ---------------------------

def render_copilot_instructions() -> str:
    return f"""\
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
"""


# ---------------------------
# Render: rules
# ---------------------------

def rule_10_style_guide(tokens: Optional[StitchTokens]) -> str:
    status = "FROZEN" if tokens and (tokens.colors or tokens.fonts) else "PENDING"
    src = "design/stitch/stitch.html" if tokens else "（尚未提供 Stitch HTML）"
    colors_md = "- （待匯入 Stitch HTML 後自動萃取或人工補齊）"
    fonts_md = "- （待匯入 Stitch HTML 後自動萃取或人工補齊）"

    if tokens and tokens.colors:
        pairs = sorted(tokens.colors.items(), key=lambda kv: kv[0].lower())
        colors_md = "\n".join([f"- `{k}`: `{v}`" for k, v in pairs])
    if tokens and tokens.fonts:
        items = []
        for k, v in sorted(tokens.fonts.items(), key=lambda kv: kv[0].lower()):
            items.append(f"- `{k}`: {', '.join([f'`{x}`' for x in v])}")
        fonts_md = "\n".join(items)

    return f"""\
# 10-style-guide（Style Contract）

> 狀態：**{status}**
> 來源：{src}

## 1) 字體（Fonts）
{fonts_md}

## 2) 顏色（Colors）
{colors_md}

## 3) 間距 / 版面（Spacing / Layout）
- 統一使用 4px 基準（4/8/12/16/24/32...）
- 同一層級卡片 padding 一致（避免每頁漂移）
- 主要內容區塊盡量「有效滿版」：避免左右留白不一致

## 4) 按鈕 / 表單 / 互動狀態（Controls & States）
- Primary/Secondary/Link Button：高度/圓角/字重/hover/disabled/loading 必須一致
- 表單狀態：default / focus / error / success / disabled
- 空狀態（empty state）與載入（loading）必須有明確訊息與 skeleton/indicator

## 5) Freeze 機制（避免 UI 返工）
- UI 確認 OK 後：記錄「Style Freeze」決策到 `docs/decisions/`（原因→影響→驗收→證據）
- Freeze 後若需要改 UI：必須先記錄決策（原因→影響→驗收）才能動

## 6) 行動裝置 / 觸控（Mobile / Touch）
- 觸控目標最小尺寸：48×48 dp（依平台設計規範）
- Safe Area：頂部（狀態列）與底部（手勢列 / Home Indicator）必須留空
- Navigation Bar / Tab Bar：高度與圖示規格統一
- 捲動區域需有明確邊界（避免與系統手勢衝突）
- 長按（long-press）行為需有視覺回饋（highlight / tooltip）

## 7) 深色模式（Dark Mode）
- 提供 Light / Dark 兩組色彩 token（或至少預留命名空間）
- 背景：Dark 模式建議 #121212 或品牌深色，避免純黑 #000000
- 文字對比：Dark 模式下前景/背景對比 ≥ 4.5:1
- 圖片/圖示：需額外確認在深色背景上的可見度

## 8) 無障礙（Accessibility）
- 最小字級：14sp（正文），12sp（輔助文字，不可低於此值）
- 色彩對比：前景/背景 ≥ 4.5:1（WCAG AA）
- 可聚焦元件需有明確的 focus indicator
- 按鈕/連結需提供 accessibility label（螢幕閱讀器可讀）
- 觸控回饋：haptic / ripple / 視覺 highlight（至少擇一）

## 9) 使用方式
- 匯入 Stitch：重新跑 bootstrap `--stitch-html`
- 手動填入 tokens：直接編輯本文件的字體/顏色區段，將狀態改為 **FROZEN**
- 做 UI 盤點：依據本文件 + `skills/ui-designer.md` 產出 `docs/uiux/<date>_ui-review.md`
- Freeze：記錄決策到 `docs/decisions/` + `docs/decision-log.md`
"""


def rule_20_ux_flow() -> str:
    return """\
# 20-ux-flow（UX Flow Contract）

## 目標
- 盤點主要操作流程（happy path / edge cases）
- 每個流程都要有狀態設計：loading / empty / error / success
- 使用者永遠知道：我在哪、下一步是什麼、我做對了嗎

## 產出格式（建議）
- 流程清單：以「使用者目標」命名（例：建立專案、編輯提示詞、匯出、權限設定）
- 每個流程：
  - 前置條件 / 入口
  - 步驟（1..N）
  - 介面反應（按下按鈕後的反應、換頁、提示）
  - 錯誤處理與提示文字（含 retry）
  - 驗收條件（DoD）

## Navigation 架構
- 每個 flow 必須標注使用的 navigation 類型：Stack / Tab / Drawer / Modal
- 頁面層級關係需明確（從哪進、返回到哪）
- Deep link / 通知點擊的入口需標注

## 離線 / 網路狀態
- 明確定義離線策略：local-first / online-only / 混合
- 離線時的 UI 狀態：banner / toast / 功能降級範圍
- 重新上線時的同步行為（自動 / 手動 / 提示）

## 權限流程
- 需要裝置權限的功能（如麥克風、儲存、通知等），需定義：
  - 何時請求（首次使用時 / 啟動時）
  - 拒絕後的 UI 反應（功能降級 + 引導至設定）
  - 永久拒絕的處理

## App 生命週期
- 定義切換至背景時的行為（暫停 / 繼續 / 儲存進度）
- 定義從背景恢復時的行為（刷新 / 恢復 / 提示）
- 長時間背景後（被系統回收）的重新啟動行為

## 手勢規範
- 列出使用的手勢類型：swipe / long-press / pull-to-refresh / pinch 等
- 每個手勢需定義：觸發區域、行為、視覺回饋
- 手勢不可與系統手勢衝突（如邊緣滑動返回）

## 使用方式
- 依據本文件 + `skills/ux-fullstack-engineer.md` 產出 `docs/uiux/<date>_ux-review.md`
"""


def rule_30_debug_contract() -> str:
    return """\
# 30-debug-contract（Debug Contract）

## 除錯閉環（必走）
1) 重現：最短重現步驟（含環境、帳號、資料）
2) 定位：root cause 與定位證據（log / stack trace / diff）
3) 修復：改了哪些檔案、為何是這裡
4) 驗證：修復後如何驗證（步驟 + 證據）
5) 防回歸：補最小必要測試/檢查項（避免下次又壞）

## 禁止事項
- 沒有重現步驟，不得宣稱已修好
- 沒有驗證證據，不得結案

## 行動裝置偵錯（若適用）
- 重現步驟需標注測試裝置：模擬器 / 實機 + OS 版本
- 使用平台對應的 debug 工具（DevTools / 日誌檢視器 / 效能分析器）
- 若為裝置特定問題，需記錄裝置型號與 OS 版本

## 使用方式
- 依據本文件 + `skills/debug-sheriff.md` + `skills/smoke-tester.md`
- 產出 `docs/bugs/<date>_<slug>.md` + `docs/qa/<date>_smoke.md`
"""


def rule_35_quality_gate() -> str:
    return """\
# 35-quality-gate（完成宣告門檻 / Done Gate）

> 目的：處理常遇到的狀況：agent 說「完成可用了」，但一按就錯。

## Done Gate（缺一不可）
- UI 相關修改：
  - 必須更新 `docs/uiux/<date>_ui-review.md`（差異→修正→驗收→證據）
- UX 流程修改：
  - 必須更新 `docs/uiux/<date>_ux-review.md`（flow/狀態/DoD）
- Bug 修復：
  - 必須產出 `docs/bugs/<date>_<slug>.md`（重現/定位/修復/驗證/防回歸）
  - 必須產出 `docs/qa/<date>_smoke.md`（最小 smoke checklist + 結果）
- 功能實作：
  - 必須有對應的規格（spec）或需求描述
  - 必須通過基本 smoke test（主要 happy path 可用）
  - 若有 OpenSpec tasks，需更新 task 狀態
- 效能相關：
  - 批次操作 / 檔案生成 / 大量資料處理需確認不造成 UI 凍結（ANR / 無回應）
  - 若有明顯效能疑慮，需記錄測試結果（操作時間 / 記憶體用量）

## 若未通過 Done Gate
- 不得宣稱 Done
- 必須補齊 evidence 後再回報
"""


def rule_36_scope_guard() -> str:
    return """\
# 36-scope-guard（範圍護欄 / Smallest Safe Change 強化）

## 目標
- 避免為了修一個 bug/調一個 UI，把其它頁面或流程一起弄壞（引入新 bug）
- 確保每次改動可回溯、可驗收、可快速回滾

## 觸發條件（遇到就先停、先記錄決策）
- 一次改動超過 5 個檔案
- 需要改動 tokens / Style Contract（10-style-guide）
- 沒有重現步驟卻想大改
- 同一問題第 3 次仍未收斂（代表需要換策略）
- 新增或升級 dependency（套件 / 函式庫）
- 新增或移除頁面路由（navigation route）
- 變更資料庫 schema 或本地儲存結構

## 拆解策略
- 先把「最短修復」做出來 → 先通過 smoke → 再做重構/美化
"""


# ---------------------------
# Render: skills
# ---------------------------

def skill_ui_designer() -> str:
    return r"""
# Skill: ui-designer（UI 前端設計師）

## 任務目標
把「每頁都要慢慢調」變成「有規範可對照、一次修到位」，並把修正計畫做成可交付的清單。

## 依據（Evidence）
- `.github/copilot/rules/10-style-guide.md`（唯一 UI 規範）
- `design/stitch/stitch.html`（Stitch evidence；或補充截圖/錄影/URL）
- 目標頁面/元件檔案（repo 內）

## 輸出（必交付）
- `docs/uiux/<date>_ui-review.md`，內容必含：
  1) **Findings（差異清單）**：逐項列「現況 vs 規範」＋引用規範章節
  2) **Patch Plan（修正計畫）**：可直接執行的修改清單（檔案/元件/範圍）
  3) **Acceptance（驗收）**：如何驗收（視覺/互動/狀態）
  4) **Evidence（證據）**：相關 diff、截圖、或 runlog 位置

## 執行步驟（建議順序）
1) 先讀 style guide，列出「可凍結基準」：字級、按鈕高度、卡片 padding、主色/次色、表單狀態
2) 逐頁比對（或抽 3~5 個代表頁）→ 先抓最大的不一致
3) 只做 Smallest Safe Change：先把 tokens/共用元件拉齊，再調個別頁面
4) 若發現規範本身要改：停止，先記錄決策到 docs/decisions/

## 禁止事項
- 未引用 style guide 就做「主觀美化」
- 一次改太多頁面造成漂移（觸發 scope-guard）
""".lstrip()


def skill_ux_fullstack_engineer() -> str:
    return r"""
# Skill: ux-fullstack-engineer（UX 全端工程師）

## 任務目標
把操作流程一次盤清楚，讓使用者永遠知道「我在哪、下一步是什麼」，並可作為驗收基準。

## 依據（Evidence）
- `.github/copilot/rules/20-ux-flow.md`
- 現有 UI（Stitch/前端頁面）
- 現有需求（若有 OpenSpec specs）

## 輸出（必交付）
- `docs/uiux/<date>_ux-review.md`，內容必含：
  1) **Flow List**：以使用者目標命名（5~15 條）
  2) 每個 Flow 的 **Steps / UI Reaction / States**
  3) **Edge Cases**：error/permission/not found/timeout
  4) **DoD（驗收條件）**
  5) **Open Questions**（需要決策的點）

## 執行步驟
1) 先列 top flows（以最常 demo/最常用的為優先）
2) 每個 flow 強制補狀態：loading/empty/error/success
3) 每個 flow 標注 navigation 類型：Stack / Tab / Drawer / Modal
4) 針對行動 App：補充手勢互動與 haptic / transition 動畫需求
5) 決定最小可用：哪些 flow 必須在 MVP 完成、哪些可延後
""".lstrip()


def skill_debug_sheriff() -> str:
    return r"""
# Skill: debug-sheriff（除錯警長）

## 任務目標
把 bug 修復變成閉環：可重現→定位→修復→驗證→防回歸（並落檔留證據）。

## 依據（Evidence）
- `.github/copilot/rules/30-debug-contract.md`
- 錯誤訊息/stack trace/console log
- 相關頁面與程式碼（檔案路徑）

## 輸出（必交付）
- `docs/bugs/<date>_<slug>.md`，內容必含：
  1) Repro（最短重現步驟）
  2) Root Cause（含定位證據：log/diff）
  3) Fix（改了哪些檔案，為何是這裡）
  4) Verify（如何證明修好）
  5) Regression（防回歸：最小測試/檢查項）
- 需要時：交由 smoke-tester 產出 `docs/qa/<date>_smoke.md`

## 禁止事項
- 沒有重現步驟就大改
- 沒有驗證證據就結案
""".lstrip()


def skill_smoke_tester() -> str:
    return r"""
# Skill: smoke-tester（冒煙測試／最小驗收）

## 任務目標
避免「agent 說完成可用了，但一按就錯」；用最小測試快速擋掉明顯回歸。

## 依據
- `docs/uiux/<date>_ux-review.md`（flows）
- 本次變更範圍（git diff / commit）
- 主要入口頁面/按鈕

## 輸出（必交付）
- `docs/qa/<date>_smoke.md`，內容必含：
  - 測試環境（local/dev）
  - 測試資料/帳號（若需要）
  - Checklist（3~15 條，對應主要 flows）
  - 結果（Pass/Fail + 證據）
  - 若 Fail：連回 bug 文檔（docs/bugs）

## 建議 checklist 範例
- App 可啟動且首頁不報錯
- 主 CTA 按鈕可點擊且有回饋（loading/disable）
- 主要表單可送出且錯誤提示正常
- 主要列表可載入（含 empty state）
""".lstrip()


def skill_openspec_conductor() -> str:
    return r"""
# Skill: openspec-conductor（OpenSpec 指揮官）

## 任務目標
用 OpenSpec 把需求→規格→任務→實作走完；每一步都可驗收、可留證據。

## 依據
- OpenSpec 專案內 `openspec/`（changes / specs / config.yaml）
- `docs/roadmap.md`（目前階段）
- `docs/runlog/<date>_README.md`（當日進度）
- `.github/copilot/rules/70-openspec-workflow.md`（Change Lifecycle）

## 工作流程（對應 Prompt 觸發）

完整 Change Lifecycle 請參閱 `rules/70-openspec-workflow.md`

| 階段 | Prompt | 內建 Skill |
|---|---|---|
| 需求探索 | `#opsx-explore` | `openspec-explore` |
| 建立 Change | `#opsx-new` | `openspec-new-change` |
| 快進 Artifacts | `#opsx-ff` | `openspec-ff-change` |
| 驗證完整性 | `#opsx-validate` | —（CLI + 補充檢查） |
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

## 輸出（必交付）
- 下一步該做什麼（包含要下的指令/動作）
- 規格缺口清單（缺一不可的驗收點）
- evidence 應落檔的位置（runlog / decision / bugs / qa）
""".lstrip()


def skill_scribe() -> str:
    return r"""
# Skill: scribe（記錄官／投影片素材整理）

## 任務目標
把每次 session 的成果整理成可投影片化素材，不依賴冗長對話匯出。

## Inputs
- 本次做了什麼（或 git diff --stat）
- 重要決策（docs/decisions）
- 重要 bug 與修復證據（docs/bugs、docs/qa）

## Outputs（必交付）
- `experience/<YYYY-MM>/slides_<date>_talk-outline.md`，建議結構：
  1) **目標**：本次 session 要解決什麼
  2) **問題**：遇到什麼阻礙 / 挑戰
  3) **方法**：用什麼策略解決
  4) **結果**：前後對照（before/after）
  5) **學到什麼**：踩雷與修正
- 重點素材：問題/方法/對照/示範步驟/踩雷與修正

## Session 結束前 Checklist
- [ ] `docs/roadmap.md` 已更新目前階段
- [ ] `docs/runlog/<date>_README.md` 已記錄今日進度
- [ ] 未結案的 bug 已記錄在 `docs/bugs/`
- [ ] 重要決策已記錄在 `docs/decisions/`
- [ ] 產出 slides outline
""".lstrip()


def skill_git_steward() -> str:
    return r"""
# Skill: git-steward（版本控管管家）

## 任務目標
把每次變更都變成可追溯證據，降低「做了但找不到改哪」的風險。

## 分支策略
- 分支命名慣例：
  - `feature/<slug>` — 新功能
  - `bugfix/<slug>` — Bug 修復
  - `hotfix/<slug>` — 緊急修復
  - `chore/<slug>` — 雜務（依賴升級、CI、文件）
- 主分支保護：不得直接 push 到 main/master（建議）

## Commit Template（繁中）
- What：做了什麼（具體檔案/功能）
- Why：為什麼要做
- Impact：對使用者/系統的影響
- Evidence：如何驗證（測試/截圖/log/文件）

## .gitignore 建議
- 專案初始化時確認 `.gitignore` 包含：
  - 開發框架產生的暫存檔 / build 產出
  - 依賴套件目錄（`node_modules/`、`venv/` 等）
  - 組態檔案（`.env`、`*.local`）
  - OS 產生的檔案（`.DS_Store`、`Thumbs.db`）
  - IDE 設定（`.idea/`、`.vscode/` 中的個人設定）

## PR 流程（若有協作者）
- PR description 格式：What / Why / How to test / Evidence links
- 至少一人 review（或自己用 checklist 自審）
- 合併前確認 smoke test 通過

## Outputs
- 建議的 git 指令序列
- commit message（繁中，含 What/Why/Impact/Evidence）
- 若有風險：提醒需要 review / 分支策略
""".lstrip()


def rule_50_tech_stack() -> str:
    return """\
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
"""


def rule_60_testing() -> str:
    return """\
# 60-testing（測試策略）

## 目標
- 定義最低測試覆蓋標準，避免「只手動測」或「完全沒測」
- 讓每次修改都有可驗證的依據

## 測試金字塔

### 1) 單元測試（Unit）
- 覆蓋範圍：純函式、工具函式、資料轉換、商業邏輯
- 不測 UI 渲染、不測第三方 API
- 最低要求：核心邏輯模組覆蓋率 ≥ 70%

### 2) 整合測試（Integration）
- 覆蓋範圍：元件組合、頁面流程、API 串接（可 mock）
- 確認主要 flow 的 happy path 可通過

### 3) E2E 測試（End-to-End）
- 覆蓋範圍：主要使用者流程（3~5 條 critical path）
- 可使用平台對應的 E2E 工具
- 最低要求：主 CTA 流程可跑通

### 4) Smoke 測試（手動 / 自動化前的替代）
- 參考 `skills/smoke-tester.md` 的 checklist
- 每次 bugfix / feature 完成後必跑

## 命名慣例
- 測試檔案與被測檔案同目錄或 `__tests__/` 子目錄
- 命名：`<filename>.test.ts` 或 `<filename>.spec.ts`

## 何時寫測試
- Bug 修復：修復前先補重現測試（紅燈）→ 修復後轉綠燈
- 新功能：核心邏輯先寫測試 → 再實作
- 重構：確保既有測試全部通過後才動手

## 使用方式
- 此文件為通用策略，具體工具依 `50-tech-stack.md` 定義
- 測試結果作為 Done Gate 證據之一
"""


def rule_70_openspec_workflow() -> str:
    return """\
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
"""


# ---------------------------
# Render: WOS Agent
# ---------------------------

def render_wos_agent() -> str:
    return '''\
---
description: "Wilson Operation System — 自動判斷 Change Lifecycle 狀態，建議下一步操作。Use when: 開工、不確定下一步、需要流程導引、session start、status check、lifecycle、workflow guidance"
tools: [read, search, agent, todo]
---

你是 **WOS（Wilson Operation System）**，專案工作流的自動導航系統。
你的職責是**判斷目前狀態**並**建議最佳下一步**，不直接執行實作。

## 核心能力

### 1. 自動狀態偵測
每次被呼叫時，依序檢查以下資訊來判斷目前所在的 Lifecycle 階段：

```
檢查順序：
1. docs/roadmap.md → 目前大階段（S0~S6）
2. openspec/changes/ → 是否有進行中的 Change（非 archive/）
3. 若有 Change → 讀取其 artifacts 判斷進度
4. docs/runlog/<今日日期>_README.md → 今日是否已開工
5. git status → 是否有未提交的變更
```

### 2. Lifecycle 階段判斷邏輯

| 偵測到的狀態 | 判定階段 | 建議動作 |
|---|---|---|
| 無 runlog 或今日目標為空 | 未開工 | → `#session-start` |
| 無進行中 Change | 規劃階段 | → `#opsx-explore` 或 `#opsx-new` |
| Change 有 proposal，無 spec/tasks | 需要 FF | → `#opsx-ff` |
| Change 有 tasks，無實作 | 需要驗證後實作 | → `#opsx-validate` → `#opsx-apply` |
| Change tasks 部分完成 | 實作中 | → 繼續 `#opsx-apply` |
| Change tasks 全部完成 | 需要驗證 | → `#opsx-verify` |
| Verify 通過，有 UI 變更 | 品質閘 | → `#ui-review` |
| Verify 通過，有 UX 變更 | 品質閘 | → `#ux-review` |
| Verify 通過，有 Bug 修復 | 品質閘 | → `#smoke-test` |
| 品質閘通過 | 待審查 | → `#code-review` |
| Review 通過 | 待提交 | → `#commit-push` |
| 已提交，有 delta specs | 待同步 | → `#opsx-sync` |
| 已同步 | 待歸檔 | → `#opsx-archive` → `#log-decision` |
| git 有未提交變更 | 需提交 | → `#commit-push` |
| 一切就緒 | 收尾 | → `#status` → `#session-close` |

### 3. 輸出格式

```markdown
## 🔍 WOS 狀態報告

### 專案階段
- Roadmap：{S? 階段名稱}

### Change 狀態
- 進行中：{change 名稱} 或 無
- Artifacts：{已有的 / 缺少的}
- Tasks：{完成數/總數}

### Git 狀態
- 未提交檔案：{數量}
- 目前分支：{branch}

### 📌 建議下一步
1. **{最優先動作}** — `#prompt-name`
   理由：{為什麼}
2. **{次要動作}**（可選）— `#prompt-name`

### 完整 Lifecycle 進度
Session Start [✅/⬜] → New [✅/⬜] → FF [✅/⬜] → Validate [✅/⬜]
  → Apply [✅/⬜] → Verify [✅/⬜] → Quality Gate [✅/⬜]
  → Review [✅/⬜] → Commit [✅/⬜] → Sync [✅/⬜] → Archive [✅/⬜]
```

## 約束
- **不直接修改程式碼或檔案**（只讀取、分析、建議）
- **不跳過流程步驟**（嚴格按照 `rules/70-openspec-workflow.md`）
- **使用正體中文**回覆
- 若偵測到異常（如有 Change 但無 tasks），主動警告
'''


# ---------------------------
# Render: OpenSpec config.yaml
# ---------------------------

def render_openspec_config(project_name: str) -> str:
    return f"""\
schema: spec-driven

context: |
  專案名稱：{project_name}
  語言：正體中文為主
  治理規範：.github/copilot/rules/*.md
  角色分工：.github/copilot/skills/*.md
  工作流程：.github/copilot/rules/70-openspec-workflow.md
  證據結構：docs/（roadmap / decision-log / runlog / uiux / bugs / qa）
  Commit 慣例：繁體中文（What / Why / Impact / Evidence）

rules:
  proposal:
    - 使用正體中文撰寫
    - 必須包含 Non-goals 區段
    - 必須說明對 roadmap 的影響
  tasks:
    - 每個 task 拆到 2 小時內可完成
    - 每個 task 必須有明確驗收條件
    - 遵守最小安全修改原則
"""


# ---------------------------
# Render: Prompt files（17 個一鍵觸發工作流）
# ---------------------------

PROMPT_FILES: Dict[str, Tuple[str, str]] = {
    "session-start": (
        "開工流程：讀取規範、確認階段、初始化 runlog",
        """\
請執行開工流程（Session Start）：

1. 閱讀 `.github/copilot/rules/` 下所有規範
2. 確認目前階段（`docs/roadmap.md`）
3. 初始化或更新當日 runlog（`docs/runlog/<今日日期>_README.md`）
4. 檢查 Style Guide 狀態（PENDING/FROZEN）
5. 檢查 `openspec/changes/` 是否有進行中的 Change
6. 回報啟用證據：已讀規範清單、本次使用的角色、目前階段""",
    ),
    "opsx-explore": (
        "OpenSpec：需求探索與問題釐清",
        """\
請使用 `openspec-explore` skill 進入探索模式。

協助我釐清需求、調查問題、或討論設計方向。
在探索結束後，總結要點並建議是否建立新的 Change。""",
    ),
    "opsx-new": (
        "OpenSpec：建立新 Change",
        """\
請使用 `openspec-new-change` skill 建立新的 Change。

步驟：
1. 在 `openspec/changes/` 下建立 change 目錄
2. 建立 proposal artifact
3. 確認 Change 名稱和範疇
4. 更新 `docs/runlog/` 記錄本次操作

完成後告訴我下一步該執行什麼（建議 `#opsx-ff` 快進生成所有 artifacts）。""",
    ),
    "opsx-ff": (
        "OpenSpec：快進生成所有 artifacts",
        """\
請使用 `openspec-ff-change` skill 快進完成目前進行中 Change 的所有 artifacts。

這會自動生成：proposal → spec → delta-spec → tasks 等所有必要文件。
完成後提示我進行 `#opsx-validate` 驗證。""",
    ),
    "opsx-validate": (
        "OpenSpec：驗證 Change 完整性（自動呼叫 openspec validate）",
        """\
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
通過後提示進行 `#opsx-apply`。""",
    ),
    "opsx-apply": (
        "OpenSpec：實作 Change 中的 tasks",
        """\
請使用 `openspec-apply-change` skill 實作目前進行中 Change 的 tasks。

遵守規則：
- 參照 `rules/50-tech-stack.md` 技術棧約定
- 遵守 `rules/36-scope-guard.md` 範圍護欄
- 最小安全修改原則（Smallest Safe Change）
- 每完成一個 task 就更新狀態
- 在 `docs/runlog/` 記錄進度

完成後提示我進行 `#opsx-verify` 驗證實作結果。""",
    ),
    "opsx-verify": (
        "OpenSpec：驗證實作是否符合 Change artifacts",
        """\
請使用 `openspec-verify-change` skill 驗證實作結果。

檢查項目：
1. 每個 task 的驗收條件是否滿足
2. 實作是否與 spec / delta-spec 一致
3. 是否有未處理的邊界情況
4. Done Gate（`rules/35-quality-gate.md`）是否通過

若涉及：
- UI 修改 → 提示需要 `#ui-review`
- UX 流程 → 提示需要 `#ux-review`
- Bug 修復 → 提示需要 `#smoke-test`

完成後提示進入品質閘階段。""",
    ),
    "opsx-sync": (
        "OpenSpec：同步 delta specs 到 main specs",
        """\
請使用 `openspec-sync-specs` skill，將目前 Change 的 delta specs 同步到 main specs。

完成後提示進行 `#opsx-archive` 歸檔。""",
    ),
    "opsx-archive": (
        "OpenSpec：歸檔已完成的 Change",
        """\
請使用 `openspec-archive-change` skill 歸檔目前已完成的 Change。

前置條件（必須全部滿足）：
- Verify 已通過
- 相關品質閘已通過（UI/UX review、smoke test）
- Specs 已同步

歸檔後更新 `docs/roadmap.md` 和 `docs/runlog/`。""",
    ),
    "ui-review": (
        "UI 審查：依 Style Guide 比對差異並產出修正計畫",
        """\
請以 `ui-designer` 角色執行 UI 審查。

步驟：
1. 讀取 `rules/10-style-guide.md`（Style Contract）
2. 讀取 `skills/ui-designer.md`（角色說明）
3. 對目標頁面/元件進行比對
4. 產出 `docs/uiux/<今日日期>_ui-review.md`

輸出內容必含：
- Findings（差異清單）：現況 vs 規範 + 引用章節
- Patch Plan（修正計畫）：可直接執行的修改清單
- Acceptance（驗收）：如何驗收
- Evidence（證據）：diff / 截圖 / runlog 位置

如果你不確定目標頁面，請先問我。""",
    ),
    "ux-review": (
        "UX 審查：盤點操作流程、狀態設計、DoD",
        """\
請以 `ux-fullstack-engineer` 角色執行 UX 審查。

步驟：
1. 讀取 `rules/20-ux-flow.md`（UX Flow Contract）
2. 讀取 `skills/ux-fullstack-engineer.md`（角色說明）
3. 盤點目標功能的操作流程
4. 產出 `docs/uiux/<今日日期>_ux-review.md`

輸出內容必含：
- Flow List（使用者目標命名，5~15 條）
- Steps / UI Reaction / States
- Edge Cases（error / permission / not found / timeout）
- DoD（驗收條件）
- Open Questions（需要決策的點）""",
    ),
    "smoke-test": (
        "冒煙測試：最小驗收 checklist",
        """\
請以 `smoke-tester` 角色執行冒煙測試。

步驟：
1. 讀取 `skills/smoke-tester.md`（角色說明）
2. 確認本次變更範圍（git diff 或手動說明）
3. 產出 `docs/qa/<今日日期>_smoke.md`

輸出內容必含：
- 測試環境
- 測試資料/帳號（若需要）
- Checklist（3~15 條，對應主要 flows）
- 結果（Pass / Fail + 證據）
- 若 Fail：連回 bug 文檔路徑""",
    ),
    "code-review": (
        "程式碼審查：安全性、效能、一致性檢查",
        """\
請以 `code-reviewer` 角色執行程式碼審查。

步驟：
1. 讀取 `rules/50-tech-stack.md` + `rules/60-testing.md`
2. 讀取 `skills/code-reviewer.md`（角色說明 + checklist）
3. 檢視本次變更的 diff
4. 依 checklist 逐項檢查：安全性 / 效能 / 一致性 / 可維護性 / 測試

輸出格式：
- 🔴 必修（Must Fix）
- 🟡 建議（Suggestion）
- 🟢 良好（Good）

審查通過後提示可進行 `#commit-push`。""",
    ),
    "status": (
        "狀態更新：同步 roadmap 與 runlog",
        """\
請執行狀態更新：

1. 讀取 `docs/roadmap.md`，確認目前階段
2. 讀取 `openspec/changes/` 查看進行中的 Changes
3. 更新 `docs/roadmap.md`：
   - Current 階段
   - Next 步驟
   - Blockers（阻塞因素）
   - Evidence（證據連結）
4. 更新 `docs/runlog/<今日日期>_README.md`：
   - 今日目標
   - 今日進度
   - 阻塞
   - 證據連結

輸出更新摘要。""",
    ),
    "commit-push": (
        "審查 + 提交 + 推送：先 review 再 commit/push（GitKraken MCP 自動化）",
        """\
請以 `git-steward` + `code-reviewer` 角色執行提交流程。
優先使用 GitKraken MCP 工具（`mcp_gitkraken_*`）執行 git 操作，若 MCP 不可用則 fallback 到終端指令。

**嚴格順序**：

### Step 1：查看變更（GitKraken MCP）
- 使用 `mcp_gitkraken_git_status` 查看目前工作區狀態
- 使用 `mcp_gitkraken_git_log_or_diff` 查看詳細 diff
- 依 `code-reviewer.md` checklist 審查
- 若有 🔴 必修項 → 停止，先修復

### Step 2：Review 結果呈現
- 列出變更檔案清單
- 列出 review 結果（必修/建議/良好）
- **等待我確認後才繼續**

### Step 3：Commit + Push（我確認後執行）
- 產出 commit message（繁體中文，含 What / Why / Impact / Evidence）
- 使用 `mcp_gitkraken_git_add_or_commit` 執行 stage + commit
- 使用 `mcp_gitkraken_git_push` 執行 push

### Fallback（MCP 不可用時）
- 改用終端執行 `git add` + `git commit` + `git push`

注意：
- 不得跳過 review 直接 commit
- commit message 必須使用繁體中文""",
    ),
    "log-decision": (
        "記錄決策：落檔到 decision-log 和 decisions/",
        """\
請執行決策記錄：

1. 確認本次決策的內容（若不清楚，請問我）
2. 在 `docs/decision-log.md` 新增一行：
   - Date | Decision | Why | Impact | Evidence
3. 若為重大決策（Style Freeze / 規範變更 / 架構調整），額外產出：
   - `docs/decisions/<今日日期>_<slug>.md`
   - 內容：背景 / 決策 / 原因 / 影響 / 替代方案 / 證據

完成後確認 decision-log.md 已更新。""",
    ),
    "session-close": (
        "Session 收尾：更新 roadmap、產出 slides outline",
        """\
請以 `scribe` 角色執行 Session 收尾。

### Checklist（逐項完成）：
- [ ] `docs/roadmap.md` 已更新目前階段
- [ ] `docs/runlog/<今日日期>_README.md` 已記錄今日進度
- [ ] 未結案的 bug 已記錄在 `docs/bugs/`
- [ ] 進行中的 Change 狀態已更新
- [ ] 重要決策已記錄在 `docs/decisions/`

### 產出 Slides Outline
在 `experience/<YYYY-MM>/slides_<今日日期>_talk-outline.md` 產出：
1. **目標**：本次 session 要解決什麼
2. **問題**：遇到什麼阻礙/挑戰
3. **方法**：用什麼策略解決
4. **結果**：前後對照（before/after）
5. **學到什麼**：踩雷與修正

### 最後
- 列出所有本次 session 產出的證據文件路徑
- 列出下次 session 建議的第一步""",
    ),
}


def render_prompt_file(name: str) -> str:
    """Render a single .prompt.md file content."""
    desc, body = PROMPT_FILES[name]
    return f"---\nagent: agent\ndescription: \"{desc}\"\n---\n{body}\n"


def skill_code_reviewer() -> str:
    return r"""
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
""".lstrip()


# ---------------------------
# Render: docs
# ---------------------------

def doc_roadmap() -> str:
    return f"""\
# Roadmap

> 用來回答：「目前在哪個階段？下一步是什麼？」

## 階段（可自行增修）
- S0：Stitch UI 基準（HTML）
- S1：Bootstrap workspace（rules/skills）
- S2：UI/UX 盤點 + Style Freeze
- S3：OpenSpec 規格（spec→tasks）
- S4：Implement
- S5：Bugfix 收斂 + Smoke + 回歸驗證
- S6：整理投影片素材（分享）

## 目前狀態
- Current：S1（{today_str()}）
- Next：
- Blockers：
- Evidence：
"""


def doc_decision_log() -> str:
    return """\
# Decision Log（決策紀錄）

> 所有取捨與規格變更都要留痕（尤其是 Style Freeze / 規範變更）。

| Date | Decision | Why | Impact | Evidence |
|---|---|---|---|---|
"""


def doc_runlog() -> str:
    return f"""\
# Runlog {today_str()}

## 今日目標
-

## 今日進度
-

## 阻塞
-

## 證據（links / paths）
-
"""


def docs_readme(title: str, desc: str) -> str:
    return f"""\
# {title}

- {desc}
"""


# ---------------------------
# Verify-only (workspace health check)
# ---------------------------

def verify_workspace(root: Path) -> int:
    required = [
        root / ".github" / "copilot-instructions.md",
        root / ".github" / "agents" / "WOS.agent.md",
        root / ".github" / "copilot" / "rules" / "10-style-guide.md",
        root / ".github" / "copilot" / "rules" / "20-ux-flow.md",
        root / ".github" / "copilot" / "rules" / "30-debug-contract.md",
        root / ".github" / "copilot" / "rules" / "35-quality-gate.md",
        root / ".github" / "copilot" / "rules" / "36-scope-guard.md",
        root / ".github" / "copilot" / "rules" / "50-tech-stack.md",
        root / ".github" / "copilot" / "rules" / "60-testing.md",
        root / ".github" / "copilot" / "rules" / "70-openspec-workflow.md",
        root / ".github" / "copilot" / "skills" / "ui-designer.md",
        root / ".github" / "copilot" / "skills" / "ux-fullstack-engineer.md",
        root / ".github" / "copilot" / "skills" / "debug-sheriff.md",
        root / ".github" / "copilot" / "skills" / "smoke-tester.md",
        root / ".github" / "copilot" / "skills" / "openspec-conductor.md",
        root / ".github" / "copilot" / "skills" / "scribe.md",
        root / ".github" / "copilot" / "skills" / "git-steward.md",
        root / ".github" / "copilot" / "skills" / "code-reviewer.md",
        root / "openspec" / "config.yaml",
        root / "docs" / "roadmap.md",
        root / "docs" / "decision-log.md",
    ]

    # Check all 17 prompt files
    for name in PROMPT_FILES:
        required.append(root / ".github" / "copilot" / "prompts" / f"{name}.prompt.md")

    missing = [p for p in required if not p.exists()]
    if missing:
        print("❌ Missing required files:")
        for p in missing:
            print(f"  - {p.relative_to(root)}")
        return 2

    # Check style guide status
    sg = (root / ".github" / "copilot" / "rules" / "10-style-guide.md").read_text(
        encoding="utf-8", errors="ignore"
    )
    if "**PENDING**" in sg:
        print("⚠️  Style guide is PENDING. Provide Stitch HTML and run bootstrap with --stitch-html.")
    else:
        print("✅ Style guide looks ready (not PENDING).")

    # Check docs directories
    for d in ["docs/decisions", "docs/runlog", "docs/uiux", "docs/bugs", "docs/qa"]:
        dp = root / d
        if not dp.exists():
            print(f"⚠️  Missing directory: {d}")

    # Check openspec directories
    for d in ["openspec/specs", "openspec/changes", "openspec/changes/archive"]:
        dp = root / d
        if not dp.exists():
            print(f"⚠️  Missing directory: {d}")

    print("✅ Workspace verify passed.")
    return 0


# ---------------------------
# Main
# ---------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap GitHub Copilot workspace（rules/skills/prompts/agents/docs）")
    parser.add_argument("--root", default="", help="repo root（預設：本檔位於 tools/ 時，使用上一層）")
    parser.add_argument("--stitch-html", default="", help="Stitch 匯出的 html 路徑（可選）")
    parser.add_argument("--mode", choices=["overwrite", "safe"], default="overwrite", help="預設 overwrite")
    parser.add_argument("--no-backup", action="store_true", help="關閉自動備份（不建議）")
    parser.add_argument("--verify-only", action="store_true", help="只做健檢（不寫檔）")
    parser.add_argument("--project-name", default="", help="專案名稱（用於 openspec config，預設取 repo 資料夾名稱）")
    args = parser.parse_args()

    here = Path(__file__).resolve()
    default_root = here.parents[1] if here.parent.name == "tools" else Path(".").resolve()
    root = Path(args.root).resolve() if args.root else default_root
    project_name = args.project_name or root.name

    if args.verify_only:
        return verify_workspace(root)

    mode: str = args.mode
    backup_root: Optional[Path] = None
    if _should_overwrite(mode) and not args.no_backup:
        backup_root = root / ".github" / "copilot" / "_backups" / ts_str()
        ensure_dir(backup_root)
        backup_tree(root, ".github", backup_root)
        backup_paths(root, ["docs/roadmap.md", "docs/decision-log.md"], backup_root)

    # Create directories
    for d in [
        root / ".github/agents",
        root / ".github/copilot/rules",
        root / ".github/copilot/skills",
        root / ".github/copilot/prompts",
        root / "openspec/specs",
        root / "openspec/changes/archive",
        root / "docs/decisions",
        root / "docs/uiux",
        root / "docs/bugs",
        root / "docs/qa",
        root / "docs/runlog",
        root / "design/stitch",
        root / "experience",
    ]:
        ensure_dir(d)

    # Stitch: copy into canonical path + tokens
    tokens: Optional[StitchTokens] = None
    if args.stitch_html:
        stitch_path = Path(args.stitch_html).resolve()
        if stitch_path.exists():
            copy_file(root, stitch_path, "design/stitch/stitch.html", mode, backup_root)
            try:
                tokens = extract_tokens_from_stitch_html(stitch_path)
            except Exception as e:
                print(f"⚠️  Failed to extract tokens from Stitch HTML: {e}")

    # Collect all files to write
    files: List[Tuple[str, str]] = []

    # Main entry
    files.append((".github/copilot-instructions.md", render_copilot_instructions()))

    # WOS Agent
    files.append((".github/agents/WOS.agent.md", render_wos_agent()))

    # Rules
    files.append((".github/copilot/rules/10-style-guide.md", rule_10_style_guide(tokens)))
    files.append((".github/copilot/rules/20-ux-flow.md", rule_20_ux_flow()))
    files.append((".github/copilot/rules/30-debug-contract.md", rule_30_debug_contract()))
    files.append((".github/copilot/rules/35-quality-gate.md", rule_35_quality_gate()))
    files.append((".github/copilot/rules/36-scope-guard.md", rule_36_scope_guard()))
    files.append((".github/copilot/rules/50-tech-stack.md", rule_50_tech_stack()))
    files.append((".github/copilot/rules/60-testing.md", rule_60_testing()))
    files.append((".github/copilot/rules/70-openspec-workflow.md", rule_70_openspec_workflow()))

    # Skills
    files.append((".github/copilot/skills/ui-designer.md", skill_ui_designer()))
    files.append((".github/copilot/skills/ux-fullstack-engineer.md", skill_ux_fullstack_engineer()))
    files.append((".github/copilot/skills/debug-sheriff.md", skill_debug_sheriff()))
    files.append((".github/copilot/skills/smoke-tester.md", skill_smoke_tester()))
    files.append((".github/copilot/skills/openspec-conductor.md", skill_openspec_conductor()))
    files.append((".github/copilot/skills/scribe.md", skill_scribe()))
    files.append((".github/copilot/skills/git-steward.md", skill_git_steward()))
    files.append((".github/copilot/skills/code-reviewer.md", skill_code_reviewer()))

    # Prompt files（17 個一鍵觸發工作流）
    for name in PROMPT_FILES:
        files.append((f".github/copilot/prompts/{name}.prompt.md", render_prompt_file(name)))

    # OpenSpec config
    files.append(("openspec/config.yaml", render_openspec_config(project_name)))

    # Docs
    files.append(("docs/roadmap.md", doc_roadmap()))
    files.append(("docs/decision-log.md", doc_decision_log()))
    files.append((f"docs/runlog/{today_str()}_README.md", doc_runlog()))
    files.append(("docs/uiux/README.md", docs_readme("UI/UX Evidence", "每次 UI/UX 審查的輸出請放在此資料夾（以日期命名）。")))
    files.append(("docs/bugs/README.md", docs_readme("Bugs Evidence", "每個 bug 一份檔案（日期 + slug），包含重現/定位/修復/驗證/防回歸。")))
    files.append(("docs/qa/README.md", docs_readme("QA Evidence（Smoke）", "每次 bugfix 都必須產出一份 smoke 檢查清單與結果（作為 Done Gate）。")))

    # Write all files
    report: List[Tuple[str, str]] = []
    for rel, content in files:
        report.append((rel, write_text(root, rel, content, mode, backup_root)))

    writes = sum(1 for _, s in report if s == "WRITE")
    skips = sum(1 for _, s in report if s == "SKIP")

    print(f"✅ Done. mode={mode} WRITE={writes} SKIP={skips} root={root}")
    print(f"📦 Project: {project_name}")
    if backup_root:
        print(f"🗂️  Backup created at: {backup_root}")

    if not args.stitch_html:
        print("ℹ️  Hint: provide Stitch HTML to freeze style guide:")
        print("   python tools/bootstrap_copilot_workspace.py --stitch-html design/stitch/stitch.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
