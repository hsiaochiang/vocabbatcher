from __future__ import annotations

"""
tools/bootstrap_antigravity_workspace.py

目標（解決兩個最耗時的痛點）
1) UI/UX 一致性：把「按鈕/字級/間距/色彩」從逐頁人工微調，改成「有規範、可對照、可 Freeze」。
2) 反覆除錯：把「修了還錯/改錯檔」改成「可重現→定位→修復→驗證→防回歸」的閉環，並強制留下證據。

核心策略（從無到有的正確順序）
- 先 Stitch 產出 UI 基準（HTML）→ 產出 Style Contract → UI/UX 盤點 → Style Freeze → 才開始大量寫 code。

輸出（repo 內會生成）
- .agent/（Antigravity 入口）：rules / workflows / skills / .agent/AGENTS.md
- docs/（證據與追蹤）：roadmap / decision-log / runlog / uiux / bugs / qa

⚠️預設行為（你選擇的 B 模式）
- **預設 = overwrite（完整覆蓋重建）**
- 覆寫前會自動備份到：`.agent/_bootstrap_backups/<timestamp>/`

用法
  # 1) 建議：先匯入 Stitch HTML（可選但強烈建議）
  python tools/bootstrap_antigravity_workspace.py --stitch-html design/stitch/stitch.html

  # 2) 只做健檢（不寫檔）
  python tools/bootstrap_antigravity_workspace.py --verify-only

參數
  --root           repo root（預設：本檔位於 tools/ 時，使用上一層）
  --stitch-html    Stitch 匯出的 html 路徑（可選）
  --mode           overwrite|safe（預設 overwrite）
  --no-backup      關閉自動備份（不建議）
  --verify-only    只做 workspace 健檢（不寫檔）
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
    """
    將既有檔案備份到 backup_root，保留相對路徑。
    """
    for rel in rel_paths:
        p = root / rel
        if p.exists() and p.is_file():
            _copy2(p, backup_root / rel)

def backup_tree(root: Path, rel_dir: str, backup_root: Path) -> None:
    p = root / rel_dir
    if not p.exists():
        return
    for fp in p.rglob("*"):
        # prevent recursive backup of backup folder
        if "_bootstrap_backups" in fp.parts:
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
# Minimal frontmatter utilities (Antigravity UI "Description")
# ---------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def parse_frontmatter(md: str) -> Dict[str, str]:
    m = FRONTMATTER_RE.match(md)
    if not m:
        return {}
    block = m.group(1)
    out: Dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out

def ensure_frontmatter(md: str, description: str) -> str:
    """
    - 若沒有 frontmatter：新增
    - 若有 frontmatter：
      - description 缺少 → 補上
      - description 存在但空白 → 置換成給定 description
    """
    description = (description or "").strip().replace("\n", " ")
    if len(description) > 240:
        description = description[:237] + "..."

    if md.lstrip().startswith("---"):
        m = FRONTMATTER_RE.match(md)
        if m:
            block = m.group(1)
            lines = block.splitlines()
            found = False
            new_lines: List[str] = []
            for line in lines:
                if re.match(r"^\s*description\s*:", line):
                    found = True
                    key, _ = line.split(":", 1)
                    val = _.strip()
                    if not val:
                        new_lines.append(f"{key}: {description}")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(f"description: {description}")
            if not any(re.match(r"^\s*created\s*:", ln) for ln in new_lines):
                new_lines.append(f"created: {today_str()}")
            new_block = "\n".join(new_lines).rstrip() + "\n"
            return md.replace(m.group(0), f"---\n{new_block}---\n\n", 1)

    # no frontmatter
    return f"---\ndescription: {description}\ncreated: {today_str()}\n---\n\n{md}"

def wf_md(name: str, description: str, body: str) -> str:
    return ensure_frontmatter(f"# /{name}\n\n{body.strip()}\n", description)

def rule_md(description: str, body: str) -> str:
    return ensure_frontmatter(body.strip() + "\n", description)

def skill_md(description: str, body: str) -> str:
    return ensure_frontmatter(body.strip() + "\n", description)


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
# Render: rules
# ---------------------------

def rule_00_instructions() -> str:
    return rule_md(
        "總規則（語言、可上網查、文件留痕、每次 implement 後要 commit/push）。",
        """
# 00-instructions.zh-TW（工作規則）

