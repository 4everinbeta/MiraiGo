import { render, screen } from '@testing-library/react'
import ResultsDashboard from '../ResultsDashboard'

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

  it('shows a dedicated flight notice panel when flight warnings are present', () => {
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
    expect(screen.getByText(/returned no flight offers/i)).toBeInTheDocument()
  })

  it('announces degraded flight warnings via aria-live polite region', () => {
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
})
