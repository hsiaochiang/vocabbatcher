"""cleaner 模組測試。"""

import json
from src.pdf_parser.cleaner import clean_entries, write_cleaned_json
from src.pdf_parser.models import VocabEntry


def _make_entry(**overrides) -> VocabEntry:
    defaults = dict(
        word="test", pos="n.", zh_definition="測試",
        frequency=3, level=None, source_page=1, ipa_us=None, ipa_uk=None,
    )
    defaults.update(overrides)
    return VocabEntry(**defaults)  # type: ignore[typeddict-item]


class TestCleanEntries:
    def test_dedup_same_word_pos(self):
        entries = [
            _make_entry(word="apple", pos="n.", source_page=5, frequency=3),
            _make_entry(word="apple", pos="n.", source_page=12, frequency=2),
        ]
        result = clean_entries(entries)
        assert len(result) == 1
        assert sorted(result[0]["source_page"]) == [5, 12]

    def test_different_pos_kept(self):
        entries = [
            _make_entry(word="run", pos="v.", source_page=1),
            _make_entry(word="run", pos="n.", source_page=2),
        ]
        result = clean_entries(entries)
        assert len(result) == 2

    def test_trim_whitespace(self):
        entries = [_make_entry(word="  apple  ")]
        result = clean_entries(entries)
        assert result[0]["word"] == "apple"

    def test_empty_string_to_null(self):
        entries = [_make_entry(zh_definition="")]
        result = clean_entries(entries)
        assert result[0]["zh_definition"] is None

    def test_level_trimmed_and_preserved(self):
        entries = [_make_entry(level=" 第三級 ")]
        result = clean_entries(entries)
        assert result[0]["level"] == "第三級"

    def test_min_frequency_filter(self):
        entries = [
            _make_entry(word="a", frequency=5),
            _make_entry(word="b", frequency=1),
            _make_entry(word="c", frequency=None),  # null frequency preserved
        ]
        result = clean_entries(entries, min_frequency=2)
        words = {e["word"] for e in result}
        assert "a" in words
        assert "b" not in words
        assert "c" in words  # null frequency is kept

    def test_sorted_by_word(self):
        entries = [
            _make_entry(word="zebra"),
            _make_entry(word="apple"),
            _make_entry(word="moon"),
        ]
        result = clean_entries(entries)
        assert [e["word"] for e in result] == ["apple", "moon", "zebra"]


class TestWriteCleanedJson:
    def test_write(self, tmp_outdir):
        entries = clean_entries([_make_entry()])
        path = write_cleaned_json(entries, tmp_outdir)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 1