## 基本輸出規則（強制）
- 過程中要給我看的內容：**一律使用正體中文**回覆與說明
- 過程中你可以上網找適合的工具或套件來使用（請附來源連結或文件名稱）
- 對我提供的文件：以中文為主；若必須用英文，請在「備註」區用中文說明我需要知道的細節

## 治理與留痕（強制）
- 當我們討論的結論：必須寫入文件（roadmap / decision-log / runlog / UIUX / bugs / QA）
- 我會常問「目前在哪個階段」：請維持 `docs/roadmap.md` 最新
- 每次 Implement 後：請把變更加入版本控制並推送到遠端（add/commit/push）
  - commit log：**繁體中文**，並包含 What / Why / Impact / Evidence

## Smallest Safe Change
- 僅做必要修改；可共用的要共用化
- 沒有證據不得宣稱「已修好」或「已符合」
        """,
    )

def rule_01_session_template() -> str:
    return rule_md(
        "每次開工必貼模板：強制讀規範 + 先跑 /preflight /status + 要有啟用證據。",
        r"""
# 01-session-template.zh-TW（每次開工必貼的提示詞模板）

> 目的：確保 rules / workflows / skills **真的被讀取與使用**，並留下「可驗證」的啟用證據。

## 你每次開新任務請直接貼這段（可複製）
```text
你是我的 Antigravity 工作夥伴。請先讀取：
1) .agent/AGENTS.md
2) .agent/rules/*（00/01/10/20/30/35/36/40）

請先輸出【啟用證據】：
- 已讀入的 rules 清單（檔名 + 你抓到的 1 句要點）
- 本次會使用的 workflows（至少 /preflight、/status；若涉及 UI/UX/bug 也列出）
- 本次會使用的 skills（ui-designer / ux-fullstack-engineer / debug-sheriff / smoke-tester / git-steward / scribe / openspec-conductor）

然後依序執行：
1) /preflight
2) /status（回報目前階段、下一步、阻塞、證據檔案位置）

規則：
- 任何規格/取捨/Freeze 變更，都必須先 /log-decision（原因→影響→驗收→證據）
- 若要改 UI：必須引用 10-style-guide.md；若要改規範，先 /log-decision
```
        """,
    )

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

    return rule_md(
        "Style Contract：字體/顏色/間距/按鈕/狀態 + Freeze 機制（避免 UI 返工）。",
        f"""
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
- UI 確認 OK 後：用 /log-decision 記錄「Style Freeze」決策（原因→影響→驗收→證據）
- Freeze 後若需要改 UI：必須先 /log-decision（原因→影響→驗收）才能動

## 6) 你要怎麼「使用」這份規範？
- 匯入 Stitch：/stitch-import（或重新跑 bootstrap --stitch-html）
- 做 UI 盤點：/ui-review（使用 ui-designer skill，輸出差異與修正計畫）
- Freeze：/log-decision（寫入 docs/decision-log + docs/decisions）
        """,
    )

def rule_20_ux_flow() -> str:
    return rule_md(
        "UX Flow Contract：盤點所有流程與狀態，定義 DoD，避免流程缺口造成返工。",
        """
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
        """,
    )

def rule_30_debug_contract() -> str:
    return rule_md(
        "Debug Contract：除錯閉環（可重現→定位→修復→驗證→防回歸）。",
        """
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
        """,
    )

def rule_35_quality_gate() -> str:
    return rule_md(
        "Quality Gate：沒有 evidence/驗收/Smoke 就不能說 Done（避免按一下就錯）。",
        """
# 35-quality-gate（完成宣告門檻 / Done Gate）

> 目的：處理你常遇到的狀況：agent 說「完成可用了」，但你一按就錯。

## Done Gate（缺一不可）
- UI 相關修改：
  - 必須更新 `docs/uiux/<date>_ui-review.md`（差異→修正→驗收→證據）
- UX 流程修改：
  - 必須更新 `docs/uiux/<date>_ux-review.md`（flow/狀態/DoD）
- Bug 修復：
  - 必須產出 `docs/bugs/<date>_<slug>.md`（重現/定位/修復/驗證/防回歸）
  - 必須產出 `docs/qa/<date>_smoke.md`（最小 smoke checklist + 結果）

## 若未通過 Done Gate
- 不得宣稱 Done
- 必須補齊 evidence 後再回報
        """,
    )

def rule_36_scope_guard() -> str:
    return rule_md(
        "Scope Guard：限制一次改動範圍，超出就先 log-decision，避免大改引入新 bug/UI 漂移。",
        """
