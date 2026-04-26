# Phase 06: fix-intent-extraction-for-timeline-and-destination-parsing - Research

**Researched:** 2026-04-25  
**Domain:** NLP extraction reliability for destination + timeline slots  
**Confidence:** MEDIUM

## Findings

1. Extraction currently relies on regex + heuristic lists in `src/app/nlp/intent.py`.
2. Date-range parsing already attempts to avoid route phrase confusion with `_looks_like_timeline_fragment`, but edge phrasing remains fragile.
3. Destination extraction still allows broad fallback on capitalized tokens, which can introduce false positives.
4. Clarification flow quality depends on slot metadata confidence/ambiguity produced by `extract_intent`.

## Recommended Direction

- Expand targeted NLP tests first for known ambiguous phrasing.
- Refactor destination/timeline extraction into clearer helper steps with explicit precedence.
- Preserve compatibility output keys while tightening parse confidence semantics.
- Validate no regressions in clarification sequencing (`SearchService._resolve_request` + service tests).

## Requirements Alignment

| Requirement | Support |
|---|---|
| INTENT-02 | Structured extraction remains accurate across route/date phrasing edge cases. |
| INTENT-03 | Ambiguous parses remain detectable via slot metadata for follow-up questions. |
| INTENT-04 | Stable metadata prevents clarification loop churn caused by parse inconsistencies. |
