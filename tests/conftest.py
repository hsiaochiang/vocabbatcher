"""測試共用 fixtures。"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_raw_entries():
    """模擬 raw 解析結果。"""
    return [
        {
            "word": "apple",
            "pos": "n.",
            "zh_definition": "蘋果",
            "frequency": 3,
            "source_page": 5,
            "ipa_us": "/ˈæp.əl/",
            "ipa_uk": "/ˈæp.əl/",
        },
        {
            "word": "run",
            "pos": "v.",
            "zh_definition": "跑",
            "frequency": 5,
            "source_page": 8,
            "ipa_us": "/rʌn/",
            "ipa_uk": "/rʌn/",
        },
        {
            "word": "apple",
            "pos": "n.",
            "zh_definition": "蘋果",
            "frequency": 2,
            "source_page": 12,
            "ipa_us": "/ˈæp.əl/",
            "ipa_uk": "/ˈæp.əl/",
        },
        {
            "word": "run",
            "pos": "n.",
            "zh_definition": "奔跑；路程",
            "frequency": 1,
            "source_page": 15,
            "ipa_us": None,
            "ipa_uk": None,
        },
    ]


@pytest.fixture
def tmp_outdir(tmp_path):
    """提供暫時輸出目錄。"""
    outdir = tmp_path / "output"
    outdir.mkdir()
    return outdir
