"""top2025_md Markdown 解析器測試。"""

import json
import pytest
from pathlib import Path
from src.pdf_parser.rules.top2025_md import (
    parse_md_file,
    _strip_bold,
    _strip_pos_brackets,
    _clean_definition,
    _to_printed_page,
)


class TestHelpers:
    def test_strip_bold(self):
        assert _strip_bold("**apple**") == "apple"
        assert _strip_bold("apple") == "apple"
        assert _strip_bold("  **run**  ") == "run"

    def test_strip_pos_brackets(self):
        assert _strip_pos_brackets("[art.]") == "art."
        assert _strip_pos_brackets("[v.]") == "v."
        assert _strip_pos_brackets("") is None
        assert _strip_pos_brackets("  ") is None
        assert _strip_pos_brackets("n.") == "n."  # 沒有方括號也不報錯

    def test_clean_definition(self):
        assert _clean_definition("一個;一種") == "一個;一種"
        assert _clean_definition("") is None
        assert _clean_definition("  ") is None
        assert _clean_definition("  好的  ") == "好的"

    def test_to_printed_page(self):
        assert _to_printed_page(3) == 1
        assert _to_printed_page(62) == 60
        assert _to_printed_page(0) == 0


class TestParseMdFile:
    def test_basic_parsing(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "## 十、出現次數：10\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **apple** | [n.] | 蘋果 |\n"
            "| **run** | [v.] | 跑 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert len(result.entries) == 2
        assert result.rejected_count == 0

        assert result.entries[0]["word"] == "apple"
        assert result.entries[0]["pos"] == "n."
        assert result.entries[0]["zh_definition"] == "蘋果"
        assert result.entries[0]["frequency"] == 10

        assert result.entries[1]["word"] == "run"
        assert result.entries[1]["pos"] == "v."
        assert result.entries[1]["zh_definition"] == "跑"
        assert result.entries[1]["frequency"] == 10

    def test_empty_pos(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "## 十、出現次數：10\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **he** |  | 他 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert len(result.entries) == 1
        assert result.entries[0]["word"] == "he"
        assert result.entries[0]["pos"] is None
        assert result.entries[0]["zh_definition"] == "他"

    def test_empty_pos_and_definition(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "## 十、出現次數：10\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **I** |  |  |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert len(result.entries) == 1
        assert result.entries[0]["word"] == "I"
        assert result.entries[0]["pos"] is None
        assert result.entries[0]["zh_definition"] is None

    def test_multiple_frequency_sections(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "## 十、出現次數：10\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **a** | [art.] | 一個 |\n\n"
            "## 九、出現次數：9\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **always** | [adv.] | 總是 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert len(result.entries) == 2
        assert result.entries[0]["frequency"] == 10
        assert result.entries[1]["frequency"] == 9

    def test_separator_and_header_skipped(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "## 十、出現次數：10\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **a** | [art.] | 一個 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert len(result.entries) == 1  # 只有資料列，表頭/分隔線已跳過

    def test_source_page_from_column(self, tmp_path):
        """頁碼欄位存在時轉為課本印刷頁碼。"""
        md = tmp_path / "test.md"
        md.write_text(
            "## 出現次數：5\n\n"
            "| 單字 | 詞性 | 中文定義 | 頁碼 |\n"
            "|------|------|---------|------|\n"
            "| **test** | [n.] | 測試 | 42 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert result.entries[0]["source_page"] == 40

    def test_source_page_fallback_zero(self, tmp_path):
        """無頁碼欄位時 source_page 為 0。"""
        md = tmp_path / "test.md"
        md.write_text(
            "## 出現次數：5\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **test** | [n.] | 測試 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert result.entries[0]["source_page"] == 0

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_md_file("nonexistent.md")

    def test_lines_before_any_frequency_header(self, tmp_path):
        """頻率標題前的資料列，frequency 為 None。"""
        md = tmp_path / "test.md"
        md.write_text(
            "# 標題\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **orphan** | [n.] | 孤兒 |\n\n"
            "## 出現次數：3\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **run** | [v.] | 跑 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert len(result.entries) == 2
        assert result.entries[0]["word"] == "orphan"
        assert result.entries[0]["frequency"] is None
        assert result.entries[1]["frequency"] == 3

    def test_full_width_colon_in_header(self, tmp_path):
        """支援全形冒號。"""
        md = tmp_path / "test.md"
        md.write_text(
            "## 十、出現次數：10\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **ok** | [adj.] | 好的 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert result.entries[0]["frequency"] == 10

    def test_ipa_fields_are_none(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "## 出現次數：1\n\n"
            "| 單字 | 詞性 | 中文定義 |\n"
            "|------|------|--------|\n"
            "| **xyz** | [n.] | 某物 |\n",
            encoding="utf-8",
        )
        result = parse_md_file(md)
        assert result.entries[0]["ipa_us"] is None
        assert result.entries[0]["ipa_uk"] is None
