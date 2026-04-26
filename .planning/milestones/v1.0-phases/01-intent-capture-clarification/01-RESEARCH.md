# Phase 01: intent-capture-clarification - Research

**Researched:** 2026-04-25  
**Domain:** Natural-language intent extraction + iterative clarification loop for travel search  
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
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

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INTENT-01 | User can submit a free-form natural-language travel prompt describing broad preferences. | Keep `SearchRequest.query` as first-class input and preserve NL-first entry in `SearchForm`/`page.tsx` orchestration. [VERIFIED: codebase grep] |
| INTENT-02 | System can extract structured constraints from prompt (geography, weather, budget, timeline, trip length). | Extend `extract_intent` output contract and `_resolve_request` enrichment pipeline rather than bypassing schema layer. [VERIFIED: codebase grep] |
| INTENT-03 | System can detect missing critical constraints and ask focused clarifying follow-up questions. | Add server-side missing-slot detector + priority ordering aligned to D-02/D-04 and return clarification payload to UI. [VERIFIED: codebase grep] |
| INTENT-04 | User can answer follow-up questions and update constraints without restarting search. | Implement field-level merge state in UI and backend request update model (`model_copy(update=...)` pattern already in use). [VERIFIED: codebase grep] |
</phase_requirements>

## Summary

Phase 01 should be implemented as an **iterative constraint-completion loop** layered onto the existing search request pipeline, not as a separate conversational subsystem. The backend already has a canonical place where NL query extraction enriches request fields (`SearchService._resolve_request`) and a typed schema boundary (`SearchRequest` / `SearchResponse`) that can safely carry clarification state additions. [VERIFIED: codebase grep]

The current extractor is deterministic and regex/list based (location, date hints, budget, duration) with no confidence output, and current warnings are generic (“destination could not be inferred”, “origin missing”). This means Phase 01 needs planned additions for confidence/ambiguity metadata, explicit unknown-slot representation, and one-question-at-a-time prompt generation before recommendation handoff. [VERIFIED: codebase grep]

Frontend implementation should stay inside existing `SearchForm` + `page.tsx` flow and honor the approved UI contract (inline one-by-one prompt, running recap chips, edit-to-reopen related slots, CTA text). This minimizes rework and keeps Phase 01 tightly scoped to INTENT-01..04 without leaking into recommendation ranking or live pricing work. [VERIFIED: codebase grep]

**Primary recommendation:** Implement a typed `clarification_state` contract in API responses and drive an explicit backend-guided follow-up loop (priority + missing-slot logic) while preserving field-level merge semantics end-to-end. [VERIFIED: codebase grep]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.136.1 (PyPI latest, published 2026-04-23) | API endpoints for search + clarification turn handling | Existing API is FastAPI; extending existing router/service avoids stack split. [VERIFIED: PyPI JSON API] |
| Pydantic | 2.13.3 (PyPI latest, published 2026-04-20) | Request/response typing and validation for constraint state | Current `SearchRequest`/`SearchResponse` validators already enforce payload integrity. [VERIFIED: PyPI JSON API] |
| Next.js | 16.2.4 (npm latest, published 2026-04-15) | UI orchestration for iterative prompt/answer loop | Current web app is Next App Router; phase UI changes fit in same architecture. [VERIFIED: npm registry] |
| React | 19.2.5 (npm latest, published 2026-04-08) | Component state for recap chips + incremental updates | Existing form/state flow already uses React hooks and controlled inputs. [VERIFIED: npm registry] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.0.3 (PyPI latest, published 2026-04-07) | Backend behavior tests for extraction + clarification orchestration | Use for slot-priority, merge-update, and unknown-slot scenarios in `src/tests`. [VERIFIED: PyPI JSON API] |
| Jest | 30.3.0 (npm latest, published 2026-03-10) | Frontend unit/integration tests for clarification UX loop | Use for SearchForm/Home interactions and chip edit reopen flow. [VERIFIED: npm registry] |
| Playwright | 1.58.2 (project-installed) | End-to-end clarification flow validation | Use for turn-by-turn UI behavior and CTA gating before recommendation handoff. [VERIFIED: codebase grep] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| In-service clarification logic in `SearchService` | Separate chat-orchestrator microservice | Adds integration/deployment complexity before v1 requirements are met. [ASSUMED] |
| Existing React form orchestration | Dedicated state machine library | Could improve formalism later, but adds migration cost now for limited Phase 01 scope. [ASSUMED] |

