<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0 (initial baseline — no prior version)
  Modified principles: N/A (new document)
  Added sections: Core Principles (I–V), Tech Stack Constraints, Development Workflow, Governance
  Removed sections: N/A
  Templates requiring updates:
    ✅ .specify/templates/plan-template.md — Constitution Check section references updated principles
    ✅ .specify/templates/spec-template.md — no structural change required; aligned with FR/SC model
    ✅ .specify/templates/tasks-template.md — task phases align with full-stack (backend/frontend) layout
  Follow-up TODOs: None — all fields resolved from codebase context.
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

**Rationale**: Clean separation enables independent deployment, testing, and iteration of each tier.
The API contract is the integration surface — keeping it explicit prevents hidden coupling.

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

- Secrets (database credentials, API keys) MUST be loaded exclusively from `.env` via
  `src/app/core/config.py` (`pydantic-settings`). Secrets MUST NOT be committed to source control.
- Sensitive model fields (e.g., search history) MUST use Fernet encryption via
  `src/app/core/security.py` (`encrypt_data` / `decrypt_data`).
- Frontend runtime configuration MUST use `NEXT_PUBLIC_*` env vars read in `web/src/lib/api.ts`.
- Generated artifacts (`web/.next/`, `web/playwright-report/`, `web/test-results/`, `venv/`) MUST
  remain out of version control.

**Rationale**: Travel query data is sensitive user intent. Encryption at rest and environment-driven
secrets prevent credential leaks and data exposure.

### V. Simplicity & Focused Modules

- Every Python module MUST have a single, clear responsibility. Functions MUST be small and
  preferably stateless (see `extract_intent`, `rank_results`).
- React components MUST own only the state they render; shared state belongs in the nearest common
  ancestor (`web/src/app/page.tsx`).
- No additional layers (repositories, service buses, state managers) MUST be introduced unless
  directly required by a concrete, documented problem. YAGNI applies.
- New dependencies MUST be justified in the PR description against existing alternatives.

**Rationale**: The current architecture is deliberately lean. Premature abstraction has a high cost
in a small team shipping at speed; complexity must earn its place.

## Tech Stack Constraints

These versions and tools are locked for the current milestone. Changes require a governance amendment.

| Layer | Technology | Version |
|---|---|---|
| Backend language | Python | 3.12 |
| Backend framework | FastAPI + Uvicorn | latest stable |
| ORM | SQLAlchemy | latest stable |
| DB driver | psycopg2-binary (PostgreSQL 16) | latest stable |
| Cache | Redis 7 (via `redis` client) | latest stable |
| HTTP client | httpx (async) | latest stable |
| Migrations | Alembic | latest stable |
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

## Development Workflow

- **Full-stack local run**: `docker compose up --build` (PostgreSQL 16 + Redis 7 + API + Web).
- **Backend only**: activate `venv`, `pip install -r requirements.txt`,
  `uvicorn src.app.main:app --reload`.
- **Frontend only**: `cd web && npm install && npm run dev`.
- **Backend tests**: `pytest --cov=src --cov-report=term-missing` — MUST pass before PR merge.
- **Frontend unit tests**: `cd web && npm test` — MUST pass before PR merge.
- **Frontend lint**: `cd web && npm run lint` — MUST be clean before PR merge.
- **E2E tests**: `cd web && npm run test:e2e` — run against a running full stack.
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

**Version**: 1.0.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
