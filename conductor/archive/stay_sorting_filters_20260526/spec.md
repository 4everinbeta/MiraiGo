# Specification: Interactive Stay Value Sorting and Filters

## 1. Overview
This track introduces interactive sorting and filtering controls directly on the stays results section of the MiraiGo Results Dashboard. It allows leisure travelers to quickly compare accommodation options, rank stays by price or ratings, and refine options by price thresholds and key amenities with zero-latency client-side rendering.

## 2. Functional Requirements
* **Dynamic Stays Sorting**:
  * Implement a dropdown or button group in the stays results header to sort items by:
    1. **Match Score** (default, descending)
    2. **Absolute Total Price** (ascending)
    3. **Hotel Star Rating** (descending)
* **Interactive Stays Filters**:
  * **Price Threshold Slider**: An interactive slider allowing users to filter stays below a custom maximum price limit (automatically computed based on the maximum price in the results set).
  * **Amenities Multi-Select**: Dynamic checkboxes/chips to filter stays by key amenities (WiFi, Pool, Gym, Parking, Breakfast).
  * **Ratings Threshold**: Toggle buttons or filter options to show only stays above specific thresholds (e.g. All, 3+ Stars, 4+ Stars).
* **Client-Side Latency-Free Execution**:
  * All sorting and filtering must execute immediately on the React client side in `ResultsDashboard.tsx` to preserve state, ensure high-fidelity animations, and maintain 0ms response latency.

## 3. Visual Styling & Design Rules
* Follow the **Premium & Animated Minimalist** theme with glassmorphic styles, subtle radial borders, and smooth transitions.
* Animate card entries and exits gracefully when sorting or filters are modified.
* Badges and text in the filter bar must comply strictly with WCAG 2 AA guidelines (minimum contrast ratio of 4.5:1).

## 4. Acceptance Criteria
* Users can toggle sorting options (Score, Price, Stars) and see the list of stays re-ordered instantly.
* Users can adjust the price slider and instantly hide stays exceeding that total price.
* Users can select multiple amenity filters (e.g. WiFi and Pool) and only see stays that contain all selected amenities.
* Filtering/sorting does not clear or reload the conversation state or session context.
* Code passes all ESLint rules and frontend Jest tests compile and execute cleanly.
