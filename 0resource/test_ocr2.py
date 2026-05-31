"""OCR 混合提取測試 - 診斷版"""
import fitz
import easyocr
import numpy as np
import re

reader = easyocr.Reader(['ch_tra', 'en'], gpu=False, verbose=False)
doc = fitz.open('0resource/top2025.pdf')


def fix_bracket(text):
    known_pos = ['adj', 'adv', 'prep', 'conj', 'pron', 'art', 'aux', 'n', 'v']
    for pos in known_pos:
        # 開頭誤辨(I/f/l) + pos + 可選. + 結尾誤辨(l/L/1/)/實際])
        text = re.sub(rf'(?<!\[)[Iffl]({pos}\.?)[lL1\)\]]', rf'[\1]', text)
        # [adj] 補 dot → [adj.]
        text = re.sub(rf'\[({pos})\]', rf'[\1.]', text)
    # [adj..] 過度加點 → [adj.]
    text = re.sub(r'\[([a-z]+)\.{2,}\]', r'[\1.]', text)
    # 中文逗號誤辨為 '
    text = re.sub(r"'([\u4e00-\u9fff])", r'，\1', text)
    return text

    text = re.sub(r"'([\u4e00-\u9fff])", r'，\1', text)
    return text


def process_page(page_idx, debug=False):
    page = doc[page_idx]

    # 1. PyMuPDF: 英文單字 + y 座標（1x 空間）
    words = page.get_text('words')
    eng_entries = []
    skip = {'copyright', 'top', 'academy', 'p1', 'p7'}
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
        cx = (x0 + x1) / 2
        if cx < 180 and re.match(r'^[a-zA-Z]{1,15}$', text.strip()):
            if text.lower() not in skip:
                eng_entries.append({
                    'word': text.lower(),
                    'y': (y0 + y1) / 2,
                    'y0': y0, 'y1': y1,
                })

    eng_entries.sort(key=lambda e: e['y'])

    # y 區間：從本單字往上 25pt 到下一個單字
    for i, e in enumerate(eng_entries):
        next_y = eng_entries[i + 1]['y'] if i + 1 < len(eng_entries) else e['y'] + 80
        e['y_start'] = e['y'] - 25
        e['y_end'] = next_y - 2

    # 2. EasyOCR（2x 影像）
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    ocr_results = reader.readtext(img, detail=1, paragraph=False)

    # 3. 分配：中欄 + 含中文 → 找對應 y 區間
    unmatched = []
    for bbox, text, conf in ocr_results:
        x_cx = (bbox[0][0] + bbox[1][0]) / 2 / 2  # 2x → 1x
        y_cy = (bbox[0][1] + bbox[2][1]) / 2 / 2

        if 100 < x_cx < 850 and re.search(r'[\u4e00-\u9fff]', text):
            matched = False
            for e in eng_entries:
                if e['y_start'] <= y_cy <= e['y_end']:
                    e.setdefault('defs', []).append(fix_bracket(text))
                    matched = True
                    break
            if not matched:
                unmatched.append((x_cx, y_cy, text))

    return eng_entries, unmatched


entries, unmatched = process_page(2, debug=True)

print('=== 第3頁 混合提取結果 ===')
for e in entries:
    defs = ' ; '.join(e.get('defs', ['(無定義)']))
    print(f"{e['word']:12} | {defs}")

if unmatched:
    print()
    print('=== 未配對（y 超出所有單字範圍）===')
    for x, y, text in unmatched:
        print(f"  x={x:.0f} y={y:.0f} | {text}")

print()
print('=== 英文單字 y 區間 ===')
for e in entries:
    print(f"  {e['word']:12} y_start={e['y_start']:.0f}  y={e['y']:.0f}  y_end={e['y_end']:.0f}")

doc.close()
