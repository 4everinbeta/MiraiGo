import { fireEvent, render, screen } from '@testing-library/react'
import type { ItineraryProposal } from '@/lib/api'
import ItineraryProposalCard from '../ItineraryProposalCard'

const proposal: ItineraryProposal = {
  proposal_id: 'proposal-1',
  destination: 'Vancouver Island',
  destination_region_key: 'vancouver-island',
  travel_window: { start: '2026-07-01', end: '2026-07-07' },
  duration_nights: 6,
  travelers: { adults: 2, children: 1, infants: 0 },
  needs_car: true,
  cost_estimate: {
    total_estimated: 6400,
    flight_estimated: 2100,
    stay_estimated: 3400,
    car_estimated: 900,
    currency_code: 'USD',
    confidence: 'medium',
  },
  rationale: 'Nature-focused itinerary',
  within_budget: true,
  over_budget_note: null,
}

describe('ItineraryProposalCard', () => {
  it('renders destination and estimate badge', () => {
    render(<ItineraryProposalCard proposal={proposal} onSelect={jest.fn()} />)

    expect(screen.getByText(/vancouver island/i)).toBeInTheDocument()
    expect(screen.getByText(/estimate/i)).toBeInTheDocument()
    expect(screen.getAllByText(/~\$/i).length).toBeGreaterThan(0)
  })

  it('renders budget indicators and fires selection callback', () => {
    const onSelect = jest.fn()
    render(<ItineraryProposalCard proposal={proposal} onSelect={onSelect} />)

    expect(screen.getByText(/within budget/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /select this trip/i }))
    expect(onSelect).toHaveBeenCalledWith(proposal)
  })

  it('shows over-budget note when proposal is over budget', () => {
    render(
      <ItineraryProposalCard
        proposal={{ ...proposal, within_budget: false, over_budget_note: 'Over by $300' }}
        onSelect={jest.fn()}
      />
    )

    expect(screen.getByText(/over by \$300/i)).toBeInTheDocument()
  })
})
