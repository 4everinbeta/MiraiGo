# Feature Research

**Domain:** Natural-language travel destination discovery (leisure)  
**Researched:** 2026-04-24  
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Free-form destination search input | Travel discovery products are expected to start from broad intent, not strict forms | MEDIUM | Input can be NL prompt or simple query, but must accept vague requests |
| Ranked destination recommendations | Users expect a “best options first” output, not an undifferentiated list | MEDIUM | Needs deterministic tie-breaking and quality signals |
| Post-search filters (budget/date/stops/duration) | Present in mainstream discovery tools (Google Flights, KAYAK Explore, Booking flights) | MEDIUM | Must work after first result set to support iterative narrowing |
| Flexible date discovery (“any time” / broad windows) | Common expectation in explore flows | MEDIUM | Requires date-window scoring and pricing aggregation |
| Price visibility on results | Users expect upfront affordability context | HIGH | For MiraiGo: must include live flight/hotel pricing integrations |
| Map/list exploration mode | Explore products commonly combine map browsing + list results | HIGH | Requires map/list sync and geocoded destination entities |
| Save shortlist / basic sharing | Core planning behavior is compare-now, decide-later | LOW | Simple saved list and shareable URL are enough for v1 |
| Reason shown for each recommendation | Especially expected in AI-assisted products to build trust | MEDIUM | At minimum: climate, budget, and travel-time fit summary |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required by market, but high-value for MiraiGo.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Clarifying follow-up questions for underspecified prompts | Converts vague intent into high-quality recommendations without forcing forms upfront | HIGH | Core differentiator vs filter-only competitors |
| Constraint conflict detection + feasible alternatives | Handles impossible asks gracefully and keeps user moving | HIGH | Example: “Not possible at this budget/date; nearest matches are X/Y” |
| Transparent fit-score breakdown | Increases trust by showing why each destination ranks where it does | MEDIUM | Prefer explicit factor weights over opaque LLM text |
| Conversational memory across turns | Feels like guided planning rather than repeated searches | MEDIUM | Must support preference updates and conflict resolution |
| “Why not this destination?” diagnostics | Reduces abandonment by explaining exclusions and adjustment paths | MEDIUM | Valuable after initial results dissatisfaction |
| Multi-objective ranking controls (cost vs warmth vs flight time) | Gives user control over tradeoffs in real time | HIGH | Strong personalization lever after baseline ranking is stable |

### Anti-Features (Commonly Requested, Often Problematic)

Features that sound attractive but are likely to derail v1.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full day-by-day itinerary generator in v1 | Feels “complete” and AI-forward | Splits focus from core destination discovery quality; large hallucination/scope risk | Keep destination-first; offer “next steps” links only |
| In-product booking checkout in v1 | Perceived conversion boost | Adds payment/compliance/support complexity too early | Partner deep links + outbound conversion tracking |
| Mandatory large form before first result | Feels safer for recommendation accuracy | Breaks natural-language-first interaction and hurts activation | Start with NL prompt; ask targeted follow-ups only when missing constraints are detected |
| Price guarantee promises at launch | Strong marketing message | Financial/legal liability and operational burden | Show price freshness timestamp + confidence band/disclaimer |
| Social feed/community content | Engagement optics | Moderation/content operations distract from product thesis | Lightweight collaborative shortlist sharing only |

## Feature Dependencies

```text
[Natural-language prompt input]
    └──requires──> [Intent extraction + normalization]
                       └──requires──> [Constraint schema: budget, dates, weather, trip length]
                       └──requires──> [Destination knowledge base]

[Clarifying follow-up questions]
    └──requires──> [Missing-constraint detection]
                       └──requires──> [Intent extraction + normalization]

[Ranked recommendations]
    └──requires──> [Scoring/ranking engine]
                       └──requires──> [Live flight/hotel pricing ingestion]
                       └──requires──> [Seasonality/weather data]
                       └──requires──> [Travel-time/connectivity data]

[Per-result rationale + fit score]
    └──requires──> [Structured scoring factors]
    └──enhances──> [User trust]

[Map exploration]
    └──requires──> [Geocoded destinations]
    └──requires──> [Synchronized filter/result state]
    └──enhances──> [Ranked recommendations]

[In-app booking checkout] ──conflicts──> [v1 destination-discovery focus]
```

