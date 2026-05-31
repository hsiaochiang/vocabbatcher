"""單字解析模組。"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

from dataclasses import dataclass, field

from src.pdf_parser.extractor import PageContent
from src.pdf_parser.models import VocabEntry
from src.pdf_parser.rules import ParserRule
from src.pdf_parser.rules.top2025 import Top2025Rule


@dataclass
class ParseResult:
    """parse_pages 的回傳結果。"""
    entries: list[VocabEntry] = field(default_factory=list)
    rejected_count: int = 0


def load_rule(rule_name: str = "top2025") -> ParserRule:
    """載入指定的 parser 規則模組。"""
    module = importlib.import_module(f"src.pdf_parser.rules.{rule_name}")
    # 尋找模組中第一個實作 ParserRule 的類別
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and attr is not ParserRule:
            try:
                instance = attr()
            except TypeError:
                continue
            if isinstance(instance, ParserRule):
                return instance
    raise ValueError(f"規則模組 '{rule_name}' 中找不到實作 ParserRule 的類別")


def parse_pages(
    pages: list[PageContent],
    rule: ParserRule | None = None,
) -> ParseResult:
    """將抽取的頁面內容解析為 VocabEntry 清單。

    Args:
        pages: 由 extractor 產出的頁面內容清單。
        rule: parser 規則實例，預設使用 Top2025Rule。

    Returns:
        ParseResult 包含解析成功的 entries 與被拒絕的行數。
    """
    if rule is None:
        rule = Top2025Rule()

    entries: list[VocabEntry] = []
    rejected_count = 0

    for page in pages:
        # 優先使用表格列解析
        if page.used_table and page.table_rows:
            for row in page.table_rows:
                if hasattr(rule, "parse_table_row"):
                    entry = rule.parse_table_row(row)  # type: ignore[attr-defined]
                else:
                    line = "\t".join(row)
                    entry = rule.parse_line(line)

                if entry is not None:
                    entry["source_page"] = page.page_number
                    entries.append(entry)
                else:
                    rejected_count += 1
        else:
            # 逐行解析純文字
            for line in page.text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                entry = rule.parse_line(line)
                if entry is not None:
                    entry["source_page"] = page.page_number
                    entries.append(entry)
                else:
                    rejected_count += 1

    return ParseResult(entries=entries, rejected_count=rejected_count)


def write_raw_json(entries: list[VocabEntry], outdir: str | Path) -> Path:
    """將解析結果寫入 vocab.raw.json。"""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "vocab.raw.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    return out_path
