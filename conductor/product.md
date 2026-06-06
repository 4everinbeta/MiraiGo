# Initial Concept
MiraiGo Travel Discovery: An interactive, multi-agent travel discovery website that converts loose, vague natural-language prompts into ranked destination, stay, and flight packages.

# Product Guide: MiraiGo Travel Discovery

## 1. Product Vision & Goal
MiraiGo Travel Discovery is an interactive, multi-agent travel discovery website that converts loose, vague natural-language prompts into ranked destination, stay, and flight packages. It bridges the gap between natural human conversation and structured, live-pricing inventory searches.

## 2. Target Audience
* **Leisure Travelers**: Individual or group travelers seeking personalized destination suggestions and dynamic vacation planning without filling out rigid travel forms.
* **Exploratory Planners**: Users who have high-level travel desires (e.g., "Warm beach in June") but require conversational guidance and clarification to refine details like budget and timeline.

## 3. Core Features & User Flows
* **Conversational Clarification**: A guided intake form that accepts free-form text, parses slots, and conversationally asks targeted single-question follow-ups for ambiguous slots (e.g., budget, trip length, origin).
* **Accumulated State & Recap**: Interactive chip lists summarizing extracted constraints, permitting real-time manual slot edits and direct "Continue to Recommendations" bypasses once critical inputs are resolved.
* **Premium Stays & Flights Dashboard**: Rich visual cards showing real-time flight details (Duffel integration) and stay details (synthesized Expedia properties and Booking.com scraper) complete with rating badges, amenity tags, and computed total pricing.
* **User Search Persistence**: Telemetric tracking that records search runs, discovery preferences, and automates profile settings in the database.

## 4. Technology Stack & Architecture
* **Frontend**: Next.js App Router (TypeScript, Tailwind CSS, SWR, Axios).
* **Backend**: FastAPI web services, multi-agent orchestration, Redis caching, SQLAlchemy, PostgreSQL, BeautifulSoup stays scraper.

## 5. Scope Boundaries (v1)
* **In Scope**:
  * Free-text conversational travel intake with natural language processing.
  * Deterministic adapters for Duffel Flights and Expedia/Booking Stays.
  * Persistent user search history and default search preferences.
* **Out of Scope (v1)**:
  * Full day-by-day itinerary generation.
  * Direct payment processing and checkout booking execution (outbound referral/deep links only).
