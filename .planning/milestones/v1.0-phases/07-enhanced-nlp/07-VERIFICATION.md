---
phase: 07-enhanced-nlp
verified: 2026-04-26T14:34:49Z
status: complete
---

# Phase 07 Verification Strategy

## Goal-Backward Checks

Phase 7 is complete only when these are true:

1. Extraction accuracy is improved for ambiguous phrasing without route/date regressions.
2. Supported multilingual queries map to canonical slots with sane confidence behavior.
3. Synonym expansion improves recall while keeping false positives constrained.
4. Clarification loop and API-level search behavior remain stable.

## Required Automated Evidence

- NLP tests covering extraction, confidence, multilingual cases, and synonyms.
- Clarification loop tests.
- API search tests affected by intent extraction behavior.

## Human/UAT Checks

1. Try mixed-language and colloquial queries end-to-end; confirm recap chips and follow-up prompts remain coherent.
2. Compare before/after behavior on known ambiguous prompts; ensure fewer incorrect confident parses.

## Fresh Rerun Evidence (2026-04-26)

- Command: `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q`
- Result: `21 passed in 2.75s`
