import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Home from '../app/page'
import { fetchProviderStatuses, searchTrips } from '@/lib/api'

jest.mock('@/lib/api', () => ({
  fetchProviderStatuses: jest.fn(),
  searchTrips: jest.fn(),
}))

const mockedFetchProviderStatuses = fetchProviderStatuses as jest.Mock
const mockedSearchTrips = searchTrips as jest.Mock

describe('Home Page Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockedFetchProviderStatuses.mockResolvedValue([
      {
        provider: 'duffel',
        label: 'Duffel',
        configured: true,
        healthy: true,
        inventory_types: ['flight'],
        reason: null,
      },
      {
        provider: 'expedia',
        label: 'Expedia',
        configured: true,
        healthy: true,
        inventory_types: ['stay'],
        reason: 'Redirect-only hotel handoff. Live rates open on Expedia.',
      },
    ])
  })

  it('renders initial state and loads providers', async () => {
    render(<Home />)

    expect(screen.getByText(/miraiGo mvp/i)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('Duffel')).toBeInTheDocument()
    })
  })

  it('stores clarification response and keeps the same session across follow-up answers', async () => {
    mockedSearchTrips
      .mockResolvedValueOnce({
        search_id: 'search-1',
        query: 'Warm trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Japan',
          origin: null,
          date_range: { start: '2026-06-01', end: '2026-06-10' },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [
          {
            provider: 'duffel',
            label: 'Duffel',
            configured: true,
            healthy: true,
            inventory_types: ['flight'],
            reason: null,
          },
        ],
        warnings: [],
        results: [],
        clarification_state: {
          destination: {
            slot: 'destination',
            value_label: 'Japan',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          timeline: {
            slot: 'timeline',
            value_label: 'June 2026',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          trip_length: {
            slot: 'trip_length',
            value_label: null,
            confidence: 0.1,
            ambiguous: true,
            explicit_unknown: false,
            source: 'extracted',
          },
          budget: {
            slot: 'budget',
            value_label: '$2,000',
            confidence: 0.9,
            ambiguous: false,
            explicit_unknown: false,
            source: 'extracted',
          },
          next_question: {
            slot: 'trip_length',
            prompt: 'How many days should this trip be?',
            helper_text: 'A rough estimate is fine.',
          },
          recap: {
            chips: [
              {
                slot: 'destination',
                label: 'Destination',
                value_label: 'Japan',
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
        },
      })
      .mockResolvedValueOnce({
        search_id: 'search-2',
        query: 'Warm trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Japan',
          origin: null,
          date_range: { start: '2026-06-01', end: '2026-06-10' },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [],
        warnings: [],
        results: [],
        clarification_state: {
          destination: {
            slot: 'destination',
            value_label: 'Japan',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          timeline: {
            slot: 'timeline',
            value_label: 'June 2026',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          trip_length: {
            slot: 'trip_length',
            value_label: '7 days',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          budget: {
            slot: 'budget',
            value_label: '$2,000',
            confidence: 0.9,
            ambiguous: false,
            explicit_unknown: false,
            source: 'extracted',
          },
          next_question: null,
          recap: {
            chips: [],
            continue_label: 'Continue to Recommendations',
          },
          all_critical_slots_resolved: true,
        },
      })

    render(<Home />)

    fireEvent.change(screen.getByLabelText(/travel prompt/i), {
      target: { value: 'Warm beach trip in June' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => {
      expect(screen.getByText(/how many days should this trip be\?/i)).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/your answer/i), {
      target: { value: '7 days' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit answer/i }))

    await waitFor(() => {
      expect(mockedSearchTrips).toHaveBeenCalledTimes(2)
    })

    expect(mockedSearchTrips).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        query: 'Warm beach trip in June',
        destination: 'Japan',
        date_range: { start: '2026-06-01', end: '2026-06-10' },
        clarification_answer: {
          slot: 'trip_length',
          answer_text: '7 days',
          explicit_unknown: false,
        },
      })
    )
  })

  it('recap edit emits targeted reopen request and preserves unrelated constraints', async () => {
    mockedSearchTrips.mockResolvedValue({
      search_id: 'search-1',
      query: 'Tokyo summer trip',
      requested_inventory: ['stay', 'flight'],
      applied_filters: {
        destination: 'Japan',
        origin: null,
        date_range: { start: '2026-06-01', end: '2026-06-10' },
        travelers: { adults: 2, children: 0, infants: 0 },
        stay_filters: { amenities: ['wifi'] },
        flight_filters: { nonstop: false },
      },
      provider_status: [
        {
          provider: 'duffel',
          label: 'Duffel',
          configured: true,
          healthy: true,
          inventory_types: ['flight'],
          reason: null,
        },
        {
          provider: 'expedia',
          label: 'Expedia',
          configured: true,
          healthy: true,
          inventory_types: ['stay'],
          reason: 'Redirect-only hotel handoff. Live rates open on Expedia.',
        },
      ],
      warnings: [],
      results: [],
      clarification_state: {
        destination: {
          slot: 'destination',
          value_label: 'Japan',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        timeline: {
          slot: 'timeline',
          value_label: 'June 2026',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        trip_length: {
          slot: 'trip_length',
          value_label: '7 days',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        budget: {
          slot: 'budget',
          value_label: '$2,000',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        next_question: {
          slot: 'budget',
          prompt: 'What budget should we target?',
          helper_text: 'A rough range works.',
        },
        recap: {
          chips: [
            {
              slot: 'destination',
              label: 'Destination',
              value_label: 'Japan',
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
      },
    })

    render(<Home />)

    fireEvent.change(screen.getByLabelText(/travel prompt/i), {
      target: { value: 'Tokyo summer trip' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /edit destination/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /edit destination/i }))
    fireEvent.change(screen.getByLabelText(/update destination/i), {
      target: { value: 'Seoul' },
    })
    fireEvent.click(screen.getByRole('button', { name: /save destination edit/i }))

    await waitFor(() => {
      expect(mockedSearchTrips).toHaveBeenCalledTimes(2)
    })

    expect(mockedSearchTrips).toHaveBeenLastCalledWith(
      expect.objectContaining({
        query: 'Tokyo summer trip',
        date_range: { start: '2026-06-01', end: '2026-06-10' },
        recap_edit: {
          slot: 'destination',
          edited_value: 'Seoul',
          explicit_unknown: false,
        },
      })
    )

    expect(mockedSearchTrips).toHaveBeenLastCalledWith(
      expect.not.objectContaining({
        destination: undefined,
      })
    )
    expect(mockedSearchTrips).toHaveBeenLastCalledWith(
      expect.objectContaining({
        destination: 'Japan',
      })
    )
  })

  it('keeps continue CTA text contract when clarification complete', async () => {
    mockedSearchTrips.mockResolvedValue({
      search_id: 'search-1',
      query: 'Europe trip',
      requested_inventory: ['stay', 'flight'],
      applied_filters: {
        destination: 'Lisbon',
        origin: null,
        date_range: { start: '2026-07-01', end: '2026-07-07' },
        travelers: { adults: 2, children: 0, infants: 0 },
        stay_filters: { amenities: ['wifi'] },
        flight_filters: { nonstop: false },
      },
      provider_status: [],
      warnings: [],
      results: [],
      clarification_state: {
        destination: {
          slot: 'destination',
          value_label: 'Lisbon',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        timeline: {
          slot: 'timeline',
          value_label: 'July',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        trip_length: {
          slot: 'trip_length',
          value_label: '6 days',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        budget: {
          slot: 'budget',
          value_label: '$1800',
          confidence: 1,
          ambiguous: false,
          explicit_unknown: false,
          source: 'user',
        },
        next_question: null,
        recap: {
          chips: [
            {
              slot: 'destination',
              label: 'Destination',
              value_label: 'Lisbon',
              editable: true,
              explicit_unknown: false,
            },
          ],
          continue_label: 'Continue to Recommendations',
        },
        all_critical_slots_resolved: true,
      },
    })

    render(<Home />)

    fireEvent.change(screen.getByLabelText(/travel prompt/i), {
      target: { value: 'Europe trip' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: 'Continue to Recommendations' })
      ).toBeInTheDocument()
    })
  })

  it('preserves resolved trip length, budget, and weather fields on continue', async () => {
    mockedSearchTrips
      .mockResolvedValueOnce({
        search_id: 'search-continue-1',
        query: 'Warm beach trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Honolulu',
          origin: null,
          date_range: { start: '2026-06-10', end: '2026-06-17' },
          trip_length_days: 7,
          budget_range: {
            minimum: 1500,
            maximum: 2500,
            currency_code: 'USD',
          },
          weather_preference: {
            temperature: 'warm',
            precipitation: 'avoid_rain',
            source_text: 'warm and dry',
          },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [],
        warnings: [],
        results: [],
        clarification_state: {
          destination: {
            slot: 'destination',
            value_label: 'Honolulu',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          timeline: {
            slot: 'timeline',
            value_label: 'June 10-17',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          trip_length: {
            slot: 'trip_length',
            value_label: '7 days',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          budget: {
            slot: 'budget',
            value_label: '$1500-$2500',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          next_question: null,
          recap: {
            chips: [
              {
                slot: 'destination',
                label: 'Destination',
                value_label: 'Honolulu',
                editable: true,
                explicit_unknown: false,
              },
            ],
            continue_label: 'Continue to Recommendations',
          },
          all_critical_slots_resolved: true,
        },
      })
      .mockResolvedValueOnce({
        search_id: 'search-continue-2',
        query: 'Warm beach trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Honolulu',
          origin: null,
          date_range: { start: '2026-06-10', end: '2026-06-17' },
          trip_length_days: 7,
          budget_range: {
            minimum: 1500,
            maximum: 2500,
            currency_code: 'USD',
          },
          weather_preference: {
            temperature: 'warm',
            precipitation: 'avoid_rain',
            source_text: 'warm and dry',
          },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [],
        warnings: [],
        results: [],
        clarification_state: null,
      })

    render(<Home />)

    fireEvent.change(screen.getByLabelText(/travel prompt/i), {
      target: { value: 'Warm beach trip' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: 'Continue to Recommendations' })
      ).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: 'Continue to Recommendations' }))

    await waitFor(() => {
      expect(mockedSearchTrips).toHaveBeenCalledTimes(2)
    })

    expect(mockedSearchTrips).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        destination: 'Honolulu',
        date_range: { start: '2026-06-10', end: '2026-06-17' },
        trip_length_days: 7,
        budget_range: {
          minimum: 1500,
          maximum: 2500,
          currency_code: 'USD',
        },
        weather_preference: {
          temperature: 'warm',
          precipitation: 'avoid_rain',
          source_text: 'warm and dry',
        },
      })
    )
  })

  it('keeps resolved trip length and budget answers through continue in same turn sequence', async () => {
    mockedSearchTrips
      .mockResolvedValueOnce({
        search_id: 'seq-1',
        query: 'Warm beach trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Honolulu',
          origin: null,
          date_range: { start: '2026-06-10', end: '2026-06-17' },
          trip_length_days: null,
          budget_range: null,
          weather_preference: {
            temperature: 'warm',
            precipitation: 'avoid_rain',
            source_text: 'warm',
          },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [],
        warnings: [],
        results: [],
        clarification_state: {
          destination: {
            slot: 'destination',
            value_label: 'Honolulu',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          timeline: {
            slot: 'timeline',
            value_label: 'June 10-17',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          trip_length: {
            slot: 'trip_length',
            value_label: null,
            confidence: 0.2,
            ambiguous: true,
            explicit_unknown: false,
            source: 'extracted',
          },
          budget: {
            slot: 'budget',
            value_label: null,
            confidence: 0.2,
            ambiguous: true,
            explicit_unknown: false,
            source: 'extracted',
          },
          next_question: {
            slot: 'trip_length',
            prompt: 'How many days should this trip be?',
            helper_text: null,
          },
          recap: {
            chips: [],
            continue_label: 'Continue to Recommendations',
          },
          all_critical_slots_resolved: false,
        },
      })
      .mockResolvedValueOnce({
        search_id: 'seq-2',
        query: 'Warm beach trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Honolulu',
          origin: null,
          date_range: { start: '2026-06-10', end: '2026-06-17' },
          trip_length_days: 7,
          budget_range: null,
          weather_preference: {
            temperature: 'warm',
            precipitation: 'avoid_rain',
            source_text: 'warm',
          },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [],
        warnings: [],
        results: [],
        clarification_state: {
          destination: {
            slot: 'destination',
            value_label: 'Honolulu',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          timeline: {
            slot: 'timeline',
            value_label: 'June 10-17',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          trip_length: {
            slot: 'trip_length',
            value_label: '7 days',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          budget: {
            slot: 'budget',
            value_label: null,
            confidence: 0.2,
            ambiguous: true,
            explicit_unknown: false,
            source: 'extracted',
          },
          next_question: {
            slot: 'budget',
            prompt: 'What budget should we target?',
            helper_text: null,
          },
          recap: {
            chips: [],
            continue_label: 'Continue to Recommendations',
          },
          all_critical_slots_resolved: false,
        },
      })
      .mockResolvedValueOnce({
        search_id: 'seq-3',
        query: 'Warm beach trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Honolulu',
          origin: null,
          date_range: { start: '2026-06-10', end: '2026-06-17' },
          trip_length_days: 7,
          budget_range: {
            minimum: 1500,
            maximum: 2500,
            currency_code: 'USD',
          },
          weather_preference: {
            temperature: 'warm',
            precipitation: 'avoid_rain',
            source_text: 'warm',
          },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [],
        warnings: [],
        results: [],
        clarification_state: {
          destination: {
            slot: 'destination',
            value_label: 'Honolulu',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          timeline: {
            slot: 'timeline',
            value_label: 'June 10-17',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          trip_length: {
            slot: 'trip_length',
            value_label: '7 days',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          budget: {
            slot: 'budget',
            value_label: '$1500-$2500',
            confidence: 1,
            ambiguous: false,
            explicit_unknown: false,
            source: 'user',
          },
          next_question: null,
          recap: {
            chips: [],
            continue_label: 'Continue to Recommendations',
          },
          all_critical_slots_resolved: true,
        },
      })
      .mockResolvedValueOnce({
        search_id: 'seq-4',
        query: 'Warm beach trip',
        requested_inventory: ['stay', 'flight'],
        applied_filters: {
          destination: 'Honolulu',
          origin: null,
          date_range: { start: '2026-06-10', end: '2026-06-17' },
          trip_length_days: 7,
          budget_range: {
            minimum: 1500,
            maximum: 2500,
            currency_code: 'USD',
          },
          weather_preference: {
            temperature: 'warm',
            precipitation: 'avoid_rain',
            source_text: 'warm',
          },
          travelers: { adults: 2, children: 0, infants: 0 },
          stay_filters: { amenities: ['wifi'] },
          flight_filters: { nonstop: false },
        },
        provider_status: [],
        warnings: [],
        results: [],
        clarification_state: null,
      })

    render(<Home />)

    fireEvent.change(screen.getByLabelText(/travel prompt/i), {
      target: { value: 'Warm beach trip' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => {
      expect(screen.getByText(/how many days should this trip be\?/i)).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/your answer/i), {
      target: { value: '7 days' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit answer/i }))

    await waitFor(() => {
      expect(screen.getByText(/what budget should we target\?/i)).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/your answer/i), {
      target: { value: '$1500-$2500' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit answer/i }))

    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: 'Continue to Recommendations' })
      ).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: 'Continue to Recommendations' }))

    await waitFor(() => {
      expect(mockedSearchTrips).toHaveBeenCalledTimes(4)
    })

    expect(mockedSearchTrips).toHaveBeenNthCalledWith(
      4,
      expect.objectContaining({
        trip_length_days: 7,
        budget_range: {
          minimum: 1500,
          maximum: 2500,
          currency_code: 'USD',
        },
        weather_preference: {
          temperature: 'warm',
          precipitation: 'avoid_rain',
          source_text: 'warm',
        },
      })
    )
  })
})
