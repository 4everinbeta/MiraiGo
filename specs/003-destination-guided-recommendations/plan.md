# Implementation Plan: Destination Guided Recommendations

**Branch**: `003-destination-guided-recommendations` | **Date**: 2026-05-17 | **Spec**: `specs/003-destination-guided-recommendations/spec.md`

**Input**: Feature specification from `/specs/003-destination-guided-recommendations/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Introduce a destination-first conversational clarification flow for destination-missing intents, including region suggestions, “don’t care” popular picks, richer preference capture, and comparison-ready recommendation bundles. Extend the existing flight-first flow to support nearby-date price alternatives and lodging follow-through tied to selected flight/date context, while preserving graceful degradation across providers.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 / React 19.2.3 (frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, Redis client, httpx, Next.js App Router, SWR/Axios, shadcn/ui

**Storage**: PostgreSQL 16 for persisted search runs, Redis 7 for cache/token/session-like transient state

**Testing**: pytest + pytest-cov, Jest + Testing Library, Playwright + @axe-core/playwright

**Target Platform**: Linux containers via Docker Compose (local), Railway/Azure service deployment

**Project Type**: Web application (API + web frontend)

**Performance Goals**: Clarification responses feel interactive (<2s perceived for non-live steps); live search should return usable partial results within provider deadlines

**Constraints**: Must not crash when optional providers/credentials are unavailable; preserve existing `/api/v1/search` compatibility; avoid adding new architectural layers beyond routes → services → providers/NLP

**Scale/Scope**: MVP scale for conversational trip discovery with multi-destination comparison and live provider fan-out in a single-session workflow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Natural Language-First**: PASS — feature starts from free-text query and expands clarification.
- **II. Full-Stack Separation with API Contract**: PASS — work remains in API schemas/services/providers and web UI consumers via `/api/v1/`.
- **III. Test Coverage is Non-Negotiable**: PASS — plan includes backend parser/service tests plus frontend unit/E2E updates.
- **IV. Security & Configuration Hygiene**: PASS — no new secret model; optional provider behavior remains graceful.
- **V. Simplicity & Focused Modules**: PASS — extend existing clarification and search orchestration, no extra layer.
- **VI. Resilience & Graceful Degradation**: PASS — partial/empty provider behavior explicitly preserved in design.

**Post-Design Re-check**: PASS — Phase 1 artifacts keep route→service→provider boundaries, define fallback behavior for destination suggestions and partial live inventory, and do not introduce constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-destination-guided-recommendations/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── search-clarification-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── app/
│   ├── api/v1/search.py
│   ├── nlp/intent.py
│   ├── schemas/search.py
│   ├── services/
│   │   ├── clarification.py
│   │   └── search.py
│   └── providers/
└── tests/
    ├── nlp/
    ├── services/
    └── api/

web/
├── src/
│   ├── app/page.tsx
│   ├── lib/api.ts
│   └── components/search/
└── tests/e2e/
```

**Structure Decision**: Keep current full-stack split (`src/` backend + `web/` frontend) and implement feature changes in existing NLP, schema, service orchestration, API contract, and search UI surfaces.

## Complexity Tracking

No constitution violations requiring exception.
