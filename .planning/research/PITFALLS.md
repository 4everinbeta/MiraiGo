# Pitfalls Research

**Domain:** Natural-language travel destination recommendation (with live flight/hotel pricing)
**Researched:** 2026-04-24
**Confidence:** MEDIUM (strong on repo-specific risks, lower on externally-validated ecosystem claims in this run)

## Critical Pitfalls

### Pitfall 1: Treating vague intent as “search text only” instead of a progressive intent state

**What goes wrong:**
The system accepts free text, extracts partial intent, but does not maintain a structured “known vs unknown” intent state across turns. Users get generic destination lists that feel random.

**Why it happens:**
Teams optimize for first demo (“type prompt, get results”) and skip clarification orchestration (what to ask next, when to stop asking, how to resolve conflicts like “cheap but luxury”).

**How to avoid:**
- Define a typed `IntentState` contract (`known_constraints`, `missing_constraints`, `confidence_by_field`, `hard_constraints`, `soft_preferences`).
- Add a clarification policy: ask at most 1–2 highest-information questions per turn.
- Gate ranking quality on minimum intent completeness for key fields (budget range, date window/season, trip length, origin region).

**Warning signs:**
- Frequent user reformulations like “No, I meant…” after first results.
- Same prompt yields unstable destinations with minor wording changes.
- Clarification questions are either never asked or overly broad (“Tell me more”).

**Phase to address:**
**Phase 1 — Intent & Clarification Foundation**

---

### Pitfall 2: Silent fallback to mock/stale inventory that looks like live data

**What goes wrong:**
Provider failures return fabricated or stale fallback results, but responses still appear “successful.” Users assume prices and availability are real.

**Why it happens:**
Fail-soft patterns are added for resilience, but provenance metadata and degraded-state UX are not implemented.

**How to avoid:**
- Remove hidden mock fallbacks from production path.
- Require result provenance fields: `source`, `fetched_at`, `price_type` (`live|cached|estimated`), `provider_status`.
- Return partial results with explicit provider health status instead of pretending full success.

**Warning signs:**
- Same prices repeated across days/providers.
- Internal logs show provider errors while UI still claims “live results.”
- QA cannot tell whether a card is live, cached, or synthetic.

**Phase to address:**
**Phase 2 — Provider Reliability & Data Truthfulness**

---

### Pitfall 3: “Real-time pricing” promise without quote freshness SLOs

**What goes wrong:**
Prices drift between recommendation screen and click-through; users perceive bait-and-switch and lose trust quickly.

**Why it happens:**
“Live pricing integration” is treated as a binary integration milestone, not an operational reliability problem (TTL, refresh cadence, stale handling, currency normalization).

**How to avoid:**
- Set explicit freshness SLOs per source (example: flights ≤15 min, hotels ≤30 min for “live” label).
- Add stale-state policy: hide/grey out price if freshness exceeded; show “last checked X min ago.”
- Separate ranking score from pricing certainty score; don’t over-rank uncertain prices.

**Warning signs:**
- High click-through but low downstream conversion/engagement.
- User complaints: “price changed immediately.”
- Wide variance between repeated queries minutes apart with no freshness indicator.

**Phase to address:**
**Phase 2 — Provider Reliability & Data Truthfulness**

---

### Pitfall 4: Constraint leakage between NLP extraction, API contract, and ranking

**What goes wrong:**
The parser extracts fields (dates, modes, budget, duration), but downstream filtering/ranking ignores some of them. Product appears to “understand” language but behaves inconsistently.

**Why it happens:**
No single typed search contract enforced end-to-end; each layer evolves independently.

**How to avoid:**
- Introduce one canonical request/response schema used by NLP output, API layer, ranking, and frontend rendering.
- Add “constraint honor rate” tests (for each supported constraint, verify measurable result impact).
- Block release if any supported input field is accepted but ignored.

**Warning signs:**
- API accepts params that do not affect results.
- Frontend controls exist but are cosmetic.
- Test failures where expected filtering does not change result set.

**Phase to address:**
**Phase 1 — Intent & Clarification Foundation** (schema) and **Phase 3 — Relevance QA & Contract Enforcement** (verification)

