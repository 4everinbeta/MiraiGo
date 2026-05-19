import { render, screen } from '@testing-library/react'
import ResultsDashboard from '../ResultsDashboard'

describe('Suggestion quality cards', () => {
  it('renders top suggestions with fallback label and reason tags', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={[]}
        response={{
          search_id: 'search-qa',
          query: 'Lisbon in June',
          requested_inventory: ['stay'],
          applied_filters: {
            destination: 'Lisbon',
            date_range: { start: '2026-06-10', end: '2026-06-16' },
            travelers: { adults: 2, children: 0, infants: 0 },
            stay_filters: { amenities: [] },
            flight_filters: { nonstop: false },
          },
          provider_status: [],
          warnings: [],
          results: [],
          recommendation_packages: [
            {
              bundle_id: 'pkg-1',
              destination: 'Lisbon',
              score: 89,
              rationale: ['Matches your key constraints with the strongest available inventory.'],
              rationale_text: 'Matches your key constraints with the strongest available inventory.',
              reason_tags: ['timeline match', 'budget fit', 'top provider score 88'],
              hard_constraint_status: {
                destination: true,
                timeline: true,
                budget: true,
              },
              fallback_level: 'high-fit',
            },
          ],
        }}
      />
    )

    expect(screen.getByText(/top suggestions/i)).toBeInTheDocument()
    expect(screen.getByText('Lisbon')).toBeInTheDocument()
    expect(screen.getByText(/high fit/i)).toBeInTheDocument()
    expect(screen.getByText(/timeline match/i)).toBeInTheDocument()
    expect(screen.getByText(/budget fit/i)).toBeInTheDocument()
  })
})
