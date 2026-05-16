<!--
  Sync Impact Report
  ==================
  Version change: 1.0.0 → 1.1.0 (MINOR: provider architecture additions, services layer
  acknowledgement, Duffel/Amadeus integration, graceful degradation, deployment target)

  Modified principles:
    II. Full-Stack Separation with API Contract — added provider adapter + services layer detail
    IV. Security & Configuration Hygiene — expanded to cover Duffel/Amadeus token handling
    V. Simplicity & Focused Modules — corrected: services layer is intentional, not prohibited

  Added sections:
    VI. Resilience & Graceful Degradation (new principle)
    Tech Stack Constraints table — added Duffel, Amadeus, provider registry, deployment targets

  Removed sections: N/A

  Templates requiring updates:
    ✅ .specify/templates/plan-template.md — Constitution Check gates reflect 6 principles
    ✅ .specify/templates/spec-template.md — no structural change required
    ✅ .specify/templates/tasks-template.md — task phases reflect services + providers layers

  Follow-up TODOs: None — all fields resolved from README, config.py, and directory inspection.
-->

# MiraiGo Travel Discovery Constitution

## Core Principles

### I. Natural Language-First

The primary user interface MUST accept free-text travel queries; structured forms MUST NOT gate the
initial search experience. The NLP pipeline (`src/app/nlp/intent.py`) MUST convert vague intent into
ranked destination suggestions via `extract_intent` → scraper fan-out → `rank_results`. Every feature
that touches search MUST preserve this end-to-end flow.

**Rationale**: MiraiGo's core value is removing friction between a traveler's vague idea and
personalized suggestions. Forcing rigid input first undermines the product promise.

### II. Full-Stack Separation with API Contract

The backend (Python 3.12 / FastAPI under `src/`) and frontend (TypeScript 5 / Next.js under `web/`)
MUST remain independently buildable and testable. All cross-stack communication MUST go through the
versioned REST API (`/api/v1/`). Frontend code MUST NOT import or embed backend logic, and backend
code MUST NOT reference frontend assets.

The backend is structured in deliberate layers: route handlers (`src/app/api/v1/`) call services
(`src/app/services/`), which orchestrate provider adapters (`src/app/providers/`). The provider
registry (`src/app/providers/registry.py`) is the single point for registering live and fallback
providers. New travel data sources MUST be implemented as provider adapters, not inlined into routes.

**Rationale**: Clean separation enables independent deployment, testing, and iteration of each tier.
The provider adapter layer decouples the search pipeline from individual third-party API details,
making it safe to add, remove, or swap providers without touching route logic.

### III. Test Coverage is Non-Negotiable

- Backend: every new module MUST have a corresponding `pytest` test file under `src/tests/` mirroring
  the source path. `pytest --cov=src` MUST pass with no regressions before merging.
- Frontend (unit): new React components MUST have a Jest / Testing Library test in
  `web/src/components/<area>/__tests__/` or `web/src/__tests__/`.
- Frontend (E2E): user-facing flows MUST be covered by a Playwright test in `web/tests/e2e/`.
- Accessibility: Playwright tests MUST include `@axe-core/playwright` checks for all primary pages.
- Tests MUST be written before or alongside implementation — not as a post-merge afterthought.

**Rationale**: The scraper and NLP layers have complex branching; untested changes silently degrade
result quality. E2E tests protect the conversational search UX that defines the product.

### IV. Security & Configuration Hygiene

- Secrets (database credentials, provider API keys) MUST be loaded exclusively from `.env` via
  `src/app/core/config.py` (`pydantic-settings`). Secrets MUST NOT be committed to source control.
  A checked-in `.env.example` MUST document every required and optional variable.
- Sensitive model fields (e.g., search history) MUST use Fernet encryption via
  `src/app/core/security.py` (`encrypt_data` / `decrypt_data`).
