'use client'

import type { ItineraryProposal } from '@/lib/api'

interface ItineraryProposalCardProps {
  proposal: ItineraryProposal
  onSelect: (proposal: ItineraryProposal) => void
}

function formatEstimate(value: number): string {
  return `~$${Math.round(value).toLocaleString()}`
}

export default function ItineraryProposalCard({ proposal, onSelect }: ItineraryProposalCardProps) {
  const confidenceLabel = proposal.cost_estimate.confidence.toUpperCase()

  return (
    <article
      data-testid={`proposal-card-${proposal.proposal_id}`}
      className="rounded-xl border bg-white p-4 shadow-sm"
    >
      <header className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-sumi">{proposal.destination}</h3>
          <p className="text-sm text-muted-foreground">
            {proposal.duration_nights} nights · {proposal.travel_window.start}
            {proposal.travel_window.end ? ` to ${proposal.travel_window.end}` : ''}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-700">
            ESTIMATE
          </span>
          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
            {confidenceLabel}
          </span>
        </div>
      </header>

      <p className="mt-3 text-sm text-muted-foreground">{proposal.rationale}</p>

      <div className="mt-4 space-y-1 text-sm">
        <p>✈ Flight {formatEstimate(proposal.cost_estimate.flight_estimated)}</p>
        <p>🏨 Stay {formatEstimate(proposal.cost_estimate.stay_estimated)}</p>
        <p>
          🚗 Car{' '}
          {proposal.needs_car
            ? formatEstimate(proposal.cost_estimate.car_estimated)
            : 'Not needed'}
        </p>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <p className="text-base font-semibold">
          Total {formatEstimate(proposal.cost_estimate.total_estimated)}
        </p>
        <span
          className={`text-sm font-medium ${
            proposal.within_budget ? 'text-emerald-700' : 'text-amber-700'
          }`}
        >
          {proposal.within_budget ? 'Within budget' : proposal.over_budget_note ?? 'Over budget'}
        </span>
      </div>

      <button
        type="button"
        className="mt-4 rounded-lg border px-3 py-2 text-sm font-medium hover:bg-muted"
        onClick={() => onSelect(proposal)}
      >
        Select this trip
      </button>
    </article>
  )
}