---

### Pitfall 5: Over-personalized ranking before baseline relevance is stable

**What goes wrong:**
System introduces preference weighting/personalization early, masking basic retrieval failures. Users see confidently wrong results.

**Why it happens:**
Teams chase “smart” recommendations before building robust baseline matching and evaluation datasets.

**How to avoid:**
- Freeze v1 ranking to transparent, inspectable features (constraint match, climate fit, budget fit, travel-time fit).
- Build an offline relevance set with golden queries (including vague prompts) before advanced personalization.
- Log explanation factors per result and expose top factors in UI.

**Warning signs:**
- Team cannot explain *why* a destination ranked #1 in one sentence.
- Small model or synonym changes cause large rank volatility.
- Internal raters disagree heavily on top-3 relevance.

**Phase to address:**
**Phase 3 — Relevance QA & Contract Enforcement**

---

### Pitfall 6: No confidence-aware UX for ambiguous or contradictory user intent

**What goes wrong:**
System returns definitive recommendations despite low-confidence interpretation (“warm in December, no long flights, ultra-cheap, Europe-only”).

**Why it happens:**
Confidence is treated as internal telemetry only, not a product behavior driver.

**How to avoid:**
- Compute field-level confidence and contradiction detection.
- In low-confidence cases, switch UX mode from “ranked answers” to “option narrowing.”
- Surface assumption chips (“Assuming budget: <$1500”, “Assuming trip length: 7–10 days”) with quick edits.

**Warning signs:**
- Users repeatedly edit core constraints after seeing results.
- High abandonment after first result page for ambiguous prompts.
- Support feedback: “It misunderstands me.”

**Phase to address:**
**Phase 1 — Intent & Clarification Foundation** and **Phase 4 — Trust UX & Explainability**

---

### Pitfall 7: No provider-level observability or quality scoring

**What goes wrong:**
One weak provider quietly degrades the whole ranking pool (bad parsing, stale prices, missing amenities), but the team lacks visibility into which provider is hurting quality.

**Why it happens:**
Telemetry focuses on endpoint latency only, not data quality dimensions.

**How to avoid:**
- Track provider KPIs: success rate, freshness lag, parse completeness, null-price rate, median latency.
- Add provider circuit breakers and temporary disable toggles.
- Include provider quality penalties in ranking blend.

**Warning signs:**
- Spikes in null/malformed fields with no alert.
- Latency regressions without clear source attribution.
- Team discovers provider outages from users first.

**Phase to address:**
**Phase 2 — Provider Reliability & Data Truthfulness**

---

### Pitfall 8: Worldwide coverage goal without geographic data normalization

**What goes wrong:**
Destination names, currencies, seasons, airport-city mappings, and visa/travel assumptions are inconsistent across regions; recommendations feel US/EU-biased.

**Why it happens:**
Teams launch with global ambition but keep region-specific heuristics and incomplete normalization.

**How to avoid:**
- Normalize location entities (city/metro/airport/country), currencies, and climate seasonality by hemisphere.
- Build region-diverse test sets (APAC, LATAM, Africa, smaller cities).
- Require i18n-safe formatting for prices/dates.

**Warning signs:**
- Duplicate/fragmented destinations (“Tokyo”, “Tokyo Prefecture”, “NRT area”).
- Budget fit errors due to currency mismatch.
- Poor relevance on non-English or non-US-centric prompts.

