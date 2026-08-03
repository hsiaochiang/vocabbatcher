"""topsat.md Markdown 格式專用解析器。

Markdown 格式（每個頻率章節含一個表格）：

    ## 出現次數：5

    | 單字 | 詞性 | 中文定義 | Level | 頁碼 |
    |------|------|---------|-------|------|
    | **word** | [pos] | zh_definition | 第三級 | 12 |

frequency 從章節標題 `## 出現次數：N` 讀取。
若章節標題為範圍（例如 `10~7`），採範圍下界作為保守頻率值。
topsat.md 產生檔目前已依年份數量拆成精確頻率章節，範圍解析僅供相容。
"""

from __future__ import annotations

import re
from pathlib import Path

from src.pdf_parser.models import VocabEntry
from src.pdf_parser.parser import ParseResult

_FREQ_HEADER_RE = re.compile(r"^##\s+.*出現次數\s*[：:]\s*(\d+)(?:\s*[~～-]\s*(\d+))?")
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
_HEADER_RE = re.compile(r"^\|.*單字.*\|$")

# 學測 PDF 第 3 頁對應清單印刷第 1 頁；topsat.md 已填印刷頁碼。
PDF_TO_PRINTED_PAGE_OFFSET = 2


def _strip_bold(text: str) -> str:
    """去除 Markdown 粗體標記 **word**。"""
    text = text.strip()
    if text.startswith("**") and text.endswith("**"):
        return text[2:-2].strip()
    return text


def _strip_pos_brackets(text: str) -> str | None:
    """將 [n.] 格式轉為 n.，空值回傳 None。"""
    text = text.strip()
    if not text:
        return None
    text = re.sub(r"^\[(.+)\]$", r"\1", text).strip()
    return text if text else None


def _clean_definition(text: str) -> str | None:
    """清理中文定義欄位。"""
    text = text.strip()
    return text if text else None


def _clean_level(text: str) -> str | None:
    """清理 Level 欄位。"""
    text = text.strip()
    return text if text else None


def _parse_frequency(raw: str, lower_bound_for_range: bool = True) -> int:
    """解析頻率章節；範圍預設採下界，避免高估出現次數。"""
    parts = [int(part) for part in re.findall(r"\d+", raw)]
    if not parts:
        raise ValueError(f"無法解析出現次數：{raw}")
    if len(parts) >= 2 and lower_bound_for_range:
        return min(parts[0], parts[1])
    return parts[0]


def _to_printed_page(pdf_page_number: int) -> int:
    """將 PDF 內部頁碼轉為印刷頁碼；0 保留為未知頁。"""
    if pdf_page_number <= 0:
        return 0
    return pdf_page_number - PDF_TO_PRINTED_PAGE_OFFSET


def parse_md_file(md_path: str | Path) -> ParseResult:
    """從 topsat.md 解析所有單字為 VocabEntry 清單。"""
    path = Path(md_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown 檔案不存在：{path}")

    lines = path.read_text(encoding="utf-8").split("\n")
    entries: list[VocabEntry] = []
    rejected_count = 0
    current_frequency: int | None = None

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        freq_match = _FREQ_HEADER_RE.match(line_stripped)
        if freq_match:
            current_frequency = _parse_frequency(freq_match.group(0))
            continue

        if not _TABLE_ROW_RE.match(line_stripped):
            continue
        if _SEPARATOR_RE.match(line_stripped) or _HEADER_RE.match(line_stripped):
            continue

        cells = [cell.strip() for cell in line_stripped.strip("|").split("|")]
        if len(cells) < 5:
            rejected_count += 1
            continue

        word = _strip_bold(cells[0])
        if not word:
            rejected_count += 1
            continue

        source_page = int(cells[4]) if cells[4].isdigit() else 0

        entries.append(
            VocabEntry(
                word=word,
                pos=_strip_pos_brackets(cells[1]),
                zh_definition=_clean_definition(cells[2]),
                frequency=current_frequency,
                level=_clean_level(cells[3]),
                source_page=source_page,
                ipa_us=None,
                ipa_uk=None,
            )
        )

    return ParseResult(entries=entries, rejected_count=rejected_count)
