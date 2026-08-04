"""topsat_md Markdown 解析器測試（六欄明確格式）。"""

import pytest

from src.pdf_parser.rules.topsat_md import (
    _clean_text,
    _strip_bold,
    _strip_pos_brackets,
    parse_md_file,
)


class TestHelpers:
    def test_strip_bold(self):
        assert _strip_bold("**unique**") == "unique"
        assert _strip_bold("unique") == "unique"

    def test_strip_pos_brackets(self):
        assert _strip_pos_brackets("[adj.]") == "adj."
        assert _strip_pos_brackets("") is None

    def test_clean_text(self):
        assert _clean_text("獨特的;唯一的") == "獨特的;唯一的"
        assert _clean_text("") is None
        assert _clean_text("第三級") == "第三級"
        assert _clean_text(" ") is None


class TestParseMdFile:
    def test_basic_parsing_with_level_frequency_and_page(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "| **advantage** | [n.] | 優勢;利益 | 第三級 | 5 | 3 |\n"
            "| **adopt** | [v.] | 採用;接受 | 第四級 | 4 | 4 |\n",
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

    def test_empty_level_pos_and_definition(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "| **unknown** |  |  |  | 1 | 0 |\n",
            encoding="utf-8",
        )

        result = parse_md_file(md)

        assert result.entries[0]["pos"] is None
        assert result.entries[0]["zh_definition"] is None
        assert result.entries[0]["level"] is None
        assert result.entries[0]["frequency"] == 1
        assert result.entries[0]["source_page"] == 0

    def test_reject_short_rows(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "| **broken** | [n.] | 少欄位 |\n",
            encoding="utf-8",
        )

        result = parse_md_file(md)

        assert len(result.entries) == 0
        assert result.rejected_count == 1

    def test_skips_header_comment_lines(self, tmp_path):
        md = tmp_path / "topsat.md"
        md.write_text(
            "# topsat.md 說明\n\n"
            "> | 單字 | 詞性 | 中文定義 | Level | 出現次數 | 頁碼 |\n"
            "> |------|------|---------|-------|---------|------|\n\n"
            "| **passage** | [n.] | 文章的一段 | 第三級 | 10 | 1 |\n",
            encoding="utf-8",
        )

        result = parse_md_file(md)

        assert len(result.entries) == 1
        assert result.entries[0]["word"] == "passage"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_md_file("missing-topsat.md")
