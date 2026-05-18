# Repository Guidelines

## Project Structure & Module Organization
MiraiGo is split into a FastAPI backend and a Next.js frontend. Backend code lives in `src/app/` with domain folders for `api/v1`, `core`, `db`, `models`, `nlp`, `optimization`, `schemas`, and `scrapers`. Backend tests live under `src/tests/` and mirror the same feature areas, for example `src/tests/nlp/` and `src/tests/api/`. Frontend code lives in `web/src/`: route files in `web/src/app/`, shared UI in `web/src/components/ui/`, search-specific UI in `web/src/components/search/`, and client helpers in `web/src/lib/`. Static assets belong in `web/public/`.

## Build, Test, and Development Commands
Run the full stack with `docker compose up --build`. For backend-only work, create a venv, install `requirements.txt`, then start the API with `uvicorn src.app.main:app --reload`. Run backend tests with `pytest` and collect coverage with `pytest --cov=src --cov-report=term-missing`. For frontend work, use `cd web && npm install`, then `npm run dev` for local development, `npm run build` for a production build, and `npm run lint` before opening a PR.

## Coding Style & Naming Conventions
Follow the existing style in the repo: Python uses 4-space indentation, snake_case for modules and functions, and small focused files. TypeScript components use PascalCase file names such as `SearchForm.tsx`; helper modules stay lowercase under `web/src/lib/`. Keep imports grouped and local naming consistent with the feature folder. Frontend linting is enforced through `web/eslint.config.mjs`; no separate Python formatter is configured, so keep Python edits minimal and consistent with surrounding code.

## Testing Guidelines
Backend tests use `pytest` and `pytest-cov`; name files `test_*.py` and place them near the relevant domain folder. Frontend unit tests use Jest in `web/src/**/__tests__/` or `*.test.tsx` form via `npm test`. End-to-end and accessibility coverage use Playwright in `web/tests/e2e/`; run `npm run test:e2e` and update visual baselines only with `npm run test:e2e:update` when UI changes are intentional.

## Commit & Pull Request Guidelines
Recent history follows scoped, imperative subjects like `feat(api): ...`, `feat(web): ...`, and `chore(core): ...`. Keep commits small and use a scope that matches the area changed. PRs should include a short summary, linked issue or task when available, test evidence (`pytest`, `npm test`, `npm run test:e2e` as applicable), and screenshots for visible UI changes.

## Configuration & Environment
Runtime settings come from `.env` via `src/app/core/config.py`. At minimum, verify PostgreSQL and Redis settings before local runs. Do not commit secrets or generated artifacts such as `web/.next/`, `web/playwright-report/`, `web/test-results/`, or local virtualenv contents.

<!-- GSD:project-start source:PROJECT.md -->
## Project

**MiraiGo Travel Discovery**

MiraiGo Travel Discovery is a travel planning website for leisure travelers that turns loose natural-language prompts into ranked destination suggestions. Users can describe broad preferences, and MiraiGo asks targeted follow-up questions when details are missing. The result is a guided, conversational way to narrow travel options by geography, weather, budget, and timeline.

**Core Value:** Given vague travel intent, MiraiGo reliably converts it into personalized, ranked destination suggestions with clear rationale.

### Constraints

