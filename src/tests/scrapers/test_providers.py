import pytest

from src.app.core.config import settings
from src.app.providers.duffel import DuffelFlightsProvider


@pytest.mark.asyncio
async def test_duffel_provider_without_credentials_is_unconfigured(monkeypatch):
    monkeypatch.setattr(settings, "DUFFEL_ACCESS_TOKEN", "")
    provider = DuffelFlightsProvider()
    status = await provider.healthcheck()
    assert status.configured is False
    assert "Duffel access token" in (status.reason or "")
