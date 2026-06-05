from src.app.providers.amadeus import AmadeusFlightsProvider
from src.app.providers.duffel import DuffelFlightsProvider
from src.app.providers.expedia import ExpediaRedirectProvider
from src.app.providers.booking import BookingDemandProvider
from src.app.providers.base import TravelProvider


def get_provider_registry() -> list[TravelProvider]:
    return [
        AmadeusFlightsProvider(),
        DuffelFlightsProvider(),
        ExpediaRedirectProvider(),
        BookingDemandProvider(),
    ]
