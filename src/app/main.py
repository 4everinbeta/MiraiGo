from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.v1 import itinerary, search
from src.app.core.config import settings
from src.app.core.logging import configure_logging
from src.app.db.redis import check_redis_connection
from src.app.db.session import check_database_connection
from src.app.schemas.search import HealthResponse
from src.app.services.search import search_service

configure_logging(settings.LOG_LEVEL)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(itinerary.router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/live", response_model=HealthResponse)
async def health_live() -> HealthResponse:
    statuses = await search_service.provider_status()
    return HealthResponse(
        status="ok",
        database=True,
        redis=True,
        providers=statuses,
        warnings=[],
    )


@app.get("/health/ready", response_model=HealthResponse)
async def health_ready() -> HealthResponse:
    database_ok = check_database_connection()
    redis_ok = check_redis_connection()
    provider_status = await search_service.provider_status()
    warnings = []
    if not database_ok:
        warnings.append("Database is not reachable.")
    if not redis_ok:
        warnings.append("Redis is not reachable.")
    if not any(status.configured and status.healthy for status in provider_status):
        warnings.append("No live providers are configured.")

    status = "ok" if database_ok and redis_ok else "degraded"
    return HealthResponse(
        status=status,
        database=database_ok,
        redis=redis_ok,
        providers=provider_status,
        warnings=warnings,
    )
