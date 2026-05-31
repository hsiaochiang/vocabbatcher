"""parser 模組測試。"""

import json
import pytest
from src.pdf_parser.extractor import PageContent
from src.pdf_parser.models import VocabEntry
from src.pdf_parser.parser import parse_pages, load_rule, write_raw_json, ParseResult
from src.pdf_parser.rules.top2025 import Top2025Rule


class TestTop2025Rule:
    def test_parse_complete_line(self):
        rule = Top2025Rule()
        result = rule.parse_line("apple\t\t05 06 07\t○○○")
        assert result is not None
        assert result["word"] == "apple"
        assert result["frequency"] == 3

    def test_parse_line_with_ipa(self):
        """音標不在 top2025 PDF 中，但確認不會因額外文字出錯。"""
        rule = Top2025Rule()
        result = rule.parse_line("run\t\t05 06 07 08 09\t○○○")
        assert result is not None
        assert result["word"] == "run"
        assert result["frequency"] == 5
        assert result["ipa_us"] is None

    def test_parse_unparseable_line(self):
        rule = Top2025Rule()
        assert rule.parse_line("Copyright © 2025 Top Academy") is None
        assert rule.parse_line("") is None
        assert rule.parse_line("○○○") is None

    def test_parse_table_row(self):
        rule = Top2025Rule()
        result = rule.parse_table_row(["book", "", "05 06 07\n10 11 12", "○○○"])
        assert result is not None
        assert result["word"] == "book"
        assert result["frequency"] == 6


class TestParsePages:
    def test_table_pages(self):
        pages = [
            PageContent(
                page_number=3,
                text="apple\t\t05 06 07\t○○○",
                table_rows=[["apple", "", "05 06 07", "○○○"]],
                used_table=True,
            ),
        ]
        result = parse_pages(pages)
        assert len(result.entries) == 1
        assert result.entries[0]["word"] == "apple"
        assert result.entries[0]["source_page"] == 3

    def test_text_pages(self):
        pages = [
            PageContent(
                page_number=5,
                text="run\t\t05 06\t○○○\n\nCopyright line",
            ),
        ]
        result = parse_pages(pages)
        assert len(result.entries) == 1
        assert result.entries[0]["word"] == "run"
        assert result.rejected_count == 1  # "Copyright line" rejected

    def test_custom_rule(self):
        class DummyRule:
            def parse_line(self, line: str) -> VocabEntry | None:
                if line.startswith("WORD:"):
                    return VocabEntry(
                        word=line[5:].strip(),
                        pos=None,
                        zh_definition=None,
                        frequency=None,
                        source_page=0,
                        ipa_us=None,
                        ipa_uk=None,
                    )
                return None

        pages = [PageContent(page_number=1, text="WORD:test\ngarbage")]
        result = parse_pages(pages, rule=DummyRule())
        assert len(result.entries) == 1
        assert result.entries[0]["word"] == "test"
        assert result.rejected_count == 1  # "garbage" rejected


class TestWriteRawJson:
    def test_write(self, tmp_outdir):
        entries = [
            VocabEntry(
                word="apple", pos=None, zh_definition=None,
                frequency=3, source_page=5, ipa_us=None, ipa_uk=None,
            )
        ]
        path = write_raw_json(entries, tmp_outdir)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["word"] == "apple"
