'use client'

import { useEffect, useState } from 'react'
import ItineraryPricingResult from '@/components/itinerary/ItineraryPricingResult'
import ItineraryProposalList from '@/components/itinerary/ItineraryProposalList'
import SearchForm from '@/components/search/SearchForm'
import ResultsDashboard from '@/components/search/ResultsDashboard'
import {
  type ClarificationState,
  fetchProviderStatuses,
  priceItinerary,
  proposeItinerary,
  searchTrips,
  type ItineraryPriceResponse,
  type ItineraryProposal,
  type ProviderStatus,
  type SearchRequest,
  type SearchResponse,
} from '@/lib/api'

interface TurnSessionState {
  query?: string
  inventory: SearchRequest['inventory']
  destination?: string
  origin?: string
  date_range?: SearchRequest['date_range']
  trip_length_days?: SearchRequest['trip_length_days']
  budget_range?: SearchRequest['budget_range']
  weather_preference?: SearchRequest['weather_preference']
  travelers: SearchRequest['travelers']
  stay_filters: SearchRequest['stay_filters']
  flight_filters: SearchRequest['flight_filters']
  currency_code: string
  limit_per_provider: number
}

function slotValueOrUndefined(value: string | null | undefined): string | undefined {
  if (!value) return undefined
  const normalized = value.trim().toLowerCase()
  if (normalized === 'missing' || normalized === "i don't know") {
    return undefined
  }
  return value
}

const DEFAULT_TURN_BASE: Omit<TurnSessionState, 'query' | 'destination' | 'origin' | 'date_range'> = {
  inventory: ['stay', 'flight'],
  travelers: { adults: 2, children: 0, infants: 0 },
  stay_filters: { amenities: ['wifi'] },
  flight_filters: { nonstop: false },
  currency_code: 'USD',
  limit_per_provider: 5,
}

function resolveTurnRequest(
  incoming: SearchRequest,
  previous: TurnSessionState | null
): SearchRequest {
  const base = previous ?? DEFAULT_TURN_BASE

  return {
    query: incoming.query ?? previous?.query,
    inventory: incoming.inventory.length ? incoming.inventory : base.inventory,
    destination: incoming.destination ?? previous?.destination,
    origin: incoming.origin ?? previous?.origin,
    date_range: incoming.date_range ?? previous?.date_range,
    trip_length_days: incoming.trip_length_days ?? previous?.trip_length_days,
    budget_range: incoming.budget_range ?? previous?.budget_range,
    weather_preference: incoming.weather_preference ?? previous?.weather_preference,
    travelers: incoming.travelers ?? base.travelers,
    stay_filters: {
      max_price: incoming.stay_filters.max_price ?? base.stay_filters.max_price,
      amenities: incoming.stay_filters.amenities ?? base.stay_filters.amenities,
    },
    flight_filters: {
      max_price: incoming.flight_filters.max_price ?? base.flight_filters.max_price,
      nonstop: incoming.flight_filters.nonstop ?? base.flight_filters.nonstop,
    },
    currency_code: incoming.currency_code ?? base.currency_code,
    limit_per_provider: incoming.limit_per_provider ?? base.limit_per_provider,
    clarification_answer: incoming.clarification_answer,
    recap_edit: incoming.recap_edit,
    constraint_updates: incoming.constraint_updates,
  }
}

const ITINERARY_KEYWORDS = ['itinerary', 'trip options', 'best travel options', 'budget for']

function isItineraryIntent(query?: string): boolean {
  if (!query) return false
  const normalized = query.toLowerCase()
  return ITINERARY_KEYWORDS.some((keyword) => normalized.includes(keyword))
}

