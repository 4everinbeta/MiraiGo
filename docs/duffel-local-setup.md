# Duffel Local Setup

This walkthrough gets the current MVP into a usable local state with:

- live flight search through `Duffel`
- hotel handoff through `Expedia` redirect links

In the current codebase, Duffel is the only live API-backed provider. Hotels use a redirect-first partner workflow rather than a live hotel inventory API.

## 1. Create a Duffel Account And Token

1. Sign up for a Duffel account.
2. Open the Duffel dashboard.
3. Create a test access token from the Developers area.
4. Copy the token for local use.

The backend defaults to Duffel's public API URL and `v2` request header in [src/app/core/config.py](/home/rbrown/workspace/MiraiGo/src/app/core/config.py:10), so you only need the token for local setup.

## 2. Populate `.env`

Copy the example file:

```bash
cp .env.example .env
```

Set:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=miraigo
DUFFEL_ACCESS_TOKEN=your_duffel_test_access_token
```

Important behavior:

- If `DUFFEL_ACCESS_TOKEN` is blank, the app still starts.
- When the token is blank, `Duffel` will show as unavailable.
- `Expedia` hotel redirects will still be available without any extra credentials.

## 3. Start The Stack

Run:

```bash
docker compose up --build
```

This starts:

- `db` on `localhost:5432`
- `redis` on `localhost:6379`
- `app` on `localhost:8000`
- `web` on `localhost:3000`

## 4. Verify Provider Health

Open:

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Readiness: `http://localhost:8000/health/ready`
- Provider status: `http://localhost:8000/api/v1/providers/status`

What to expect from `/api/v1/providers/status`:

- `duffel` shows `configured: true` and `healthy: true` when the token works
- `expedia` shows `configured: true` and `healthy: true`
- Expedia's reason explains that it is a redirect-only hotel handoff

What to expect from `/health/ready`:

- `database: true`
- `redis: true`
- no dependency warnings when the stack is healthy

Provider behavior is defined in:

- [src/app/providers/duffel.py](/home/rbrown/workspace/MiraiGo/src/app/providers/duffel.py:1)
- [src/app/providers/expedia.py](/home/rbrown/workspace/MiraiGo/src/app/providers/expedia.py:1)

## 5. Run A Real Search

Use a search that matches the current provider behavior:

- Flights require `origin`, `destination`, and a start date.
- Roundtrip flights also use the end date.
- Hotels always return an Expedia handoff card when `destination` is present.

Example values:

- Origin: `Denver`
- Destination: `Barcelona`
- Dates: future start and end dates
- Inventory: both `stay` and `flight`
- Adults: `1` or more

Important limitation:

- Duffel flight search in this MVP supports adults only.
- The current request model tracks child counts but not child ages, and Duffel requires ages for under-18 passengers.

Expected behavior:

- Flight results come from `Duffel`
- Stay results show an `Expedia` redirect card
- Duffel flight cards do not yet include a direct booking handoff URL

## 6. Troubleshooting

### Duffel shows unavailable

Check:

- `DUFFEL_ACCESS_TOKEN` is present in `.env`
- the stack was restarted after changing `.env`
- `/api/v1/providers/status` includes a Duffel error reason instead of a missing-token message

If needed, restart:

```bash
docker compose down
docker compose up --build
```

### Flights return no results

Check:

- origin and destination are present
- the start date is in the future
- the search uses adults only
- the city or airport names can be resolved to IATA codes by Duffel

No Duffel results for a given trip can still be a valid search outcome, even when provider health is good.

### Expedia is live but prices are not shown

That is expected. Expedia is currently a redirect-only stay provider in this MVP. Pricing is resolved on Expedia after the handoff.
