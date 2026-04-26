# Phase 07: enhanced-nlp - Research

**Researched:** 2026-04-25  
**Domain:** Intent extraction quality, multilingual normalization, synonym recall  
**Confidence:** MEDIUM

## Summary

Current NLP is deterministic and regex/keyword driven in `src/app/nlp/intent.py`. This supports stable behavior but is brittle for:
- non-English phrasing,
- semantic variants not in static keyword lists,
- ambiguous wording where confidence scoring needs stronger calibration.

A phased plan inside this phase reduces risk:
1. Strengthen extraction and ambiguity gates first.
2. Add multilingual normalization with explicit fallback behavior.
3. Expand synonym mapping with conflict-safe scoring and regression tests.

## Requirements Alignment

| Requirement | Support |
|---|---|
| INTENT-02 | Broader and more accurate extraction across languages and phrasing variants. |
| INTENT-03 | Improved ambiguity/confidence quality for follow-up question triggering. |
| INTENT-04 | More robust normalization reduces clarification churn and preserves turn continuity. |

## Recommended Delivery Shape

- **Plan 07-01:** Accuracy + ambiguity calibration hardening.
- **Plan 07-02:** Multilingual normalization and language-aware parsing.
- **Plan 07-03:** Synonym expansion + regression coverage and tuning.