# 36-scope-guard（範圍護欄 / Smallest Safe Change 強化）

## 目標
- 避免為了修一個 bug/調一個 UI，把其它頁面或流程一起弄壞（引入新 bug）
- 確保每次改動可回溯、可驗收、可快速回滾

## 觸發條件（遇到就先停、先 /log-decision）
- 一次改動超過 5 個檔案
- 需要改動 tokens / Style Contract（10-style-guide）
- 沒有重現步驟卻想大改
- 同一問題第 3 次仍未收斂（代表需要換策略）

## 拆解策略
- 先把「最短修復」做出來 → 先通過 smoke → 再做重構/美化
        """,
    )

def rule_40_activation_proof() -> str:
    return rule_md(
        "啟用證據規則：每次回覆都要列 rules/workflows/skills + evidence 位置，缺少則視為不合格。",
        """
# 40-activation-proof（啟用證據規則）

> 目的：避免「它說修好了，但其實沒改到點上」。

## 強制輸出：每次回覆都要包含【啟用證據】段落
- 已讀入的 rules 清單（至少列出檔名）
- 本次使用的 workflow（例如 /preflight / ui-review / bugfix）
- 本次使用的 skill（例如 ui-designer / debug-sheriff / smoke-tester）
- 產出的 evidence 位置（docs/runlog、docs/uiux、docs/bugs、docs/qa、docs/decisions、git diff / 測試輸出）

## 若缺少啟用證據 → 視為不合格
- 你可以直接回覆：「請補上啟用證據段落，並更新 runlog」
        """,
    )


# ---------------------------
# Render: skills
# ---------------------------

def skill_ui_designer() -> str:
    return skill_md(
        "UI 前端設計師：對照 Style Contract + Stitch evidence，輸出差異清單與可執行修正計畫（含驗收）。",
        r"""
# Skill: ui-designer（UI 前端設計師）

## 任務目標
把「每頁都要慢慢調」變成「有規範可對照、一次修到位」，並把修正計畫做成可交付給 coding agent 的清單。

## 依據（Evidence）
- `.agent/rules/10-style-guide.md`（唯一 UI 規範）
- `design/stitch/stitch.html`（Stitch evidence；或補充截圖/錄影/URL）
- 目標頁面/元件檔案（repo 內）

## 輸出（必交付）
- `docs/uiux/<date>_ui-review.md`，內容必含：
  1) **Findings（差異清單）**：逐項列「現況 vs 規範」＋引用規範章節
  2) **Patch Plan（修正計畫）**：可直接交給 coding agent 的修改清單（檔案/元件/範圍）
  3) **Acceptance（驗收）**：如何驗收（視覺/互動/狀態）
  4) **Evidence（證據）**：相關 diff、截圖、或 runlog 位置

## 執行步驟（建議順序）
1) 先讀 style guide，列出「可凍結基準」：字級、按鈕高度、卡片 padding、主色/次色、表單狀態
2) 逐頁比對（或抽 3~5 個代表頁）→ 先抓最大的不一致（會造成“看起來不像同一套系統”）
3) 只做 Smallest Safe Change：先把 tokens/共用元件拉齊，再調個別頁面
4) 若發現規範本身要改：停止，先 /log-decision（原因→影響→驗收→證據）

## 禁止事項
- 未引用 style guide 就做「主觀美化」
- 一次改太多頁面造成漂移（觸發 36-scope-guard）
        """,
    )

def skill_ux_fullstack_engineer() -> str:
    return skill_md(
        "UX 全端工程師：盤點流程與狀態、定義動線與 DoD，避免流程缺口造成返工。",
        r"""
# Skill: ux-fullstack-engineer（UX 全端工程師）

## 任務目標
把操作流程一次盤清楚，讓使用者永遠知道「我在哪、下一步是什麼」，並可作為驗收基準。

## 依據（Evidence）
- `.agent/rules/20-ux-flow.md`
- 現有 UI（Stitch/前端頁面）
- 現有需求（若有 OpenSpec specs）

## 輸出（必交付）
- `docs/uiux/<date>_ux-review.md`，內容必含：
  1) **Flow List**：以使用者目標命名（5~15 條）
  2) 每個 Flow 的 **Steps / UI Reaction / States**
  3) **Edge Cases**：error/permission/not found/timeout
  4) **DoD（驗收條件）**
  5) **Open Questions**（需要你決策的點）

