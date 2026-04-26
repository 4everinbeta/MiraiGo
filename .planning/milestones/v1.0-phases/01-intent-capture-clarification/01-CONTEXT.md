# Phase 1: Intent Capture & Clarification - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn vague travel prompts into complete, actionable search constraints by (1) accepting free-form intent, (2) extracting structured slots, (3) asking focused follow-up questions for missing critical slots, and (4) letting users continue the same search without restarting.

</domain>

<decisions>
## Implementation Decisions

### Clarification Strategy
- **D-01:** Trigger a follow-up when any critical slot is missing.
- **D-02:** Critical slots are: destination/region, timeline/date-window, trip length, and budget.
- **D-03:** Ask one focused follow-up at a time.
- **D-04:** Follow-up priority order is: destination/region → timeline/date-window → trip length → budget.

### Constraint Memory & Update Model
- **D-05:** Use field-level merge updates; only answered slots change, existing slots persist.
- **D-06:** Latest explicit user answer overrides previous extracted values; preserve prior values in history/audit trail.
- **D-07:** After each answer, immediately re-run missing-slot detection and continue iterative clarification as needed.
- **D-08:** If user is uncertain (e.g., “I don’t know”), store slot as explicit unknown and continue with warning-aware broader recommendations.

### Intent Extraction Behavior
- **D-09:** For each slot, trigger follow-up on low confidence or ambiguous parse (not only total parse failure).
- **D-10:** Use a single global confidence threshold for v1.
- **D-11:** Normalize flexible timeline language (e.g., “early summer”, “next month”) into a date window plus precision marker.
- **D-12:** Map qualitative budgets (e.g., “cheap”, “mid-range”) into bounded normalized ranges while preserving original text.

### Conversation UX Flow
- **D-13:** Present clarification inline as conversational one-by-one prompts with a running constraint summary.
- **D-14:** End clarification when all critical slots are either known or explicitly unknown.
- **D-15:** Before recommendation handoff, show a recap with editable constraint chips and a continue CTA.
- **D-16:** If a recap chip is edited, reopen only related clarification slots instead of restarting full clarification.

### Claude's Discretion
- Choose concrete confidence threshold value and calibration method during planning.
- Define exact “related slots” dependency graph used when recap chips are edited.
- Define warning copy tone and UI microcopy details.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and requirement definitions
- `.planning/ROADMAP.md` — Phase 1 goal, dependency, and success criteria (Intent Capture & Clarification).
- `.planning/REQUIREMENTS.md` — INTENT-01, INTENT-02, INTENT-03, INTENT-04 requirement definitions.
- `.planning/PROJECT.md` — product scope, core value, and constraints for v1 natural-language-first interaction.

### Project state and sequencing context
- `.planning/STATE.md` — current milestone position and sequencing context for Phase 1 kickoff.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/app/nlp/intent.py`: existing extraction hooks for location, date/date_range, budget, and duration.
- `src/app/services/search.py` (`_resolve_request`): current slot enrichment + warning pipeline and request model updates.
- `src/app/schemas/search.py`: typed request/response schema and validation envelope for search constraints.
- `web/src/components/search/SearchForm.tsx`: current natural-language query entry and structured constraint controls.
- `web/src/app/page.tsx`: orchestration shell for submitting requests and showing result/error state.

### Established Patterns
- Search flow is request/response with `SearchRequest` payload and server-side request resolution.
- Warnings are first-class output (`SearchResponse.warnings`) and already surfaced in the UI.
- Frontend currently mixes NL prompt with explicit structured fields; this can host iterative clarification.

### Integration Points
- Clarification loop should integrate between NL extraction (`extract_intent`) and provider search execution in `SearchService.search`.
- Constraint recap/edit loop should wire through `SearchForm` state and submission handler in `web/src/app/page.tsx`.
- Slot confidence/ambiguity metadata should be attached where extraction occurs and passed into follow-up orchestration.

</code_context>

<specifics>
## Specific Ideas

- Keep follow-up prompts tightly focused and sequential instead of batching many prompts.
- Recap should use editable chips so users can quickly correct one constraint without restarting.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-intent-capture-clarification*
*Context gathered: 2026-04-24*
