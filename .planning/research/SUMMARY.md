# Project Research Summary

**Project:** MiraiGo Travel Discovery  
**Domain:** Natural-language-first travel destination recommendation with live pricing context  
**Researched:** 2026-04-24  
**Confidence:** MEDIUM-HIGH

## Executive Summary

MiraiGo is best positioned as a **destination discovery engine**, not a full trip planner: users start with vague natural-language intent, the system asks focused follow-up questions, then returns ranked destinations with transparent reasons and live budget context. Across all research, expert implementations converge on the same pattern: constrain intent first, then run selective pricing aggregation, then rank/explain from a canonical schema.

The recommended implementation path is a modular monolith: **Next.js + TypeScript frontend**, **FastAPI orchestration backend**, **PostgreSQL (+pgvector) as system of record**, and **Redis for freshness-aware caching**. Multi-provider travel integration is non-negotiable for production trust; start with Amadeus plus a second flight/hotel source behind adapter boundaries so ranking logic never depends on vendor-specific payloads.

Primary risks are trust failures, not UI polish: stale/synthetic prices presented as live, constraint leakage (parsed but not honored), and premature personalization masking weak baseline relevance. Mitigation is clear: canonical end-to-end contracts, provenance/freshness metadata on every priced result, provider observability, and a phased roadmap that validates intent quality + pricing truthfulness before advanced ranking controls.

## Key Findings

### Recommended Stack

Research indicates a pragmatic and modern stack with strong implementation fit for MiraiGo’s current repo and product shape.

**Core technologies:**
- **Next.js 16 + React 19 + TypeScript 6**: web experience, SSR/streaming, and maintainable conversational UX.
- **FastAPI 0.136 + Pydantic v2**: API orchestration, strict schemas, and strong fit for NL/tool-calling workflows.
- **PostgreSQL 16–18 + pgvector**: combines relational travel constraints with semantic destination matching.
- **Redis 7**: short-TTL cache for provider responses, session state, and rate-limit relief.
- **OpenAI Responses/tool-calling SDKs**: structured NL intent extraction and clarification/explanation generation.

**Critical version/implementation requirements:**
- Keep **FastAPI + Pydantic v2-native** alignment.
- Keep **Next.js 16 + React 19 major versions aligned**.
- Use **canonical provider adapters** from day one; do not couple ranking to raw vendor fields.

### Expected Features

**Must have (table stakes):**
- Natural-language prompt input with iterative narrowing.
- Ranked destination recommendations (best options first).
- Post-search filters (budget/date/stops/flight duration/trip length).
- Flexible date discovery and visible pricing context.
- Save/share shortlist.
- Per-result rationale (why this matches).

**Should have (competitive):**
- Clarifying follow-up questions for underspecified prompts.
- Constraint conflict detection with feasible alternatives.
- Transparent fit-score breakdown / “why not this destination”.
- Conversation memory and explicit tradeoff controls.

**Defer (v2+):**
- Full itinerary generation.
- In-product checkout/payments.
- Price guarantees.
- Social/community feed features.

### Architecture Approach

Architecture research strongly supports a **two-stage retrieval pipeline** with strict boundaries:
1. **Experience layer (Next.js)** captures prompt, handles clarification, and renders ranked + explained results.
2. **Orchestration layer (FastAPI services)** performs intent extraction, missing-constraint detection, candidate generation, provider fan-out, ranking, and explanation.
3. **Data + ingestion layer (Postgres/Redis/workers)** maintains freshness-aware pricing cache, provider telemetry, and background revalidation.

Key patterns to enforce:
- Provider adapter + canonical internal model.
- Recall → price enrichment → rank (avoid pricing the entire world per request).
- Freshness-aware caching with async revalidation and explicit degraded-state handling.

### Critical Pitfalls

1. **No progressive intent state** — causes random-feeling results.  
   *Prevention:* typed `IntentState`, completeness gates, high-information clarification policy.
2. **Silent mock/stale fallback disguised as live** — destroys trust quickly.  
   *Prevention:* strict provenance fields (`source`, `fetched_at`, `price_type`, `provider_status`) and explicit degraded UX.
3. **“Real-time” claim without freshness SLOs** — creates bait-and-switch perception.  
   *Prevention:* source-specific freshness SLOs + stale display policy + certainty-aware ranking.
4. **Constraint leakage across layers** — parser “understands” but ranking ignores fields.  
   *Prevention:* one canonical contract and constraint-honor test suite.
5. **Premature personalization** — obscures baseline relevance defects.  
   *Prevention:* transparent baseline scoring first, then controlled personalization rollout.

## Implications for Roadmap

Based on dependency and risk convergence across all four research streams, use the following phase structure.

### Phase 1: Intent & Contract Foundation
**Rationale:** Everything downstream fails if intent is underspecified or contracts drift.  
**Delivers:** Canonical request/response schemas, typed `IntentState`, clarification policy, baseline NL parsing, contract tests.  
**Addresses:** NL input, follow-up questions, rationale readiness, core filter semantics.  
**Avoids:** Progressive intent failure, constraint leakage.

