from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from src.app.schemas.search import ConversionStatus

_ISO_DURATION_PATTERN = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?)?$"
)


def normalize_airfare_offer(
    *,
    provider: str,
    provider_offer_id: str | None,
    origin_code: str | None,
    destination_code: str | None,
    departure_at: str | None,
    arrival_at: str | None,
    total_price: Any,
    provider_currency: str | None,
    requested_currency: str | None,
    duration: Any,
    stops: Any,
    source_quote_at: str | None = None,
    fetched_at: str | None = None,
    source_payload_ref: str | None = None,
) -> dict[str, Any]:
    missing_fields: set[str] = set()

    canonical_origin = _normalize_airport_code(origin_code)
    canonical_destination = _normalize_airport_code(destination_code)
    canonical_departure = _normalize_datetime_string(departure_at)
    canonical_arrival = _normalize_datetime_string(arrival_at)
    if canonical_departure is None:
        missing_fields.add("departure_at")
    if canonical_arrival is None:
        missing_fields.add("arrival_at")

    price_minor = _to_minor_units(total_price)
    if price_minor is None:
        missing_fields.add("price_minor")

    duration_minutes = _to_duration_minutes(duration)
    if duration_minutes is None:
        missing_fields.add("duration_minutes")

    stops_count = _to_stops_count(stops)
    if stops_count is None:
        missing_fields.add("stops_count")

    requested_currency_code = _normalize_currency_code(requested_currency)
    provider_currency_code = _normalize_currency_code(provider_currency)
    currency_code = provider_currency_code or requested_currency_code
    conversion_status = _resolve_conversion_status(
        provider_currency_code=provider_currency_code,
        requested_currency_code=requested_currency_code,
    )

    normalized_offer_id = _build_normalized_offer_id(
        provider=provider,
        origin_code=canonical_origin,
        destination_code=canonical_destination,
        departure_at=canonical_departure,
        arrival_at=canonical_arrival,
        price_minor=price_minor,
        currency_code=currency_code,
    )

    return {
        "price_minor": price_minor,
        "currency_code": currency_code,
        "duration_minutes": duration_minutes,
        "stops_count": stops_count,
        "normalized_offer_id": normalized_offer_id,
        "provider_offer_id": _normalize_optional_string(provider_offer_id),
        "missing_fields": sorted(missing_fields),
        "conversion_status": conversion_status,
        "airfare_provenance": {
            "source_provider": _normalize_optional_string(provider),
            "provider_offer_id": _normalize_optional_string(provider_offer_id),
            "source_quote_at": _normalize_datetime_string(source_quote_at),
            "source_payload_ref": _normalize_optional_string(source_payload_ref),
        },
        "airfare_freshness": {
            "freshness_source": _resolve_freshness_source(
                source_quote_at=source_quote_at,
                fetched_at=fetched_at,
            ),
            "freshness_at": _normalize_datetime_string(source_quote_at)
            or _normalize_datetime_string(fetched_at),
            "fetched_at": _normalize_datetime_string(fetched_at),
        },
    }


def _to_minor_units(raw_price: Any) -> int | None:
    if raw_price is None:
        return None
    try:
        decimal_value = Decimal(str(raw_price).strip())
    except (InvalidOperation, ValueError):
        return None
    quantized = decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(quantized * 100)


def _to_duration_minutes(raw_duration: Any) -> int | None:
    if raw_duration is None:
        return None
    if isinstance(raw_duration, int):
        return raw_duration if raw_duration >= 0 else None
    if isinstance(raw_duration, str):
        value = raw_duration.strip()
        if not value:
            return None
        if value.isdigit():
            return int(value)
        match = _ISO_DURATION_PATTERN.match(value)
        if not match:
            return None
        days = int(match.group("days") or 0)
        hours = int(match.group("hours") or 0)
        minutes = int(match.group("minutes") or 0)
        return (days * 24 * 60) + (hours * 60) + minutes
    return None


def _to_stops_count(raw_stops: Any) -> int | None:
    if raw_stops is None:
        return None
    if isinstance(raw_stops, bool):
        return int(raw_stops)
    try:
        parsed = int(str(raw_stops).strip())
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _build_normalized_offer_id(
    *,
    provider: str,
    origin_code: str | None,
    destination_code: str | None,
    departure_at: str | None,
    arrival_at: str | None,
    price_minor: int | None,
    currency_code: str | None,
) -> str | None:
    canonical_payload = {
        "provider": _normalize_optional_string(provider),
        "origin_code": origin_code,
        "destination_code": destination_code,
        "departure_at": departure_at,
        "arrival_at": arrival_at,
        "price_minor": price_minor,
        "currency_code": currency_code,
    }
    if any(value is None for value in canonical_payload.values()):
        return None

    serialized = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"norm_{digest[:24]}"


def _resolve_conversion_status(
    *, provider_currency_code: str | None, requested_currency_code: str | None
) -> str | None:
    if provider_currency_code is None:
        return None
    if requested_currency_code is None or requested_currency_code == provider_currency_code:
        return ConversionStatus.NATIVE.value
    return ConversionStatus.UNAVAILABLE.value


def _resolve_freshness_source(
    *, source_quote_at: str | None, fetched_at: str | None
) -> str | None:
    if _normalize_datetime_string(source_quote_at):
        return "provider_quote"
    if _normalize_datetime_string(fetched_at):
        return "provider_fetch"
    return None


def _normalize_airport_code(raw_code: str | None) -> str | None:
    if not raw_code:
        return None
    value = raw_code.strip().upper()
    if len(value) != 3 or not value.isalpha():
        return None
    return value


def _normalize_currency_code(raw_currency: str | None) -> str | None:
    if not raw_currency:
        return None
    value = raw_currency.strip().upper()
    if len(value) != 3 or not value.isalpha():
        return None
    return value


def _normalize_datetime_string(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    value = raw_value.strip()
    return value or None


def _normalize_optional_string(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    value = str(raw_value).strip()
    return value or None
