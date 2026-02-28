"""top2025.pdf 專用解析規則。

PDF 表格格式（4 欄）：
  [0] word        — 英文單字
  [1] (空)        — 無資料
  [2] 年份清單    — 如 "05 06 07 08 09\n10 11 12 13 14"
  [3] ○○○         — 勾選欄（忽略）

frequency = 欄 [2] 中年份數字的個數。
pos / zh_definition / ipa 在本 PDF 中不提供，設為 None。
"""

from __future__ import annotations

import re

from src.pdf_parser.models import VocabEntry


class Top2025Rule:
    """top2025.pdf 的解析規則（表格列模式）。"""

    def parse_line(self, line: str) -> VocabEntry | None:
        """解析以 tab 分隔的表格列。

        預期格式：word\\t\\tyears\\t○○○
        """
        parts = line.split("\t")
        if len(parts) < 3:
            return None

        word = parts[0].strip()
        if not word or not re.match(r"^[a-zA-Z\-' ]+$", word):
            return None

        years_str = parts[2].strip() if len(parts) > 2 else ""
        years = re.findall(r"\d+", years_str)
        frequency = len(years) if years else None

        return VocabEntry(
            word=word,
            pos=None,
            zh_definition=None,
            frequency=frequency,
            source_page=0,  # 由 parser.py 在呼叫時填入
            ipa_us=None,
            ipa_uk=None,
        )

    def parse_table_row(self, row: list[str]) -> VocabEntry | None:
        """直接解析表格列（list 形式）。"""
        if len(row) < 3:
            return None

        word = (row[0] or "").strip()
        if not word or not re.match(r"^[a-zA-Z\-' ]+$", word):
            return None

        years_str = (row[2] or "").strip()
        years = re.findall(r"\d+", years_str)
        frequency = len(years) if years else None

        return VocabEntry(
            word=word,
            pos=None,
            zh_definition=None,
            frequency=frequency,
            source_page=0,
            ipa_us=None,
            ipa_uk=None,
        )
