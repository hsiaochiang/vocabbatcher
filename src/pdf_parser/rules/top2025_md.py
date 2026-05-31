"""top2025.md Markdown 格式專用解析器。

Markdown 格式（每個頻率章節含一個表格）：

    ## 十、出現次數：10

    | 單字 | 詞性 | 中文定義 |
    |------|------|---------|
    | **word** | [pos] | zh_definition |

frequency 從章節標題 `## ...出現次數：N` 讀取。
pos 欄位為 `[art.]` 格式，解析時去除方括號。
word 欄位為 `**word**` 粗體格式，解析時去除星號。
"""

from __future__ import annotations

import re
from pathlib import Path

from src.pdf_parser.models import VocabEntry
from src.pdf_parser.parser import ParseResult

# 匹配章節標題：## 十、出現次數：10
_FREQ_HEADER_RE = re.compile(r"^##\s+.*出現次數\s*[：:]\s*(\d+)")

# 匹配 Markdown 表格資料列（非分隔線、非表頭）
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")

# 表格分隔線
_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")

# 表頭行（含「單字」）
_HEADER_RE = re.compile(r"^\|.*單字.*\|$")


def _strip_bold(text: str) -> str:
    """去除 Markdown 粗體標記 **word**。"""
    text = text.strip()
    if text.startswith("**") and text.endswith("**"):
        return text[2:-2].strip()
    return text


def _strip_pos_brackets(text: str) -> str | None:
    """將 [art.] 格式轉為 art.，空值回傳 None。"""
    text = text.strip()
    if not text:
        return None
    # 移除方括號
    text = re.sub(r"^\[(.+)\]$", r"\1", text)
    text = text.strip()
    return text if text else None


def _clean_definition(text: str) -> str | None:
    """清理中文定義欄位。"""
    text = text.strip()
    return text if text else None


def parse_md_file(md_path: str | Path) -> ParseResult:
    """從 top2025.md 解析所有單字為 VocabEntry 清單。

    Args:
        md_path: Markdown 檔案路徑。

    Returns:
        ParseResult 包含解析成功的 entries 與被拒絕的行數。

    Raises:
        FileNotFoundError: 檔案不存在。
    """
    path = Path(md_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown 檔案不存在：{path}")

    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    entries: list[VocabEntry] = []
    rejected_count = 0
    current_frequency: int | None = None

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # 檢查是否為頻率章節標題
        freq_match = _FREQ_HEADER_RE.match(line_stripped)
        if freq_match:
            current_frequency = int(freq_match.group(1))
            continue

        # 跳過非表格行
        if not _TABLE_ROW_RE.match(line_stripped):
            continue

        # 跳過表頭和分隔線
        if _SEPARATOR_RE.match(line_stripped) or _HEADER_RE.match(line_stripped):
            continue

        # 解析表格資料列
        cells = [c.strip() for c in line_stripped.strip("|").split("|")]
        if len(cells) < 3:
            rejected_count += 1
            continue

        word = _strip_bold(cells[0])
        if not word:
            rejected_count += 1
            continue

        pos = _strip_pos_brackets(cells[1])
        zh_definition = _clean_definition(cells[2])

        # 頁碼欄位（第 4 欄，可選）
        source_page = 0
        if len(cells) >= 4:
            page_str = cells[3].strip()
            if page_str.isdigit():
                source_page = int(page_str)

        entries.append(VocabEntry(
            word=word,
            pos=pos,
            zh_definition=zh_definition,
            frequency=current_frequency,
            source_page=source_page,
            ipa_us=None,
            ipa_uk=None,
        ))

    return ParseResult(entries=entries, rejected_count=rejected_count)
