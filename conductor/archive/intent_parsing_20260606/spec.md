# Specification: Improved Search Intent Parsing

## 1. Overview
The goal of this track is to improve the NLP search intent parsing logic (`src/app/nlp/intent.py`) to handle discovery queries more accurately. Specifically, it resolves confusion where the origin city (e.g., Denver in "from Denver") is falsely extracted as the destination, improves standalone origin extraction, and refines destination suggestions for "warm beach" queries.

## 2. Functional Requirements
* **Origin-Destination Confusion Guard**:
  - Prevent the destination extractor from extracting a city as the destination if it is explicitly preceded by "from" (indicating it is the origin) in the search query.
* **Stand-alone Origin Extraction**:
  - Enhance `extract_intent` and `extract_route_hints` to cleanly parse and extract the origin from phrases like `from <location>` even when no destination (`to <location>`) is present.
* **Warm & Beach Suggestion Expansion**:
  - Update `_generate_llm_candidate_destinations` in `src/app/services/search.py` to suggest "Miami", "Hawaii", and "Bahamas" (in addition to "Lisbon", "Mallorca", "Cancun") when "warm" or "beach" keywords are present in discovery queries.
* **Relative and Month-Based Timeline Parsing**:
  - Ensure that queries specifying a month (e.g. "in July") are mapped to the next future occurrence of that month (e.g. July 1, 2026 if today is June 2026) and that duration in days (e.g. "for seven days") updates the end date of the timeline.

## 3. Acceptance Criteria
* **No Origin-as-Destination Confusion**: A query like "Flights in July from Denver" extracts "Denver" as the origin, leaving the destination slot empty (to be clarified) rather than setting "Denver" as the destination.
* **Stand-alone Origin Extracted**: The origin slot is populated with "Denver" directly from "from Denver".
* **Expanded Suggestions**: "warm beach" query lists Miami, Hawaii, and Bahamas as suggestions.
* **Test Verification**: Pytest unit tests cover the new parsing edge cases and suggestions.

## 4. Out of Scope (v1)
* Integration of external LLM APIs (like OpenAI) for parsing.
* Changes to the stays/flights provider search APIs.
