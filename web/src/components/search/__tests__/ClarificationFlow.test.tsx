import { fireEvent, render, screen } from '@testing-library/react'
import type { ClarificationState } from '@/lib/api'
import SearchForm from '../SearchForm'
import ResultsDashboard from '../ResultsDashboard'

function buildClarificationState(
  overrides: Partial<ClarificationState> = {}
): ClarificationState {
  return {
    destination: {
      slot: 'destination',
      value_label: null,
      confidence: 0.1,
      ambiguous: true,
      explicit_unknown: false,
      source: 'extracted',
    },
    timeline: {
      slot: 'timeline',
      value_label: 'June 2026',
      confidence: 0.9,
      ambiguous: false,
      explicit_unknown: false,
      source: 'user',
    },
    trip_length: {
      slot: 'trip_length',
      value_label: '7 days',
      confidence: 0.9,
      ambiguous: false,
      explicit_unknown: false,
      source: 'user',
    },
    budget: {
      slot: 'budget',
      value_label: '$2,500',
      confidence: 0.8,
      ambiguous: false,
      explicit_unknown: false,
      source: 'extracted',
    },
    next_question: {
      slot: 'destination',
      prompt: 'Where do you want to travel?',
      helper_text: 'City, country, or a broad region all work.',
    },
    recap: {
      chips: [
        {
          slot: 'destination',
          label: 'Destination',
          value_label: 'Missing',
          editable: true,
          explicit_unknown: false,
        },
        {
          slot: 'timeline',
          label: 'Timeline',
          value_label: 'June 2026',
          editable: true,
          explicit_unknown: false,
        },
      ],
      continue_label: 'Continue to Recommendations',
    },
    all_critical_slots_resolved: false,
    flight_requirements_pending: [],
    continue_block_reason: null,
    ...overrides,
  }
}

