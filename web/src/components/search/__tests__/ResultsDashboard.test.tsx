import { render, screen } from '@testing-library/react'
import ResultsDashboard from '../ResultsDashboard'
import type { FlightSearchResult } from '@/lib/api'

const normalizedContractFixture = {
  inventory_type: 'flight',
  provider: 'duffel',
  provider_label: 'Duffel',
  title: 'Contract fixture',
  description: 'Canonical normalized contract fixture',
  total_price: 640,
  currency: 'USD',
  score: 90,
  price_known: true,
  price_label: null,
  origin_code: 'DEN',
  destination_code: 'BCN',
  departure_at: '2026-05-03T09:30:00',
  arrival_at: '2026-05-03T20:15:00',
  carrier_codes: ['TP'],
  stops: 1,
  duration: 'PT10H45M',
  price_minor: 64000,
  currency_code: 'USD',
  duration_minutes: 645,
  stops_count: 1,
  normalized_offer_id: 'offer-den-bcn-001',
  provider_offer_id: 'duffel-offer-123',
  missing_fields: [],
  conversion_status: 'native',
  airfare_provenance: {
    source_provider: 'duffel',
    provider_offer_id: 'duffel-offer-123',
    source_quote_at: '2026-05-01T12:00:00Z',
    source_payload_ref: 'payload-ref-1',
  },
  airfare_freshness: {
    freshness_source: 'provider_quote',
    freshness_at: '2026-05-01T12:00:00Z',
    fetched_at: '2026-05-01T12:01:00Z',
  },
} satisfies FlightSearchResult

