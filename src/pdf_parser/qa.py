"""品質報告模組。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from src.pdf_parser.models import VocabEntry, CleanedEntry, QAReport

# 用於 confidence 計算的欄位權重
_OPTIONAL_FIELDS = ["pos", "zh_definition", "frequency", "ipa_us", "ipa_uk"]
_TOTAL_WEIGHT = 1.0 + len(_OPTIONAL_FIELDS) * 0.2  # word(1.0) + 5 * 0.2 = 2.0


def compute_confidence(entry: VocabEntry) -> float:
    """計算單筆記錄的 parse_confidence（0.0–1.0）。

    評分規則：
    - word 有值且為純英文：+1.0
    - word 有值但含非英文字元：+0.5
    - 每個選填欄位有值：+0.2
    """
    score = 0.0
    word = (entry.get("word") or "").strip()

    if word:
        if re.match(r"^[a-zA-Z\-' ]+$", word):
            score += 1.0
        else:
            score += 0.5

    for field in _OPTIONAL_FIELDS:
        val = entry.get(field)  # type: ignore[literal-required]
        if val is not None and val != "":
            score += 0.2

    return round(min(score / _TOTAL_WEIGHT, 1.0), 4)


def compute_issues(entry: VocabEntry, confidence: float) -> list[str]:
    """計算單筆記錄的 issues 陣列。"""
    issues: list[str] = []

    if entry.get("pos") is None:
        issues.append("missing_pos")
    if entry.get("zh_definition") is None:
        issues.append("missing_definition")

    word = (entry.get("word") or "").strip()
    if word and not re.match(r"^[a-zA-Z\-' ]+$", word):
        issues.append("suspicious_word")

    if confidence < 0.5:
        issues.append("low_confidence")

    return issues


def generate_qa_report(
    raw_entries: list[VocabEntry],
    cleaned_entries: list[CleanedEntry],
) -> QAReport:
    """產出品質報告。"""
    total_raw = len(raw_entries)
    total_cleaned = len(cleaned_entries)
    duplicates_removed = total_raw - total_cleaned

    low_confidence_count = sum(
        1 for e in cleaned_entries if e["parse_confidence"] < 0.5
    )

    # 各欄位填充率
    fields = ["word", "pos", "zh_definition", "frequency", "ipa_us", "ipa_uk"]
    field_completeness: dict[str, float] = {}
    for field in fields:
        if total_cleaned == 0:
            field_completeness[field] = 0.0
        else:
            filled = sum(
                1 for e in cleaned_entries
                if e.get(field) is not None and e.get(field) != ""  # type: ignore[literal-required]
            )
            field_completeness[field] = round(filled / total_cleaned, 4)

    # Issues 彙總
    issue_counter: Counter[str] = Counter()
    for e in cleaned_entries:
        for issue in e["issues"]:
            issue_counter[issue] += 1

    issues_summary = [
        {"issue": issue, "count": count}
        for issue, count in issue_counter.most_common()
    ]

    return QAReport(
        total_raw=total_raw,
        total_cleaned=total_cleaned,
        duplicates_removed=duplicates_removed,
        low_confidence_count=low_confidence_count,
        field_completeness=field_completeness,
        issues_summary=issues_summary,
    )


def write_qa_report(report: QAReport, outdir: str | Path) -> Path:
    """將品質報告寫入 vocab.qa_report.json。"""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "vocab.qa_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return out_path
