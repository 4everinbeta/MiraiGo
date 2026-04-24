# Stack Research

**Domain:** Natural-language travel destination recommendation website with real-time flight/hotel pricing  
**Researched:** 2026-04-24  
**Confidence:** MEDIUM-HIGH (official docs + package registries; limited direct vendor pricing-contract visibility)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Next.js + React + TypeScript | Next.js 16.2.x, React 19.2.x, TypeScript 6.0.x | Web app UI, conversational discovery flow, SEO landing pages | This is the 2025–2026 default for production travel web apps: strong SSR/streaming support, mature routing/data-fetching patterns, and best hiring/maintainability profile. | HIGH |
| FastAPI (Python) | 0.136.x | API gateway for intent parsing, recommendation orchestration, pricing aggregation | FastAPI remains a standard Python backend for LLM-adjacent products: async IO, strong validation, OpenAPI-first contracts, and easy integration with existing MiraiGo backend modules. | HIGH |
| PostgreSQL + pgvector | PostgreSQL 16–18, pgvector 0.4.x (Python client) + current pgvector extension | Source-of-truth relational data + vector search for semantic destination matching | Travel recommendation requires both strict relational joins (availability, geography, constraints) and semantic recall (natural-language intent). Postgres + pgvector is now the pragmatic “one-database” default before separate vector infra. | HIGH |
| Redis | 7.x | Short-TTL caching for search + pricing responses; session and rate-limit support | Real-time pricing APIs are rate-limited and expensive. Redis materially reduces vendor calls and latency while preserving freshness using TTL + stale-while-revalidate patterns. | HIGH |
| OpenAI API (Responses/function calling) | OpenAI Python SDK 2.32.x / JS SDK 6.34.x | Natural-language understanding, clarification question generation, explanation synthesis | For this product shape, tool-calling + structured outputs is the fastest path to reliable NL-to-constraints extraction and explainable ranking. | MEDIUM-HIGH |

### Real-Time Travel Pricing Providers (Recommended Integration Order)

| Provider | Scope | Why This Order | Notes | Confidence |
|---------|-------|----------------|-------|------------|
| **Amadeus Self-Service APIs** | Flights + Hotels | Best first production integration because one vendor covers both domains and is accessible for MVP onboarding | Use for unified initial launch and fallback if specialized provider access is delayed. | MEDIUM |
| **Duffel API** | Flights (NDC-centric) | Add second for better modern airline coverage/offer quality where supported | Keep adapter-based architecture; do not hard-wire business logic to one provider schema. | HIGH |
| **Booking.com Demand API or Expedia Rapid API** | Hotels | Add one major hotel demand API after baseline launch for broader inventory and rate competitiveness | Access/commercial terms vary by region and partner status; design provider switching from day one. | MEDIUM |

**Prescriptive call:** Start with **Amadeus + Duffel (flights)** and **Amadeus + one hotel demand API** behind a canonical provider interface. Do not ship with a single provider lock-in.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic + pydantic-settings | pydantic 2.13.x, pydantic-settings 2.14.x | Strict schema validation for intent, constraints, provider payload normalization | Always; this is foundational for safe LLM tool outputs and API interoperability |
| SQLAlchemy + Alembic | SQLAlchemy 2.0.49, Alembic 1.18.x | Data modeling + migrations | Always; required for reliable schema evolution as ranking logic evolves |
| HTTPX | 0.28.x | Async outbound calls to flight/hotel vendors and geodata services | Always for provider clients and retries/timeouts/circuit-breaker wrappers |
| SWR or TanStack Query | SWR 2.4.x / TanStack Query 5.100.x | Frontend server-state management for conversational + pricing refresh UX | Use when you need automatic revalidation and stale-data handling in search flows |
| OpenTelemetry SDK | current stable (language-specific) | Tracing across NL parse → recommendation pipeline → provider fan-out | Use before scaling traffic; required for diagnosing vendor latency and ranking regressions |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Docker Compose | Local full-stack parity (`web` + `api` + `postgres` + `redis`) | Keep local-first reproducibility; use managed DB/cache in cloud |
| Playwright + Jest + Pytest | E2E + unit/integration quality gates | Include provider-contract tests and synthetic pricing fixtures |
| Ruff + mypy (Python) / ESLint (web) | Code quality and type safety | Enforce in CI before shipping provider integrations |