describe('ResultsDashboard', () => {
  const providerStatuses = [
    {
      provider: 'duffel',
      label: 'Duffel',
      configured: true,
      healthy: true,
      inventory_types: ['flight'] as const,
      reason: null,
    },
    {
      provider: 'expedia',
      label: 'Expedia',
      configured: true,
      healthy: true,
      inventory_types: ['stay'] as const,
      reason: 'Redirect-only hotel handoff. Live rates open on Expedia.',
    },
  ]

  it('renders provider availability even before results load', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={null}
      />
    )

    expect(screen.getByText(/provider availability/i)).toBeInTheDocument()
    expect(screen.getByText(/^Expedia$/i)).toBeInTheDocument()
    expect(screen.getByText(/redirect-only hotel handoff/i)).toBeInTheDocument()
  })

  it('splits stay and flight results', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-1',
          query: 'Barcelona trip',
          requested_inventory: ['stay', 'flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: 'Denver',
            date_range: { start: '2026-05-03', end: '2026-05-08' },
            travelers: { adults: 2, children: 0, infants: 0 },
            stay_filters: { amenities: ['wifi'] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: ['One provider unavailable.'],
          results: [
            {
              inventory_type: 'stay',
              provider: 'expedia',
              provider_label: 'Expedia',
              title: 'Hotels in Barcelona',
              description: 'Open Expedia to see live hotel inventory and current partner pricing.',
              total_price: 0,
              currency: 'USD',
              redirect_url: 'https://example.com/stay',
              deep_link_label: 'View stays on Expedia',
              score: 50,
              price_known: false,
              price_label: 'Check live rates on Expedia',
              location_label: 'Barcelona',
              amenities: ['wifi'],
              nightly_price: null,
              check_in: '2026-05-03',
              check_out: '2026-05-08',
            },
            {
              inventory_type: 'flight',
              provider: 'duffel',
              provider_label: 'Duffel',
              title: 'DEN to BCN',
              description: 'Flight option',
              total_price: 640,
              currency: 'USD',
              redirect_url: 'https://example.com/flight',
              deep_link_label: 'Continue search',
              score: 90,
              price_known: true,
              price_label: null,
              origin_code: 'DEN',
              destination_code: 'BCN',
              departure_at: '2026-05-03T09:30:00',
              arrival_at: '2026-05-03T20:15:00',
              carrier_codes: ['TP'],
              stops: 1,
              duration: 'PT10H45M',
            },
          ],
        }}
      />
    )

    expect(screen.getByText(/stay results/i)).toBeInTheDocument()
    expect(screen.getByText(/flight results/i)).toBeInTheDocument()
    expect(screen.getByText(/hotels in barcelona/i)).toBeInTheDocument()
    expect(screen.getAllByText(/den to bcn/i).length).toBeGreaterThan(0)
    expect(screen.getByText(/one provider unavailable/i)).toBeInTheDocument()
    expect(screen.getByText(/check live rates on expedia/i)).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={true}
        providerStatuses={providerStatuses}
        response={null}
      />
    )

    expect(screen.getByTestId('loading-state')).toBeInTheDocument()
  })

  it('shows inventory-empty no-flight guidance when providers return no offers', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-2',
          query: 'Barcelona trip',
          requested_inventory: ['flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: 'DEN',
            date_range: { start: '2026-05-03', end: '2026-05-08' },
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: ['Duffel returned no flight offers for the selected route and dates.'],
          results: [],
        }}
      />
    )

    expect(screen.getByText(/flight search notice/i)).toBeInTheDocument()
    expect(screen.getByText(/duffel returned no flight offers/i)).toBeInTheDocument()
    expect(
      screen.getByText(
        /providers returned no flight offers for this route and date range, so airfare provenance details are unavailable/i
      )
    ).toBeInTheDocument()
    expect(screen.getByText(/try nearby airports or wider date ranges/i)).toBeInTheDocument()
    expect(screen.getByText(/relax nonstop, time, or budget filters/i)).toBeInTheDocument()
  })

  it('shows provider-degraded no-flight guidance when flight search is unavailable', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-3',
          query: 'Barcelona trip',
          requested_inventory: ['flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: 'DEN',
            date_range: { start: '2026-05-03', end: '2026-05-08' },
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: ['Duffel flight search unavailable: timeout'],
          results: [],
        }}
      />
    )

    const warningMessage = screen.getByText(/flight search unavailable/i)
    expect(warningMessage.closest('[aria-live="polite"]')).toBeInTheDocument()
    expect(
      screen.getByText(
        /live flight search is temporarily unavailable, so airfare provenance details cannot be shown right now/i
      )
    ).toBeInTheDocument()
    expect(screen.getByText(/retry this search in a few minutes/i)).toBeInTheDocument()
    expect(screen.getByText(/continue with stays now and rerun flights later/i)).toBeInTheDocument()
  })

  it('renders remediation callout for stay-only responses when flight prerequisites are pending', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-structured-1',
          query: 'Barcelona trip',
          requested_inventory: ['stay', 'flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: null,
            date_range: null,
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: [],
          clarification_state: {
            ...({
              destination: { slot: 'destination', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              timeline: { slot: 'timeline', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              trip_length: { slot: 'trip_length', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              budget: { slot: 'budget', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              recap: { chips: [], continue_label: 'Continue' },
              all_critical_slots_resolved: false,
              flight_requirements_pending: ['origin', 'date_range'],
              continue_block_reason: 'Add an origin city and travel dates to unlock flight pricing.',
            }),
          },
          results: [
            {
              inventory_type: 'stay',
              provider: 'expedia',
              provider_label: 'Expedia',
              title: 'Hotels in Barcelona',
              description: 'Open Expedia to see live hotel inventory and current partner pricing.',
              total_price: 0,
              currency: 'USD',
              redirect_url: 'https://example.com/stay',
              deep_link_label: 'View stays on Expedia',
              score: 50,
              price_known: false,
              price_label: 'Check live rates on Expedia',
              location_label: 'Barcelona',
              amenities: ['wifi'],
              nightly_price: null,
              check_in: '2026-05-03',
              check_out: '2026-05-08',
            },
          ],
        }}
      />
    )

    expect(screen.getByText(/flight search notice/i)).toBeInTheDocument()
    expect(screen.getByText(/add an origin city and travel dates to unlock flight pricing/i)).toBeInTheDocument()
    expect(screen.getByText(/missing prerequisites: origin, date_range/i)).toBeInTheDocument()
  })

  it('uses structured remediation fields even when warnings are empty', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-structured-2',
          query: 'Flight remediation copy',
          requested_inventory: ['flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: null,
            date_range: null,
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: [],
          clarification_state: {
            ...({
              destination: { slot: 'destination', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              timeline: { slot: 'timeline', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              trip_length: { slot: 'trip_length', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              budget: { slot: 'budget', confidence: 1, ambiguous: false, explicit_unknown: false, source: 'user' },
              recap: { chips: [], continue_label: 'Continue' },
              all_critical_slots_resolved: false,
              flight_requirements_pending: ['origin'],
              continue_block_reason: 'Add your departure airport to continue.',
            }),
          },
          results: [],
        }}
      />
    )

    expect(screen.getByText(/flight search notice/i)).toBeInTheDocument()
    expect(screen.getByText(/add your departure airport to continue/i)).toBeInTheDocument()
    expect(screen.getByText(/missing prerequisites: origin/i)).toBeInTheDocument()
    expect(
      screen.getByText(
        /flight prerequisites are still missing, so live airfare provenance details are not available yet/i
      )
    ).toBeInTheDocument()
    expect(screen.getByText(/add the missing flight prerequisites listed above/i)).toBeInTheDocument()
    expect(screen.getByText(/continue once those details are filled to fetch flight offers/i)).toBeInTheDocument()
    expect(screen.queryByText(/^no flight results returned\.$/i)).not.toBeInTheDocument()
  })

  it('keeps provenance and freshness metadata visible when flight data exists', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-structured-3',
          query: 'Flight metadata visibility',
          requested_inventory: ['flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: 'DEN',
            date_range: { start: '2026-05-03', end: '2026-05-08' },
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: [],
          results: [{ ...normalizedContractFixture, title: 'Metadata flight card' }],
        }}
      />
    )

    expect(screen.getByText(/source: duffel/i)).toBeInTheDocument()
    expect(screen.getByText(/freshness: provider_quote/i)).toBeInTheDocument()
  })

  it('keeps provider labels visible and preserves API flight ordering', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={[
          {
            provider: 'duffel',
            label: 'Duffel status',
            configured: true,
            healthy: true,
            inventory_types: ['flight'] as const,
            reason: null,
          },
        ]}
        response={{
          search_id: 'search-4',
          query: 'Flight order check',
          requested_inventory: ['flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: 'DEN',
            date_range: { start: '2026-05-03', end: '2026-05-08' },
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: [],
          results: [
            {
              inventory_type: 'flight',
              provider: 'duffel',
              provider_label: 'Carrier Alpha',
              title: 'First API flight',
              description: 'Flight option A',
              total_price: 640,
              currency: 'USD',
              redirect_url: 'https://example.com/flight-a',
              deep_link_label: 'Continue search',
              score: 92,
              price_known: true,
              price_label: null,
              origin_code: 'DEN',
              destination_code: 'BCN',
              departure_at: '2026-05-03T09:30:00',
              arrival_at: '2026-05-03T20:15:00',
              carrier_codes: ['TP'],
              stops: 1,
              duration: 'PT10H45M',
            },
            {
              inventory_type: 'flight',
              provider: 'duffel',
              provider_label: 'Carrier Beta',
              title: 'Second API flight',
              description: 'Flight option B',
              total_price: 680,
              currency: 'USD',
              redirect_url: 'https://example.com/flight-b',
              deep_link_label: 'Continue search',
              score: 91,
              price_known: true,
              price_label: null,
              origin_code: 'DEN',
              destination_code: 'BCN',
              departure_at: '2026-05-03T12:30:00',
              arrival_at: '2026-05-03T22:15:00',
              carrier_codes: ['TP'],
              stops: 1,
              duration: 'PT9H45M',
            },
          ],
        }}
      />
    )

    expect(screen.getByText('Carrier Alpha')).toBeInTheDocument()
    expect(screen.getByText('Carrier Beta')).toBeInTheDocument()
    const firstFlight = screen.getByText('First API flight')
    const secondFlight = screen.getByText('Second API flight')
    expect(firstFlight.compareDocumentPosition(secondFlight) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('renders normalized airfare comparison and provenance metadata', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-5',
          query: 'Normalized comparison',
          requested_inventory: ['flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: 'DEN',
            date_range: { start: '2026-05-03', end: '2026-05-08' },
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: [],
          results: [
            {
              ...normalizedContractFixture,
              title: 'Normalized flight',
              total_price: 999,
              stops: 3,
              duration: 'PT1H',
              price_minor: 64000,
              currency_code: 'USD',
              stops_count: 1,
              duration_minutes: 645,
            },
          ],
        }}
      />
    )

    expect(screen.getByText('$640')).toBeInTheDocument()
    expect(screen.getByText(/den to bcn • 1 stop • 645 min/i)).toBeInTheDocument()
    expect(screen.getByText(/source: duffel/i)).toBeInTheDocument()
    expect(screen.getByText(/freshness: provider_quote/i)).toBeInTheDocument()
    expect(screen.getByText(/conversion: native/i)).toBeInTheDocument()
  })

  it('keeps normalized_offer_id-driven ordering stable across rerenders', () => {
    const baseResponse = {
      search_id: 'search-6',
      query: 'Stable ordering',
      requested_inventory: ['flight'] as const,
      applied_filters: {
        destination: 'Barcelona',
        origin: 'DEN',
        date_range: { start: '2026-05-03', end: '2026-05-08' },
        travelers: { adults: 1, children: 0, infants: 0 },
        stay_filters: { amenities: [] },
        flight_filters: { nonstop: false },
      },
      provider_status: providerStatuses,
      warnings: [],
    }

    const { rerender } = render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          ...baseResponse,
          results: [
            { ...normalizedContractFixture, normalized_offer_id: 'offer-002', title: 'Offer B' },
            { ...normalizedContractFixture, normalized_offer_id: 'offer-001', title: 'Offer A' },
          ],
        }}
      />
    )

    rerender(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          ...baseResponse,
          results: [
            { ...normalizedContractFixture, normalized_offer_id: 'offer-001', title: 'Offer A' },
            { ...normalizedContractFixture, normalized_offer_id: 'offer-002', title: 'Offer B' },
          ],
        }}
      />
    )

    const offerA = screen.getByText('Offer A')
    const offerB = screen.getByText('Offer B')
    expect(offerA.compareDocumentPosition(offerB) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('renders deterministic fallback text when normalized fields are null-present', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={providerStatuses}
        response={{
          search_id: 'search-7',
          query: 'Fallback normalized fields',
          requested_inventory: ['flight'],
          applied_filters: {
            destination: 'Barcelona',
            origin: 'DEN',
            date_range: { start: '2026-05-03', end: '2026-05-08' },
            travelers: { adults: 1, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: providerStatuses,
          warnings: [],
          results: [
            {
              ...normalizedContractFixture,
              title: 'Fallback flight',
              price_minor: null,
              currency_code: null,
              duration_minutes: null,
              stops_count: null,
              missing_fields: ['price_minor', 'currency_code', 'duration_minutes', 'stops_count'],
            },
          ],
        }}
      />
    )

    expect(screen.getByText(/missing fields: price_minor, currency_code, duration_minutes, stops_count/i)).toBeInTheDocument()
    expect(screen.getByText(/den to bcn • 1 stop • pt10h45m/i)).toBeInTheDocument()
    expect(screen.getByText(/fallback: using legacy airfare fields/i)).toBeInTheDocument()
  })
})