- **Product Scope**: v1 must prioritize ranked destination suggestions over itinerary generation — preserve focus and reduce delivery risk.
- **Coverage**: Suggestions must support global destinations from day one — users should not encounter region lock-in.
- **Data Freshness**: Budget recommendations require live pricing integrations — static cost bands are insufficient for expected behavior.
- **Interaction Model**: Input must remain natural-language-first — avoid forcing rigid forms before initial suggestion generation.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12 - Backend API, caching, scraping, NLP, and ranking logic under `src/app/` are built for the `python:3.12-slim` runtime in `Dockerfile`.
- TypeScript 5 - Frontend application, UI, and test code live under `web/src/`, with compiler settings in `web/tsconfig.json`.
- CSS - Global styling and theme tokens are defined in `web/src/app/globals.css`.
- YAML - Local orchestration is defined in `docker-compose.yml`.
## Runtime
- Python 3.12 container runtime in `Dockerfile`.
- Node.js 20 container runtime in `web/Dockerfile`.
- Browser runtime for the Next.js client app rendered from `web/src/app/page.tsx`.
- `pip` - Backend dependencies install from `requirements.txt`.
- `npm` - Frontend dependencies and scripts are defined in `web/package.json`.
- Lockfile: frontend lockfile present at `web/package-lock.json`; backend lockfile not detected.
## Frameworks
- FastAPI - HTTP API app is created in `src/app/main.py` and the search route is mounted from `src/app/api/v1/search.py`.
- SQLAlchemy - ORM models and engine setup are in `src/app/models/*.py`, `src/app/models/base.py`, and `src/app/db/session.py`.
- Pydantic Settings - Environment-backed config is defined in `src/app/core/config.py`.
- Next.js 16.1.6 - App Router frontend entrypoints are `web/src/app/layout.tsx` and `web/src/app/page.tsx`.
- React 19.2.3 - Client UI components are implemented in `web/src/components/` and `web/src/app/page.tsx`.
- `pytest` / `pytest-cov` - Backend tests live under `src/tests/` and are installed from `requirements.txt`.
- Jest 30 with `next/jest` and Testing Library - Frontend unit tests are configured in `web/jest.config.ts` and `web/jest.setup.ts`.
- Playwright 1.58 - Frontend E2E, accessibility, and visual tests are configured in `web/playwright.config.ts` and stored under `web/tests/e2e/`.
- Uvicorn - Backend dev and container startup command uses `uvicorn src.app.main:app` from `Dockerfile` and `README.md`.
- Docker Compose - Full local stack orchestration is defined in `docker-compose.yml`.
- Tailwind CSS v4 - Frontend styling pipeline is enabled by `web/postcss.config.mjs` and `web/src/app/globals.css`.
- shadcn/ui - Component registry settings live in `web/components.json`, with generated UI primitives under `web/src/components/ui/`.
- SWR - Client-side data fetching in `web/src/app/page.tsx`.
- Axios - HTTP client wrapper is defined in `web/src/lib/api.ts`.
## Key Dependencies
- `fastapi` - Core backend web framework from `requirements.txt`, instantiated in `src/app/main.py`.
- `uvicorn[standard]` - ASGI server used by `Dockerfile` and local dev commands in `README.md`.
- `sqlalchemy` - Database engine and ORM models in `src/app/db/session.py` and `src/app/models/`.
- `redis` - Cache client for `/search` responses in `src/app/db/redis.py` and `src/app/api/v1/search.py`.
- `httpx` - Async outbound HTTP transport for scrapers in `src/app/scrapers/base.py`.
- `beautifulsoup4` and `lxml` - HTML parsing stack used by `src/app/scrapers/expedia.py`, `src/app/scrapers/booking.py`, and `src/app/scrapers/airbnb.py`.
- `cryptography` - Fernet helpers for model-level encrypted fields are in `src/app/core/security.py` and referenced by `src/app/models/search.py`.
- `next` / `react` / `react-dom` - Core frontend runtime defined in `web/package.json`.
- `axios` - Frontend API client in `web/src/lib/api.ts`.
- `swr` - Client-side search request lifecycle in `web/src/app/page.tsx`.
- `psycopg2-binary` - PostgreSQL driver paired with the SQLAlchemy engine in `src/app/db/session.py`.
- `pydantic-settings` - Loads environment config in `src/app/core/config.py`.
- `python-multipart` - Installed for FastAPI form/multipart support in `requirements.txt`; no consuming route is detected in `src/app/api/`.
- `alembic` - Installed in `requirements.txt`; Alembic config or migration directories are not detected in the repo root.
- `date-fns` and `react-day-picker` - Date UI logic in `web/src/components/search/SearchForm.tsx`.
- `lucide-react` - Icon set used across `web/src/components/search/` and `web/src/components/ui/`.
- `class-variance-authority`, `clsx`, `tailwind-merge`, `tw-animate-css` - UI styling helpers wired through `web/src/components/ui/` and `web/src/lib/utils.ts`.
- `@playwright/test` and `@axe-core/playwright` - Browser automation and accessibility checks for `web/tests/e2e/`.
## Configuration
- Backend settings are centralized in `src/app/core/config.py` and loaded from `.env` via `SettingsConfigDict(env_file=".env")`.
- Backend-required variables are `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, optional `DATABASE_URL`, `REDIS_HOST`, and `REDIS_PORT` from `src/app/core/config.py`.
- Frontend runtime uses `NEXT_PUBLIC_API_URL` in `web/src/lib/api.ts`; `docker-compose.yml` sets it to `http://localhost:8000/api/v1` for the `web` service.
- Playwright behavior changes on `CI` in `web/playwright.config.ts`.
- A tracked `.env` or `.env.example` file is not detected in the repository root; configuration is expected to be supplied locally.
- Backend container build is defined in `Dockerfile`.
- Frontend multi-stage build is defined in `web/Dockerfile`.
- Full-stack local service wiring is in `docker-compose.yml`.
- TypeScript compiler and path alias config are in `web/tsconfig.json`.
- ESLint config is in `web/eslint.config.mjs`.
- Jest config is in `web/jest.config.ts`.
- PostCSS + Tailwind config is in `web/postcss.config.mjs`.
## Platform Requirements
- Docker and Docker Compose are the documented default in `README.md`.
- Manual backend development expects Python, a virtual environment, and packages from `requirements.txt` as documented in `README.md`.
- Manual frontend development expects Node.js and `npm install` in `web/` per `README.md`.
- Local service dependencies are PostgreSQL 16 and Redis 7 via `docker-compose.yml`.
- Backend target is a containerized FastAPI service exposing port `8000` from `Dockerfile`.
- Frontend target is a containerized Next.js server exposing port `3000` from `web/Dockerfile`.
- Deployment platform config for managed hosting, CI/CD, or cloud infra is not detected; the repo’s concrete deployment shape is Docker-based local orchestration in `docker-compose.yml`.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Python modules use snake_case file names under `src/app/` and `src/tests/`, for example `src/app/core/config.py`, `src/app/api/v1/search.py`, and `src/tests/test_security.py`.
- Frontend feature components use PascalCase file names, for example `web/src/components/search/SearchForm.tsx` and `web/src/components/search/ResultsDashboard.tsx`.
- Frontend shared UI primitives use lowercase file names under `web/src/components/ui/`, for example `web/src/components/ui/button.tsx` and `web/src/components/ui/slider.tsx`.
- Frontend test files end in `.test.tsx` or `.test.ts`, for example `web/src/__tests__/Home.test.tsx` and `web/tests/e2e/search.test.ts`.
- Python functions use snake_case, for example `extract_intent` in `src/app/nlp/intent.py`, `rank_results` in `src/app/optimization/engine.py`, and `health_check` in `src/app/main.py`.
- Python methods also stay snake_case, for example `get_database_url` in `src/app/core/config.py` and `get_headers` in `src/app/scrapers/base.py`.
- React component functions exported from route files are PascalCase by identifier, for example `Home` in `web/src/app/page.tsx` and `RootLayout` in `web/src/app/layout.tsx`.
- Local TypeScript handlers stay camelCase, for example `handleSearch` in `web/src/app/page.tsx`, `handleSubmit` and `toggleQuality` in `web/src/components/search/SearchForm.tsx`, and `toggleProvider` in `web/src/components/search/ResultsDashboard.tsx`.
- Python module-level constants use UPPER_SNAKE_CASE, for example `QUALITIES`, `DATES`, `MODES`, and `NUMBER_MAP` in `src/app/nlp/intent.py`, plus `SYNONYMS` in `src/app/optimization/engine.py`.
- Python short-lived local variables are brief and descriptive, for example `query_lower`, `date_range`, `effective_max_price`, and `filtered_results`.
- TypeScript constants use UPPER_SNAKE_CASE when they are configuration lists, for example `AVAILABLE_QUALITIES` in `web/src/components/search/SearchForm.tsx`, `PROVIDERS` and `AMENITY_OPTIONS` in `web/src/components/search/ResultsDashboard.tsx`.
- React state uses `[value, setValue]` pairs with camelCase names, for example `searchParams`/`setSearchParams` in `web/src/app/page.tsx` and `selectedQualities`/`setSelectedQualities` in `web/src/components/search/SearchForm.tsx`.
- Python type hints rely on `typing` imports such as `List`, `Dict`, `Any`, and `Optional`, for example in `src/app/optimization/engine.py`, `src/app/nlp/intent.py`, and `src/app/scrapers/base.py`.
- Pydantic models use PascalCase class names, for example `Settings` in `src/app/core/config.py`, `DateRange` and `SearchFilterParams` in `src/app/schemas/search.py`.
- SQLAlchemy models use PascalCase class names, for example `User`, `SearchHistory`, and `UserPreference` in `src/app/models/user.py` and `src/app/models/search.py`.
- Frontend prop and data contracts are declared as `interface`, for example `SearchFormProps` in `web/src/components/search/SearchForm.tsx`, `TravelResult` and `ResultsDashboardProps` in `web/src/components/search/ResultsDashboard.tsx`.
## Code Style
- No Python formatter config is detected at repo root. There is no `pyproject.toml`, `ruff.toml`, `setup.cfg`, or `.flake8`.
- Python formatting is conventional 4-space indentation with blank lines between top-level declarations, as seen in `src/app/core/config.py`, `src/app/models/user.py`, and `src/tests/test_main.py`.
- TypeScript formatting is not enforced by a checked-in Prettier config. No `.prettierrc` is present in the repo.
- TypeScript style is mixed by source:
- `web/src/app/layout.tsx` and `web/src/components/ui/button.tsx` use double quotes and semicolons, which matches generated Next.js and shadcn-style files.
- `web/src/app/page.tsx`, `web/src/lib/api.ts`, and the component test files use single quotes and typically omit semicolons.
- In practice, edits should match the surrounding file rather than normalize the entire frontend.
- Frontend linting is configured in `web/eslint.config.mjs`.
- The ESLint config composes `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript`; there are no repo-specific custom rules beyond ignore overrides in `web/eslint.config.mjs`.
- TypeScript strict mode is enabled in `web/tsconfig.json` with `"strict": true`.
- No Python lint config is detected, so backend style is enforced socially through consistency with nearby modules.
## Import Organization
- Backend modules import framework libraries before local modules, for example `src/app/main.py` imports `fastapi` modules before `from src.app.api.v1 import search`.
- Backend commonly uses absolute imports rooted at `src.app`, for example `src/app/models/search.py` imports `from src.app.models.base import Base` and `from src.app.core.security import encrypt_data, decrypt_data`.
- Frontend feature files import React and third-party packages first, then `@/` aliases, then local relative imports if any, as seen in `web/src/components/search/SearchForm.tsx` and `web/src/components/search/ResultsDashboard.tsx`.
- The `@/*` path alias is defined in `web/tsconfig.json` and used broadly in `web/src/app/page.tsx`, `web/src/components/search/SearchForm.tsx`, and `web/src/components/ui/button.tsx`.
- Frontend uses `@/* -> ./src/*` from `web/tsconfig.json`.
- Backend does not use a short alias; it imports through the full `src.app...` path.
- The backend’s `src.app...` import convention depends on running with repo-root import visibility. This is a convention in code, but not fully packaged in test configuration.
## Error Handling
- Backend route code tends to swallow infrastructure exceptions for non-critical operations. In `src/app/api/v1/search.py`, Redis cache `get` and `setex` calls are each wrapped in `try/except Exception: pass`.
- Backend scraper infrastructure re-raises terminal request failures after retry exhaustion. `src/app/scrapers/base.py` catches `httpx.RequestError` and `httpx.HTTPStatusError`, retries with exponential backoff, then raises on the last attempt.
- Backend request handlers generally return plain dict payloads rather than response models or custom exception objects, for example `src/app/main.py` and `src/app/api/v1/search.py`.
- Frontend page-level error handling is simple conditional rendering. `web/src/app/page.tsx` checks SWR `error` and renders a static error banner.
- Frontend client helpers do not add centralized error transformation. `web/src/lib/api.ts` exposes the raw Axios instance and a simple `fetcher`.
## Logging
- No structured logging library is detected in backend runtime code under `src/app/`.
- No `logging` module usage is present in the representative backend files inspected: `src/app/main.py`, `src/app/api/v1/search.py`, `src/app/core/config.py`, and `src/app/scrapers/base.py`.
- Frontend runtime code also avoids logging in the main app flow.
- Playwright accessibility helper logs violations with `console.error` in `web/tests/e2e/axe-util.ts` before asserting zero violations.
## Comments
- Comments are sparse and mostly explain high-level steps or intent, not line-by-line logic.
- Backend uses numbered workflow comments inside larger handlers, for example steps `# 1. Check Cache` through `# 7. Store in Cache` in `src/app/api/v1/search.py`.
- Backend uses short clarifying comments around heuristics, for example `# Common cities for better extraction` in `src/app/nlp/intent.py` and `# Synonym matching` in `src/app/optimization/engine.py`.
- Tests use comments to describe scenario setup and expectations, for example mocked provider scoring notes in `src/tests/api/test_search.py` and staged UI flow notes in `web/tests/e2e/search.test.ts`.
- No regular JSDoc or TSDoc usage is present in `web/src/`.
- Python docstrings are minimal. The clearest example is the abstract scraper method docstring in `src/app/scrapers/base.py`.
## Function Design
- Most backend functions are small and single-purpose, such as `encrypt_data`, `decrypt_data`, `get_redis_client`, and `health_check`.
- The main exception is the route handler in `src/app/api/v1/search.py`, which contains caching, intent extraction, scraping orchestration, filtering, ranking, and response shaping in one function.
- Frontend components are medium-sized and stateful. `web/src/components/search/SearchForm.tsx` and `web/src/components/search/ResultsDashboard.tsx` each own local UI state, derived values, and rendering.
- Backend functions usually accept primitives and return plain dict/list structures, for example `extract_intent(query: str) -> Dict[str, Any]` in `src/app/nlp/intent.py` and `rank_results(results, qualities)` in `src/app/optimization/engine.py`.
- FastAPI query parameters are declared inline in route signatures using `Query`, as seen in `src/app/api/v1/search.py`.
- Frontend component props are declared inline via interfaces and passed as plain objects, for example `onSearch` in `web/src/components/search/SearchForm.tsx`.
- Backend service-style helpers and scrapers return dictionaries rather than typed domain objects. Examples include `extract_intent` in `src/app/nlp/intent.py` and `scrape` implementations under `src/app/scrapers/`.
- Frontend utility functions return straightforward values with minimal wrapping, for example `fetcher` in `web/src/lib/api.ts` returns `res.data`, and `cn` in `web/src/lib/utils.ts` returns a merged class name string.
- React page and component functions return JSX and keep side effects close to user interaction or SWR invocation.
## Module Design
- Python modules usually expose a small set of top-level names without explicit `__all__`, for example `settings` in `src/app/core/config.py`, `engine` and `SessionLocal` in `src/app/db/session.py`, and `router` in `src/app/api/v1/search.py`.
- TypeScript feature components generally default-export the component, for example `web/src/app/page.tsx`, `web/src/components/search/SearchForm.tsx`, and `web/src/components/search/ResultsDashboard.tsx`.
- Shared frontend utilities and primitives prefer named exports, for example `Button` and `buttonVariants` in `web/src/components/ui/button.tsx`, plus `apiClient` and `fetcher` in `web/src/lib/api.ts`.
- No barrel file pattern is detected in `src/app/` or `web/src/`.
- Imports target concrete modules directly, for example `@/components/search/SearchForm` and `src.app.scrapers.expedia`.
## Configuration Practices
- Runtime settings are centralized in `src/app/core/config.py` via `pydantic_settings.BaseSettings`.
- `.env` is referenced through `SettingsConfigDict(env_file=".env")` in `src/app/core/config.py`.
- Configuration is accessed through a singleton `settings = Settings()` instance imported directly into modules such as `src/app/db/session.py`, `src/app/db/redis.py`, and `src/app/core/security.py`.
- Defaults are embedded in code for local development, for example `POSTGRES_SERVER = "localhost"` and `REDIS_PORT = 6379` in `src/app/core/config.py`.
- Frontend runtime configuration is light and environment-variable based. `web/src/lib/api.ts` reads `process.env.NEXT_PUBLIC_API_URL` with a localhost fallback.
- Next.js config is present but minimal in `web/next.config.ts`.
- Path resolution and type strictness are configured in `web/tsconfig.json`.
## Cross-Stack Consistency Notes
- Domain folders are mirrored between implementation and tests on the backend: `src/app/nlp/` aligns with `src/tests/nlp/`, `src/app/optimization/` aligns with `src/tests/optimization/`, and `src/app/scrapers/` aligns with `src/tests/scrapers/`.
- The frontend keeps feature-specific tests adjacent to the feature area, for example `web/src/components/search/__tests__/`.
- Generated or third-party scaffold files preserve their own style conventions. `web/src/app/layout.tsx` and `web/src/components/ui/button.tsx` should be edited in-place with their existing quote and semicolon style instead of force-normalized to the rest of the app.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- `src/app/api/v1/search.py` is the backend composition point. It parses query intent, dispatches provider calls, filters results, ranks them, and caches the response in one route module.
- `web/src/app/page.tsx` is the frontend composition point. It owns search state, triggers data fetching with SWR, and renders feature components for input and results.
- Domain helpers exist as focused modules under `src/app/nlp`, `src/app/optimization`, `src/app/scrapers`, `src/app/db`, and `src/app/models`, but there is no separate service layer or repository layer implemented between the route and those helpers.
## Layers
- Purpose: Create the FastAPI app, apply middleware, and register routes.
- Location: `src/app/main.py`
- Contains: `FastAPI(...)`, CORS middleware setup, router registration, and a `/health` endpoint.
- Depends on: `src/app/api/v1/search.py`, `fastapi`, `fastapi.middleware.cors`.
- Used by: `uvicorn src.app.main:app --reload`, Docker `app` service in `docker-compose.yml`, backend tests such as `src/tests/test_main.py`.
- Purpose: Convert HTTP query parameters into a search workflow and return an API response.
- Location: `src/app/api/v1/search.py`
- Contains: `@router.get("/search")`, cache key construction, Redis lookups, NLP extraction, async provider fan-out, result normalization, filter application, ranking, and cache writes.
- Depends on: `src/app/nlp/intent.py`, `src/app/scrapers/*.py`, `src/app/optimization/engine.py`, `src/app/db/redis.py`.
- Used by: `src/app/main.py`; frontend requests made through `web/src/lib/api.ts`.
- Purpose: Interpret free-text travel queries and score provider results.
- Location: `src/app/nlp/intent.py`, `src/app/optimization/engine.py`
- Contains: Regex and keyword extraction in `extract_intent`, plus keyword/synonym scoring in `rank_results`.
- Depends on: Python standard library types and regex utilities.
- Used by: `src/app/api/v1/search.py`, backend unit tests in `src/tests/nlp/*.py` and `src/tests/optimization/test_engine.py`.
- Purpose: Encapsulate each travel source behind a common async `scrape()` contract.
- Location: `src/app/scrapers/base.py`, `src/app/scrapers/expedia.py`, `src/app/scrapers/booking.py`, `src/app/scrapers/airbnb.py`, `src/app/scrapers/amadeus.py`, `src/app/scrapers/niche_local.py`
- Contains: `BaseScraper.fetch()` retry logic, provider-specific request params, HTML parsing, and mock fallback result generation.
- Depends on: `httpx`, `bs4`, `asyncio`, provider subclasses.
- Used by: `src/app/api/v1/search.py`, scraper tests in `src/tests/scrapers/*.py`.
- Purpose: Centralize runtime configuration, database connectivity, Redis access, encryption helpers, and ORM models.
- Location: `src/app/core/config.py`, `src/app/core/security.py`, `src/app/db/session.py`, `src/app/db/redis.py`, `src/app/models/*.py`
- Contains: Pydantic settings loading, SQLAlchemy engine/session construction, Redis client construction, Fernet encryption helpers, and ORM table definitions.
- Depends on: `.env` via `SettingsConfigDict(env_file=".env")`, SQLAlchemy, Redis, Cryptography.
- Used by: `src/app/api/v1/search.py` for cache access; tests in `src/tests/test_config.py`, `src/tests/test_db.py`, `src/tests/test_models.py`, `src/tests/test_security.py`. The SQLAlchemy models are defined but are not wired into the live `/api/v1/search` request path.
- Purpose: Provide the Next.js application shell and root page.
- Location: `web/src/app/layout.tsx`, `web/src/app/page.tsx`, `web/src/app/globals.css`
- Contains: Global metadata, fonts, page-level layout, search state, SWR invocation, and page composition.
- Depends on: Next App Router runtime, `web/src/lib/api.ts`, `web/src/components/search/SearchForm.tsx`, `web/src/components/search/ResultsDashboard.tsx`.
- Used by: Next.js runtime, frontend tests in `web/src/__tests__/Home.test.tsx`, Playwright flows in `web/tests/e2e/*.ts`.
- Purpose: Normalize backend access behind a single HTTP client and SWR fetcher.
- Location: `web/src/lib/api.ts`
- Contains: `axios.create(...)` with `NEXT_PUBLIC_API_URL` and a `fetcher` helper used by SWR.
- Depends on: `axios`, `NEXT_PUBLIC_API_URL`.
- Used by: `web/src/app/page.tsx`.
- Purpose: Keep page-level UI behavior in focused search modules.
- Location: `web/src/components/search/SearchForm.tsx`, `web/src/components/search/ResultsDashboard.tsx`
- Contains: Query input, optional date and quality controls, provider/price/amenity filtering, loading states, and result rendering.
- Depends on: `web/src/components/ui/*.tsx`, `web/src/lib/utils.ts`, `date-fns`, `react-day-picker`, `lucide-react`.
- Used by: `web/src/app/page.tsx`; unit tests in `web/src/components/search/__tests__/*.tsx`.
- Purpose: Provide reusable building blocks used by feature components.
- Location: `web/src/components/ui/*.tsx`
- Contains: `Button`, `Input`, `Card`, `Calendar`, `Checkbox`, `Popover`, `Separator`, and `Slider`.
- Depends on: Radix UI primitives, Tailwind utility composition in `web/src/lib/utils.ts`.
- Used by: `web/src/components/search/*.tsx`.
## Data Flow
- Backend request state is ephemeral and lives inside `src/app/api/v1/search.py`; persistence is limited to Redis caching and unused SQLAlchemy models.
- Frontend state is local component state in `web/src/app/page.tsx` and `web/src/components/search/*.tsx`; there is no global store.
- Remote data state on the frontend is handled by SWR in `web/src/app/page.tsx`.
## Key Abstractions
- Purpose: Backend application service in practice, even though it is implemented as a route module.
- Examples: `src/app/api/v1/search.py`
- Pattern: Direct orchestration inside the endpoint rather than delegating to separate service classes.
- Purpose: Convert a natural-language query into structured travel intent.
- Examples: `src/app/nlp/intent.py`
- Pattern: Stateless functional helper returning a plain `dict`.
- Purpose: Score normalized results against extracted qualities.
- Examples: `src/app/optimization/engine.py`
- Pattern: Stateless functional post-processing over result lists.
- Purpose: Give each travel source a shared async interface.
- Examples: `src/app/scrapers/base.py`, `src/app/scrapers/expedia.py`, `src/app/scrapers/booking.py`, `src/app/scrapers/airbnb.py`, `src/app/scrapers/amadeus.py`, `src/app/scrapers/niche_local.py`
- Pattern: Abstract base class plus concrete subclasses with provider-specific query construction and parsing.
- Purpose: Hide backend base URL configuration from feature components.
- Examples: `web/src/lib/api.ts`
- Pattern: Shared Axios instance plus a small SWR-compatible fetcher function.
- Purpose: Separate user input and result presentation from the page container.
- Examples: `web/src/components/search/SearchForm.tsx`, `web/src/components/search/ResultsDashboard.tsx`
- Pattern: Local-state React function components composed by `web/src/app/page.tsx`.
## Entry Points
- Location: `src/app/main.py`
- Triggers: `uvicorn`, Docker `app` service, FastAPI TestClient in backend tests.
- Responsibilities: Instantiate the API app, enable CORS, mount the search router, expose `/health`.
- Location: `src/app/api/v1/search.py`
- Triggers: `GET /api/v1/search`
- Responsibilities: Run the full travel search flow and return ranked results.
- Location: `web/src/app/layout.tsx`
- Triggers: Next.js App Router request handling.
- Responsibilities: Apply fonts, metadata, and global page shell.
- Location: `web/src/app/page.tsx`
- Triggers: Browser request to `/`
- Responsibilities: Hold current search params, call SWR, show search form, error state, and results dashboard.
- Location: `docker-compose.yml`
- Triggers: `docker compose up --build`
- Responsibilities: Start PostgreSQL, Redis, FastAPI app, and Next.js web app with matching environment wiring.
## Error Handling
- `src/app/api/v1/search.py` wraps Redis `get` and `setex` calls in broad `try/except` blocks and ignores cache failures rather than failing the request.
- Provider scrapers such as `src/app/scrapers/expedia.py`, `src/app/scrapers/booking.py`, and `src/app/scrapers/airbnb.py` catch fetch or parsing errors and fall back to mock result lists.
- `src/app/scrapers/base.py` retries HTTP failures with exponential backoff before surfacing the final exception to the subclass.
- `web/src/app/page.tsx` renders a generic connection error message when SWR returns an error.
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
