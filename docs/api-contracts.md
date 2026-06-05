# Tool Adapter Contracts (Pricing)

The Pricing agent must use adapters. Start with stubs; later swap for real APIs.

## searchFlights
Input:
- originAirport (IATA)
- destination (city/airport)
- startDate, endDate
- travelers { adults, children, child_ages }
- constraints { nonstopOnly?, maxStops?, maxFlightHours? }

Output:
- flights[]: {
  id,
  carrier,
  departTime,
  returnTime,
  stops,
  cabin,
  baggage,
  fareRulesSummary,
  totalPrice,
  currency
}

## searchHotels
Input:
- destination
- startDate, endDate
- rooms (derived from travelers)
- preferences (hotel_type, area preference, star rating targets if any)

Output:
- hotels[]: {
  id,
  name,
  starRating,
  area,
  cancellation,
  nightlyRate,
  totalPrice,
  currency
}

## buildPackage
Input:
- flightId
- hotelId

Output:
- package: {
  id,
  flightId,
  hotelId,
  totalPrice,
  pricePerTraveler,
  included,
  excluded,
  bookingLinksOrIds
}