# Architecture Research

**Domain:** Natural-language travel destination recommendation platform with live pricing
**Researched:** 2026-04-24
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                              Experience Layer                                │
├───────────────────────────────────────────────────────────────────────────────┤
│  Next.js Web App                                                             │
│  - Free-text prompt input                                                    │
│  - Clarification Q&A UI                                                      │
│  - Ranked destination cards + rationale + live price freshness              │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                │ HTTPS
┌───────────────────────────────▼───────────────────────────────────────────────┐
│                             API / Orchestration                              │
├───────────────────────────────────────────────────────────────────────────────┤
│  FastAPI                                                                      │
│  ├─ Intent & Entity Extraction (NL → structured constraints)                 │
│  ├─ Clarification Service (ask for missing origin/date/budget constraints)   │
│  ├─ Candidate Generator (destination recall)                                 │
│  ├─ Pricing Aggregation Gateway (provider adapter fan-out)                   │
│  ├─ Ranking Service (fit score + affordability + confidence)                 │
│  └─ Explanation Service (why each destination was ranked)                    │
└───────────────┬───────────────────────────────────────┬──────────────────────┘
                │                                       │
┌───────────────▼───────────────────────┐   ┌──────────▼───────────────────────┐
│      Live Pricing Ingestion Plane     │   │            Data Plane             │
├───────────────────────────────────────┤   ├───────────────────────────────────┤
│  Scheduled jobs / workers             │   │ PostgreSQL                         │
│  ├─ Flight provider pull (Duffel)     │   │ - destinations, climate metadata   │
│  ├─ Hotel provider pull/redirect data │   │ - search runs, provider telemetry  │
│  ├─ Rate normalization + FX convert   │   │ - prompt/session constraints       │
│  └─ Freshness + SLA monitoring        │   │                                   │
│                                       │   │ Redis                              │
│  Dead-letter + retry queues           │   │ - provider response cache          │
│                                       │   │ - hot recommendation cache         │
└───────────────┬───────────────────────┘   │ - clarification session state      │
                │                           └───────────────────────────────────┘
                │
┌───────────────▼───────────────────────────────────────────────────────────────┐
│                           External Provider APIs                               │
├───────────────────────────────────────────────────────────────────────────────┤
│  Flights: Duffel API                                                           │
│  Stays: redirect-first provider now, upgrade to API providers later            │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Web experience | Prompt capture, follow-up Q&A, result display | Next.js client + typed API client |
| API orchestration | Route requests, enforce contracts, return composed response | FastAPI with Pydantic schemas |
| Intent extraction | Parse destination/weather/budget/dates from free text | Rule-based parser first, model-backed parser second |
| Clarification service | Detect missing constraints and ask next best question | Constraint completeness rules + session memory |
| Candidate generator | Produce destination shortlist before pricing | Metadata filter + heuristic recall |
| Pricing aggregation | Call provider adapters, normalize response shape | Async provider registry + canonical result model |
| Ranking service | Score and sort candidates across fit + price + quality | Weighted scoring with explicit features |
| Explanation service | Return transparent rationale per recommendation | Deterministic explanation templates from rank features |
| Ingestion workers | Refresh prices and provider health in background | Scheduled async jobs + retry/backoff |
| Persistence/cache | Store telemetry and short-lived live responses | PostgreSQL + Redis TTL caches |

## Recommended Project Structure

```
src/app/
├── api/                    # FastAPI routers/controllers
│   └── v1/
├── services/
│   ├── orchestration/      # request orchestration + workflow
│   ├── ranking/            # ranking + explanation logic
│   ├── clarification/      # missing-constraint detection/Q&A
│   └── pricing/            # provider aggregation facade
├── providers/              # provider adapters (Duffel, Expedia, etc.)
├── workers/                # scheduled ingestion + freshness checks
├── nlp/                    # intent extraction + query understanding
├── models/                 # SQLAlchemy models
├── schemas/                # API and internal typed contracts
├── db/                     # Postgres and Redis setup
└── core/                   # config, logging, security
```

### Structure Rationale

