from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

import httpx

from src.app.schemas.search import InventoryType, ProviderStatus, SearchRequest, SearchResult


class ProviderError(Exception):
    """Raised when a provider cannot complete a search."""


class TravelProvider(ABC):
    provider_name: str
    display_name: str
    inventory_types: tuple[InventoryType, ...]

    def __init__(self, timeout_seconds: float = 12.0, max_retries: int = 2):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Whether the provider has enough credentials to serve live traffic."""

    @property
    def unconfigured_reason(self) -> str | None:
        if self.is_configured:
            return None
        return "Missing provider credentials."

    def supports_inventory(self, inventory_type: InventoryType) -> bool:
        return inventory_type in self.inventory_types

    async def healthcheck(self) -> ProviderStatus:
        healthy = self.is_configured
        return ProviderStatus(
            provider=self.provider_name,
            label=self.display_name,
            configured=self.is_configured,
            healthy=healthy,
            inventory_types=list(self.inventory_types),
            reason=None if healthy else self.unconfigured_reason,
        )

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.request(
                        method,
                        url,
                        headers=headers,
                        params=params,
                        data=data,
                        json=json,
                    )
                    response.raise_for_status()
                    return response.json()
                except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                    if attempt == self.max_retries - 1:
                        raise ProviderError(str(exc)) from exc
                    await asyncio.sleep(0.4 * (2**attempt))
        raise ProviderError("Provider request failed after retries.")

    @abstractmethod
    async def search(
        self, request: SearchRequest, inventory_type: InventoryType
    ) -> list[SearchResult]:
        """Execute a provider search for a specific inventory type."""