## 執行步驟
1) 先列 top flows（先以你最常 demo/最常用的為優先）
2) 每個 flow 強制補狀態：loading/empty/error/success
3) 決定最小可用：哪些 flow 必須在 MVP 完成、哪些可延後
        """,
    )

def skill_debug_sheriff() -> str:
    return skill_md(
        "除錯警長：以閉環方式修 bug，強制留下重現/驗證/防回歸證據，避免反覆修錯檔。",
        r"""
# Skill: debug-sheriff（除錯警長）

## 任務目標
把 bug 修復變成閉環：可重現→定位→修復→驗證→防回歸（並落檔留證據）。

## 依據（Evidence）
- `.agent/rules/30-debug-contract.md`
- 錯誤訊息/stack trace/console log
- 相關頁面與程式碼（檔案路徑）

## 輸出（必交付）
- `docs/bugs/<date>_<slug>.md`，內容必含：
  1) Repro（最短重現步驟）
  2) Root Cause（含定位證據：log/diff）
  3) Fix（改了哪些檔案，為何是這裡）
  4) Verify（如何證明修好）
  5) Regression（防回歸：最小測試/檢查項）
- 需要時：交由 `smoke-tester` 產出 `docs/qa/<date>_smoke.md`

## 禁止事項
- 沒有重現步驟就大改
- 沒有驗證證據就結案
        """,
    )

def skill_smoke_tester() -> str:
    return skill_md(
        "Smoke Tester：最小冒煙測試清單（點得到、走得通、不會立刻報錯），作為 Done Gate 證據。",
        r"""
# Skill: smoke-tester（冒煙測試／最小驗收）

## 任務目標
避免「agent 說完成可用了，但你一按就錯」；用最小測試快速擋掉明顯回歸。

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
        """,
    )

def skill_openspec_conductor() -> str:
    return skill_md(
        "OpenSpec 指揮官：引導 spec→tasks→implement 的節奏，避免先寫 code 造成返工，並強制 evidence。",
        r"""
# Skill: openspec-conductor（OpenSpec 指揮官）

## 任務目標
用 OpenSpec 把需求→規格→任務→實作走完；每一步都可驗收、可留證據。

## 依據
- OpenSpec 專案內 specs/tasks（依你的版本）
- `docs/roadmap.md`（目前階段）
- `docs/runlog/<date>_README.md`（當日進度）

## 輸出
- 下一步該做什麼（包含你要下的指令/動作）
- 規格缺口清單（缺一不可的驗收點）
- evidence 應落檔的位置（runlog/decision/bugs/qa）
        """,
    )

def skill_scribe() -> str:
    return skill_md(
        "Scribe：把每次 session 的成果整理成可投影片化素材（problem→method→demo→before/after→lessons）。",
        r"""
# Skill: scribe（記錄官／投影片素材整理）

## 任務目標
把過程整理成可投影片化素材，不依賴冗長對話匯出。

## Inputs
- 你貼 5~10 行本次做了什麼（或 git diff --stat）
- 重要決策（docs/decisions）
- 重要 bug 與修復證據（docs/bugs、docs/qa）

## Outputs（建議）
- `experience/<YYYY-MM>/slides_<date>_talk-outline.md`
- 重點素材：問題/方法/對照/示範步驟/踩雷與修正
        """,
    )

def skill_git_steward() -> str:
    return skill_md(
        "Git Steward：繁中 commit log（What/Why/Impact/Evidence）+ add/commit/push 指令，確保可追溯。",
        r"""
# Skill: git-steward（版本控管管家）

## 任務目標
把每次變更都變成可追溯證據，降低「做了但找不到改哪」的風險。

## Outputs
- 建議的 git 指令序列
- commit message（繁中，含 What/Why/Impact/Evidence）
- 若有風險：提醒需要 review / 分支策略

## Commit Template（繁中）
- What：做了什麼（具體檔案/功能）
- Why：為什麼要做
- Impact：對使用者/系統的影響
- Evidence：如何驗證（測試/截圖/log/文件）
        """,
    )


# ---------------------------
# Render: workflows
# ---------------------------

def wf_preflight() -> str:
    return wf_md(
        "preflight",
        "開工前健檢：檔案齊全、Style 狀態、Description 欄位、runlog 初始化。",
        f"""
