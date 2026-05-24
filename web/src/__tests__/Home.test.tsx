import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Home from '../app/page'
import { fetchProviderStatuses, orchestratorTurn } from '@/lib/api'

jest.mock('@/lib/api', () => ({
  fetchProviderStatuses: jest.fn(),
  orchestratorTurn: jest.fn(),
}))

const mockedFetchProviderStatuses = fetchProviderStatuses as jest.Mock
const mockedOrchestratorTurn = orchestratorTurn as jest.Mock

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
})
