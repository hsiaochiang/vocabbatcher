"""Transcribe the TopAcademy GSAT PDF into topsat.md.

This is a GSAT-specific preprocessor. It keeps the structured fields that the
PDF exposes reliably through table/text extraction, and OCRs only the Chinese
definition cell that is missing from the PDF text layer.
"""

from __future__ import annotations

import argparse
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import fitz
import pdfplumber
import pytesseract
from pytesseract import Output
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


PDF_TO_PRINTED_PAGE_OFFSET = 2
DEFAULT_DPI = 300

LEVEL_MAP = {
    "3": "第三級",
    "4": "第四級",
    "5": "第五級",
    "6": "第六級",
}

KNOWN_POS = ("adj", "adv", "prep", "conj", "pron", "art", "aux", "n", "v")

# These are limited, visually verified corrections for OCR output that remains
# wrong even after using the correct cell, 300 DPI rendering, and preprocessing.
MANUAL_FIXES = {
    "accord": ("v.", "符合;[n.] 協議 *考題多出現 according to(根據)"),
    "cruelly": ("adv.", "殘忍地;殘酷地"),
    "information": ("n.", "資訊;消息"),
    "injury": ("n.", "傷害;損傷"),
    "pollution": ("n.", "污染;污染物"),
    "preference": ("n.", "偏愛;偏好;優先選擇"),
    "reduce": ("v.", "減少;降低"),
    "refer": ("v.", "提及;參考(+to)"),
    "reference": ("n.", "參考;參考書目"),
    "risk": ("n.", "風險;危險;[v.] 擔...的風險"),
    "splendor": ("n.", "壯麗;輝煌;壯觀"),
    "suffer": ("v.", "遭受;忍受;患病"),
}


@dataclass
class TranscribedEntry:
    word: str
    pos: str | None
    definition: str | None
    level: str | None
    frequency: int | None
    source_page: int


@dataclass
class OcrToken:
    text: str
    x: float
    y: float
    line_key: tuple[int, int, int]


class OcrEngine(Protocol):
    name: str

    def recognize(self, page: fitz.Page, bbox: tuple[float, float, float, float], dpi: int) -> str:
        """Return raw OCR text for a definition cell."""


class TesseractEngine:
    name = "tesseract"

    def __init__(self) -> None:
        self._page_cache: dict[tuple[int, int], list[OcrToken]] = {}

    def recognize(self, page: fitz.Page, bbox: tuple[float, float, float, float], dpi: int) -> str:
        text = self._run_cell(page, bbox, dpi, lang="eng+chi_tra", psm=11, threshold=None, scale=1, contrast=1.0)
        if _score_ocr_text(text) >= 24 and _extract_pos(text):
            return text

        candidates = [
            text,
            self._run_cell(page, bbox, dpi, lang="chi_tra", psm=7, threshold=200, scale=1, contrast=1.0),
            self._run_cell(page, bbox, dpi, lang="eng+chi_tra", psm=6, threshold=180, scale=2, contrast=1.0),
        ]
        primary = candidates[0]
        if _score_ocr_text(primary) >= 24 and _extract_pos(primary):
            return primary

        return max(candidates, key=_score_ocr_text, default="")

    def _get_page_tokens(self, page: fitz.Page, dpi: int) -> list[OcrToken]:
        key = (page.number, dpi)
        if key in self._page_cache:
            return self._page_cache[key]

        pix = page.get_pixmap(dpi=dpi, alpha=False)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        image = ImageOps.grayscale(image)
        data = pytesseract.image_to_data(
            image,
            lang="eng+chi_tra",
            config="--psm 6 --oem 1 -c preserve_interword_spaces=1",
            output_type=Output.DICT,
        )
        scale = dpi / 72
        tokens: list[OcrToken] = []
        for index, raw_text in enumerate(data.get("text", [])):
            text = _normalize_ocr_text(str(raw_text))
            if not text:
                continue
            left = float(data["left"][index])
            top = float(data["top"][index])
            width = float(data["width"][index])
            height = float(data["height"][index])
            tokens.append(
                OcrToken(
                    text=text,
                    x=(left + width / 2) / scale,
                    y=(top + height / 2) / scale,
                    line_key=(
                        int(data["block_num"][index]),
                        int(data["par_num"][index]),
                        int(data["line_num"][index]),
                    ),
                )
            )

        self._page_cache[key] = tokens
        return tokens

    def _run_cell(
        self,
        page: fitz.Page,
        bbox: tuple[float, float, float, float],
        dpi: int,
        *,
        lang: str,
        psm: int,
        threshold: int | None,
        scale: int,
        contrast: float,
    ) -> str:
        image = _render_cell(page, bbox, dpi=dpi, scale=scale, threshold=threshold, contrast=contrast)
        config = f"--psm {psm} --oem 1 -c preserve_interword_spaces=1"
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        return _normalize_ocr_text(text)