流程：
1) 檢查必要檔案是否存在：`.agent/AGENTS.md`、`.agent/rules/*`、`.agent/workflows/*`、`.agent/skills/*`
2) 檢查 `10-style-guide.md` 狀態（PENDING/FROZEN）
3) Lint：workflows/skills 的 frontmatter.description 不得為空（避免 UI 空白）
4) 更新本日 runlog：`docs/runlog/{today_str()}_README.md`

建議搭配（Terminal）：
- `python tools/bootstrap_antigravity_workspace.py --verify-only`
        """,
    )

def wf_ui_review() -> str:
    return wf_md(
        "ui-review",
        "UI 一致性審查：對照 Style Guide + Stitch evidence，輸出差異與修正計畫並落檔。",
        """
目標：針對字級、顏色、間距、按鈕尺寸、元件狀態做一致性盤點並提出可執行修正清單。

流程：
1) 讀 `10-style-guide.md`（若 PENDING，先 /stitch-import）
2) 使用 `ui-designer` skill 產出 `docs/uiux/<date>_ui-review.md`
3) 若涉及改規範：先 /log-decision
4) 若改動範圍過大：遵守 36-scope-guard 拆解
        """,
    )

def wf_ux_review() -> str:
    return wf_md(
        "ux-review",
        "UX 流程盤點：列出 flows 與狀態，定義 DoD，輸出可驗收動線並落檔。",
        """
目標：盤點主要 flows（happy path/edge cases），補齊 loading/empty/error/success 狀態，並定義 DoD。

流程：
1) 使用 `ux-fullstack-engineer` 產出 `docs/uiux/<date>_ux-review.md`
2) 把 MVP vs 延後項目寫清楚（避免 scope 漂移）
        """,
    )

def wf_bugfix() -> str:
    return wf_md(
        "bugfix",
        "除錯閉環：重現→定位→修復→驗證→防回歸，並強制 smoke evidence（Done Gate）。",
        """
依據：`30-debug-contract.md` + `35-quality-gate.md`

流程：
1) 使用 `debug-sheriff` 產出 `docs/bugs/<date>_<slug>.md`
2) 使用 `smoke-tester` 產出 `docs/qa/<date>_smoke.md`
3) 若 smoke 失敗：回到 bugfix 文檔補齊、再跑 smoke
4) 完成後再回報（禁止口頭 Done）

產出：
- `docs/bugs/<date>_<slug>.md`
- `docs/qa/<date>_smoke.md`
        """,
    )

def wf_stitch_import() -> str:
    return wf_md(
        "stitch-import",
        "匯入 Stitch HTML，更新 10-style-guide，讓 UI 規範可落地並可 Freeze。",
        """
流程：
1) 確認 `design/stitch/stitch.html` 存在
2) 重新跑 bootstrap：
   - `python tools/bootstrap_antigravity_workspace.py --stitch-html design/stitch/stitch.html`
3) 確認 `10-style-guide.md` 狀態為 FROZEN（或至少具備可用 tokens）
        """,
    )

def wf_commit_push() -> str:
    return wf_md(
        "commit-push",
        "標準化 git add/commit/push，要求繁中 commit log（含 What/Why/Impact/Evidence）。",
        """
流程：
1) `git status`
2) `git add -A`
3) `git commit`（繁中，含 What/Why/Impact/Evidence）
4) `git push`

注意：若你開啟 terminal 自動執行，請確保每一步可 review。
        """,
    )

def wf_log_decision() -> str:
    return wf_md(
        "log-decision",
        "決策留痕：原因→影響→驗收→證據（含 Style Freeze/規範變更/重大取捨）。",
        """
流程：
1) 更新 `docs/decision-log.md`（摘要）
2) 新增 `docs/decisions/<date>_<slug>.md`（詳細：原因→影響→驗收→證據）
3) 若涉及 Style Freeze：同步在 `10-style-guide.md` 或 decision 中標記
        """,
    )

def wf_status() -> str:
    return wf_md(
        "status",
        "進度回報：階段/下一步/阻塞/證據位置，並更新 roadmap 與 runlog（強制啟用證據）。",
        f"""
流程：
1) 以 3~7 行回報：目前階段 / 下一步 / 阻塞
2) 更新 `docs/roadmap.md`（若有變動）
3) 更新 `docs/runlog/{today_str()}_README.md`（附 evidence 路徑）

強制：回覆需包含【啟用證據】（見 40-activation-proof）。
        """,
    )

def wf_session_close() -> str:
    return wf_md(
        "session-close",
        "收尾整理：把 session 變成可投影片化素材（problem→method→demo→lessons）。",
        """