export default function Home() {
  const [providerStatuses, setProviderStatuses] = useState<ProviderStatus[]>([])
  const [response, setResponse] = useState<SearchResponse | null>(null)
  const [proposals, setProposals] = useState<ItineraryProposal[]>([])
  const [selectedProposal, setSelectedProposal] = useState<ItineraryProposal | null>(null)
  const [pricingResult, setPricingResult] = useState<ItineraryPriceResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isProposalLoading, setIsProposalLoading] = useState(false)
  const [isPricingLoading, setIsPricingLoading] = useState(false)
  const [clarificationState, setClarificationState] = useState<ClarificationState | null>(null)
  const [turnSession, setTurnSession] = useState<TurnSessionState | null>(null)

  useEffect(() => {
    let active = true

    const loadProviders = async () => {
      try {
        const providers = await fetchProviderStatuses()
        if (active) {
          setProviderStatuses(providers)
        }
      } catch {
        if (active) {
          setErrorMessage('Unable to load provider availability right now.')
        }
      }
    }

    void loadProviders()

    return () => {
      active = false
    }
  }, [])

  const handleSearch = async (request: SearchRequest) => {
    if (isItineraryIntent(request.query)) {
      setErrorMessage(null)
      setResponse(null)
      setPricingResult(null)
      setSelectedProposal(null)
      setIsProposalLoading(true)
      try {
        const proposed = await proposeItinerary({ query: request.query ?? '' })
        setProposals(proposed.proposals)
      } catch {
        setProposals([])
        setErrorMessage('Unable to generate itinerary options right now.')
      } finally {
        setIsProposalLoading(false)
      }
      return
    }

    const turnRequest = resolveTurnRequest(request, turnSession)
    setIsSubmitting(true)
    setErrorMessage(null)
    setProposals([])
    setSelectedProposal(null)
    setPricingResult(null)
    try {
      const nextResponse = await searchTrips(turnRequest)
      setResponse(nextResponse)
      setProviderStatuses(nextResponse.provider_status)
      setClarificationState(nextResponse.clarification_state ?? null)
      const clarificationDestination = slotValueOrUndefined(
        nextResponse.clarification_state?.destination?.value_label
      )
      setTurnSession({
        query: turnRequest.query,
        inventory: turnRequest.inventory,
        destination:
          nextResponse.applied_filters.destination ??
          turnRequest.destination ??
          clarificationDestination ??
          turnSession?.destination ??
          undefined,
        origin: nextResponse.applied_filters.origin ?? turnRequest.origin ?? turnSession?.origin ?? undefined,
        date_range:
          nextResponse.applied_filters.date_range ??
          turnRequest.date_range ??
          turnSession?.date_range ??
          undefined,
        trip_length_days:
          nextResponse.applied_filters.trip_length_days ??
          turnRequest.trip_length_days ??
          turnSession?.trip_length_days ??
          undefined,
        budget_range:
          nextResponse.applied_filters.budget_range ??
          turnRequest.budget_range ??
          turnSession?.budget_range ??
          undefined,
        weather_preference:
          nextResponse.applied_filters.weather_preference ??
          turnRequest.weather_preference ??
          turnSession?.weather_preference ??
          undefined,
        travelers: turnRequest.travelers,
        stay_filters: turnRequest.stay_filters,
        flight_filters: turnRequest.flight_filters,
        currency_code: turnRequest.currency_code,
        limit_per_provider: turnRequest.limit_per_provider,
      })
    } catch {
      setResponse(null)
      setErrorMessage('The search request failed. Check provider credentials or try a broader query.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSelectProposal = async (proposal: ItineraryProposal) => {
    setSelectedProposal(proposal)
    setPricingResult(null)
    setErrorMessage(null)
    setIsPricingLoading(true)
    try {
      const result = await priceItinerary({
        proposal_id: proposal.proposal_id,
        proposal_snapshot: proposal,
        travelers: turnSession?.travelers ?? { adults: 2, children: 1, infants: 0 },
        currency_code: 'USD',
      })
      setPricingResult(result)
      setProviderStatuses(result.provider_status)
    } catch {
      setErrorMessage('Live itinerary pricing failed. Please try selecting again.')
    } finally {
      setIsPricingLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(43,58,103,0.08),_transparent_35%),linear-gradient(180deg,_#fff_0%,_#fff7f8_100%)] text-foreground">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-14">
        <header className="space-y-6">
          <div className="inline-flex rounded-full border border-primary/15 bg-white/70 px-4 py-1 text-[11px] font-semibold uppercase tracking-[0.32em] text-primary">
            MiraiGo MVP
          </div>
          <div className="grid gap-6 md:grid-cols-[1.3fr_0.9fr] md:items-end">
            <div className="space-y-4">
              <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-sumi lg:text-6xl">
                Search live flights with Duffel and hand hotel discovery off with clean partner redirects.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-muted-foreground">
                This production MVP is designed to run locally in Docker Compose first, expose provider availability clearly, and stay portable for Railway or Azure deployment.
              </p>
            </div>
            <div className="rounded-3xl border border-primary/10 bg-white/75 p-5 shadow-sm backdrop-blur">
              <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-primary">
                What this version does
              </p>
              <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
                <li>Self-serve Duffel flight search with explicit provider status</li>
                <li>Canonical stay and flight result models</li>
                <li>Redirect-first hotel handoff, no payments or booking state</li>
              </ul>
            </div>
          </div>
        </header>

        <SearchForm
          clarificationState={clarificationState}
          isSubmitting={isSubmitting || isProposalLoading || isPricingLoading}
          preservedRequest={turnSession}
          onSearch={handleSearch}
        />

        {selectedProposal && pricingResult ? (
          <ItineraryPricingResult
            result={pricingResult}
            proposal={selectedProposal}
            onBack={() => {
              setPricingResult(null)
              setSelectedProposal(null)
            }}
          />
        ) : proposals.length > 0 || isProposalLoading ? (
          <ItineraryProposalList
            proposals={proposals}
            isLoading={isProposalLoading}
            onSelect={(proposal) => {
              void handleSelectProposal(proposal)
            }}
          />
        ) : (
          <ResultsDashboard
            errorMessage={errorMessage}
            isLoading={isSubmitting || isProposalLoading || isPricingLoading}
            providerStatuses={providerStatuses}
            response={response}
          />
        )}
      </div>
    </main>
  )
}
