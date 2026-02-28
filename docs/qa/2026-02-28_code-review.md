# Code Review - pdf-parser (2026-02-28)

## Scope
- `src/pdf_parser/**`
- `tests/**`
- `openspec/changes/pdf-parser/specs/**`

## Findings

### CRITICAL

1. `parse_confidence` scoring diverges from spec acceptance for "word-only" entries.
- Evidence:
  - Spec requires word-only confidence `<= 0.3`: `openspec/changes/pdf-parser/specs/qa-report/spec.md:35`
  - Current implementation returns `0.5` for word-only because total weight is `2.0`: `src/pdf_parser/qa.py:14`, `src/pdf_parser/qa.py:17`, `src/pdf_parser/qa.py:39`
  - Test expectation was weakened to `<= 0.6`: `tests/test_qa.py:26`
- Risk:
  - QA confidence threshold semantics are inflated; low-quality records may be treated as acceptable.
- Recommendation:
  - Recalibrate `compute_confidence()` to satisfy spec scenario (`word-only <= 0.3`) and update tests accordingly.

2. Unparseable lines are dropped without recording low-confidence items, conflicting with spec.
- Evidence:
  - Spec requires "skip but record as low-confidence": `openspec/changes/pdf-parser/specs/vocab-parse/spec.md:27`
  - Implementation only appends when parsed, with no tracking path for failed lines: `src/pdf_parser/parser.py:58`, `src/pdf_parser/parser.py:60`, `src/pdf_parser/parser.py:68`, `src/pdf_parser/parser.py:70`
- Risk:
  - QA report undercounts parsing uncertainty; difficult to audit parser quality regressions.
- Recommendation:
  - Add failed-line tracking (e.g., parse failures counter or rejected-items list) and surface in QA/report output.

### WARNING

1. Issues are computed before trim/null normalization, causing possible false negatives.
- Evidence:
  - Issues calculated from raw entry first: `src/pdf_parser/cleaner.py:43`, `src/pdf_parser/cleaner.py:44`
  - Trim/null conversion happens later: `src/pdf_parser/cleaner.py:63`, `src/pdf_parser/cleaner.py:64`, `src/pdf_parser/cleaner.py:65`
- Risk:
  - Input such as `pos="   "` becomes `None` after cleaning but may miss `missing_pos` issue tagging.
- Recommendation:
  - Compute issues/confidence on normalized values (after trim/null conversion) or normalize a copy before scoring.

2. Rule loader may crash for classes requiring constructor args.
- Evidence:
  - `load_rule()` probes classes by calling `attr()` directly: `src/pdf_parser/parser.py:24`
- Risk:
  - Custom rule modules can fail at load time unexpectedly (TypeError) even if valid parser exists.
- Recommendation:
  - Guard instantiation with `try/except TypeError` and continue scanning, or use an explicit exported symbol contract.

### SUGGESTION

1. Generated artifacts in `output/` are large and currently tracked.
- Evidence:
  - `output/vocab.raw.json`, `output/vocab.cleaned.json`, `output/vocab.qa_report.json` present in changes.
- Risk:
  - Repo noise and large diffs in future commits.
- Recommendation:
  - Decide policy: keep only minimal fixtures for tests, and git-ignore runtime outputs if not required as release artifacts.

## Test Gap Summary
- Existing tests pass (`37 passed`) but do not enforce two critical spec constraints:
  - word-only confidence upper bound (`<= 0.3`)
  - unparseable-line low-confidence recording path