**Phase to address:**
**Phase 3 — Relevance QA & Contract Enforcement** and **Phase 5 — Globalization Hardening**

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Keep provider mock fallbacks in production code path | Demo resilience | Data trust collapse; impossible to verify “live” claims | Never in production |
| Let frontend re-filter server results ad hoc | Faster UI iteration | Contract drift, cache waste, inconsistent counts/ranking | MVP-only if explicitly labeled as UI-only filter |
| Use broad exception swallowing for providers/cache | Avoid user-facing errors | Hidden outages, no root-cause visibility | Only temporarily with explicit alerts |
| Promise “real-time” without freshness metadata | Simpler UI copy | Bait-and-switch perception, churn | Never |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Flight/hotel providers | Treating scrape fallback as equivalent to API quote | Distinguish `live/cached/estimated`; show provider status |
| Multi-provider aggregation | Merging fields without canonical schema | Normalize to strict schema + validation per provider |
| Caching layer | Cache key built from raw/unordered filters | Canonicalize params, hash normalized payload, version keys |
| Currency/pricing | Comparing raw prices across currencies/fees | Convert to common currency and include fee/tax caveats |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Fan-out to all providers per query | Slow p95 latency, cost spikes | Intent-based provider routing + timeboxed partial responses | ~100+ concurrent users (depends on provider latency) |
| Retry-heavy synchronous provider path | Tail latencies explode | Lower timeout caps, jittered retries, circuit breakers | Under intermittent provider failures |
| No pagination/streaming | Large payloads, slow UI rendering | Paginate + progressively enrich results | Query volumes with broad intents |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing partner keys in client or logs | Credential compromise, vendor bans | Server-only key usage, redaction, rotation |
| No rate limiting on expensive search endpoint | Abuse, unexpected infra cost | Per-IP/token throttling + bot mitigation |
| Storing user intent/history without data lifecycle | Privacy/compliance risk | Retention policy, deletion controls, minimal PII storage |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Asking too many clarifying questions before any value | Early drop-off | Show provisional top picks quickly, then refine |
| Showing exact-looking prices with weak certainty | Trust erosion | Show confidence/freshness badges and caveats |
| Opaque ranking (“AI picked this”) | Perceived randomness | Show concise explanation factors tied to user constraints |

## "Looks Done But Isn't" Checklist

- [ ] **Natural-language search:** Verify extracted constraints are all honored in ranking/filtering (not just parsed).
- [ ] **Live pricing:** Verify each shown price has source + timestamp + freshness label.
- [ ] **Clarification flow:** Verify low-confidence prompts trigger targeted follow-up questions.
- [ ] **Global coverage:** Verify non-US/non-English prompts produce valid results.
- [ ] **Provider resilience:** Verify partial outage behavior is explicit, not silently fabricated.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Silent mock fallback in production | HIGH | Disable fallback path, mark stale/synthetic data, communicate incident, rebuild trust metrics |
| Contract drift between NLP/API/UI | MEDIUM | Freeze schema, add contract tests, deprecate unsupported params |
| Pricing trust regression | HIGH | Introduce freshness SLO + labels, audit provider timestamps, adjust ranking to confidence |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Progressive intent state missing | Phase 1 — Intent & Clarification Foundation | Clarification rate, reduced reformulation rate, intent completeness metrics |
| Silent mock/stale fallback | Phase 2 — Provider Reliability & Data Truthfulness | 100% result provenance coverage; no synthetic data in prod path |
| Real-time pricing without freshness SLOs | Phase 2 — Provider Reliability & Data Truthfulness | Price freshness SLO dashboard + alerting |
| Constraint leakage across layers | Phase 3 — Relevance QA & Contract Enforcement | Constraint honor test suite passes per field |
| Premature personalization | Phase 3 — Relevance QA & Contract Enforcement | Stable baseline relevance on golden dataset |
| Confidence-blind UX | Phase 4 — Trust UX & Explainability | Low-confidence prompts show assumptions/clarifications |
| No provider observability | Phase 2 — Provider Reliability & Data Truthfulness | Provider KPI dashboards + circuit-breaker events |
| Weak globalization normalization | Phase 5 — Globalization Hardening | Region-diverse eval set meets quality threshold |

## Sources

- Project context: `/home/rbrown/workspace/MiraiGo/.planning/PROJECT.md`
- Existing codebase risk audit: `/home/rbrown/workspace/MiraiGo/.planning/codebase/CONCERNS.md`
- Architecture reference: `/home/rbrown/workspace/MiraiGo/.planning/codebase/ARCHITECTURE.md`
- Integration reference: `/home/rbrown/workspace/MiraiGo/.planning/codebase/INTEGRATIONS.md`
- Stack reference: `/home/rbrown/workspace/MiraiGo/.planning/codebase/STACK.md`

---
*Pitfalls research for: natural-language travel recommendation with live pricing trust*
*Researched: 2026-04-24*