## Installation

```bash
# Backend core (Python)
pip install fastapi==0.136.1 uvicorn[standard]==0.46.0 \
  pydantic==2.13.3 pydantic-settings==2.14.0 \
  sqlalchemy==2.0.49 alembic==1.18.4 \
  redis==7.4.0 httpx==0.28.1 psycopg[binary]==3.3.3 \
  openai==2.32.0 pgvector==0.4.2

# Frontend core (web/)
npm install next@16.2.4 react@19.2.5 react-dom@19.2.5 \
  typescript@6.0.3 swr@2.4.1 zod@4.3.6

# Optional richer server-state management
npm install @tanstack/react-query@5.100.1
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| FastAPI | Node/NestJS API | Choose NestJS if your team is heavily TypeScript-only and wants one-language full-stack; otherwise FastAPI is faster for ML/NLP integration. |
| PostgreSQL + pgvector | Dedicated vector DB (Pinecone/Weaviate/Qdrant) | Move only when vector scale/latency requirements outgrow Postgres or you need advanced ANN multi-tenant features. |
| Multi-provider pricing adapters | Single vendor integration | Single vendor is acceptable only for prototype demos; not acceptable for production pricing resilience. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Scraping OTA websites for live prices | Breaks TOS, fragile selectors, anti-bot risk, legal/commercial instability | Official partner APIs (Amadeus, Duffel, Booking Demand, Expedia Rapid) |
| `psycopg2-binary` as long-term production default | Packaging/runtime caveats and weaker modern async posture vs psycopg3 ecosystem | `psycopg` 3.x (`psycopg[binary]` for deployment simplicity) |
| Pure keyword destination matching only | Fails on vague natural-language intent and nuanced preference combinations | Hybrid scoring: structured filters + embedding similarity + business rules |
| Hard-coding one provider’s schema through the app | Causes expensive rewrites when adding/replacing suppliers | Canonical domain models + provider adapters at boundary layer |

## Stack Patterns by Variant

**If launching MVP in 8–12 weeks:**  
- Use Postgres + pgvector (single DB), FastAPI monolith, and 2-provider integration (1 flight-focused + 1 broad fallback).  
- Because this minimizes operational complexity while still giving pricing resiliency.

**If entering growth stage (high query volume, multi-region):**  
- Split pricing aggregation into async worker/service, add queue-based refresh, and implement provider-level circuit breakers + dynamic fallback routing.  
- Because vendor latency/error spikes become the primary reliability risk before raw model quality does.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| fastapi 0.136.x | pydantic 2.x | Current FastAPI line is Pydantic v2-native |
| next 16.2.x | react 19.x | Use aligned major versions; avoid mixed major React versions |
| sqlalchemy 2.0.x | alembic 1.18.x | Standard migration pair for modern SQLAlchemy projects |
| psycopg 3.3.x | PostgreSQL 16–18 | Preferred modern Postgres driver path |

## Sources

- Project context: `/home/rbrown/workspace/MiraiGo/.planning/PROJECT.md`  
- Existing implementation baseline: `/home/rbrown/workspace/MiraiGo/README.md`, `/home/rbrown/workspace/MiraiGo/web/package.json`, `/home/rbrown/workspace/MiraiGo/requirements.txt`, `/home/rbrown/workspace/MiraiGo/docker-compose.yml`  
- Next.js documentation: https://nextjs.org/docs  
- FastAPI documentation: https://fastapi.tiangolo.com/  
- PostgreSQL current release notes: https://www.postgresql.org/docs/current/release.html  
- pgvector project: https://github.com/pgvector/pgvector  
- OpenAI function/tool calling docs: https://platform.openai.com/docs/guides/function-calling  
- Amadeus Flights APIs guide: https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/resources/flights/  
- Amadeus Hotels APIs guide: https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/resources/hotels/  
- Duffel API overview: https://duffel.com/docs/api/overview  
- Expedia Rapid API hub: https://developers.expediagroup.com/rapid  
- Booking.com Demand API docs: https://developers.booking.com/demand/docs  
- Package registry verification (latest versions queried 2026-04-24): npm registry + PyPI JSON APIs

---
*Stack research for: NL-first travel destination recommendation with live pricing*  
*Researched: 2026-04-24*
