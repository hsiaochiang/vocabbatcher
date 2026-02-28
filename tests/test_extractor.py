"""extractor 模組測試。"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.pdf_parser.extractor import extract_pages, parse_page_range, PageContent


class TestParsePageRange:
    def test_none_returns_none(self):
        assert parse_page_range(None) is None

    def test_valid_range(self):
        assert parse_page_range("5-20") == (5, 20)

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_page_range("abc")

    def test_invalid_range(self):
        with pytest.raises(ValueError):
            parse_page_range("20-5")


class TestExtractPages:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="PDF 檔案不存在"):
            extract_pages("nonexistent.pdf")

    @patch("src.pdf_parser.extractor.Path.exists", return_value=True)
    @patch("src.pdf_parser.extractor.pdfplumber")
    def test_extract_all_pages(self, mock_pdfplumber, _mock_exists):
        mock_page1 = MagicMock()
        mock_page1.page_number = 1
        mock_page1.extract_tables.return_value = []
        mock_page1.extract_text.return_value = "apple n. 蘋果"

        mock_page2 = MagicMock()
        mock_page2.page_number = 2
        mock_page2.extract_tables.return_value = []
        mock_page2.extract_text.return_value = "run v. 跑"

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdfplumber.open.return_value = mock_pdf

        results = extract_pages("dummy.pdf")
        assert len(results) == 2
        assert results[0].page_number == 1
        assert results[0].text == "apple n. 蘋果"
        assert results[0].used_table is False

    @patch("src.pdf_parser.extractor.Path.exists", return_value=True)
    @patch("src.pdf_parser.extractor.pdfplumber")
    def test_page_range_filter(self, mock_pdfplumber, _mock_exists):
        pages = []
        for i in range(1, 6):
            p = MagicMock()
            p.page_number = i
            p.extract_tables.return_value = []
            p.extract_text.return_value = f"page {i}"
            pages.append(p)

        mock_pdf = MagicMock()
        mock_pdf.pages = pages
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdfplumber.open.return_value = mock_pdf

        results = extract_pages("dummy.pdf", page_range="2-4")
        assert len(results) == 3
        assert [r.page_number for r in results] == [2, 3, 4]

    @patch("src.pdf_parser.extractor.Path.exists", return_value=True)
    @patch("src.pdf_parser.extractor.pdfplumber")
    def test_table_extraction(self, mock_pdfplumber, _mock_exists):
        mock_page = MagicMock()
        mock_page.page_number = 1
        mock_page.extract_tables.return_value = [
            [["apple", "n.", "蘋果"], ["book", "n.", "書"]]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdfplumber.open.return_value = mock_pdf

        results = extract_pages("dummy.pdf")
        assert len(results) == 1
        assert results[0].used_table is True
        assert len(results[0].table_rows) == 2
        assert results[0].table_rows[0] == ["apple", "n.", "蘋果"]
