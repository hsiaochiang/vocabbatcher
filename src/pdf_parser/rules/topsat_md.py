"""topsat.md Markdown 格式專用解析器。

Markdown 格式（六欄明確格式，每列自帶完整資訊，不依賴章節標題狀態）：

    | **word** | [pos] | zh_definition | 第三級 | 10 | 12 |

欄位依序為：單字、詞性、中文定義、Level、出現次數、頁碼（課本印刷頁碼）。
"""

from __future__ import annotations

import re
from pathlib import Path

from src.pdf_parser.models import VocabEntry
from src.pdf_parser.parser import ParseResult

_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
_HEADER_RE = re.compile(r"^\|.*單字.*\|$")


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


def _clean_text(text: str) -> str | None:
    """清理文字欄位，空字串回傳 None。"""
    text = text.strip()
    return text if text else None


def parse_md_file(md_path: str | Path) -> ParseResult:
    """從 topsat.md 解析所有單字為 VocabEntry 清單。"""
    path = Path(md_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown 檔案不存在：{path}")

    lines = path.read_text(encoding="utf-8").split("\n")
    entries: list[VocabEntry] = []
    rejected_count = 0

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        if not _TABLE_ROW_RE.match(line_stripped):
            continue
        if _SEPARATOR_RE.match(line_stripped) or _HEADER_RE.match(line_stripped):
            continue
        if line_stripped.startswith("|--") or line_stripped.startswith("> |"):
            continue

        cells = [cell.strip() for cell in line_stripped.strip("|").split("|")]
        if len(cells) < 6:
            rejected_count += 1
            continue

        word = _strip_bold(cells[0])
        if not word:
            rejected_count += 1
            continue

        frequency = int(cells[4]) if cells[4].isdigit() else None
        source_page = int(cells[5]) if cells[5].isdigit() else 0

        entries.append(
            VocabEntry(
                word=word,
                pos=_strip_pos_brackets(cells[1]),
                zh_definition=_clean_text(cells[2]),
                frequency=frequency,
                level=_clean_text(cells[3]),
                source_page=source_page,
                ipa_us=None,
                ipa_uk=None,
            )
        )

    return ParseResult(entries=entries, rejected_count=rejected_count)
