"""PDF 文字抽取模組。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber


@dataclass
class PageContent:
    """單頁抽取結果。"""

    page_number: int
    text: str
    table_rows: list[list[str]] = field(default_factory=list)
    used_table: bool = False


def parse_page_range(page_range: str | None) -> tuple[int, int] | None:
    """解析 'start-end' 格式的頁碼範圍（1-based）。"""
    if not page_range:
        return None
    parts = page_range.split("-", 1)
    if len(parts) != 2:
        raise ValueError(f"頁碼範圍格式錯誤，應為 'start-end'：{page_range}")
    start, end = int(parts[0]), int(parts[1])
    if start < 1 or end < start:
        raise ValueError(f"頁碼範圍無效：{page_range}")
    return (start, end)


def extract_pages(
    pdf_path: str | Path,
    page_range: str | None = None,
) -> list[PageContent]:
    """從 PDF 逐頁抽取文字，優先嘗試表格解析。

    Args:
        pdf_path: PDF 檔案路徑。
        page_range: 頁碼範圍字串（'start-end'，1-based），None 表示全部。

    Returns:
        依頁碼排列的 PageContent 清單。

    Raises:
        FileNotFoundError: PDF 檔案不存在。
        ValueError: 頁碼範圍格式錯誤。
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF 檔案不存在：{path}")

    bounds = parse_page_range(page_range)
    results: list[PageContent] = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_num = page.page_number  # 1-based
            if bounds and not (bounds[0] <= page_num <= bounds[1]):
                continue

            # 表格優先策略
            tables = page.extract_tables()
            if tables:
                all_rows: list[list[str]] = []
                for table in tables:
                    for row in table:
                        cleaned = [cell.strip() if cell else "" for cell in row]
                        all_rows.append(cleaned)
                text = "\n".join("\t".join(row) for row in all_rows)
                results.append(
                    PageContent(
                        page_number=page_num,
                        text=text,
                        table_rows=all_rows,
                        used_table=True,
                    )
                )
            else:
                raw_text = page.extract_text() or ""
                results.append(
                    PageContent(
                        page_number=page_num,
                        text=raw_text,
                    )
                )

    return results