### Dependency Notes

- **Do not ship clarifying Q&A before missing-constraint detection is reliable** or follow-ups will feel random.
- **Do not ship explanations before structured scoring exists** or “AI rationale” will drift from actual ranking logic.
- **Do not ship map-first UX before filter/result sync is stable** or users will see contradictory map/list results.
- **Live pricing ingestion is a hard dependency** for MiraiGo’s budget credibility requirement.

## MVP Definition

### Launch With (v1)

Minimum viable product to validate MiraiGo’s core thesis.

- [ ] Natural-language prompt input with targeted follow-up questions  
- [ ] Ranked destination recommendations with per-result rationale  
- [ ] Budget + season + trip-length constraint handling with live pricing context  
- [ ] Core filters (budget/date window/stops/flight duration)  
- [ ] Save/share shortlist  
- [ ] Global destination coverage baseline

### Add After Validation (v1.x)

- [ ] Map-first exploration mode (once ranking + state sync are stable)  
- [ ] Fit-score drilldown + “why not” diagnostics  
- [ ] Tradeoff controls for ranking weights

### Future Consideration (v2+)

- [ ] Alerting on shortlist changes (price/weather/season shifts)  
- [ ] Lightweight trip skeletons (still not full itinerary authoring)  
- [ ] Booking handoff optimization / affiliate orchestration

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| NL prompt + clarifying follow-up | HIGH | HIGH | P1 |
| Ranked destinations + rationale | HIGH | MEDIUM | P1 |
| Live pricing-aware budget fit | HIGH | HIGH | P1 |
| Core filters | HIGH | MEDIUM | P1 |
| Save/share shortlist | MEDIUM | LOW | P1 |
| Map exploration | MEDIUM | HIGH | P2 |
| Fit-score drilldown + why-not | MEDIUM | MEDIUM | P2 |
| Tradeoff controls | MEDIUM | HIGH | P2 |
| Alerts on shortlisted destinations | MEDIUM | MEDIUM | P3 |
| Itinerary generation | LOW (for current thesis) | HIGH | P3 / defer |

**Priority key:**
- P1: Must have for launch
- P2: Should have after core validation
- P3: Future consideration

## Competitor Feature Analysis

| Feature | Competitor A | Competitor B | Our Approach |
|---------|--------------|--------------|--------------|
| Explore discovery with flexible constraints | Google Flights shows Explore + flexible trip window + destination deal surfacing | KAYAK Explore shows “Any time, any duration,” map, price/stops filters | Keep these capabilities, but drive from natural-language prompt first |
| Discovery + price context | Google Flights emphasizes flight deals + tracked prices | Booking flights emphasizes compare/search + flexibility messaging + broad destination browsing | Provide live price context and freshness, but keep recommendation-first UX |
| AI planning entrypoint | Google Flights includes “Flexible? Discover the best flight deals with AI” prompt | KAYAK has “AI Travel Planner” and chat-like planning entry | Differentiate via constraint-aware clarifying dialogue and explainable ranking |

## Sources

- Project context: `/home/rbrown/workspace/MiraiGo/.planning/PROJECT.md` (**HIGH**)
- Google Flights official page (feature labels): https://r.jina.ai/http://www.google.com/travel/flights (**HIGH**)
- Google Explore page (flexible trip window/map context): https://r.jina.ai/http://www.google.com/travel/explore (**HIGH**)
- KAYAK Explore official page: https://r.jina.ai/http://www.kayak.com/explore (**HIGH**)
- KAYAK AI Travel Planner official page: https://r.jina.ai/http://www.kayak.com/ai (**HIGH**)
- Booking.com flights official page: https://r.jina.ai/http://www.booking.com/flights/index.html (**HIGH**)

**Research gaps / caveats:**
- Some major travel sites (e.g., Skyscanner, Tripadvisor, Expedia) were bot-blocked or CAPTCHA-gated from this environment, so competitor breadth is narrower than ideal.
- Confidence is **MEDIUM** because feature conclusions are strong, but cross-competitor coverage is partially constrained by access limits.

---
*Feature research for: Natural-language travel destination discovery*
*Researched: 2026-04-24*