流程：
1) 摘要：本次解決的痛點（UI 一致性 / 反覆除錯）
2) 方法：本次用到的 rules/workflows/skills、Stitch、OpenSpec
3) Before/After：返工下降的證據（runlog/decision/bugs/qa）
4) Demo steps：3~5 分鐘展示流程
5) Lessons learned：踩雷與修正

產出：
- `experience/<YYYY-MM>/slides_<date>_talk-outline.md`
        """,
    )


# ---------------------------
# Render: entries + docs
# ---------------------------

def agent_entry() -> str:
    return ensure_frontmatter(
        """
# .agent/AGENTS.md（Antigravity 啟用入口）

> 本檔案給 Antigravity 作為「優先讀取」的入口。  
> 注意：OpenSpec 等工具可能會在 repo 根目錄產生/覆寫 `AGENTS.md`，因此入口固定放在 `.agent/AGENTS.md`。

## 必讀順序（強制）
1) `.agent/rules/00-instructions.zh-TW.md`
2) `.agent/rules/01-session-template.zh-TW.md`
3) `.agent/rules/10-style-guide.md`
4) `.agent/rules/20-ux-flow.md`
5) `.agent/rules/30-debug-contract.md`
6) `.agent/rules/35-quality-gate.md`
7) `.agent/rules/36-scope-guard.md`
8) `.agent/rules/40-activation-proof.md`

## 固定開工流程（建議）
- `/preflight` → `/status`
- UI：`/stitch-import`（若需）→ `/ui-review` → `/log-decision`（Freeze）
- 流程：`/ux-review`
- 除錯：`/bugfix`（含 smoke）
- 每次 implement 後：`/commit-push`
- 每次 session 結束：`/session-close`

## Skills（角色分工）
- ui-designer
- ux-fullstack-engineer
- debug-sheriff
- smoke-tester
- openspec-conductor
- scribe
- git-steward
        """,
        "Antigravity 入口：必讀順序、固定流程、可用 skills/workflows。",
    )

def root_agents_stub() -> str:
    return ensure_frontmatter(
        """
# AGENTS.md（根目錄：導引 stub）

注意：OpenSpec 等工具可能會在根目錄自動產生/覆寫本檔。  
本 repo 的 Antigravity 啟用入口請看：`.agent/AGENTS.md`（必讀）。
        """,
        "root stub：導引到 .agent/AGENTS.md",
    )

def root_instructions_stub() -> str:
    return ensure_frontmatter(
        """
# instructions.md（最小入口）

請優先閱讀：`.agent/AGENTS.md` 與 `.agent/rules/00-instructions.zh-TW.md`
        """,
        "最小入口：導引到 .agent/AGENTS.md",
    )

def doc_roadmap() -> str:
    return ensure_frontmatter(
        """
# Roadmap

> 用來回答：「目前在哪個階段？下一步是什麼？」

## 階段（可自行增修）
- S0：Stitch UI 基準（HTML）
- S1：Bootstrap workspace（rules/skills/workflows）
- S2：UI/UX 盤點 + Style Freeze
- S3：OpenSpec 規格（spec→tasks）
- S4：Implement
- S5：Bugfix 收斂 + Smoke + 回歸驗證
- S6：整理投影片素材（分享）

## 目前狀態
- Current：
- Next：
- Blockers：
- Evidence：
        """,
        "專案階段與狀態追蹤（/status 會更新）。",
    )

def doc_decision_log() -> str:
    return ensure_frontmatter(
        """
# Decision Log（決策紀錄）

> 所有取捨與規格變更都要留痕（尤其是 Style Freeze / 規範變更）。

| Date | Decision | Why | Impact | Evidence |
|---|---|---|---|---|
        """,
        "決策留痕（含 Style Freeze/規格變更/重大取捨）。",
    )

def doc_runlog(today_iso: str) -> str:
    return ensure_frontmatter(
        f"""
# Runlog {today_iso}

## 今日目標
-

## 今日進度
-

## 阻塞
-

## 證據（links / paths）
-
        """,
        "每日 runlog：目標/進度/阻塞/證據（/preflight 會初始化）。",
    )

def docs_readme_uiux() -> str:
    return ensure_frontmatter(
        """
# UI/UX Evidence

- 每次 /ui-review 與 /ux-review 的輸出請放在此資料夾（以日期命名）。
        """,
        "UI/UX 盤點輸出位置（evidence）。",
    )

def docs_readme_bugs() -> str:
    return ensure_frontmatter(
        """