describe('ClarificationFlow', () => {
  it('renders one active clarification prompt at a time', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState()}
      />
    )

    const prompts = screen.getAllByRole('heading', {
      name: /where do you want to travel\?/i,
    })

    expect(prompts).toHaveLength(1)
    expect(
      screen.queryByText(/no active clarification question/i)
    ).not.toBeInTheDocument()
  })

  it('renders editable recap chips and sends recap_edit payload on chip edit', () => {
    const onSearch = jest.fn()
    render(
      <SearchForm
        onSearch={onSearch}
        clarificationState={buildClarificationState()}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /edit destination/i }))
    fireEvent.change(screen.getByLabelText(/update destination/i), {
      target: { value: 'Japan' },
    })
    fireEvent.click(screen.getByRole('button', { name: /save destination edit/i }))

    expect(onSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        recap_edit: {
          slot: 'destination',
          edited_value: 'Japan',
          explicit_unknown: false,
        },
      })
    )
  })

  it('shows exact continue CTA label when clarification is complete', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
        })}
      />
    )

    expect(
      screen.getByRole('button', { name: 'Continue to Recommendations' })
    ).toBeInTheDocument()
  })

  it('continues with preserved resolved constraints without resetting unrelated fields', () => {
    const onSearch = jest.fn()
    render(
      <SearchForm
        onSearch={onSearch}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
        })}
        preservedRequest={{
          destination: 'Lisbon',
          date_range: { start: '2026-06-01', end: '2026-06-08' },
          trip_length_days: 7,
          budget_range: { minimum: 1500, maximum: 2500, currency_code: 'USD' },
        }}
      />
    )

    fireEvent.change(screen.getByLabelText(/travel prompt/i), {
      target: { value: 'Lisbon trip in June' },
    })
    fireEvent.click(screen.getByRole('button', { name: /continue to recommendations/i }))

    expect(onSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        destination: 'Lisbon',
        trip_length_days: 7,
        budget_range: expect.objectContaining({ maximum: 2500 }),
      })
    )
  })

  it('submits clarification answers with preserved resolved constraints to keep continuity across degraded turns', () => {
    const onSearch = jest.fn()
    render(
      <SearchForm
        onSearch={onSearch}
        clarificationState={buildClarificationState({
          next_question: {
            slot: 'trip_length',
            prompt: 'How many days?',
          },
        })}
        preservedRequest={{
          destination: 'Lisbon',
          origin: 'Denver',
          date_range: { start: '2026-06-01', end: '2026-06-08' },
          budget_range: { minimum: 1500, maximum: 2500, currency_code: 'USD' },
        }}
      />
    )

    fireEvent.change(screen.getByLabelText(/your answer/i), {
      target: { value: '7 days' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit answer/i }))

    expect(onSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        destination: 'Lisbon',
        origin: 'Denver',
        date_range: { start: '2026-06-01', end: '2026-06-08' },
        clarification_answer: {
          slot: 'trip_length',
          answer_text: '7 days',
          explicit_unknown: false,
        },
      })
    )
  })

  it('blocks continue and shows deterministic remediation when flight prerequisites remain unresolved', () => {
    const onSearch = jest.fn()
    render(
      <SearchForm
        onSearch={onSearch}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
          flight_requirements_pending: ['origin', 'date_range'],
          continue_block_reason: 'Continue needs origin and date_range before flight recommendations can load.',
        })}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /continue to recommendations/i }))

    expect(onSearch).not.toHaveBeenCalled()
    expect(
      screen.getByText('Continue needs origin and date_range before flight recommendations can load.')
    ).toBeInTheDocument()
  })

  it('renders origin remediation controls when continue is blocked by missing origin', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
          flight_requirements_pending: ['origin'],
          continue_block_reason: 'Continue needs origin before flight recommendations can load.',
        })}
      />
    )

    expect(screen.getByLabelText(/origin/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit origin/i })).toBeInTheDocument()
  })

  it('submits origin remediation with constraint_updates.origin while continue stays blocked', () => {
    const onSearch = jest.fn()
    render(
      <SearchForm
        onSearch={onSearch}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
          flight_requirements_pending: ['origin'],
          continue_block_reason: 'Continue needs origin before flight recommendations can load.',
        })}
        preservedRequest={{
          query: 'Lisbon trip in June',
          destination: 'Lisbon',
          date_range: { start: '2026-06-01', end: '2026-06-08' },
          trip_length_days: 7,
          budget_range: { minimum: 1500, maximum: 2500, currency_code: 'USD' },
        }}
      />
    )

    const continueButton = screen.getByRole('button', { name: /continue to recommendations/i })
    expect(continueButton).toBeDisabled()

    fireEvent.change(screen.getByLabelText(/origin/i), {
      target: { value: 'Denver' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit origin/i }))

    expect(onSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        destination: 'Lisbon',
        constraint_updates: expect.objectContaining({
          origin: 'Denver',
        }),
      })
    )
    expect(continueButton).toBeDisabled()
  })

  it('renders date-range remediation controls when continue is blocked by missing date_range', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
          flight_requirements_pending: ['date_range'],
          continue_block_reason: 'Continue needs date_range before flight recommendations can load.',
        })}
      />
    )

    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit date range/i })).toBeInTheDocument()
  })

  it('submits date-range remediation with constraint_updates.date_range shape', () => {
    const onSearch = jest.fn()
    render(
      <SearchForm
        onSearch={onSearch}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
          flight_requirements_pending: ['date_range'],
          continue_block_reason: 'Continue needs date_range before flight recommendations can load.',
        })}
        preservedRequest={{
          query: 'Lisbon trip in June',
          destination: 'Lisbon',
          origin: 'Denver',
          trip_length_days: 7,
          budget_range: { minimum: 1500, maximum: 2500, currency_code: 'USD' },
        }}
      />
    )

    fireEvent.change(screen.getByLabelText(/start date/i), {
      target: { value: '2026-06-01' },
    })
    fireEvent.change(screen.getByLabelText(/end date/i), {
      target: { value: '2026-06-08' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit date range/i }))

    expect(onSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        destination: 'Lisbon',
        constraint_updates: expect.objectContaining({
          date_range: {
            start: '2026-06-01',
            end: '2026-06-08',
          },
        }),
      })
    )
  })

  it('renders origin and date-range remediation controls together when both requirements are pending', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
          flight_requirements_pending: ['origin', 'date_range'],
          continue_block_reason: 'Continue needs origin and date_range before flight recommendations can load.',
        })}
      />
    )

    expect(screen.getByLabelText(/origin/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit origin/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit date range/i })).toBeInTheDocument()
  })

  it('shows explicit airfare remediation guidance mapped to each pending requirement key', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
          flight_requirements_pending: ['origin', 'date_range'],
          continue_block_reason: 'Continue needs origin and date_range before flight recommendations can load.',
        })}
      />
    )

    expect(
      screen.getByText('Add your departure origin to unlock airfare recommendations.')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Add a travel date range (start and optional end date) to unlock airfare recommendations.')
    ).toBeInTheDocument()
  })

  it('renders explicit degraded-state reliability guidance from typed response fields', () => {
    render(
      <ResultsDashboard
        errorMessage={null}
        isLoading={false}
        providerStatuses={[]}
        response={
          {
            search_id: 'search-degraded',
            query: 'Warm beach trip',
            requested_inventory: ['flight'],
            applied_filters: {
              destination: 'Honolulu',
              origin: 'Denver',
              date_range: { start: '2026-06-01', end: '2026-06-08' },
              travelers: { adults: 1, children: 0, infants: 0 },
              stay_filters: { amenities: [] },
              flight_filters: { nonstop: false },
            },
            provider_status: [],
            warnings: [],
            results: [],
            degraded_state: {
              active: true,
              inventory_types: ['flight'],
              degraded_providers: [
                {
                  provider: 'partialfail',
                  label: 'Partial Failure',
                  reason: 'upstream timeout',
                  inventory_types: ['flight'],
                },
              ],
            },
          } as never
        }
      />
    )

    expect(screen.getByText(/flight reliability degraded/i)).toBeInTheDocument()
    expect(screen.getByText(/partial failure/i)).toBeInTheDocument()
    expect(screen.getByText(/upstream timeout/i)).toBeInTheDocument()
  })
})
