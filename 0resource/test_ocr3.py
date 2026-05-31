"""測試前幾頁 OCR"""
import sys
sys.path.insert(0, '.')
import fitz
from src.pdf_parser.ocr_extractor import _get_reader, _extract_page

reader = _get_reader()
doc = fitz.open('0resource/top2025.pdf')

for i in range(2, 7):
    page = doc[i]
    entries = _extract_page(page, reader)
    print(f"=== 第 {i+1} 頁 ({len(entries)} 個) ===")
    for e in entries:
        d = e['definition'] or '(無)'
        print(f"  {e['word']:12} | {d}")
    print()

doc.close()
