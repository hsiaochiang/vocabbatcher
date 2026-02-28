"""資料清洗模組。"""

from __future__ import annotations

import json
from pathlib import Path

from src.pdf_parser.models import VocabEntry, CleanedEntry
from src.pdf_parser.qa import compute_confidence, compute_issues


def _trim_or_null(value: str | None) -> str | None:
    """Trim 字串，空字串轉 None。"""
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed if trimmed else None


def _dedup_key(entry: VocabEntry) -> tuple[str, str]:
    """產生去重 key。"""
    word = (entry.get("word") or "").lower().strip()
    pos = (entry.get("pos") or "").strip()
    return (word, pos)


def clean_entries(
    raw_entries: list[VocabEntry],
    min_frequency: int | None = None,
) -> list[CleanedEntry]:
    """清洗、去重並排序。

    Args:
        raw_entries: 原始解析記錄。
        min_frequency: 最低頻率門檻，None 表示不過濾。

    Returns:
        清洗後的 CleanedEntry 清單（按 word 字母排序）。
    """
    # 先計算每筆的 confidence 以便去重時比較
    enriched: list[tuple[VocabEntry, float, list[str]]] = []
    for entry in raw_entries:
        confidence = compute_confidence(entry)
        issues = compute_issues(entry, confidence)
        enriched.append((entry, confidence, issues))

    # 去重：group by (word, pos)，保留 confidence 最高者
    groups: dict[tuple[str, str], list[tuple[VocabEntry, float, list[str]]]] = {}
    for item in enriched:
        key = _dedup_key(item[0])
        groups.setdefault(key, []).append(item)

    cleaned: list[CleanedEntry] = []
    for key, items in groups.items():
        # 保留 confidence 最高的
        best = max(items, key=lambda x: x[1])
        entry, confidence, issues = best

        # 合併所有 source_page
        all_pages = sorted({item[0]["source_page"] for item in items})

        # Trim 文字欄位
        word = _trim_or_null(entry.get("word")) or ""
        pos = _trim_or_null(entry.get("pos"))
        zh_def = _trim_or_null(entry.get("zh_definition"))
        ipa_us = _trim_or_null(entry.get("ipa_us"))
        ipa_uk = _trim_or_null(entry.get("ipa_uk"))

        frequency = entry.get("frequency")

        # min-frequency 過濾（null frequency 保留）
        if min_frequency is not None and frequency is not None:
            if frequency < min_frequency:
                continue

        cleaned.append(
            CleanedEntry(
                word=word,
                pos=pos,
                zh_definition=zh_def,
                frequency=frequency,
                source_page=all_pages,
                ipa_us=ipa_us,
                ipa_uk=ipa_uk,
                parse_confidence=confidence,
                issues=issues,
            )
        )

    # 按 word 字母排序
    cleaned.sort(key=lambda e: e["word"].lower())
    return cleaned


def write_cleaned_json(entries: list[CleanedEntry], outdir: str | Path) -> Path:
    """將清洗結果寫入 vocab.cleaned.json。"""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "vocab.cleaned.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    return out_path