class PaddleEngine:
    name = "paddleocr"

    def __init__(self) -> None:
        from paddleocr import PaddleOCR  # noqa: PLC0415

        self._ocr = PaddleOCR(
            lang="chinese_cht",
            ocr_version="PP-OCRv5",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def recognize(self, page: fitz.Page, bbox: tuple[float, float, float, float], dpi: int) -> str:
        image = _render_cell(page, bbox, dpi=dpi, scale=1, threshold=None, contrast=1.0)
        result = self._ocr.predict(_pil_to_numpy(image.convert("RGB")))
        texts: list[str] = []
        for item in result:
            data = dict(item) if not isinstance(item, dict) and hasattr(item, "items") else item
            if isinstance(data, dict):
                if isinstance(data.get("rec_texts"), list):
                    texts.extend(str(text) for text in data["rec_texts"])
                elif isinstance(data.get("text"), str):
                    texts.append(data["text"])
        return _normalize_ocr_text(" ".join(texts))


def _pil_to_numpy(image: Image.Image):
    import numpy as np  # noqa: PLC0415

    return np.asarray(image)


def _render_cell(
    page: fitz.Page,
    bbox: tuple[float, float, float, float],
    *,
    dpi: int,
    scale: int,
    threshold: int | None,
    contrast: float,
) -> Image.Image:
    rect = fitz.Rect(*bbox)
    rect.x0 += 2
    rect.y0 += 2
    rect.x1 -= 2
    rect.y1 -= 2
    pix = page.get_pixmap(dpi=dpi, clip=rect, alpha=False)
    image = Image.open(io.BytesIO(pix.tobytes("png")))
    image = ImageOps.grayscale(image)
    if contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if scale != 1:
        image = image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)
    if threshold is not None:
        image = image.point(lambda pixel: 255 if pixel > threshold else 0)
    return image.filter(ImageFilter.SHARPEN)


def _normalize_ocr_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("；", ";").replace("﹔", ";")
    text = text.replace(" ,", ",").replace(";,", ";").replace(";，", ";")
    text = text.replace("(+o)", "(+to)")
    text = text.replace("殘酪地", "殘酷地")
    text = re.sub(r"^[lI1|]\s*(adj|adv|prep|conj|pron|art|aux|n|v)\.?\]", r"[\1.]", text)
    text = re.sub(r"^\[(?:i|l)?n\.?\]", "[n.]", text, flags=re.IGNORECASE)
    text = re.sub(r"\[([a-z]+)\]", r"[\1.]", text)
    text = re.sub(r"\[([a-z]+)\.{2,}\]", r"[\1.]", text)
    text = re.sub(r"\s*;\s*", ";", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", text)
    text = re.sub(r"\s+", " ", text).strip(" ;")
    return text


def _score_ocr_text(text: str) -> float:
    if not text:
        return -10_000
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    if cjk_count == 0:
        return -5_000
    without_pos = re.sub(r"\[[a-z]+\.?\]", "", text, flags=re.IGNORECASE)
    latin_noise = len(re.findall(r"[A-Za-z]{2,}", without_pos))
    digit_noise = len(re.findall(r"\d", without_pos))
    bad_symbol_noise = sum(without_pos.count(ch) for ch in ("Ё", "Г", "□", "�"))
    pos_bonus = 8 if _extract_pos(text) else 0
    return cjk_count * 6 + pos_bonus - latin_noise * 8 - digit_noise * 4 - bad_symbol_noise * 12


def _extract_pos(text: str) -> str | None:
    match = re.search(r"\[(adj|adv|prep|conj|pron|art|aux|n|v)\.?\]", text, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1).lower()}."
    return None