### Phase 2: Provider Integration & Pricing Truthfulness
**Rationale:** Live pricing trust is central product value and highest external risk.  
**Delivers:** Adapter-based multi-provider integration (flight + hotel paths), provenance metadata, freshness SLO dashboards, circuit-breaker/retry strategy, partial-result UX.  
**Uses:** FastAPI async orchestration, Redis TTL cache, HTTPX, OpenTelemetry.  
**Avoids:** Silent mock fallback, stale-price trust failures, provider blind spots.

### Phase 3: Recommendation Core (Recall → Rank → Explain)
**Rationale:** Once constraints and truthful prices exist, ranking quality becomes the core differentiator.  
**Delivers:** Candidate generator, pricing enrichment pipeline, weighted ranking model, deterministic explanation templates, baseline relevance evaluation set.  
**Implements:** Two-stage retrieval and canonical scoring features.  
**Avoids:** Opaque/unstable ranking and premature personalization.

### Phase 4: UX Differentiators & Control Layer
**Rationale:** Add high-value features only after core recommendation reliability is validated.  
**Delivers:** Fit-score drilldown, “why not” diagnostics, tradeoff controls, improved conversational memory, assumption chips for ambiguity.  
**Addresses:** Differentiators from FEATURES.md without expanding to itinerary/checkout scope.  
**Avoids:** Overbuilding v1 and trust regressions from unexplained behavior.

### Phase 5: Globalization & Scale Hardening
**Rationale:** Worldwide coverage is a core promise and requires explicit normalization/evaluation work.  
**Delivers:** Region-diverse test sets, currency/location normalization hardening, multilingual prompt QA, worker split/queueing as traffic grows.  
**Addresses:** Global coverage and operational resilience.  
**Avoids:** US/EU bias, location fragmentation, region-specific relevance degradation.

### Phase Ordering Rationale

- Intent contracts must precede provider/ranking work to prevent downstream rework.
- Pricing truthfulness is prioritized before advanced UX because trust loss is existential for this product category.
- Ranking/explanation comes before control-layer features to avoid “controls on top of unstable relevance.”
- Globalization hardening is late only in sequence, not priority: baseline global support should ship in earlier phases, with formal hardening in Phase 5.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Provider commercial access and regional coverage tradeoffs (Amadeus/Duffel/Booking/Expedia onboarding constraints).
- **Phase 5:** Global normalization strategy (airport-city mapping, seasonality by hemisphere, non-English prompt behavior).
- **Phase 4:** Human-factors validation for ambiguity/confidence UX patterns.

Phases with standard patterns (can usually skip extra research-phase):
- **Phase 1:** FastAPI/Pydantic contract-first API + clarification state handling patterns are well-established.
- **Phase 3:** Two-stage recall→rank architecture and deterministic explanation patterns are mature and well-documented.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Mostly official docs/registries with concrete versioning and strong repo fit. |
| Features | MEDIUM | Strong table-stakes/differentiator signal, but competitor breadth was partially blocked by access limits. |
| Architecture | MEDIUM | Strong internal-repo grounding and established patterns; less externally benchmarked at large scale in this run. |
| Pitfalls | MEDIUM | High practical relevance and actionable controls, but partially inference-based beyond repo-specific issues. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Hotel API partner readiness/commercial constraints:** validate exact onboarding path and fallback plan during roadmap planning.
- **Freshness SLO targets by provider/market:** define measurable thresholds per inventory type before launch commitments.
- **Global quality validation dataset:** create multilingual, region-diverse golden query set early in execution.
- **Pricing/trust legal language:** align “live”, “cached”, and disclaimer copy with compliance expectations.
- **Personalization readiness gate:** define explicit baseline relevance KPI before enabling user-specific ranking weights.

## Sources

### Primary (HIGH confidence)
- `/home/rbrown/workspace/MiraiGo/.planning/PROJECT.md` — product scope, constraints, and success criteria.
- Official docs referenced in research files:
  - Next.js docs, FastAPI docs, PostgreSQL docs, pgvector project docs.
  - OpenAI function/tool-calling docs.
  - Amadeus, Duffel, Booking Demand, Expedia Rapid provider docs.
  - Google Flights/Explore, KAYAK Explore/AI, Booking flights product pages.

### Secondary (MEDIUM confidence)
- Repository implementation references in ARCHITECTURE/PITFALLS research:
  - `src/app/services/search.py`
  - `src/app/providers/base.py`
  - `src/app/providers/duffel.py`
  - `src/app/providers/expedia.py`
  - `.planning/codebase/*.md` concern/architecture/integration references.

### Tertiary (LOW confidence)
- Competitor comparisons where access was constrained (CAPTCHA/bot blocks) and inferred market parity assumptions require ongoing validation.

---
*Research completed: 2026-04-24*  
*Ready for roadmap: yes*
