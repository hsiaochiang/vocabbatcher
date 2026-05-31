import fitz
import easyocr
import numpy as np
import re

reader = easyocr.Reader(['ch_tra', 'en'], gpu=False, verbose=False)
doc = fitz.open('0resource/top2025.pdf')


def fix_bracket(text):
    text = re.sub(r'(?<!\[)[Iffl]([a-z]+\.?\])', r'[\1', text)
    text = re.sub(r'(\[[^\]]+)[lL]\]', r'\1]', text)
    return text


def process_page(page_idx):
    page = doc[page_idx]

    # 1. PyMuPDF: 取得英文單字及其 y 座標（1x 空間）
    words = page.get_text('words')
    eng_entries = []
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
        cx = (x0 + x1) / 2
        if cx < 180 and re.match(r'^[a-zA-Z]{1,15}$', text.strip()):
            if text.lower() not in {'copyright', 'top', 'academy'}:
                eng_entries.append({'word': text.lower(), 'y': (y0 + y1) / 2, 'y0': y0, 'y1': y1})

    eng_entries.sort(key=lambda e: e['y'])

    # 計算每個單字的 y 區間
    for i, e in enumerate(eng_entries):
        if i + 1 < len(eng_entries):
            e['y_end'] = eng_entries[i + 1]['y'] - 1
        else:
            e['y_end'] = e['y'] + 50
        e['y_start'] = e['y'] - 20

    # 2. EasyOCR: 取得中文定義（2x 影像座標）
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    ocr_results = reader.readtext(img_array, detail=1, paragraph=False)

    # 3. 分配 OCR 結果到對應英文單字的 y 區間
    unmatched = []
    for bbox, text, conf in ocr_results:
        x_cx = (bbox[0][0] + bbox[1][0]) / 2 / 2  # 換算回 1x
        y_cy = (bbox[0][1] + bbox[2][1]) / 2 / 2   # 換算回 1x

        # 只取中欄定義欄（有中文字）
        if 170 < x_cx < 850 and re.search(r'[\u4e00-\u9fff]', text):
            matched = False
            for e in eng_entries:
                if e['y_start'] <= y_cy <= e['y_end']:
                    if 'defs' not in e:
                        e['defs'] = []
                    e['defs'].append(fix_bracket(text))
                    matched = True
                    break
            if not matched:
                unmatched.append((x_cx, y_cy, text))

    return eng_entries, unmatched


entries, unmatched = process_page(2)
# 以下重複刪除


if unmatched:
    print()
    print('=== 未配對的中文 OCR 結果 ===')
    for x, y, text in unmatched:
        print(f"  x={x:.0f} y={y:.0f} | {text}")

# 印出英文單字的 y 範圍供對照
print()
print('=== 英文單字 y 範圍 ===')
for e in entries:
    print(f"  {e['word']:12} y_start={e['y_start']:.0f} y={e['y']:.0f} y_end={e['y_end']:.0f}")

doc.close()
