"""OCR-based PDF extractor for top2025.pdf.

使用 PyMuPDF（英文單字 + 座標）+ EasyOCR（中文定義）混合策略，
解決 PMingLiU 字型 ToUnicode CMap 幾乎空白導致中文無法提取的問題。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz
import numpy as np


@dataclass
class OcrPageResult:
    """單頁 OCR 提取結果。"""
    page_number: int
    entries: list[dict] = field(default_factory=list)


# ─── OCR reader（延遲初始化，避免 import 時下載模型）─────────────────────────
_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        import easyocr  # noqa: PLC0415
        _reader = easyocr.Reader(['ch_tra', 'en'], gpu=False, verbose=False)
    return _reader


# ─── 後處理：修正 OCR 對 [ 與 ] 的誤辨 ─────────────────────────────────────

_KNOWN_POS = ['adj', 'adv', 'prep', 'conj', 'pron', 'art', 'aux', 'n', 'v']

def _fix_bracket(text: str) -> str:
    """修正 OCR 常見的詞性標記誤辨，如 Iadv.] → [adv.]。"""
    for pos in _KNOWN_POS:
        # 開頭誤辨(I/f/l) + pos + 可選. + 結尾誤辨(l/L/1/)/])
        text = re.sub(rf'(?<!\[)[Iffl]({pos}\.?)[lL1\)\]]', rf'[\1]', text)
        # [adj] 補 dot → [adj.]
        text = re.sub(rf'\[({pos})\]', rf'[\1.]', text)
    # [adj..] 過度加點 → [adj.]
    text = re.sub(r'\[([a-z]+)\.{2,}\]', r'[\1.]', text)
    # 中文逗號誤辨為 '
    text = re.sub(r"'([\u4e00-\u9fff])", r'，\1', text)
    return text


def _dedup_definition(defs_raw: list[str]) -> str:
    """拼接多個 OCR 定義片段並去除重複的中文詞彙。

    原理：去掉詞性標記後，以 ; 和空格做 token 分割，
    保留首次出現的 token（order-preserving dedup）。
    """
    joined = ' '.join(defs_raw)
    # 去掉詞性標記（用於去重比較）
    stripped = re.sub(r'\[[a-z]+\.?\]\s*', '', joined)
    stripped = re.sub(r'\s+', ' ', stripped).strip()

    # 以 ; 和空格分割，取出所有中文詞彙 token
    tokens_for_dedup = [t.strip().rstrip(';') for t in re.split(r'[;；\s]+', stripped) if t.strip()]

    seen: set[str] = set()
    kept: set[str] = set()
    for t in tokens_for_dedup:
        key = t.strip()
        if key and key not in seen:
            seen.add(key)
            kept.add(key)

    # 從原始 joined 中移除重複 token（只在第二次以後出現時刪除）
    result_parts = []
    seen2: set[str] = set()
    for part in defs_raw:
        # 逐 token 掃描 part，保留首次出現
        tokens = re.split(r'(\s+|;|；)', part)
        out_tokens = []
        for tok in tokens:
            clean = tok.strip().rstrip(';；')
            if not clean or not re.search(r'[\u4e00-\u9fff]', clean):
                out_tokens.append(tok)  # 非中文（詞性標記、空格）直接保留
            elif clean not in seen2:
                seen2.add(clean)
                out_tokens.append(tok)
            # 重複的中文 token：略過
        rebuilt = ''.join(out_tokens).strip().strip(';；').strip()
        if rebuilt:
            result_parts.append(rebuilt)

    return ' '.join(result_parts)


# ─── 核心提取邏輯 ──────────────────────────────────────────────────────────

_SKIP_WORDS = {'copyright', 'top', 'academy', 'p1', 'p7', 'p10', 'p13', 'p17',
               'p20', 'p25', 'p32', 'p39', 'p48'}


def _extract_page(page: fitz.Page, reader) -> list[dict]:
    """提取單頁的單字 + 中文定義。"""
    # 1. PyMuPDF：左欄英文單字（1x 座標，準確）
    words_raw = page.get_text('words')
    eng_entries: list[dict] = []
    for w in words_raw:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
        cx = (x0 + x1) / 2
        if cx < 180 and re.match(r'^[a-zA-Z]{1,15}$', text.strip()):
            if text.lower() not in _SKIP_WORDS:
                eng_entries.append({
                    'word': text.lower(),
                    'y': (y0 + y1) / 2,
                })

    if not eng_entries:
        return []

    eng_entries.sort(key=lambda e: e['y'])

    # y 區間：從本單字往上 25pt 到下一個單字
    for i, e in enumerate(eng_entries):
        next_y = eng_entries[i + 1]['y'] if i + 1 < len(eng_entries) else e['y'] + 80
        e['y_start'] = e['y'] - 25
        e['y_end'] = next_y - 2

    # 2. EasyOCR（2x 影像）：中欄中文定義
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    ocr_results = reader.readtext(img, detail=1, paragraph=False)

    # 3. 分配：x 在中欄（100~850 1x）+ 含中文 → 配對最近的英文單字 y 區間
    for bbox, text, _conf in ocr_results:
        x_cx = (bbox[0][0] + bbox[1][0]) / 2 / 2  # 2x → 1x
        y_cy = (bbox[0][1] + bbox[2][1]) / 2 / 2

        if 100 < x_cx < 850 and re.search(r'[\u4e00-\u9fff]', text):
            fixed = _fix_bracket(text)
            for e in eng_entries:
                if e['y_start'] <= y_cy <= e['y_end']:
                    e.setdefault('defs', []).append(fixed)
                    break

    # 整理輸出：拼接 defs 並去除重複的中文詞彙
    results = []
    for e in eng_entries:
        defs_raw = e.get('defs', [])
        definition = _dedup_definition(defs_raw) if defs_raw else None
        results.append({
            'word': e['word'],
            'definition': definition,
        })

    return results


def extract_all_pages(pdf_path: str | Path) -> list[OcrPageResult]:
    """對整份 PDF 執行 OCR 混合提取。"""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF 不存在：{path}")

    reader = _get_reader()
    doc = fitz.open(str(path))
    results: list[OcrPageResult] = []

    print(f"開始處理 {len(doc)} 頁...")
    for page in doc.pages():
        page_num = page.number + 1  # 1-based
        entries = _extract_page(page, reader)
        if entries:
            results.append(OcrPageResult(page_number=page_num, entries=entries))
            print(f"  第 {page_num:2d} 頁：{len(entries)} 個單字")

    doc.close()
    return results
