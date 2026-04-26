---
status: complete
phase: 07-enhanced-nlp
source: 07-01-SUMMARY.md, 07-02-SUMMARY.md, 07-03-SUMMARY.md
started: 2026-04-25T15:59:29Z
updated: 2026-04-25T16:16:25Z
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

[testing complete]

## Tests

### 1. Spanish destination + budget normalization
expected: Submit a query like "Quiero un viaje economico para lisboa en julio". Destination should resolve to Lisboa, budget should normalize to budget/cheap range, and month should normalize to July without breaking flow.
result: pass

### 2. Synonym-to-canonical quality mapping
expected: A prompt like "affordable seaside getaway to porto" should map to canonical qualities (budget + beach) rather than missing or duplicating quality slots.
result: pass

### 3. Uncertain prompt clarification priority
expected: A prompt like "Maybe somewhere warm in early summer" should keep destination ambiguous and ask destination first in clarification order.
result: pass

### 4. Date-range guardrail for non-timeline text
expected: Non-temporal "between X and Y" phrasing should not be treated as a high-confidence timeline range unless both fragments are timeline-like.
result: pass

### 5. API clarification stability with multilingual prompt
expected: POST /api/v1/search with multilingual + synonym prompt should preserve clarification state, keep destination filled, and move next question away from destination.
result: skipped
reason: "Not sure how to test this"

### 6. Unsupported-language fallback behavior
expected: Unsupported-language prompts should remain ambiguous (low-confidence destination/timeline) rather than confidently wrong extraction.
result: pass

## Summary

total: 6
passed: 5
issues: 0
pending: 0
skipped: 1
blocked: 0

## Gaps

- truth: "Destination should resolve to Lisboa, budget should normalize to budget/cheap range, and month should normalize to July without breaking flow."
  status: resolved
  reason: "Retest passed: destination now resolves for the multilingual prompt."
  severity: major
  test: 1
  root_cause: "Destination preposition handling favors explicit `to/para` forms; single-letter romance-language `a <city>` phrasing was intentionally excluded to avoid false positives and can still surface as unclear in the clarification loop."
  artifacts:
    - path: "src/app/nlp/intent.py"
      issue: "Multilingual destination preposition coverage remains conservative."
  missing:
    - "Add guarded support for `a <destination>` in romance-language travel intents without reintroducing english article false positives."
  debug_session: ".planning/debug/07-destination-unclear.md"
- truth: "Prompt should map to canonical qualities (budget + beach) without dropping prior clarified values."
  status: resolved
  reason: "Retest passed after follow-up policy and turn-session preservation fixes."
  severity: major
  test: 2
  root_cause: "Destination follow-up state can still be reopened after sequential edits due aggressive related-slot reopening, even when recap retains a destination value."
  artifacts:
    - path: "src/app/services/clarification.py"
      issue: "Related-slot reopen policy can mark destination unresolved after downstream slot edits."
    - path: "web/src/app/page.tsx"
      issue: "Turn session receives recap values but still honors backend follow-up state, surfacing repeated destination prompts."
  missing:
    - "Narrow destination reopening conditions so destination is not re-asked when a valid destination remains in resolved state."
  debug_session: ".planning/debug/07-clarification-slot-regression.md"
- truth: "Extracting early-summer timeline should prevent redundant follow-up asking when user wants to travel."
  status: resolved
  reason: "Retest passed: timeline follow-up no longer repeats for early-summer prompt."
  severity: major
  test: 3
  root_cause: "Early-summer timeline normalization is marked ambiguous with low confidence, so clarification logic still requests timeline confirmation."
  artifacts:
    - path: "src/app/nlp/intent.py"
      issue: "`early summer` currently returns confidence 0.55 with ambiguous=true."
    - path: "src/app/services/clarification.py"
      issue: "Timeline follow-up triggers when confidence stays below global threshold."
  missing:
    - "Recalibrate early-summer confidence/ambiguity policy or treat extracted season-part windows as sufficient when destination is still the primary unknown."
  debug_session: ".planning/debug/07-timeline-redundant-clarification.md"
