"""執行全 PDF OCR 提取，輸出到 output/vocab.ocr.json"""
import sys
import json
sys.path.insert(0, '.')
from src.pdf_parser.ocr_extractor import extract_all_pages

results = extract_all_pages('0resource/top2025.pdf')

all_entries = []
for page_result in results:
    all_entries.extend(page_result.entries)

# 去重（同一個 word 可能在不同頻率頁出現，保留第一筆）
seen = {}
for e in all_entries:
    word = e['word']
    if word not in seen:
        seen[word] = e

deduped = sorted(seen.values(), key=lambda e: e['word'])

output_path = 'output/vocab.ocr.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

print(f"\n完成！共 {len(deduped)} 個單字，輸出至 {output_path}")
