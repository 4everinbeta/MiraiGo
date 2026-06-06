# Technology Stack: MiraiGo Travel Discovery

This document details the exact languages, frameworks, databases, and third-party integrations utilized by the MiraiGo Travel Discovery project.

## 1. Programming Languages & Runtime
* **Python 3.12**: Powering the backend API, caching, scrapers, natural language processing, and database session layers.
* **TypeScript 5**: Powering the frontend Next.js App Router client, component styling, and frontend tests.
* **Node.js 20**: Runtime for frontend building and package execution.

## 2. Backend Architecture & Frameworks
* **FastAPI**: Core ASGI backend framework exposing RESTful HTTP endpoints (e.g. `/api/v1/orchestrator/turn`, `/health`).
* **SQLAlchemy & psycopg2-binary**: Python Object-Relational Mapper (ORM) and PostgreSQL database driver.
* **Alembic**: Database migrations management.
* **Redis**: Fast key-value store used to cache search query intents and provider results.
* **Pydantic Settings**: Centralized environment variable loading and validation.
* **BeautifulSoup4 & lxml**: High-performance HTML parsers for stay search scrapers (e.g. Booking.com scraper).

## 3. Frontend Architecture & Styling
* **Next.js 16 (App Router)**: Core React framework for client-side routing, server rendering, and page layout.
* **React 19 & SWR**: Component architecture with reactive, client-side data caching and fetching.
* **Axios**: HTTP client wrapper for orchestrator API requests.
* **Tailwind CSS v4 & PostCSS**: Custom style variables, theme tokens, and dynamic layouts.
* **shadcn/ui & Lucide Icons**: Premium UI primitives (buttons, cards, date pickers) and iconography.

## 4. Third-Party API Integrations
* **Duffel API**: Live self-service flight searches and flight offer parsing.
* **Expedia & Booking.com**: Synthesized and scraped accommodation results.

## 5. Testing & Quality Assurance
* **Pytest & Pytest-Cov**: Automated unit and integration testing suite for backend providers, services, and telemetry.
* **Jest & Testing Library**: Unit and component tests for Next.js files.
* **Playwright**: End-to-end (E2E) browser automation testing, visual regression snapshots, and `@axe-core/playwright` accessibility audits.
