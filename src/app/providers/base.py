from __future__ import annotations

from abc import ABC, abstractmethod

from src.app.core.config import settings
from src.app.schemas.search import InventoryType, ProviderStatus, SearchRequest, SearchResult


class ProviderError(RuntimeError):
    pass


class TravelProvider(ABC):
    provider_name: str = "provider"
    display_name: str = "Provider"
    inventory_types: tuple[InventoryType, ...] = ()

    def __init__(
        self,
        *,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds or settings.PROVIDER_TIMEOUT_SECONDS
        self.max_retries = settings.PROVIDER_MAX_RETRIES if max_retries is None else max_retries

    @property
    def is_configured(self) -> bool:
        return True

    @property
    def unconfigured_reason(self) -> str | None:
        if self.is_configured:
            return None
        return f"{self.display_name} is not configured."

    def supports_inventory(self, inventory_type: InventoryType) -> bool:
        return inventory_type in self.inventory_types

    async def healthcheck(self) -> ProviderStatus:
        configured = self.is_configured
        return ProviderStatus(
            provider=self.provider_name,
            label=self.display_name,
            configured=configured,
            healthy=configured,
            inventory_types=list(self.inventory_types),
            reason=None if configured else self.unconfigured_reason,
        )

    @abstractmethod
    async def search(
        self,
        request: SearchRequest,
        inventory_type: InventoryType,
    ) -> list[SearchResult]:
        raise NotImplementedError
