"""資料模型定義。"""

from __future__ import annotations

from typing import TypedDict


class VocabEntry(TypedDict):
    """原始解析的單字記錄。"""

    word: str
    pos: str | None
    zh_definition: str | None
    frequency: int | None
    source_page: int
    ipa_us: str | None
    ipa_uk: str | None


class CleanedEntry(TypedDict):
    """清洗後的單字記錄。"""

    word: str
    pos: str | None
    zh_definition: str | None
    frequency: int | None
    source_page: list[int]
    ipa_us: str | None
    ipa_uk: str | None
    parse_confidence: float
    issues: list[str]


class QAReport(TypedDict):
    """品質報告。"""

    total_raw: int
    total_cleaned: int
    duplicates_removed: int
    rejected_lines: int
    low_confidence_count: int
    field_completeness: dict[str, float]
    issues_summary: list[dict[str, object]]