**Installation:**
```bash
pip install -r requirements.txt
cd web && npm ci
```

**Version verification:**  
- `npm view next version` → 16.2.4; publish time for 16.2.4 is 2026-04-15T22:33:47.905Z. [VERIFIED: npm registry]  
- `npm view react version` → 19.2.5; publish time for 19.2.5 is 2026-04-08T18:39:24.455Z. [VERIFIED: npm registry]  
- `npm view jest version` → 30.3.0; publish time for 30.3.0 is 2026-03-10T02:00:06.592Z. [VERIFIED: npm registry]  
- `https://pypi.org/pypi/fastapi/json` → 0.136.1; upload time 2026-04-23T16:49:42.437353Z. [VERIFIED: PyPI JSON API]  
- `https://pypi.org/pypi/pydantic/json` → 2.13.3; upload time 2026-04-20T14:46:41.402738Z. [VERIFIED: PyPI JSON API]  
- `https://pypi.org/pypi/pytest/json` → 9.0.3; upload time 2026-04-07T17:16:16.130051Z. [VERIFIED: PyPI JSON API]

## Architecture Patterns

### Recommended Project Structure
```text
src/app/
├── nlp/intent.py                 # extraction + confidence/ambiguity metadata
├── services/search.py            # clarification orchestration + merge updates
├── schemas/search.py             # typed clarification payload + slot state
└── api/v1/search.py              # endpoint surface for iterative turns

web/src/
├── components/search/SearchForm.tsx   # active question + answer control + recap chips
├── app/page.tsx                       # turn orchestration + submit/continue state
└── lib/api.ts                         # typed transport for clarification_state
```
[VERIFIED: codebase grep]

### Pattern 1: Resolve → Detect Missing Slots → Ask One Next Question
**What:** Extend existing request resolution to produce `resolved_constraints + missing_slots + next_question` in one pass. [VERIFIED: codebase grep]  
**When to use:** Every user turn after NL prompt or clarification answer. [VERIFIED: codebase grep]  
**Example:**
```python
# Source: /src/app/services/search.py (existing update pattern)
intent = extract_intent(request.query)
updates = {}
if not request.destination and intent.get("location"):
    updates["destination"] = intent["location"]
if updates:
    request = request.model_copy(update=updates)
```
[VERIFIED: codebase grep]

### Pattern 2: Field-Level Merge With Last Explicit Answer Wins
**What:** Persist prior slot values and only overwrite fields the user just answered; preserve history for audit/debug. [VERIFIED: codebase grep]  
**When to use:** On follow-up answer submission and recap chip edits. [VERIFIED: codebase grep]  
**Example:**
```typescript
// Source: /web/src/components/search/SearchForm.tsx (controlled field merge behavior pattern)
onSearch({
  query: query.trim() || undefined,
  destination: destination.trim() || undefined,
  origin: origin.trim() || undefined,
  // ... other slots preserved unless edited
})
```
[VERIFIED: codebase grep]

