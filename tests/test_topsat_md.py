"""topsat_md Markdown 解析器測試。"""

import pytest

from src.pdf_parser.rules.topsat_md import (
    PDF_TO_PRINTED_PAGE_OFFSET,
    _clean_definition,
    _clean_level,
    _parse_frequency,
    _strip_bold,
    _strip_pos_brackets,
    _to_printed_page,
    parse_md_file,
)


class TestHelpers:
    def test_strip_bold(self):
        assert _strip_bold("**unique**") == "unique"
        assert _strip_bold("unique") == "unique"

    def test_strip_pos_brackets(self):
        assert _strip_pos_brackets("[adj.]") == "adj."
        assert _strip_pos_brackets("") is None

    def test_clean_definition(self):
        assert _clean_definition("獨特的;唯一的") == "獨特的;唯一的"
        assert _clean_definition("") is None

    def test_clean_level(self):
        assert _clean_level("第三級") == "第三級"
        assert _clean_level(" ") is None

    def test_parse_frequency_exact_and_range(self):
        assert _parse_frequency("出現次數：5") == 5
        assert _parse_frequency("出現次數：10~7") == 7

    def test_to_printed_page(self):
        assert PDF_TO_PRINTED_PAGE_OFFSET == 2
        assert _to_printed_page(3) == 1
        assert _to_printed_page(81) == 79
        assert _to_printed_page(0) == 0


class TestParseMdFile:
    def test_basic_parsing_with_level_and_page(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "## 出現次數：5\n\n"
            "| 單字 | 詞性 | 中文定義 | Level | 頁碼 |\n"
            "|------|------|---------|-------|------|\n"
            "| **advantage** | [n.] | 優勢;利益 | 第三級 | 3 |\n"
            "| **adopt** | [v.] | 採用;接受 | 第四級 | 4 |\n",
            encoding="utf-8",
        )

        result = parse_md_file(md)

        assert result.rejected_count == 0
        assert len(result.entries) == 2
        assert result.entries[0]["word"] == "advantage"
        assert result.entries[0]["pos"] == "n."
        assert result.entries[0]["zh_definition"] == "優勢;利益"
        assert result.entries[0]["frequency"] == 5
        assert result.entries[0]["level"] == "第三級"
        assert result.entries[0]["source_page"] == 3
        assert result.entries[0]["ipa_us"] is None
        assert result.entries[0]["ipa_uk"] is None

    def test_range_header_uses_lower_bound(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "## 出現次數：10~7\n\n"
            "| 單字 | 詞性 | 中文定義 | Level | 頁碼 |\n"
            "|------|------|---------|-------|------|\n"
            "| **refer** | [v.] | 提及;參考(+to) | 第四級 | 1 |\n",
            encoding="utf-8",
        )

        result = parse_md_file(md)

        assert result.entries[0]["frequency"] == 7

    def test_empty_level_and_definition(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "## 出現次數：1\n\n"
            "| 單字 | 詞性 | 中文定義 | Level | 頁碼 |\n"
            "|------|------|---------|-------|------|\n"
            "| **unknown** |  |  |  | 0 |\n",
            encoding="utf-8",
        )

        result = parse_md_file(md)

        assert result.entries[0]["pos"] is None
        assert result.entries[0]["zh_definition"] is None
        assert result.entries[0]["level"] is None
        assert result.entries[0]["source_page"] == 0

    def test_reject_short_rows(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "## 出現次數：1\n\n"
            "| **broken** | [n.] | 少欄位 |\n",
            encoding="utf-8",
        )

        result = parse_md_file(md)

        assert len(result.entries) == 0
        assert result.rejected_count == 1

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_md_file("missing-topsat.md")
