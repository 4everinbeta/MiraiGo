# Azure Deployment

MiraiGo is intended for split-service deployment on Azure:

- FastAPI API as a custom container App Service
- Next.js web app as a custom container App Service
- Azure Database for PostgreSQL
- Azure Cache for Redis

## Required Variables

### API service

- `DATABASE_URL`
- `REDIS_URL`
- `FRONTEND_ORIGIN`
- `DUFFEL_ACCESS_TOKEN` optional

### Web service

- `NEXT_PUBLIC_API_URL`

## Notes

- Do not model cloud deployment around Docker Compose.
- The included GitHub Actions workflow can push images to GHCR and optionally deploy to Azure App Service when publish-profile secrets are configured.