# Bugs Evidence

- 每個 bug 一份檔案（日期 + slug），包含重現/定位/修復/驗證/防回歸。
        """,
        "Bugfix 輸出位置（evidence）。",
    )

def docs_readme_qa() -> str:
    return ensure_frontmatter(
        """
# QA Evidence（Smoke）

- 每次 /bugfix 都必須產出一份 smoke 檢查清單與結果（作為 Done Gate）。
        """,
        "QA/Smoke evidence 位置。",
    )


# ---------------------------
# Verify-only (workspace health check)
# ---------------------------

def verify_workspace(root: Path) -> int:
    required = [
        root / ".agent" / "AGENTS.md",
        root / ".agent" / "rules" / "00-instructions.zh-TW.md",
        root / ".agent" / "rules" / "10-style-guide.md",
        root / ".agent" / "workflows" / "preflight.md",
        root / ".agent" / "workflows" / "ui-review.md",
        root / ".agent" / "workflows" / "ux-review.md",
        root / ".agent" / "workflows" / "bugfix.md",
        root / ".agent" / "skills" / "ui-designer" / "SKILL.md",
    ]
    missing = [p for p in required if not p.exists()]
    if missing:
        print("❌ Missing required files:")
        for p in missing:
            print(" -", p.relative_to(root))
        return 2

    def lint_desc(dirp: Path, globpat: str) -> List[Path]:
        bad: List[Path] = []
        for p in sorted(dirp.glob(globpat)):
            md = p.read_text(encoding="utf-8", errors="ignore")
            fm = parse_frontmatter(md)
            if not fm.get("description") or fm.get("description") == "":
                bad.append(p)
        return bad

    bad_wf = lint_desc(root / ".agent" / "workflows", "*.md")
    if bad_wf:
        print("❌ Workflows missing/empty frontmatter.description:")
        for p in bad_wf:
            print(" -", p.relative_to(root))
        return 3

    bad_rules = lint_desc(root / ".agent" / "rules", "*.md")
    if bad_rules:
        print("❌ Rules missing/empty frontmatter.description:")
        for p in bad_rules:
            print(" -", p.relative_to(root))
        return 4

    bad_skills = lint_desc(root / ".agent" / "skills" / "ui-designer", "SKILL.md")
    # also lint all skills
    for sd in (root / ".agent" / "skills").glob("*"):
        if sd.is_dir():
            bad_skills += lint_desc(sd, "SKILL.md")
    # dedupe
    bad_skills = sorted(set(bad_skills))
    if bad_skills:
        print("❌ Skills missing/empty frontmatter.description:")
        for p in bad_skills:
            print(" -", p.relative_to(root))
        return 5

    sg = (root / ".agent" / "rules" / "10-style-guide.md").read_text(encoding="utf-8", errors="ignore")
    if "狀態：**PENDING**" in sg:
        print("⚠️ Style guide is PENDING. Provide Stitch HTML and run bootstrap with --stitch-html, or use /stitch-import.")
    else:
        print("✅ Style guide looks ready (not PENDING).")

    print("✅ Workspace verify passed.")
    return 0


# ---------------------------
# Main
# ---------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="", help="repo root (default: parent of tools/)")
    parser.add_argument("--stitch-html", default="", help="path to Stitch exported html (optional)")
    parser.add_argument("--mode", choices=["overwrite", "safe"], default="overwrite", help="default: overwrite (B)")
    parser.add_argument("--no-backup", action="store_true", help="disable auto backup before overwrite")
    parser.add_argument("--verify-only", action="store_true", help="verify workspace only (no writes)")
    args = parser.parse_args()

    here = Path(__file__).resolve()
    default_root = here.parents[1] if here.parent.name == "tools" else Path(".").resolve()
    root = Path(args.root).resolve() if args.root else default_root

    if args.verify_only:
        return verify_workspace(root)

    mode: str = args.mode
    backup_root: Optional[Path] = None
    if _should_overwrite(mode) and not args.no_backup:
        backup_root = root / ".agent" / "_bootstrap_backups" / ts_str()
        ensure_dir(backup_root)
        # backup entire .agent if exists + key root files + docs
        backup_tree(root, ".agent", backup_root)
        backup_paths(root, ["AGENTS.md", "instructions.md", "docs/roadmap.md", "docs/decision-log.md"], backup_root)

    # dirs
    for d in [
        root / ".agent/rules",
        root / ".agent/workflows",
        root / ".agent/skills",
        root / "docs/decisions",
        root / "docs/uiux",
        root / "docs/bugs",
        root / "docs/qa",
        root / "docs/runlog",
        root / "design/stitch",
        root / "experience",
    ]:
        ensure_dir(d)

    # stitch: copy into canonical path + tokens
    tokens: Optional[StitchTokens] = None
    if args.stitch_html:
        stitch_path = Path(args.stitch_html).resolve()
        if stitch_path.exists():
            copy_file(root, stitch_path, "design/stitch/stitch.html", mode, backup_root)
            try:
                tokens = extract_tokens_from_stitch_html(stitch_path)
            except Exception as e:
                print("⚠️ Failed to extract tokens from Stitch HTML:", e)

    # write rules
    rules: List[Tuple[str, str]] = [
        (".agent/rules/00-instructions.zh-TW.md", rule_00_instructions()),
        (".agent/rules/01-session-template.zh-TW.md", rule_01_session_template()),
        (".agent/rules/10-style-guide.md", rule_10_style_guide(tokens)),
        (".agent/rules/20-ux-flow.md", rule_20_ux_flow()),
        (".agent/rules/30-debug-contract.md", rule_30_debug_contract()),
        (".agent/rules/35-quality-gate.md", rule_35_quality_gate()),
        (".agent/rules/36-scope-guard.md", rule_36_scope_guard()),
        (".agent/rules/40-activation-proof.md", rule_40_activation_proof()),
    ]

    workflows: List[Tuple[str, str]] = [
        (".agent/workflows/preflight.md", wf_preflight()),
        (".agent/workflows/ui-review.md", wf_ui_review()),
        (".agent/workflows/ux-review.md", wf_ux_review()),
        (".agent/workflows/bugfix.md", wf_bugfix()),
        (".agent/workflows/stitch-import.md", wf_stitch_import()),
        (".agent/workflows/commit-push.md", wf_commit_push()),
        (".agent/workflows/log-decision.md", wf_log_decision()),
        (".agent/workflows/status.md", wf_status()),
        (".agent/workflows/session-close.md", wf_session_close()),
    ]

    skills: List[Tuple[str, str]] = [
        (".agent/skills/ui-designer/SKILL.md", skill_ui_designer()),
        (".agent/skills/ux-fullstack-engineer/SKILL.md", skill_ux_fullstack_engineer()),
        (".agent/skills/debug-sheriff/SKILL.md", skill_debug_sheriff()),
        (".agent/skills/smoke-tester/SKILL.md", skill_smoke_tester()),
        (".agent/skills/openspec-conductor/SKILL.md", skill_openspec_conductor()),
        (".agent/skills/scribe/SKILL.md", skill_scribe()),
        (".agent/skills/git-steward/SKILL.md", skill_git_steward()),
    ]

    entries: List[Tuple[str, str]] = [
        (".agent/AGENTS.md", agent_entry()),
        ("AGENTS.md", root_agents_stub()),
        ("instructions.md", root_instructions_stub()),
        ("docs/roadmap.md", doc_roadmap()),
        ("docs/decision-log.md", doc_decision_log()),
        (f"docs/runlog/{today_str()}_README.md", doc_runlog(today_str())),
        ("docs/uiux/README.md", docs_readme_uiux()),
        ("docs/bugs/README.md", docs_readme_bugs()),
        ("docs/qa/README.md", docs_readme_qa()),
    ]

    report: List[Tuple[str, str]] = []
    for rel, content in rules:
        report.append((rel, write_text(root, rel, content, mode, backup_root)))
    for rel, content in workflows:
        report.append((rel, write_text(root, rel, content, mode, backup_root)))
    for rel, content in skills:
        report.append((rel, write_text(root, rel, content, mode, backup_root)))
    for rel, content in entries:
        report.append((rel, write_text(root, rel, content, mode, backup_root)))

    writes = sum(1 for _, s in report if s == "WRITE")
    skips = sum(1 for _, s in report if s == "SKIP")

    print(f"✅ Done. mode={mode} WRITE={writes} SKIP={skips} root={root}")
    if backup_root:
        print(f"🗂️ Backup created at: {backup_root}")

    if not args.stitch_html:
        print("ℹ️ Hint: provide Stitch HTML to freeze style guide:")
        print("   python tools/bootstrap_antigravity_workspace.py --stitch-html design/stitch/stitch.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
