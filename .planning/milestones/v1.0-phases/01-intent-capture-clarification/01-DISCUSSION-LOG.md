# Phase 1: Intent Capture & Clarification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-24T23:35:34Z
**Phase:** 01-intent-capture-clarification
**Areas discussed:** Clarification Strategy, Constraint Memory & Update Model, Intent Extraction Behavior, Conversation UX Flow

---

## Clarification Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Ask follow-up when ANY critical slot is missing | Deterministic and complete for Phase 1 | ✓ |
| Ask follow-up when 2+ critical slots are missing | Fewer interruptions | |
| Ask only on low-confidence extraction | More adaptive, less deterministic | |

**User's choice:** Ask follow-up if any critical slot is missing.
**Notes:** Critical slots chosen: destination/region, timeline/date-window, trip length, budget. Prompting format chosen: one question at a time in priority order destination → timeline → trip length → budget.

---

## Constraint Memory & Update Model

| Option | Description | Selected |
|--------|-------------|----------|
| Field-level merge | Update only answered slot values | ✓ |
| Replace whole constraint payload | Simpler state model, more destructive | |
| Merge + aggressive dependent clears | Strong normalization, higher churn | |

**User's choice:** Field-level merge, latest explicit user answer wins on conflicts.
**Notes:** Re-run missing-slot detection after each answer. If user is uncertain, store explicit unknown and continue with warning-aware broader output.

---

## Intent Extraction Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Follow-up on low confidence or ambiguity | Balances automation and quality | ✓ |
| Follow-up only on parse failure | Minimal interruption, lower quality | |
| Always ask for every slot | Maximum certainty, highest friction | |

**User's choice:** Confidence/ambiguity-triggered follow-up with a single global threshold in v1.
**Notes:** Timeline should normalize to date window + precision marker. Budget language should map to bounded normalized range with original text preserved.

---

## Conversation UX Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Inline conversational one-by-one prompts + running summary | Natural interaction and continuity | ✓ |
| Modal wizard | Structured, less conversational | |
| Sidebar checklist | Form-like, less guided | |

**User's choice:** Inline conversational flow.
**Notes:** Stop when all critical slots are known or explicitly unknown. Show recap with editable chips and continue CTA. Chip edits reopen only related slots.

---

## Claude's Discretion

- Select concrete threshold value and calibration method.
- Define slot dependency mapping for “related slot reopening”.
- Define exact UX copy for warnings and recap messages.

## Deferred Ideas

None.