- Live provider credentials (`DUFFEL_ACCESS_TOKEN`, `AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET`)
  are OPTIONAL at startup — their absence MUST make the relevant provider unavailable, not crash the
  app. Required variables are `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Amadeus OAuth tokens MUST be cached in Redis under `providers:amadeus:oauth-token` and MUST NOT
  be fetched on every request.
- Frontend runtime configuration MUST use `NEXT_PUBLIC_*` env vars read in `web/src/lib/api.ts`.
- Generated artifacts (`web/.next/`, `web/playwright-report/`, `web/test-results/`, `venv/`) MUST
  remain out of version control.

**Rationale**: Travel query data is sensitive user intent. Encryption at rest, environment-driven
secrets, and graceful token absence prevent both data exposure and hard startup failures in
environments where not all provider credentials are available.

### V. Simplicity & Focused Modules

- Every Python module MUST have a single, clear responsibility. Functions MUST be small and
  preferably stateless (see `extract_intent`, `rank_results`).
- The services layer (`src/app/services/`) is intentional and MUST be used for orchestration logic
  that crosses provider or NLP boundaries. Route handlers MUST delegate to services; business logic
  MUST NOT be inlined into route functions.
- React components MUST own only the state they render; shared state belongs in the nearest common
  ancestor (`web/src/app/page.tsx`).
- No additional architectural layers beyond routes → services → providers/NLP MUST be introduced
  unless directly required by a concrete, documented problem. YAGNI applies.
- New dependencies MUST be justified in the PR description against existing alternatives.

**Rationale**: The layered architecture (routes → services → providers) is the deliberate ceiling.
Premature abstraction beyond this has a high cost in a small team; each new layer must solve a
concrete problem that the existing layer cannot.

### VI. Resilience & Graceful Degradation

- Provider failures MUST NOT crash the search endpoint. Each provider adapter MUST handle its own
  errors and return an empty result set rather than propagating exceptions to the route.
- Missing optional credentials (e.g., `DUFFEL_ACCESS_TOKEN`) MUST result in the provider reporting
  itself as unavailable — the API response MUST surface provider availability clearly to the frontend.
- Redis cache failures MUST be swallowed silently; the search pipeline MUST complete without cache.
- Scraper-based providers (`src/app/scrapers/`) MUST fall back to mock result sets when live
  fetching fails, so the frontend always receives a well-formed response.
- Timeouts MUST be enforced per provider (`PROVIDER_TIMEOUT_SECONDS`, `DUFFEL_SUPPLIER_TIMEOUT_MS`)
  to prevent a slow provider from blocking the entire request.

**Rationale**: MiraiGo is a discovery product — a partial result set is far better than a 500
error. Users should always see something, even when some providers are unavailable.

## Tech Stack Constraints

These versions and tools are locked for the current milestone. Changes require a governance amendment.

| Layer | Technology | Version |
|---|---|---|
| Backend language | Python | 3.12 |
| Backend framework | FastAPI + Uvicorn | latest stable |
| ORM | SQLAlchemy | latest stable |
| DB driver | psycopg2-binary (PostgreSQL 16) | latest stable |
| Migrations | Alembic | latest stable |
| Cache | Redis 7 (via `redis` client) | latest stable |
| HTTP client | httpx (async) | latest stable |
| Flight provider | Duffel API v2 | latest stable |
| Flight provider (alt) | Amadeus (test env) | latest stable |
| Hotel provider | Expedia redirect workflow | N/A |
| Backend testing | pytest + pytest-cov | latest stable |
| Frontend language | TypeScript | 5 (strict mode) |
| Frontend framework | Next.js (App Router) | 16.1.6 |
| UI runtime | React | 19.2.3 |
| Styling | Tailwind CSS v4 + shadcn/ui | latest stable |
| Data fetching | SWR + Axios | latest stable |
| Frontend unit test | Jest 30 + Testing Library | latest stable |
| Frontend E2E/a11y | Playwright + @axe-core/playwright | 1.58.x |
| Linting | ESLint 9 (eslint-config-next) | 9.x |
| Containerisation | Docker + Docker Compose | latest stable |
| Cloud deployment | Railway or Azure (split api + web services) | N/A |

## Development Workflow

- **Full-stack local run**: `docker compose up --build` (PostgreSQL 16 + Redis 7 + API + Web).
- **Backend only**: activate `venv`, `pip install -r requirements.txt`, `alembic upgrade head`,
  `uvicorn src.app.main:app --reload`.
- **Frontend only**: `cd web && npm ci && npm run dev`.
- **Environment setup**: copy `.env.example` to `.env`; set `DUFFEL_ACCESS_TOKEN` for live flight
  search (optional — app starts cleanly without it).
- **Backend tests**: `pytest --cov=src --cov-report=term-missing` — MUST pass before PR merge.
- **Frontend unit tests**: `cd web && npm test -- --runInBand` — MUST pass before PR merge.
- **Frontend lint**: `cd web && npm run lint` — MUST be clean before PR merge.
- **Frontend build check**: `cd web && npm run build` — MUST succeed before PR merge.
- **E2E tests**: `cd web && npm run test:e2e` — run against a running full stack.
- **API docs**: available at `http://localhost:8000/docs` during local development.
- **Commit format**: scoped imperative subjects — `feat(api): ...`, `feat(web): ...`,
  `fix(nlp): ...`, `chore(core): ...`. Scope MUST match the changed area.
- PRs MUST include: summary, test evidence, screenshots for visible UI changes.

## Governance

This constitution supersedes all informal conventions and prior agreements. It is the authoritative
source of non-negotiable rules for MiraiGo development.

- All PRs MUST include a **Constitution Check** section (see `plan-template.md`) confirming no
  principles are violated, or documenting a justified exception with a simpler-alternative analysis.
- Amendments MUST increment the version according to semantic versioning (MAJOR/MINOR/PATCH),
  document what changed and why, and be merged via a dedicated PR.
- Complexity exceptions MUST be recorded in the plan's Complexity Tracking table with the simpler
  alternative that was considered and rejected.
- Review `.specify/memory/constitution.md` at the start of each milestone to confirm it still
  reflects current reality.

**Version**: 1.1.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
