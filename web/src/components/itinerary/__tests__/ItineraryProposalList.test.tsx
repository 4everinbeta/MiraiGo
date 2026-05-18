import { fireEvent, render, screen } from '@testing-library/react'
import type { ItineraryProposal } from '@/lib/api'
import ItineraryProposalList from '../ItineraryProposalList'

const proposals: ItineraryProposal[] = [
  {
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
  },
  {
    proposal_id: 'proposal-2',
    destination: 'New England',
    destination_region_key: 'new-england',
    travel_window: { start: '2026-07-01', end: '2026-07-07' },
    duration_nights: 6,
    travelers: { adults: 2, children: 1, infants: 0 },
    needs_car: true,
    cost_estimate: {
      total_estimated: 6900,
      flight_estimated: 1800,
      stay_estimated: 3800,
      car_estimated: 1300,
      currency_code: 'USD',
      confidence: 'medium',
    },
    rationale: 'Road-trip itinerary',
    within_budget: true,
    over_budget_note: null,
  },
]

describe('ItineraryProposalList', () => {
  it('renders all proposal cards', () => {
    render(<ItineraryProposalList proposals={proposals} onSelect={jest.fn()} />)
    expect(screen.getByText(/vancouver island/i)).toBeInTheDocument()
    expect(screen.getByText(/new england/i)).toBeInTheDocument()
  })

  it('renders loading state', () => {
    render(<ItineraryProposalList proposals={[]} onSelect={jest.fn()} isLoading />)
    expect(screen.getByText(/generating itinerary options/i)).toBeInTheDocument()
  })

  it('renders empty state when proposals are empty', () => {
    render(<ItineraryProposalList proposals={[]} onSelect={jest.fn()} />)
    expect(screen.getByText(/no proposals found/i)).toBeInTheDocument()
  })

  it('passes through onSelect callback to cards', () => {
    const onSelect = jest.fn()
    render(<ItineraryProposalList proposals={[proposals[0]]} onSelect={onSelect} />)
    fireEvent.click(screen.getByRole('button', { name: /select this trip/i }))
    expect(onSelect).toHaveBeenCalledWith(proposals[0])
  })
})
