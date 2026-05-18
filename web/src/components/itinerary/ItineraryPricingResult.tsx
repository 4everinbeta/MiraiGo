'use client'

import type { ItineraryPriceResponse, ItineraryProposal } from '@/lib/api'

interface ItineraryPricingResultProps {
  result: ItineraryPriceResponse
  proposal: ItineraryProposal
  onBack: () => void
}

function formatMoney(value: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value)
}

export default function ItineraryPricingResult({
  result,
  proposal,
  onBack,
}: ItineraryPricingResultProps) {
  const liveTotal =
    result.flight_results.reduce((sum, flight) => sum + flight.total_price, 0) +
    result.stay_results
      .filter((stay) => stay.price_known)
      .reduce((sum, stay) => sum + stay.total_price, 0)

  return (
    <section data-testid="itinerary-pricing-result" className="space-y-4 rounded-2xl border bg-white p-6 shadow-sm">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Live Prices</p>
          <h2 className="text-2xl font-semibold text-sumi">{proposal.destination}</h2>
        </div>
        <button
          type="button"
          onClick={onBack}
          className="rounded-lg border px-3 py-2 text-sm font-medium hover:bg-muted"
        >
          Back to options
        </button>
      </header>

      <div className="flex flex-wrap gap-2 text-xs">
        {result.provider_status.map((status) => (
          <span
            key={status.provider}
            className={`rounded-full px-3 py-1 ${
              status.healthy ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
            }`}
          >
            {status.label}: {status.healthy ? 'available' : 'unavailable'}
          </span>
        ))}
      </div>

      <div className="rounded-xl border bg-slate-50 p-3 text-sm text-slate-700">
        Estimated: ~${Math.round(proposal.cost_estimate.total_estimated).toLocaleString()} → Live total:{' '}
        {formatMoney(liveTotal, proposal.cost_estimate.currency_code)} (from available offers)
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-muted-foreground">Flights</h3>
        {result.flight_results.length === 0 ? (
          <p className="text-sm text-muted-foreground">No live flight offers returned.</p>
        ) : (
          <div className="grid gap-3">
            {result.flight_results.map((flight, index) => (
              <article key={`${flight.provider}-${index}`} className="rounded-xl border p-4">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold">{flight.title}</p>
                  <span className="rounded-full bg-emerald-100 px-2 py-1 text-[11px] font-semibold text-emerald-700">
                    LIVE PRICE
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {flight.carrier_codes.join(', ') || flight.provider_label} · {flight.stops} stop(s)
                </p>
                <p className="text-sm text-muted-foreground">
                  {flight.departure_at} → {flight.arrival_at}
                </p>
                <p className="mt-2 text-base font-semibold">{formatMoney(flight.total_price, flight.currency)}</p>
                {flight.redirect_url ? (
                  <a className="mt-2 inline-block text-sm text-primary underline" href={flight.redirect_url} target="_blank" rel="noreferrer">
                    {flight.deep_link_label ?? 'Book'}
                  </a>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-muted-foreground">Stays</h3>
        {result.stay_results.length === 0 ? (
          <p className="text-sm text-muted-foreground">No live stay offers returned.</p>
        ) : (
          <div className="grid gap-3">
            {result.stay_results.map((stay, index) => (
              <article key={`${stay.provider}-${index}`} className="rounded-xl border p-4">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold">{stay.title}</p>
                  <span className="rounded-full bg-emerald-100 px-2 py-1 text-[11px] font-semibold text-emerald-700">
                    LIVE PRICE
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{stay.description}</p>
                <p className="mt-2 text-base font-semibold">
                  {stay.price_known ? formatMoney(stay.total_price, stay.currency) : stay.price_label ?? 'Live pricing'}
                </p>
                {stay.redirect_url ? (
                  <a className="mt-2 inline-block text-sm text-primary underline" href={stay.redirect_url} target="_blank" rel="noreferrer">
                    {stay.deep_link_label ?? 'Book'}
                  </a>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </div>

      {result.car_redirect_url ? (
        <div className="rounded-xl border p-4">
          <p className="text-sm font-semibold">Car rental</p>
          <a className="text-sm text-primary underline" href={result.car_redirect_url} target="_blank" rel="noreferrer">
            {result.car_redirect_label ?? 'Search car rentals'}
          </a>
        </div>
      ) : null}

      {result.warnings.length > 0 ? (
        <ul className="list-disc space-y-1 pl-5 text-sm text-amber-700">
          {result.warnings.map((warning, index) => (
            <li key={`${warning}-${index}`}>{warning}</li>
          ))}
        </ul>
      ) : null}
    </section>
  )
}
