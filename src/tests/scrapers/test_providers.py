import pytest

from src.app.providers.duffel import DuffelFlightsProvider


@pytest.mark.asyncio
async def test_duffel_provider_without_credentials_is_unconfigured():
    provider = DuffelFlightsProvider()
    status = await provider.healthcheck()
    assert status.configured is False
    assert "Duffel access token" in (status.reason or "")
