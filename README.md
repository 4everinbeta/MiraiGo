# MiraiGo

Discover your next journey with the clarity of the future. MiraiGo is a travel search platform that uses natural language processing and parallel scraping to find the best travel options.

## Features

- **Natural Language Search:** Describe your dream trip in plain English.
- **Parallel Scraping:** Aggregates results from Expedia, Booking.com, and Airbnb simultaneously.
- **Intelligent Ranking:** Results are ranked based on how well they match your desired qualities.
- **Modern UI:** A clean, responsive frontend built with Next.js and shadcn/ui, featuring subtle Japanese-inspired design.

## Getting Started

### Using Docker (Recommended)

The easiest way to run the full stack (Frontend, Backend, Database, and Redis) is using Docker Compose.

1. **Ensure you have Docker and Docker Compose installed.**
2. **Start the stack:**
   ```bash
   docker compose up --build
   ```
3. **Access the application:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Manual Setup (Development)

#### Backend (FastAPI)

1. Navigate to the root directory.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   uvicorn src.app.main:app --reload
   ```

#### Frontend (Next.js)

1. Navigate to the `web/` directory:
   ```bash
   cd web
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

### UI Testing

MiraiGo includes a comprehensive UI testing suite using **Playwright**, covering functional regression, accessibility, and visual regression.

1. Navigate to the `web/` directory.
2. Run all E2E tests:
   ```bash
   npm run test:e2e
   ```
3. Run tests in UI mode (interactive):
   ```bash
   npm run test:e2e:ui
   ```
4. Update visual snapshots:
   ```bash
   npm run test:e2e:update
   ```

**Accessibility Audits:** Every functional test includes an automated accessibility audit powered by `axe-core`. Tests will fail if WCAG AA violations are detected.

## Tech Stack

- **Frontend:** Next.js (TypeScript), Tailwind CSS v4, shadcn/ui, SWR.
- **Backend:** FastAPI (Python), SQLAlchemy, PostgreSQL, Redis.
- **Infrastructure:** Docker, Docker Compose.

## License

MIT
# MiraiGo
