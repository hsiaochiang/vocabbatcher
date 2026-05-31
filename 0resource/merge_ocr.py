"""合併 vocab.raw.json（frequency）與 vocab.ocr.json（zh_definition）"""
import json
import re
import sys
sys.path.insert(0, '.')
from src.pdf_parser.cleaner import clean_entries, write_cleaned_json
from src.pdf_parser.qa import generate_qa_report, write_qa_report

# ── 載入兩份資料 ──────────────────────────────────────────────────
with open('output/vocab.raw.json', encoding='utf-8') as f:
    raw_entries = json.load(f)

with open('output/vocab.ocr.json', encoding='utf-8') as f:
    ocr_entries = {e['word']: e['definition'] for e in json.load(f)}


def dedup_zh(text: str) -> str:
    """去除中文定義中重複的詞彙（order-preserving）。

    [prep.]大約 和 大約 的比較 key 都正規化為 大約，第二次出現略過。
    """
    if not text:
        return text
    # 以 ; 和空格做 token 切割（保留分隔符）
    tokens = re.split(r'([;；\s]+)', text)
    seen: set[str] = set()
    result = []
    for tok in tokens:
        stripped = tok.strip().rstrip(';；').strip()
        if not stripped:
            result.append(tok)  # 純分隔符，直接保留
            continue
        # 去掉詞性標記後的比較 key
        key = re.sub(r'\[[a-z]+\.?\]\s*', '', stripped).strip().rstrip(';；').strip()
        if not key:
            result.append(tok)  # 純詞性標記（如 [v.]），保留
        elif not re.search(r'[\u4e00-\u9fff]', key):
            result.append(tok)  # 無中文（數字、英文），保留
        elif key not in seen:
            seen.add(key)
            result.append(tok)  # 首次出現，保留
        # else: 重複的中文詞彙，略過
    return ''.join(result).strip().strip(';；').strip()


def parse_definition(text: str | None) -> tuple[str | None, str | None]:
    """從 OCR 定義字串解析出第一個 pos 標記與完整中文定義。

    例：'[adv.] 在附近 大約 [prep.]大約 關於'
    → pos='adv.', zh_definition='[adv.] 在附近 大約 [prep.]大約 關於'
    """
    if not text:
        return None, None
    # 先去重
    text = dedup_zh(text)
    # 取第一個 [pos.] 作為主詞性
    m = re.search(r'\[([a-z]+\.?)\]', text)
    pos = m.group(1) if m else None
    # 整理中文定義：去除多餘空白
    zh = re.sub(r'  +', ' ', text.strip())
    return pos, zh


# ── 合併：以 word 對齊，注入 pos + zh_definition ──────────────────
enriched = []
matched = 0
for entry in raw_entries:
    word = entry['word']
    definition = ocr_entries.get(word)
    pos, zh = parse_definition(definition)
    if definition:
        matched += 1
    enriched.append({
        **entry,
        'pos': pos,
        'zh_definition': zh,
    })

print(f"raw_entries: {len(raw_entries)} 筆")
print(f"ocr_entries: {len(ocr_entries)} 筆")
print(f"成功配對: {matched} 筆（{matched/len(raw_entries)*100:.1f}%）")

# ── 寫出更新後的 vocab.raw.json ───────────────────────────────────
with open('output/vocab.raw.json', 'w', encoding='utf-8') as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)
print("✓ output/vocab.raw.json 已更新（含 zh_definition）")

# ── 重跑 cleaner ──────────────────────────────────────────────────
cleaned = clean_entries(enriched)
write_cleaned_json(cleaned, 'output')
print(f"✓ output/vocab.cleaned.json 已更新（{len(cleaned)} 筆）")

# ── 重跑 QA ───────────────────────────────────────────────────────
report = generate_qa_report(enriched, cleaned)
write_qa_report(report, 'output')
print("✓ output/vocab.qa_report.json 已更新")

# ── 預覽前 10 筆 ─────────────────────────────────────────────────
print()
print("=== 前 10 筆 (enriched) ===")
for e in cleaned[:10]:
    print(f"  {e['word']:14} freq={e['frequency']}  pos={e['pos']!r:8}  {e['zh_definition']}")