def _split_pos_definition(word: str, raw_text: str, use_manual_fixes: bool) -> tuple[str | None, str | None]:
    if use_manual_fixes and word in MANUAL_FIXES:
        return MANUAL_FIXES[word]

    text = _normalize_ocr_text(raw_text)
    pos = _extract_pos(text)
    definition = re.sub(r"\[[a-z]+\.?\]", "", text, flags=re.IGNORECASE).strip(" ;")
    definition = re.sub(r"^[\u4e00-\u9fff]{1,2}\.?\]\s*", "", definition)
    definition = re.sub(r"^[\[\]Il1|. ]+", "", definition)
    definition = re.sub(r"\s*;\s*", ";", definition)
    definition = re.sub(r"\s+", " ", definition).strip()
    return pos, definition or None


def _parse_level(row: list[str | None]) -> str | None:
    joined = " ".join(cell or "" for cell in row)
    match = re.search(r"Level\.?\s*(\d)", joined, flags=re.IGNORECASE)
    if not match:
        return None
    return LEVEL_MAP.get(match.group(1))


def _parse_frequency(year_cell: str | None) -> int | None:
    if not year_cell:
        return None
    years = re.findall(r"\b\d{2}\b", year_cell)
    return len(years) if years else None


def _definition_col_index(row: list[str | None]) -> int:
    # Early pages expose 6 logical columns. Later pages expose 4 columns.
    return 2 if len(row) >= 5 else 1


def _year_col_index(row: list[str | None]) -> int:
    return 3 if len(row) >= 5 else 2


def _is_word_cell(value: str | None) -> bool:
    if not value:
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z-]{1,24}", value.strip()))


def transcribe_pdf(
    pdf_path: Path,
    output_path: Path,
    *,
    engine: OcrEngine,
    dpi: int,
    use_manual_fixes: bool,
    pos_fallback: dict[str, str] | None = None,
) -> list[TranscribedEntry]:
    if dpi < 300:
        raise ValueError("DPI must be at least 300 for this slice")

    entries: list[TranscribedEntry] = []
    current_level: str | None = None

    with pdfplumber.open(pdf_path) as plumber_doc, fitz.open(str(pdf_path)) as fitz_doc:
        for page_index, plumber_page in enumerate(plumber_doc.pages):
            fitz_page = fitz_doc[page_index]
            printed_page = page_index + 1 - PDF_TO_PRINTED_PAGE_OFFSET
            before_count = len(entries)
            for table in plumber_page.find_tables():
                extracted_rows = table.extract()
                for row_index, row in enumerate(extracted_rows):
                    level = _parse_level(row)
                    if level:
                        current_level = level
                        continue
                    if not row or not _is_word_cell(row[0]):
                        continue

                    word = row[0].strip().lower()
                    definition_col = _definition_col_index(row)
                    year_col = _year_col_index(row)
                    cells = table.rows[row_index].cells
                    if definition_col >= len(cells) or cells[definition_col] is None:
                        raw_definition = ""
                    else:
                        raw_definition = engine.recognize(fitz_page, cells[definition_col], dpi)

                    pos, definition = _split_pos_definition(word, raw_definition, use_manual_fixes)
                    if not pos and pos_fallback:
                        pos = pos_fallback.get(word)
                    entries.append(
                        TranscribedEntry(
                            word=word,
                            pos=pos,
                            definition=definition,
                            level=current_level,
                            frequency=_parse_frequency(row[year_col] if year_col < len(row) else None),
                            source_page=printed_page,
                        )
                    )
            page_count = len(entries) - before_count
            if page_count:
                print(f"page={page_index + 1} printed={printed_page} entries={page_count}")

    write_markdown(entries, output_path)
    return entries


