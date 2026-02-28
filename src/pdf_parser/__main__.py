"""CLI 入口點：python -m src.pdf_parser"""

from __future__ import annotations

import argparse
import sys

from src.pdf_parser.extractor import extract_pages
from src.pdf_parser.parser import parse_pages, load_rule, write_raw_json
from src.pdf_parser.cleaner import clean_entries, write_cleaned_json
from src.pdf_parser.qa import generate_qa_report, write_qa_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf_parser",
        description="將 PDF 教材轉換為結構化 JSON 單字庫",
    )
    p.add_argument("--input", required=True, help="PDF 檔案路徑")
    p.add_argument("--outdir", required=True, help="輸出目錄")
    p.add_argument(
        "--min-frequency", type=int, default=None,
        help="最低頻率門檻（不指定則不過濾）",
    )
    p.add_argument(
        "--page-range", default=None,
        help="頁碼範圍，格式 start-end（1-based）",
    )
    p.add_argument(
        "--rule", default="top2025",
        help="parser 規則模組名稱（預設 top2025）",
    )
    return p


def run(args: argparse.Namespace) -> None:
    """執行完整 pipeline：extract → parse → clean → qa_report。"""
    # 1. Extract
    print(f"[1/4] 抽取 PDF：{args.input}")
    pages = extract_pages(args.input, page_range=args.page_range)
    print(f"      抽取 {len(pages)} 頁")

    # 2. Parse
    print(f"[2/4] 解析單字（規則：{args.rule}）")
    rule = load_rule(args.rule)
    raw_entries = parse_pages(pages, rule=rule)
    raw_path = write_raw_json(raw_entries, args.outdir)
    print(f"      解析 {len(raw_entries)} 筆 → {raw_path}")

    # 3. Clean
    print("[3/4] 清洗與去重")
    cleaned = clean_entries(raw_entries, min_frequency=args.min_frequency)
    cleaned_path = write_cleaned_json(cleaned, args.outdir)
    print(f"      清洗後 {len(cleaned)} 筆 → {cleaned_path}")

    # 4. QA Report
    print("[4/4] 產出品質報告")
    report = generate_qa_report(raw_entries, cleaned)
    report_path = write_qa_report(report, args.outdir)
    print(f"      報告 → {report_path}")

    # Summary
    print()
    print("=== 完成 ===")
    print(f"  Raw:     {report['total_raw']} 筆")
    print(f"  Cleaned: {report['total_cleaned']} 筆")
    print(f"  去重:    {report['duplicates_removed']} 筆")
    print(f"  低信心:  {report['low_confidence_count']} 筆")
    for field, rate in report["field_completeness"].items():
        print(f"  {field}: {rate:.1%}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        run(args)
    except FileNotFoundError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
