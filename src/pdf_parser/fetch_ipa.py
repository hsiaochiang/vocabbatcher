"""從 dictionaryapi.dev 批次取得 IPA 音標。

用法：python -m src.pdf_parser.fetch_ipa --input output/vocab.cleaned.json --output output/ipa_cache.json

特性：
- 限流：每秒最多 2 個請求
- 斷點續傳：已有快取的單字不會重新查詢
- 404 容錯：找不到的單字記錄為 null
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from pathlib import Path


_API_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en"
_HEADERS = {"User-Agent": "VocabBatcher/1.0"}
_RATE_LIMIT = 0.5  # 每次請求間隔秒數


def fetch_ipa(word: str) -> tuple[str | None, str | None]:
    """從 API 取得單一單字的 IPA (US, UK)。"""
    url = f"{_API_BASE}/{word}"
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise
    except (urllib.error.URLError, TimeoutError):
        return None, None

    phonetics = data[0].get("phonetics", []) if data else []
    ipa_us: str | None = None
    ipa_uk: str | None = None

    for p in phonetics:
        text = p.get("text", "")
        if not text:
            continue
        audio = p.get("audio", "")
        if "us" in audio:
            ipa_us = text
        elif "uk" in audio:
            ipa_uk = text
        elif ipa_us is None:
            ipa_us = text

    return ipa_us, ipa_uk


def batch_fetch(
    words: list[str],
    cache_path: str | Path,
    progress_interval: int = 50,
) -> dict[str, dict]:
    """批次取得 IPA，支援快取續傳。

    Args:
        words: 單字清單。
        cache_path: 快取 JSON 路徑。
        progress_interval: 每幾筆印一次進度。

    Returns:
        字典 {word: {"ipa_us": str|None, "ipa_uk": str|None}}
    """
    cache_path = Path(cache_path)

    # 載入既有快取
    cache: dict[str, dict] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        print(f"  載入快取：{len(cache)} 筆")

    total = len(words)
    fetched = 0
    skipped = 0

    for i, word in enumerate(words):
        if word in cache:
            skipped += 1
            continue

        ipa_us, ipa_uk = fetch_ipa(word)
        cache[word] = {"ipa_us": ipa_us, "ipa_uk": ipa_uk}
        fetched += 1

        # 定期存檔
        if fetched % progress_interval == 0:
            cache_path.write_text(
                json.dumps(cache, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  進度：{i+1}/{total}（已查 {fetched}，跳過 {skipped}）")

        time.sleep(_RATE_LIMIT)

    # 最終存檔
    cache_path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  完成：查詢 {fetched} 筆，跳過 {skipped} 筆，總計 {len(cache)} 筆")
    return cache


def merge_ipa_to_cleaned(
    cleaned_path: str | Path,
    cache_path: str | Path,
    output_path: str | Path | None = None,
) -> int:
    """將 IPA 快取合併到 vocab.cleaned.json。

    Args:
        cleaned_path: vocab.cleaned.json 路徑。
        cache_path: ipa_cache.json 路徑。
        output_path: 輸出路徑（預設覆寫 cleaned_path）。

    Returns:
        成功合併的筆數。
    """
    cleaned_path = Path(cleaned_path)
    cache_path = Path(cache_path)
    if output_path is None:
        output_path = cleaned_path
    else:
        output_path = Path(output_path)

    cleaned = json.loads(cleaned_path.read_text(encoding="utf-8"))
    cache = json.loads(cache_path.read_text(encoding="utf-8"))

    merged = 0
    for entry in cleaned:
        word = entry["word"].lower()
        if word in cache:
            ipa_data = cache[word]
            if ipa_data.get("ipa_us"):
                entry["ipa_us"] = ipa_data["ipa_us"]
                merged += 1
            if ipa_data.get("ipa_uk"):
                entry["ipa_uk"] = ipa_data["ipa_uk"]

    output_path.write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return merged


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="批次取得 IPA 音標")
    p.add_argument("--input", required=True, help="vocab.cleaned.json 路徑")
    p.add_argument("--cache", default="output/ipa_cache.json", help="快取檔路徑")
    p.add_argument("--merge", action="store_true", help="取得後直接合併到 cleaned JSON")
    args = p.parse_args()

    # 讀取單字列表
    cleaned = json.loads(Path(args.input).read_text(encoding="utf-8"))
    words = [e["word"].lower() for e in cleaned]
    print(f"待查詢：{len(words)} 個單字")

    # 批次查詢
    batch_fetch(words, args.cache)

    # 合併
    if args.merge:
        count = merge_ipa_to_cleaned(args.input, args.cache)
        print(f"已合併 {count} 筆 IPA 到 {args.input}")
