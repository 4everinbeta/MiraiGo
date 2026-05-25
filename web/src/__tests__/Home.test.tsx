import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Home from '../app/page'
import { fetchProviderStatuses, orchestratorTurn } from '@/lib/api'

jest.mock('@/lib/api', () => ({
  fetchProviderStatuses: jest.fn(),
  orchestratorTurn: jest.fn(),
}))

const mockedFetchProviderStatuses = fetchProviderStatuses as jest.Mock
const mockedOrchestratorTurn = orchestratorTurn as jest.Mock

const makeDegradedOrchestratorResponse = (overrides = {}) => ({
  session_id: 'session-1',
  response_type: 'questions',
  markdown: '## Quick Questions\n- What dates are you considering?',
  open_questions: ['What dates are you considering?'],
  candidate_destinations: [],
  packages: [],
  itineraries: [],
  disclaimers: ['Prices are subject to change until booking is confirmed.'],
  executed_agents: ['intake', 'presenter'],
  search_response: {
    search_id: 'sid-1',
    query: 'beach vacation',
    requested_inventory: ['flight'],
    applied_filters: {
      travelers: { adults: 2, children: 0, infants: 0 },
      stay_filters: { amenities: [] },
      flight_filters: { nonstop: false },
    },
    provider_status: [
      {
        provider: 'duffel',
        label: 'Duffel',
        configured: true,
        healthy: false,
        inventory_types: ['flight'],
        reason: 'connection timeout',
      },
    ],
    degraded_state: {
      active: true,
      inventory_types: ['flight'],
      degraded_providers: [
        {
          provider: 'duffel',
          label: 'Duffel',
          reason: 'connection timeout',
          inventory_types: ['flight'],
        },
      ],
    },
    warnings: ['Duffel unavailable — flight prices may not reflect live rates.'],
    results: [],
    clarification_state: {
      destination: { slot: 'destination', confidence: 0.9, ambiguous: false, explicit_unknown: false, source: 'extracted' },
      timeline: { slot: 'timeline', confidence: 0.9, ambiguous: false, explicit_unknown: false, source: 'extracted' },
      trip_length: { slot: 'trip_length', confidence: 0.5, ambiguous: false, explicit_unknown: false, source: 'system' },
      budget: { slot: 'budget', confidence: 0.5, ambiguous: false, explicit_unknown: false, source: 'system' },
      recap: { chips: [], continue_label: 'Continue' },
      all_critical_slots_resolved: true,
      flight_requirements_pending: [],
    },
  },
  ...overrides,
})

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
    ])
  })

  it('renders initial state and loads providers', async () => {
    render(<Home />)

    expect(screen.getByText(/miraigo multi-agent/i)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('Duffel')).toBeInTheDocument()
    })
  })

  it('submits prompt to orchestrator and shows markdown response', async () => {
    mockedOrchestratorTurn.mockResolvedValue({
      session_id: 'session-1',
      response_type: 'questions',
      markdown: '## Quick Questions\n- What dates are you considering?',
      open_questions: ['What dates are you considering?'],
      candidate_destinations: [],
      packages: [],
      itineraries: [],
      disclaimers: ['Prices are subject to change until booking is confirmed.'],
      executed_agents: ['intake', 'policy_trust', 'presenter'],
      search_response: null,
    })

    render(<Home />)

    fireEvent.change(screen.getByPlaceholderText(/warm beach trip/i), {
      target: { value: 'I want a warm beach vacation.' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => {
      expect(mockedOrchestratorTurn).toHaveBeenCalledTimes(1)
    })
    expect(screen.getByText(/quick questions/i)).toBeInTheDocument()
  })

  it('includes search_payload in orchestrator request when submitting', async () => {
    mockedOrchestratorTurn.mockResolvedValue(makeDegradedOrchestratorResponse())

    render(<Home />)

    fireEvent.change(screen.getByPlaceholderText(/warm beach trip/i), {
      target: { value: 'I want a beach vacation.' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => expect(mockedOrchestratorTurn).toHaveBeenCalledTimes(1))

    const call = mockedOrchestratorTurn.mock.calls[0][0]
    expect(call).toHaveProperty('search_payload')
    expect(call.search_payload).not.toBeNull()
  })

  it('shows degraded provider notice from search_response', async () => {
    mockedOrchestratorTurn.mockResolvedValue(makeDegradedOrchestratorResponse())

    render(<Home />)

    fireEvent.change(screen.getByPlaceholderText(/warm beach trip/i), {
      target: { value: 'beach vacation' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    await waitFor(() => expect(mockedOrchestratorTurn).toHaveBeenCalledTimes(1))

    // Should render degraded notice in ResultsDashboard (unique text from degraded section)
    await waitFor(() => {
      expect(screen.getByText(/flight reliability degraded/i)).toBeInTheDocument()
    })
  })

  it('preserves clarification_state from search_response in follow-up turns', async () => {
    const firstResponse = makeDegradedOrchestratorResponse()
    const secondResponse = makeDegradedOrchestratorResponse({
      response_type: 'ideas',
      markdown: '## Destination Ideas\n- Cancun\n- Miami',
      open_questions: [],
    })

    mockedOrchestratorTurn
      .mockResolvedValueOnce(firstResponse)
      .mockResolvedValueOnce(secondResponse)

    render(<Home />)

    // First turn
    fireEvent.change(screen.getByPlaceholderText(/warm beach trip/i), {
      target: { value: 'beach vacation' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))
    await waitFor(() => expect(mockedOrchestratorTurn).toHaveBeenCalledTimes(1))

    // Second turn — should send preserved clarification_state back
    fireEvent.change(screen.getByPlaceholderText(/warm beach trip/i), {
      target: { value: 'Actually I prefer mountains' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))
    await waitFor(() => expect(mockedOrchestratorTurn).toHaveBeenCalledTimes(2))

    const secondCall = mockedOrchestratorTurn.mock.calls[1][0]
    expect(secondCall.search_payload?.clarification_state).toBeDefined()
    expect(secondCall.search_payload?.clarification_state?.all_critical_slots_resolved).toBe(true)
  })
})
