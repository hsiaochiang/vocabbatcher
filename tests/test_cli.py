"""CLI 模組測試。"""

import argparse
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from src.pdf_parser.__main__ import build_parser, run
from src.pdf_parser.extractor import PageContent


class TestBuildParser:
    def test_required_args(self):
        p = build_parser()
        args = p.parse_args(["--input", "test.pdf", "--outdir", "out"])
        assert args.input == "test.pdf"
        assert args.outdir == "out"
        assert args.min_frequency is None
        assert args.page_range is None
        assert args.rule == "top2025"

    def test_all_args(self):
        p = build_parser()
        args = p.parse_args([
            "--input", "test.pdf", "--outdir", "out",
            "--min-frequency", "3", "--page-range", "5-20", "--rule", "custom",
        ])
        assert args.min_frequency == 3
        assert args.page_range == "5-20"
        assert args.rule == "custom"

    def test_missing_required(self):
        p = build_parser()
        with pytest.raises(SystemExit):
            p.parse_args([])


class TestRun:
    @patch("src.pdf_parser.__main__.extract_pages")
    @patch("src.pdf_parser.__main__.load_rule")
    def test_end_to_end(self, mock_load_rule, mock_extract, tmp_path):
        # Setup mocks
        mock_extract.return_value = [
            PageContent(
                page_number=3,
                text="apple\t\t05 06 07\t○○○",
                table_rows=[["apple", "", "05 06 07", "○○○"]],
                used_table=True,
            ),
            PageContent(
                page_number=5,
                text="book\t\t05 06\t○○○",
                table_rows=[["book", "", "05 06", "○○○"]],
                used_table=True,
            ),
        ]

        from src.pdf_parser.rules.top2025 import Top2025Rule
        mock_load_rule.return_value = Top2025Rule()

        outdir = tmp_path / "output"
        args = argparse.Namespace(
            input="dummy.pdf",
            outdir=str(outdir),
            min_frequency=None,
            page_range=None,
            rule="top2025",
        )
        run(args)

        # Verify output files
        assert (outdir / "vocab.raw.json").exists()
        assert (outdir / "vocab.cleaned.json").exists()
        assert (outdir / "vocab.qa_report.json").exists()

        raw = json.loads((outdir / "vocab.raw.json").read_text(encoding="utf-8"))
        assert len(raw) == 2

        cleaned = json.loads((outdir / "vocab.cleaned.json").read_text(encoding="utf-8"))
        assert len(cleaned) == 2
        assert cleaned[0]["word"] == "apple"  # sorted
        assert cleaned[1]["word"] == "book"

        report = json.loads((outdir / "vocab.qa_report.json").read_text(encoding="utf-8"))
        assert report["total_raw"] == 2
        assert report["total_cleaned"] == 2
        assert report["duplicates_removed"] == 0
