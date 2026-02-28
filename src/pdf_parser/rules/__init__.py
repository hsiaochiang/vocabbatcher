"""可替換的 parser 規則介面定義。"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.pdf_parser.models import VocabEntry


@runtime_checkable
class ParserRule(Protocol):
    """Parser 規則介面。每個規則模組須實作此 Protocol。"""

    def parse_line(self, line: str) -> VocabEntry | None:
        """解析單行文字為 VocabEntry，無法解析時回傳 None。"""
        ...