def write_markdown(entries: list[TranscribedEntry], output_path: Path) -> None:
    groups: dict[int, list[TranscribedEntry]] = {}
    for entry in entries:
        groups.setdefault(entry.frequency or 0, []).append(entry)

    lines = [
        "# TopAcademy 學測高頻率單字表",
        "",
        "由 `src/pdf_parser/tools/topsat_transcribe.py` 從 PDF 轉錄；單字、Level、頁碼與出現次數來自 PDF 表格層，中文定義來自 OCR。",
        "",
        "---",
        "",
        "## 目錄",
        "",
    ]
    for frequency in sorted(groups.keys(), reverse=True):
        if frequency:
            lines.append(f"- 出現次數：{frequency}（共 {len(groups[frequency])} 個）")
    lines.extend(["", "---", ""])

    for frequency in sorted(groups.keys(), reverse=True):
        if not frequency:
            continue
        lines.append(f"## 出現次數：{frequency}")
        lines.append("")
        lines.append("| 單字 | 詞性 | 中文定義 | Level | 頁碼 |")
        lines.append("|------|------|---------|-------|------|")
        for entry in groups[frequency]:
            pos = f"[{entry.pos}]" if entry.pos else ""
            definition = _escape_markdown_cell(entry.definition or "")
            level = entry.level or ""
            source_page = str(entry.source_page) if entry.source_page > 0 else ""
            lines.append(f"| **{entry.word}** | {pos} | {definition} | {level} | {source_page} |")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|")


def read_pos_fallback(md_path: Path | None) -> dict[str, str]:
    if md_path is None:
        return {}
    result: dict[str, str] = {}
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| **"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        word = cells[0].strip("*").strip().lower()
        pos = re.sub(r"^\[(.+)\]$", r"\1", cells[1]).strip()
        if word and pos:
            result[word] = pos
    return result


def build_engine(name: str) -> OcrEngine:
    if name == "paddleocr":
        return PaddleEngine()
    if name == "tesseract":
        return TesseractEngine()
    raise ValueError(f"Unsupported OCR engine: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe the TopAcademy GSAT PDF into topsat.md")
    parser.add_argument("--input", type=Path, required=True, help="Input PDF path")
    parser.add_argument("--output", type=Path, required=True, help="Output Markdown path")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help="Render DPI for OCR; must be >= 300")
    parser.add_argument("--engine", choices=("paddleocr", "tesseract"), default="tesseract")
    parser.add_argument("--no-manual-fixes", action="store_true", help="Disable visually verified correction table")
    parser.add_argument("--pos-fallback-md", type=Path, help="Use another topsat.md only to fill missing POS tags")
    args = parser.parse_args()

    engine = build_engine(args.engine)
    pos_fallback = read_pos_fallback(args.pos_fallback_md)
    entries = transcribe_pdf(
        args.input,
        args.output,
        engine=engine,
        dpi=args.dpi,
        use_manual_fixes=not args.no_manual_fixes,
        pos_fallback=pos_fallback,
    )
    missing_pos = sum(1 for entry in entries if not entry.pos)
    missing_definition = sum(1 for entry in entries if not entry.definition)
    print(f"engine={engine.name} dpi={args.dpi}")
    if pos_fallback:
        print(f"pos_fallback={args.pos_fallback_md} entries={len(pos_fallback)}")
    print(f"entries={len(entries)} missing_pos={missing_pos} missing_definition={missing_definition}")
    print(f"wrote={args.output}")


if __name__ == "__main__":
    main()
