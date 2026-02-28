"""qa 模組測試。"""

import json
from src.pdf_parser.qa import compute_confidence, compute_issues, generate_qa_report, write_qa_report
from src.pdf_parser.models import VocabEntry, CleanedEntry


def _entry(**overrides) -> VocabEntry:
    defaults = dict(
        word="test", pos=None, zh_definition=None,
        frequency=None, source_page=1, ipa_us=None, ipa_uk=None,
    )
    defaults.update(overrides)
    return VocabEntry(**defaults)  # type: ignore[typeddict-item]


class TestConfidence:
    def test_all_fields_complete(self):
        e = _entry(pos="n.", zh_definition="測試", frequency=3, ipa_us="/t/", ipa_uk="/t/")
        c = compute_confidence(e)
        assert c >= 0.8

    def test_word_only(self):
        e = _entry()
        c = compute_confidence(e)
        assert c <= 0.6  # word(1.0) / 2.0 = 0.5

    def test_suspicious_word(self):
        e = _entry(word="apple123")
        c = compute_confidence(e)
        # word gets 0.5 instead of 1.0
        assert c < compute_confidence(_entry(word="apple"))


class TestIssues:
    def test_missing_pos(self):
        e = _entry(pos=None)
        issues = compute_issues(e, 0.5)
        assert "missing_pos" in issues

    def test_missing_definition(self):
        e = _entry(zh_definition=None)
        issues = compute_issues(e, 0.5)
        assert "missing_definition" in issues

    def test_suspicious_word(self):
        e = _entry(word="apple123")
        issues = compute_issues(e, 0.5)
        assert "suspicious_word" in issues

    def test_low_confidence(self):
        e = _entry()
        issues = compute_issues(e, 0.3)
        assert "low_confidence" in issues

    def test_no_issues_when_ok(self):
        e = _entry(pos="n.", zh_definition="測試")
        issues = compute_issues(e, 0.8)
        assert issues == []


class TestQAReport:
    def test_report_fields(self):
        raw = [_entry(word="a"), _entry(word="a"), _entry(word="b")]
        cleaned = [
            CleanedEntry(
                word="a", pos=None, zh_definition=None, frequency=None,
                source_page=[1, 2], ipa_us=None, ipa_uk=None,
                parse_confidence=0.5, issues=["missing_pos", "missing_definition"],
            ),
            CleanedEntry(
                word="b", pos=None, zh_definition=None, frequency=None,
                source_page=[1], ipa_us=None, ipa_uk=None,
                parse_confidence=0.5, issues=["missing_pos", "missing_definition"],
            ),
        ]
        report = generate_qa_report(raw, cleaned)
        assert report["total_raw"] == 3
        assert report["total_cleaned"] == 2
        assert report["duplicates_removed"] == 1
        assert report["low_confidence_count"] == 0
        assert "word" in report["field_completeness"]
        assert report["field_completeness"]["word"] == 1.0

    def test_write(self, tmp_outdir):
        report = generate_qa_report([], [])
        path = write_qa_report(report, tmp_outdir)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["total_raw"] == 0