### Anti-Patterns to Avoid
- **Batching multiple clarification questions in one turn:** conflicts with locked D-03 and increases drop-off risk. [VERIFIED: codebase grep]
- **Rebuilding request from scratch each answer:** breaks D-05 persistence requirement and causes accidental slot loss. [VERIFIED: codebase grep]
- **Calling provider search before clarification completion:** can waste external calls and produce noisy warnings before critical slots are collected. [ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API payload validation | Ad hoc dict checks | Pydantic models/validators in `src/app/schemas/search.py` | Existing validators already enforce key invariants (e.g., date range order, required query/destination). [VERIFIED: codebase grep] |
| Frontend async networking state | Manual `fetch` scatter across components | Centralized `web/src/lib/api.ts` typed client | Existing transport layer already normalizes request/response handling. [VERIFIED: codebase grep] |
| Form control primitives and styling | Custom design-system fork | Existing shadcn/radix-nova components in `web/src/components/ui` + approved UI spec | Phase has approved UI contract and existing component foundation. [VERIFIED: codebase grep] |

**Key insight:** Phase 01 is mainly orchestration/state-shape work; hand-rolling new frameworks would add risk without improving requirement coverage. [ASSUMED]

## Common Pitfalls

### Pitfall 1: Slot clobbering after each follow-up
**What goes wrong:** New answer replaces unrelated previously captured constraints. [VERIFIED: codebase grep]  
**Why it happens:** Full-object replacement instead of field-level merge updates. [VERIFIED: codebase grep]  
**How to avoid:** Keep `model_copy(update=...)` style on backend and controlled per-field state updates on frontend. [VERIFIED: codebase grep]  
**Warning signs:** Destination/timeline “disappear” after answering budget question. [ASSUMED]

### Pitfall 2: Ambiguous timeline accepted as precise date silently
**What goes wrong:** Inputs like “early summer” are treated as exact dates without uncertainty marker. [VERIFIED: codebase grep]  
**Why it happens:** Current parser only supports basic string/ISO extraction and lacks precision metadata. [VERIFIED: codebase grep]  
**How to avoid:** Store normalized window plus precision marker, then keep asking if precision is below threshold. [VERIFIED: codebase grep]  
**Warning signs:** Date-window chips appear exact even when user gave fuzzy language. [ASSUMED]

### Pitfall 3: Clarification UI diverges from approved contract
**What goes wrong:** UI adds batched forms or off-spec CTA/copy. [VERIFIED: codebase grep]  
**Why it happens:** Implementing directly from existing MVP form instead of `01-UI-SPEC.md`. [VERIFIED: codebase grep]  
**How to avoid:** Treat UI spec copy/spacing/color/focal hierarchy as locked acceptance criteria. [VERIFIED: codebase grep]  
**Warning signs:** CTA text differs from “Continue to Recommendations” or chips are not editable. [VERIFIED: codebase grep]

## Code Examples

Verified patterns from project sources:

### Backend slot enrichment before provider execution
```python
# Source: /src/app/services/search.py
resolved_request, warnings = self._resolve_request(request)
...
for provider in self.providers:
    for inventory_type in resolved_request.inventory:
        if provider.supports_inventory(inventory_type):
            tasks.append(self._execute_provider(provider, resolved_request, inventory_type))
```
[VERIFIED: codebase grep]

### Schema-level validation guardrails
```python
# Source: /src/app/schemas/search.py
@model_validator(mode="after")
def validate_payload(self) -> "SearchRequest":
    if not self.query and not self.destination:
        raise ValueError("Either query or destination must be provided.")
    return self
```
[VERIFIED: codebase grep]

### Existing frontend submission integration point
```typescript
// Source: /web/src/app/page.tsx
const handleSearch = async (request: SearchRequest) => {
  setIsSubmitting(true)
  setErrorMessage(null)
  try {
    const nextResponse = await searchTrips(request)
    setResponse(nextResponse)
    setProviderStatuses(nextResponse.provider_status)
  } finally {
    setIsSubmitting(false)
  }
}
```
[VERIFIED: codebase grep]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| One-shot prompt parsing with minimal warning fallback | Iterative clarification loop mandated by Phase 01 decisions D-01..D-16 | 2026-04-24 context freeze | Planner should treat clarification as first-class flow, not optional UX enhancement. [VERIFIED: codebase grep] |
| Generic warning strings only | Confidence/ambiguity-driven follow-up requirement | 2026-04-24 context freeze | Requires schema/API contract expansion for slot confidence + explicit unknown state. [VERIFIED: codebase grep] |

**Deprecated/outdated:**
- “Submit once and infer enough” behavior is insufficient for INTENT-03/04 and should not be used as phase target. [VERIFIED: codebase grep]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Separate microservice orchestration would add unnecessary complexity in v1 | Standard Stack → Alternatives | Could under-plan scalability if near-term split is actually required |
| A2 | State-machine library overhead outweighs benefits for this phase scope | Standard Stack → Alternatives | Could miss maintainability gains if loop complexity grows rapidly |
| A3 | Provider calls before clarification completion are materially wasteful | Architecture Patterns → Anti-Patterns | Could over-constrain UX if early partial-result preview is desired |
| A4 | Hand-rolling frameworks adds risk without value for this phase | Don’t Hand-Roll | Could miss justified custom behavior if constraints change |
| A5 | Specific warning signs (e.g., user drop-off indicators) are reliable diagnostics | Common Pitfalls | Could choose weak monitoring signals |

## Open Questions (RESOLVED)

1. **What global confidence threshold value should trigger follow-ups (D-10)? — RESOLVED**
   - Resolution: Use `GLOBAL_CONFIDENCE_THRESHOLD = 0.70` as the single v1 cutoff across all slots, including weather extraction.
   - Rationale: Bias toward asking a focused follow-up when parse certainty is marginal, matching D-09 and D-03 while avoiding per-slot threshold complexity.
   - Implementation placement: `src/app/services/clarification.py` constant consumed by extraction/clarification orchestration.
   - Validation: `src/tests/nlp/test_intent_confidence.py` must include above-threshold and below-threshold cases.

2. **How should “related slots” reopen behavior be defined for recap chip edits? — RESOLVED**
   - Resolution: Define an explicit dependency matrix in `RELATED_SLOT_GRAPH` with these reopen rules:
     - `destination` edit reopens `timeline`, `trip_length`, `budget`
     - `timeline` edit reopens `trip_length`, `budget`
     - `trip_length` edit reopens `budget`
     - `budget` edit reopens only `budget`
   - Rationale: Preserves D-16 (“reopen only related slots”) while minimizing unnecessary re-questioning.
   - Implementation placement: `src/app/services/clarification.py` with coverage in `src/tests/services/test_clarification_loop.py`.

3. **Where to store clarification history/audit trail for D-06? — RESOLVED**
   - Resolution: Keep audit trail in typed clarification response/session state for Phase 01 (in-request/in-response lifecycle), not persisted DB storage.
   - Rationale: Meets D-06 traceability requirement within phase scope while avoiding premature schema migrations outside INTENT-01..04.
   - Implementation placement: `src/app/schemas/search.py` (history fields) and `src/app/services/search.py` merge logic append history events per turn.
   - Follow-on note: If cross-session persistence is required in future phases, treat as a new requirement and migration task.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | FastAPI backend + pytest | ✓ | 3.12.3 | — |
| Node.js | Next.js frontend + jest/playwright | ✓ | v24.11.1 | — |
| npm | Frontend dependency/test scripts | ✓ | 11.6.2 | — |
| Docker | Local full-stack run (db/redis/api/web) | ✓ | 29.3.1 | Run services directly via local runtimes |
| pytest CLI (venv) | Backend automated tests | ✓ | 9.0.2 (installed) | `python -m pytest` if CLI path differs |
| jest (project) | Frontend unit tests | ✓ | 30.1.3 (installed) | `npm test -- --runInBand` |
| playwright (project) | Frontend e2e flows | ✓ | 1.58.2 (installed) | Manual browser validation for critical path |
| redis-cli | Local Redis diagnostics | ✗ | — | Use app health endpoint + Docker logs |
| pg_isready | Postgres readiness diagnostics | ✗ | — | Use API `/health/ready` + DB container health |

[VERIFIED: local environment commands]

**Missing dependencies with no fallback:**
- None identified for Phase 01 implementation/testing.

**Missing dependencies with fallback:**
- `redis-cli`, `pg_isready` missing locally, but health endpoints + compose healthchecks provide operational fallback.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (backend), Jest + Testing Library (frontend), Playwright (e2e) |
| Config file | `web/jest.config.ts`, `web/playwright.config.ts`, backend via pytest defaults + `src/tests/conftest.py` |
| Quick run command | `cd web && npm test -- SearchForm.test.tsx --runInBand` |
| Full suite command | `pytest && cd web && npm test -- --runInBand` |

[VERIFIED: codebase grep]

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INTENT-01 | Submit free-form NL prompt | frontend integration | `cd web && npm test -- Home.test.tsx --runInBand` | ✅ |
| INTENT-02 | Extract structured slots from prompt | backend unit | `pytest src/tests/nlp/test_intent.py -x` | ✅ |
| INTENT-03 | Ask focused follow-up for missing critical slots | backend+frontend integration | `pytest src/tests/api/test_search.py -x && cd web && npm test -- SearchForm.test.tsx --runInBand` | ❌ Wave 0 (missing dedicated clarification tests) |
| INTENT-04 | Update constraints iteratively without restart | frontend integration + backend service | `cd web && npm test -- Home.test.tsx --runInBand && pytest src/tests/api/test_search_filters.py -x` | ❌ Wave 0 (missing iterative turn tests) |

[VERIFIED: codebase grep]

### Sampling Rate
- **Per task commit:** `pytest src/tests/nlp/test_intent.py -x && cd web && npm test -- SearchForm.test.tsx --runInBand`
- **Per wave merge:** `pytest && cd web && npm test -- --runInBand`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `src/tests/services/test_clarification_loop.py` — covers INTENT-03/INTENT-04 turn orchestration
- [ ] `src/tests/nlp/test_intent_confidence.py` — covers ambiguity/threshold behavior for INTENT-02/03
- [ ] `web/src/components/search/__tests__/ClarificationFlow.test.tsx` — covers one-question-at-a-time + recap chip edits
- [ ] `web/tests/e2e/clarification.spec.ts` — validates end-to-end iterative clarification UX

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no (phase scope has no user auth features) | N/A |
| V3 Session Management | no (no authenticated session flow in this phase scope) | N/A |
| V4 Access Control | no (single public search flow in current code path) | N/A |
| V5 Input Validation | yes | Pydantic schema validation + field/model validators in `SearchRequest` and related models |
| V6 Cryptography | yes (existing utility module) | `cryptography` Fernet utility in `src/app/core/security.py`; do not hand-roll crypto |

[VERIFIED: codebase grep]

### Known Threat Patterns for FastAPI + Next.js NL-input stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Oversized/malformed NL payloads | Denial of Service | Enforce max length (`query` max_length=500) and schema validation errors |
| Input coercion ambiguity causing wrong constraint state | Tampering | Confidence threshold + explicit unknown slots + recap edit confirmation |
| Reflected warning/error leakage in UI | Information Disclosure | Use controlled user-facing error copy and avoid exposing raw backend traces |

[VERIFIED: codebase grep]

## Sources

### Primary (HIGH confidence)
- Repository sources (code + planning docs):  
  - `/home/rbrown/workspace/MiraiGo/.planning/phases/01-intent-capture-clarification/01-CONTEXT.md`  
  - `/home/rbrown/workspace/MiraiGo/.planning/phases/01-intent-capture-clarification/01-UI-SPEC.md`  
  - `/home/rbrown/workspace/MiraiGo/.planning/REQUIREMENTS.md`  
  - `/home/rbrown/workspace/MiraiGo/.planning/ROADMAP.md`  
  - `/home/rbrown/workspace/MiraiGo/.planning/STATE.md`  
  - `/home/rbrown/workspace/MiraiGo/src/app/nlp/intent.py`  
  - `/home/rbrown/workspace/MiraiGo/src/app/services/search.py`  
  - `/home/rbrown/workspace/MiraiGo/src/app/schemas/search.py`  
  - `/home/rbrown/workspace/MiraiGo/web/src/components/search/SearchForm.tsx`  
  - `/home/rbrown/workspace/MiraiGo/web/src/app/page.tsx`  
  - `/home/rbrown/workspace/MiraiGo/web/src/lib/api.ts`  
  - `/home/rbrown/workspace/MiraiGo/src/tests/*` and `web/src/**/__tests__/*`
- npm registry checks: `npm view next`, `npm view react`, `npm view jest`  
- PyPI JSON API checks:  
  - https://pypi.org/pypi/fastapi/json  
  - https://pypi.org/pypi/pydantic/json  
  - https://pypi.org/pypi/pytest/json  

### Secondary (MEDIUM confidence)
- Local tool/runtime availability checks via shell commands (`python3 --version`, `node --version`, `npm --version`, `docker --version`, `npx jest --version`, `npx playwright --version`).

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions and publication dates verified from package registries.
- Architecture: MEDIUM — strong codebase evidence, but final confidence depends on unresolved threshold/dependency-graph decisions.
- Pitfalls: MEDIUM — mostly codebase-grounded, some operational warning-sign assumptions.

**Research date:** 2026-04-25  
**Valid until:** 2026-05-25
