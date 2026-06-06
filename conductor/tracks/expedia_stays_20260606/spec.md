# Specification: Synthesized Expedia Accommodation Provider

## 1. Overview
The goal of this track is to refine the Expedia provider (`ExpediaRedirectProvider`) into a synthesized accommodations search provider (`ExpediaDemandProvider`). Currently, the Expedia provider returns a single redirect-only card which does not provide comparison value to travelers. This work will convert the provider to return multiple high-fidelity, realistic hotels tailored to the destination type with realistic price bands, ratings, and deep links.

## 2. Functional Requirements
* **Synthesized Hotel Results**:
  - Convert the Expedia provider to return multiple `StaySearchResult` items (e.g., 3 separate properties) rather than a single redirect card.
  - Generate properties with realistic names, ratings, nightly/total prices, and relevant amenities based on destination classification.
* **Destination-Tailored Mock Generator**:
  - Classify destinations into types (beach, mountain, historic, urban/city) to provide highly realistic and context-relevant hotel suggestions.
  - Dynamically calculate total prices based on nightly rate and the duration of stay in nights.
  - Filter and score results based on requested stay parameters (amenities, max price).
* **Deep Links**:
  - Generate deep links pointing to the Expedia search page for that specific property or query.

## 3. Acceptance Criteria
* **Multiple Results**: Searching with `InventoryType.STAY` returns multiple Expedia hotel choices instead of a single redirect card.
* **Realistic Pricing and Properties**: Stays must have pricing, ratings, and amenities generated dynamically based on destination and dates.
* **Test Verification**: Pytest unit tests cover the new Expedia provider logic, verifying pricing calculations, and result scoring.

## 4. Out of Scope (v1)
* Live HTML scraping of Expedia pages.
* Changes to other travel providers (Amadeus, Duffel, Booking).
