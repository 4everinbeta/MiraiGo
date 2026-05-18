# Research: Improve Post-Intent Suggestions

## Decision 1: Hard constraints gate ranking before soft preference scoring

**Decision**: Apply hard-constraint filtering (**destination + timeline + budget**) before soft ranking signals. Then score remaining candidates on preference fit and confidence.

**Rationale**: Users perceive "wrong but highly ranked" results as system failure. Hard constraints first ensures top results are valid before optimization.

**Alternatives considered**:

- **Single blended score only**: Rejected because hard violations can still outrank valid options.
- **Strict hard filtering with no fallback**: Rejected because empty results are worse than transparent fallback options.

---

## Decision 2: Clarification answers are additive unless user explicitly edits a slot

**Decision**: Preserve resolved slot values across turns. Only reopen related slots when user performs recap edit/constraint update, not on normal answer submission.

**Rationale**: This prevents repetitive question loops and aligns with expected conversational continuity.

**Alternatives considered**:

- **Rebuild all slot states each turn from query only**: Rejected due to loss of resolved context.
- **Lock all resolved slots permanently**: Rejected because users need to revise constraints mid-session.

---

## Decision 3: Near-duplicate suppression by signature + dominant-attribute diversity

**Decision**: Remove suggestion duplicates using a stable signature (destination region + budget band + trip style cluster + timeline bucket). Enforce minimal diversity among top suggestions.

**Rationale**: Users need meaningful alternatives, not repeated variants.

**Alternatives considered**:

- **Exact text deduplication only**: Rejected; semantic duplicates still pass.
- **No deduplication**: Rejected due to perceived low quality and choice fatigue.

---

## Decision 4: Suggestion rationale must cite at least one user-provided or resolved constraint

**Decision**: Every suggestion includes **2–3 concise reason tags** and **one plain-language sentence** tied to resolved constraints.

**Rationale**: Explanation improves trust and enables quicker user correction when constraints are imperfect.

**Alternatives considered**:

- **No rationale**: Rejected due to low transparency.
- **Verbose rationale paragraphs**: Rejected due to readability and UI clutter concerns.

---

## Decision 5: Fallback behavior remains visible and constraint-aware

**Decision**: If no high-fit suggestions exist, return constrained fallback suggestions clearly labeled as partial fit with explicit reason labels. Default suggestion set size remains **3 suggestions**.

**Rationale**: A transparent fallback keeps flow continuity while preserving user agency.

**Alternatives considered**:

- **Return zero suggestions**: Rejected because it dead-ends user flow.
- **Return generic popular suggestions without warning**: Rejected because it appears incorrect or random.

---

## Decision 6: LLM-assisted suggestion generation is permitted with hard-constraint guardrails

**Decision**: Use LLM-assisted suggestion generation where helpful, but only after deterministic checks for destination + timeline + budget are applied. Any generated suggestion must pass post-generation constraint validation before display.

**Rationale**: LLM generation can improve variety and relevance language quality while deterministic gates prevent drift, hallucinated mismatches, and loop regressions.

**Alternatives considered**:

- **No LLM usage at all**: Rejected because it limits suggestion quality improvement opportunities.
- **LLM-first without deterministic validation**: Rejected because it increases risk of constraint violations and inconsistent user outcomes.
