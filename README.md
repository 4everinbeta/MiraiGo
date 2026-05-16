# MiraiGo

MiraiGo is a local-first travel search MVP built with FastAPI and Next.js. It focuses on a clean search-and-redirect workflow for stays and flights, runs end-to-end with `docker compose`, and stays portable for split-service deployments on Railway or Azure.

## What This Version Does

- Runs locally with `web`, `api`, `postgres`, and `redis` in Docker Compose.
- Uses a provider adapter architecture with canonical stay and flight result types.
- Supports a real live-flight path through **Duffel** when a token is configured.
- Includes an **Expedia** hotel redirect provider for partner-handoff stay search.
- Surfaces provider availability clearly when flight credentials are missing.

## Architecture

- Backend: FastAPI, SQLAlchemy, Alembic, Redis caching, provider adapters
- Frontend: Next.js App Router, TypeScript, Tailwind CSS
- Data stores: PostgreSQL for search run telemetry, Redis for cache
- Deployment shape: split services for `api` and `web`, with managed Postgres/Redis in the cloud

## Quick Start

1. Copy `.env.example` to `.env`.
2. Optionally set `DUFFEL_ACCESS_TOKEN` for live Duffel flight search.
3. Start the full stack:

```bash
docker compose up --build
```

4. Open:
   - Frontend: `http://localhost:3000`
   - API docs: `http://localhost:8000/docs`
   - API readiness: `http://localhost:8000/health/ready`

If the Duffel token is absent, the app still starts cleanly. Flight search stays unavailable, while hotel redirects remain available.

For the full local live-provider walkthrough, see [docs/duffel-local-setup.md](/home/rbrown/workspace/MiraiGo/docs/duffel-local-setup.md).

## Local Development

### Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.app.main:app --reload
```

### Frontend

```bash
cd web
npm ci
npm run dev
```

## Test Commands

```bash
pytest
cd web && npm test -- --runInBand
cd web && npm run lint
cd web && npm run build
```

## Environment

### Required for local Compose

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

### Optional live-provider credentials

- `DUFFEL_ACCESS_TOKEN`

Duffel is the live self-service flight provider in the current MVP. Hotels use an Expedia redirect workflow rather than a live hotel API integration.

## Cloud Deployment Notes

- Railway and Azure should deploy the `api` and `web` as separate services.
- Keep Docker Compose for local development only.
- Use managed Postgres and Redis in cloud environments.
- Deployment guides and workflow assumptions live in:
  - [deploy/railway/README.md](/home/rbrown/workspace/MiraiGo/deploy/railway/README.md)
  - [deploy/azure/README.md](/home/rbrown/workspace/MiraiGo/deploy/azure/README.md)