- **services/** isolates business logic from HTTP routing so ranking and ingestion can evolve independently.
- **providers/** enforces a stable adapter boundary when adding/replacing flight/hotel APIs.
- **workers/** keeps freshness jobs off the synchronous request path.
- **nlp/** separates parsing quality work from pricing/ranking concerns.

## Architectural Patterns

### Pattern 1: Provider Adapter + Canonical Domain Model

**What:** Every external supplier maps to the same internal `SearchResult` contract.
**When to use:** Always, especially with multiple suppliers and uneven payload quality.
**Trade-offs:** Slight mapping overhead, but avoids provider lock-in and simplifies ranking.

**Example:**
```python
class TravelProvider(ABC):
    async def search(self, request: SearchRequest, inventory_type: InventoryType) -> list[SearchResult]:
        ...
```

### Pattern 2: Two-Stage Retrieval (Recall → Rank)

**What:** First generate a broad destination candidate set, then run expensive live pricing + ranking.
**When to use:** Natural-language discovery where user intent is vague and global.
**Trade-offs:** More moving parts, but much better latency/cost than pricing every destination.

**Example:**
```python
candidates = candidate_generator.from_intent(intent, limit=50)
priced = await pricing_gateway.enrich(candidates, request)
ranked = ranking_service.rank(priced, intent)
```

### Pattern 3: Freshness-Aware Cache with Async Revalidation

**What:** Return recent cached provider results quickly, revalidate in background when stale.
**When to use:** Live pricing integrations with latency/rate-limit constraints.
**Trade-offs:** Potential short staleness window; major reliability and cost gains.

## Data Flow

### Request Flow (Natural Language Recommendation)

```
[User prompt]
    ↓
[Next.js UI]
    ↓
[POST /search]
    ↓
[Intent extraction + constraint resolver]
    ↓ (if missing critical info)
[Clarification question returned]
    ↓ (else continue)
[Destination candidate generation]
    ↓
[Pricing aggregation over provider adapters]
    ↓
[Ranking service]
    ↓
[Explanation generation]
    ↓
[Response: ranked destinations + reasons + provider status + warnings]
```

### Ingestion Flow (Live Pricing Data)

```
[Scheduler/queue trigger]
    ↓
[Provider worker pulls fresh offers/rates]
    ↓
[Normalization + currency conversion + sanity checks]
    ↓
[Write to Redis TTL cache + optional persisted snapshots]
    ↓
[Freshness metrics + health telemetry in Postgres]
    ↓
[Alert/retry path on provider errors or stale thresholds]
```

### Key Data Flows

1. **Interactive recommendation flow:** user prompt → structured intent → priced candidates → ranked + explained destinations.
2. **Background freshness flow:** provider polling → normalization/caching → health/freshness observability.
3. **Feedback loop flow:** search run telemetry (`search_runs`, `provider_runs`) → scoring weight tuning over time.

## Suggested Build Order (Roadmap Implications)

1. **Foundation + contracts first**
   - Build canonical schemas, provider interface, API contracts, telemetry tables.
   - Rationale: everything else depends on stable data contracts.

2. **NL intent + clarification before advanced ranking**
   - Ship robust constraint extraction + follow-up questions.
   - Rationale: ranking quality is capped if intent is underspecified.

3. **Provider aggregation with one live source (Duffel) + one stay fallback**
   - Keep adapter boundary strict, return provider status/warnings.
   - Rationale: proves live-integration architecture while limiting scope risk.

4. **Candidate generation + ranking + explanation service**
   - Introduce two-stage retrieval and explicit scoring features.
   - Rationale: moves from “search cards” to true destination recommendations.

5. **Background ingestion/freshness hardening**
   - Add scheduled refresh, stale-data handling, retries, and freshness SLAs.
   - Rationale: required for budget trust and reliable scaling.

6. **Scale/quality phase**
   - Add more providers, improve scoring models, personalize from interaction history.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Modular monolith (current shape), Redis cache, async provider fan-out is enough |
| 1k-100k users | Split workers from API, add queueing, isolate ranking service, tighten cache strategy |
| 100k+ users | Separate candidate/ranking/pricing services, regional caches, provider-specific circuit breakers |

### Scaling Priorities

1. **First bottleneck:** provider latency and rate limits → solve with TTL caching, retries, and asynchronous fan-out.
2. **Second bottleneck:** expensive ranking over too many candidates → solve with tighter recall and feature precomputation.

## Anti-Patterns

### Anti-Pattern 1: Calling providers before intent is constrained

**What people do:** Fire live pricing calls from vague prompts.
**Why it's wrong:** High cost, high latency, weak relevance.
**Do this instead:** Extract intent + ask clarifying questions first, then price narrowed candidates.

### Anti-Pattern 2: Provider-specific fields leaking into core ranking logic

**What people do:** Rank directly on Duffel/Expedia raw payload fields.
**Why it's wrong:** Breaks when providers change and blocks multi-provider support.
**Do this instead:** Normalize to canonical internal fields, rank only on canonical schema.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Duffel (flights) | Async REST via provider adapter | Current live flight path in repository |
| Expedia (stays) | Redirect-first handoff | Live inventory/pricing not yet in-app; shown as redirect |
| Future hotel APIs | Same adapter contract | Add without changing ranking/public API contracts |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| API router ↔ orchestration service | Direct service call | Keep HTTP thin, business logic in services |
| Orchestration ↔ providers | Adapter interface | No provider-specific logic outside adapters |
| Orchestration ↔ ranking | Typed DTOs | Enables independent ranking experimentation |
| API/workers ↔ cache/db | Shared repository/data access | Keep access patterns explicit and observable |

## Sources

- Project context: `/home/rbrown/workspace/MiraiGo/.planning/PROJECT.md`
- Repository architecture and provider implementation:
  - `/home/rbrown/workspace/MiraiGo/src/app/services/search.py`
  - `/home/rbrown/workspace/MiraiGo/src/app/providers/base.py`
  - `/home/rbrown/workspace/MiraiGo/src/app/providers/duffel.py`
  - `/home/rbrown/workspace/MiraiGo/src/app/providers/expedia.py`
  - `/home/rbrown/workspace/MiraiGo/docs/duffel-local-setup.md`
- FastAPI async/concurrency guidance (official docs): https://fastapi.tiangolo.com/async/
- Duffel API reference overview (official docs): https://duffel.com/docs/api/overview/welcome

---
*Architecture research for: natural-language travel destination recommendation*
*Researched: 2026-04-24*
