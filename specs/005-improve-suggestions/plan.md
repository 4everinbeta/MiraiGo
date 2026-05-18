# Implementation Plan: Improve Post-Intent Suggestions

**Branch**: `005-improve-suggestions` | **Date**: 2026-05-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-improve-suggestions/spec.md`

## Summary

Improve recommendation quality after intent capture by making suggestion ranking stricter to resolved constraints, preserving resolved slots across clarification turns, reducing duplicate suggestions, and showing stronger user-facing rationale for why each suggestion was selected.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 / React 19 + Next.js 16 (frontend)

**Primary Dependencies**: FastAPI, Pydantic, existing SearchService clarification flow, existing ranking/suggestion models, LLM-assisted suggestion generation (optional), Jest/Playwright test suites

**Storage**: PostgreSQL + Redis already in use; no new persistence stores required

**Testing**: pytest, pytest-cov, Jest + Testing Library, Playwright + axe

**Target Platform**: Dockerized web stack (Linux backend service + browser frontend)

**Project Type**: Full-stack web service (API + web UI)

**Performance Goals**: Preserve current recommendation request responsiveness while improving fit quality; no additional multi-second latency in suggestion response generation

**Constraints**: Must keep natural-language-first flow, must not regress clarification loop stability, must not introduce provider coupling into suggestion ranking logic, and must enforce deterministic hard-constraint checks before any LLM-generated suggestion is returned

**Scale/Scope**: Search/clarification sessions at current product scale; scope limited to post-intent suggestion quality (not booking expansion)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Natural Language-First | ✅ PASS | Changes occur after intent extraction and clarification, preserving NL-first entry. |
| II. Full-Stack Separation with API Contract | ✅ PASS | Plan keeps backend suggestion logic in service/domain layer and frontend rendering in existing UI components. |
| III. Test Coverage is Non-Negotiable | ✅ PASS | Phase plan includes unit + integration + E2E updates for behavior and loop stability. |
| IV. Security & Configuration Hygiene | ✅ PASS | No new secrets, no additional sensitive storage paths. |
| V. Simplicity & Focused Modules | ✅ PASS | Reuse existing search/clarification components; avoid new architectural layers. |
| VI. Resilience & Graceful Degradation | ✅ PASS | Suggestion fallback behavior remains explicit when high-fit options are unavailable. |

No gate violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/005-improve-suggestions/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── suggestion-quality-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── app/
│   ├── api/v1/search.py
│   ├── services/search.py
│   ├── services/clarification.py
│   ├── nlp/intent.py
│   ├── optimization/engine.py
│   └── schemas/search.py
└── tests/
    ├── services/test_clarification_loop.py
    ├── nlp/test_intent.py
    └── api/test_search*.py

web/
└── src/
    ├── app/page.tsx
    └── components/search/
        ├── SearchForm.tsx
        └── ResultsDashboard.tsx
```

**Structure Decision**: Keep current monorepo split (FastAPI backend + Next.js frontend) and implement changes in existing search/clarification/suggestion modules to avoid architectural drift.

## Phase 0: Outline & Research

Research outcomes documented in `research.md`:

1. Decision on suggestion fit scoring and hard-constraint handling order
2. Decision on clarification state preservation behavior across follow-up turns
3. Decision on duplicate/near-duplicate suppression strategy
4. Decision on user-facing rationale content standards
5. Decision on when LLM-generated suggestions are allowed

All technical unknowns were resolved; no remaining `NEEDS CLARIFICATION`.

### User-Confirmed Planning Decisions

1. Hard blockers for ranking are **destination + timeline + budget**.
2. If no option satisfies all hard blockers, return **best partial-fit options with clear labels**.
3. Suggestion rationale format is **one sentence + 2–3 reason tags**.
4. Default response target is **3 suggestions**.
5. LLM-generated suggestions are allowed, but only after hard blockers are validated and outputs are post-checked for constraint compliance.

## Phase 1: Design & Contracts

Generated artifacts:

- `data-model.md`: intent profile + suggestion candidate + session state model updates
- `contracts/suggestion-quality-contract.md`: behavioral contract for post-intent suggestions and clarification turn progression
- `quickstart.md`: manual validation journeys for relevance, loop-stability, and rationale quality

### Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Natural Language-First | ✅ PASS | Design assumes all flows begin from free-text intent. |
| II. Full-Stack Separation with API Contract | ✅ PASS | Contract updates stay API-first; UI consumes response metadata without backend leakage. |
| III. Test Coverage is Non-Negotiable | ✅ PASS | Quickstart and contract include explicit behavior validation points for tests. |
| IV. Security & Configuration Hygiene | ✅ PASS | No new secret/config requirements introduced. |
| V. Simplicity & Focused Modules | ✅ PASS | Design extends existing modules; no extra layer introduced. |
| VI. Resilience & Graceful Degradation | ✅ PASS | Contract explicitly defines fallback behavior when high-fit results are unavailable. |

## Complexity Tracking

No constitution exceptions or complexity waivers required.
