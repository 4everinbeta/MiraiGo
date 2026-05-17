'use client'

import type { ItineraryProposal } from '@/lib/api'
import ItineraryProposalCard from './ItineraryProposalCard'

interface ItineraryProposalListProps {
  proposals: ItineraryProposal[]
  onSelect: (proposal: ItineraryProposal) => void
  isLoading?: boolean
}

export default function ItineraryProposalList({
  proposals,
  onSelect,
  isLoading = false,
}: ItineraryProposalListProps) {
  if (isLoading) {
    return (
      <section data-testid="itinerary-proposal-list" className="space-y-3 rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-semibold text-sumi">Here are your trip options</h2>
        <p className="text-sm text-muted-foreground">Generating itinerary options...</p>
      </section>
    )
  }

  if (proposals.length === 0) {
    return (
      <section data-testid="itinerary-proposal-list" className="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-semibold text-sumi">Here are your trip options</h2>
        <p className="text-sm text-muted-foreground">No proposals found.</p>
      </section>
    )
  }

  return (
    <section data-testid="itinerary-proposal-list" className="space-y-4 rounded-2xl border bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-semibold text-sumi">Here are your trip options</h2>
      <div className="grid gap-3">
        {proposals.map((proposal) => (
          <ItineraryProposalCard key={proposal.proposal_id} proposal={proposal} onSelect={onSelect} />
        ))}
      </div>
    </section>
  )
}
