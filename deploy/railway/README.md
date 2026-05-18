# Railway Deployment

MiraiGo should be deployed to Railway as separate services:

- `miraigo-api` from the repository root
- `miraigo-web` from `web/`
- managed PostgreSQL
- managed Redis

## Required Variables

### API service

- `DATABASE_URL`
- `REDIS_URL`
- `FRONTEND_ORIGIN`
- `DUFFEL_ACCESS_TOKEN` optional

### Web service

- `NEXT_PUBLIC_API_URL`

## Image Strategy

The GitHub Actions workflow publishes:

- `ghcr.io/<owner>/miraigo-api:latest`
- `ghcr.io/<owner>/miraigo-web:latest`

Railway can deploy directly from GitHub or from the published GHCR images.
