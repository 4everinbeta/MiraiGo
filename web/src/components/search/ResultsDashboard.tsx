'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { ProviderStatus, SearchResponse, SearchResult } from '@/lib/api'
import {
  Star,
  MapPin,
  Wifi,
  Wind,
  Tv,
  Coffee,
  Waves,
  Car,
  Dumbbell,
  Flame,
  Utensils,
  Sparkles,
} from 'lucide-react'

interface ResultsDashboardProps {
  response: SearchResponse | null
  providerStatuses: ProviderStatus[]
  isLoading: boolean
  errorMessage?: string | null
  onNoFlightFollowUp?: (prompt: string) => void
}

function formatMoney(amount: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount)
}

function getAmenityIcon(amenity: string) {
  const norm = amenity.toLowerCase()
  if (norm.includes('wifi')) return <Wifi className="h-3 w-3 mr-1" />
  if (norm.includes('ac') || norm.includes('air conditioning') || norm.includes('ventilation')) return <Wind className="h-3 w-3 mr-1" />
  if (norm.includes('tv')) return <Tv className="h-3 w-3 mr-1" />
  if (norm.includes('breakfast')) return <Coffee className="h-3 w-3 mr-1" />
  if (norm.includes('pool') || norm.includes('beach') || norm.includes('seaside')) return <Waves className="h-3 w-3 mr-1" />
  if (norm.includes('parking')) return <Car className="h-3 w-3 mr-1" />
  if (norm.includes('gym') || norm.includes('fitness')) return <Dumbbell className="h-3 w-3 mr-1" />
  if (norm.includes('fireplace')) return <Flame className="h-3 w-3 mr-1" />
  if (norm.includes('dining') || norm.includes('restaurant') || norm.includes('food')) return <Utensils className="h-3 w-3 mr-1" />
  return <Sparkles className="h-3 w-3 mr-1" />
}

function ResultCard({ result }: { result: SearchResult }) {
  const normalizedPrice =
    result.inventory_type === 'flight' &&
    result.price_minor != null &&
    result.currency_code != null
      ? formatMoney(result.price_minor / 100, result.currency_code)
      : null
  const priceSummary = result.price_known
    ? normalizedPrice || formatMoney(result.total_price, result.currency)
    : result.price_label || 'Check partner site for pricing'
  const flightStops =
    result.inventory_type === 'flight' ? (result.stops_count ?? result.stops) : null
  const flightDuration =
    result.inventory_type === 'flight'
      ? result.duration_minutes != null
         ? `${result.duration_minutes} min`
        : result.duration || 'Duration unavailable'
      : null
  const flightSourceProvider =
    result.inventory_type === 'flight'
      ? result.airfare_provenance?.source_provider || result.provider
      : null
  const flightFreshnessSource =
    result.inventory_type === 'flight'
      ? result.airfare_freshness?.freshness_source || 'unavailable'
      : null
  const flightFreshnessAt =
    result.inventory_type === 'flight' ? result.airfare_freshness?.freshness_at ?? null : null
  const missingFlightFields = result.inventory_type === 'flight' ? result.missing_fields ?? [] : []
  const usesLegacyFallback =
    result.inventory_type === 'flight' &&
    (result.price_minor == null ||
      result.currency_code == null ||
      result.duration_minutes == null ||
      result.stops_count == null)

  const isStay = result.inventory_type === 'stay'

  return (
    <Card className="border-border/80 bg-white/90 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-primary/20 hover:shadow-md">
      <CardHeader className="gap-3 border-b border-border/70">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                result.provider === 'booking'
                  ? 'bg-blue-50 text-blue-900 border border-blue-100'
                  : 'bg-orange-50 text-orange-900 border border-orange-100'
              }`}>
                {result.provider_label}
              </span>
              {isStay && (
                <div className="flex items-center text-xs font-semibold text-amber-500">
                  <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400 mr-0.5" />
                  {result.rating ?? '4.8'}
                </div>
              )}
            </div>
            <CardTitle className="text-xl text-sumi font-semibold">{result.title}</CardTitle>
            <p className="text-sm text-muted-foreground max-w-2xl">{result.description}</p>
          </div>
          <div className="rounded-full border border-primary/15 bg-primary/5 px-3 py-1 text-sm font-semibold text-primary">
            Score {Math.round(result.score)}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-4 pt-4">
        <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          {isStay && result.location_label && (
            <div className="flex items-center text-xs font-medium text-muted-foreground">
              <MapPin className="h-4 w-4 text-primary mr-1" />
              <span>{result.location_label}</span>
            </div>
          )}
          {!isStay && (
            <span>
              {result.origin_code} to {result.destination_code} •{' '}
              {flightStops === 0 ? 'Nonstop' : `${flightStops} stop${(flightStops ?? 0) > 1 ? 's' : ''}`} •{' '}
              {flightDuration}
            </span>
          )}
        </div>
        {!isStay && (
          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
            <span className="rounded-full border border-primary/15 bg-primary/5 px-2.5 py-1">
              Source: {flightSourceProvider}
            </span>
            <span className="rounded-full border border-primary/15 bg-primary/5 px-2.5 py-1">
              Freshness: {flightFreshnessSource}
              {flightFreshnessAt ? ` (${flightFreshnessAt})` : ''}
            </span>
            <span className="rounded-full border border-primary/15 bg-primary/5 px-2.5 py-1">
              Conversion: {result.conversion_status ?? 'unavailable'}
            </span>
            {usesLegacyFallback ? (
              <span className="rounded-full border border-primary/15 bg-primary/5 px-2.5 py-1">
                Fallback: using legacy airfare fields
              </span>
            ) : null}
            {missingFlightFields.length > 0 ? (
              <span className="rounded-full border border-border bg-background px-2.5 py-1">
                Missing fields: {missingFlightFields.join(', ')}
              </span>
            ) : null}
          </div>
        )}
        {isStay && result.amenities.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {result.amenities.map((amenity) => (
              <span
                key={amenity}
                className="inline-flex items-center rounded-full border border-border bg-background px-2.5 py-1 text-xs uppercase tracking-wide text-muted-foreground"
              >
                {getAmenityIcon(amenity)}
                {amenity}
              </span>
            ))}
          </div>
        )}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-border/40">
          <div className="flex flex-col">
            <span className="text-xl font-bold text-sumi">{priceSummary}</span>
            {isStay && result.price_known && result.total_price > 0 && (
              <span className="text-xs text-muted-foreground">
                Total for stay: {formatMoney(result.total_price, result.currency)}
              </span>
            )}
          </div>
          {result.redirect_url ? (
            <a
              className="inline-flex w-fit rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition hover:bg-indigo-jp hover:shadow"
              href={result.redirect_url}
              rel="noreferrer"
              target="_blank"
            >
              {result.deep_link_label || 'Open provider link'}
            </a>
          ) : (
            <p className="text-sm text-muted-foreground font-medium">
              Direct booking link is not yet wired for this result.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default function ResultsDashboard({
  response,
  providerStatuses,
  isLoading,
  errorMessage,
  onNoFlightFollowUp,
}: ResultsDashboardProps) {
  const stayResults = response?.results.filter((result) => result.inventory_type === 'stay') ?? []

  const prices = stayResults.map((r) => r.total_price).filter((p) => p > 0)
  const computedMaxPrice = prices.length > 0 ? Math.max(...prices) : 1000

  const [sortBy, setSortBy] = useState<'score' | 'price' | 'rating'>('score')
  const [maxPrice, setMaxPrice] = useState<number>(computedMaxPrice)
  const [selectedAmenities, setSelectedAmenities] = useState<string[]>([])
  const [ratingThreshold, setRatingThreshold] = useState<number>(0)

  const [prevResponse, setPrevResponse] = useState(response)
  if (response !== prevResponse) {
    setPrevResponse(response)
    setMaxPrice(computedMaxPrice)
  }

  const filteredStays = stayResults
    .filter((stay) => {
      if (stay.price_known && stay.total_price > 0 && stay.total_price > maxPrice) {
        return false
      }
      if (selectedAmenities.length > 0) {
        const stayAmenities = stay.amenities.map((a) => a.toLowerCase())
        const matchesAll = selectedAmenities.every((a) => stayAmenities.includes(a.toLowerCase()))
        if (!matchesAll) return false
      }
      if (ratingThreshold > 0) {
        const ratingNum = parseFloat(stay.rating || '4.8')
        if (ratingNum < ratingThreshold) return false
      }
      return true
    })
    .sort((a, b) => {
      if (sortBy === 'price') {
        const aPrice = a.price_known && a.total_price > 0 ? a.total_price : Infinity
        const bPrice = b.price_known && b.total_price > 0 ? b.total_price : Infinity
        return aPrice - bPrice
      }
      if (sortBy === 'rating') {
        const aRating = parseFloat(a.rating || '4.8')
        const bRating = parseFloat(b.rating || '4.8')
        return bRating - aRating
      }
      return b.score - a.score
    })
  const flightResults =
    response?.results
      .filter((result) => result.inventory_type === 'flight')
      .sort((a, b) => {
        const aKey = a.normalized_offer_id ?? `${a.provider}-${a.title}-${a.departure_at}`
        const bKey = b.normalized_offer_id ?? `${b.provider}-${b.title}-${b.departure_at}`
        return aKey.localeCompare(bKey)
      }) ?? []
  const providerList = response?.provider_status ?? providerStatuses
  const recommendationPackages = response?.recommendation_packages ?? []
  const hasSearched = Boolean(response || errorMessage)
  const clarificationState = response?.clarification_state ?? null
  const degradedState = response?.degraded_state ?? null
  const hasExplicitDegradedState = Boolean(
    degradedState?.active && (degradedState.degraded_providers?.length ?? 0) > 0
  )
  const degradedProviders = degradedState?.degraded_providers ?? []
  const pendingFlightRequirements = clarificationState?.flight_requirements_pending ?? []
  const continueBlockReason = clarificationState?.continue_block_reason?.trim() || null
  const structuredNoFlightGuidance = response?.no_flight_guidance ?? null
  const hasStructuredFlightRemediation =
    pendingFlightRequirements.length > 0 || Boolean(continueBlockReason)
  const flightWarnings = response?.warnings.filter((warning) => warning.toLowerCase().includes('flight')) ?? []
  const generalWarnings = response?.warnings.filter((warning) => !warning.toLowerCase().includes('flight')) ?? []
  const lowerFlightWarnings = flightWarnings.map((warning) => warning.toLowerCase())
  const hasInventoryEmptyWarning = lowerFlightWarnings.some((warning) =>
    warning.includes('returned no flight offers')
  )
  const hasProviderDegradedWarning = lowerFlightWarnings.some((warning) =>
    warning.includes('flight search unavailable')
  )
  const hasUnavailableFlightProvider = providerList.some(
    (provider) =>
      provider.inventory_types.includes('flight') &&
      (!provider.configured || !provider.healthy)
  )
  const noFlightGuidance = structuredNoFlightGuidance
    ? {
        explanation: structuredNoFlightGuidance.explanation,
        steps: structuredNoFlightGuidance.actions,
        fallbackAttempts: structuredNoFlightGuidance.fallback_attempts ?? [],
        followUpPrompt: structuredNoFlightGuidance.follow_up_prompt ?? null,
      }
    : hasStructuredFlightRemediation
    ? {
        explanation:
          'Flight prerequisites are still missing, so live airfare provenance details are not available yet.',
        steps: [
          'Add the missing flight prerequisites listed above.',
          'Continue once those details are filled to fetch flight offers.',
        ],
        fallbackAttempts: [],
        followUpPrompt: null,
      }
    : hasExplicitDegradedState
      ? {
          explanation:
            'One or more flight providers are currently degraded, so only available provider data can be shown.',
          steps: [
            'Review degraded provider details in the reliability notice.',
            'Retry shortly to refresh missing provider results.',
          ],
          fallbackAttempts: [],
          followUpPrompt: null,
        }
    : hasInventoryEmptyWarning
    ? {
        explanation:
          'Providers returned no flight offers for this route and date range, so airfare provenance details are unavailable.',
          steps: [
            'Try nearby airports or wider date ranges.',
            'Relax nonstop, time, or budget filters.',
          ],
          fallbackAttempts: [],
          followUpPrompt: null,
        }
      : hasProviderDegradedWarning || hasUnavailableFlightProvider
        ? {
            explanation:
              'Live flight search is temporarily unavailable, so airfare provenance details cannot be shown right now.',
            steps: [
              'Retry this search in a few minutes.',
              'Continue with stays now and rerun flights later.',
            ],
            fallbackAttempts: [],
            followUpPrompt: null,
          }
        : {
            explanation:
              'No live results matched the current request, so airfare provenance details are not available for this search yet.',
            steps: ['Try broadening dates, budget, or provider credentials.'],
            fallbackAttempts: [],
            followUpPrompt: null,
          }
  const flightNoticeMessages = [
    ...(continueBlockReason ? [continueBlockReason] : []),
    ...(pendingFlightRequirements.length > 0
      ? [`Missing prerequisites: ${pendingFlightRequirements.join(', ')}`]
      : []),
    ...(hasExplicitDegradedState
      ? degradedProviders.map(
          (provider) => `${provider.label} degraded (${provider.reason})`
        )
      : []),
    ...flightWarnings,
  ]

  return (
    <div className="space-y-8">
      <Card className="border-primary/10 bg-white/80 shadow-sm">
        <CardHeader className="border-b border-primary/10">
          <CardTitle className="text-lg text-sumi">Provider Availability</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 pt-4 md:grid-cols-3">
          {providerList.map((provider) => (
            <div
              key={provider.provider}
              className="rounded-2xl border border-border/70 bg-background p-4"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="font-medium text-sumi">{provider.label}</p>
                <span
                  className={`rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${
                    provider.configured && provider.healthy
                      ? 'bg-emerald-100 text-emerald-700'
                      : 'bg-amber-100 text-amber-700'
                  }`}
                >
                  {provider.configured && provider.healthy ? 'Live' : 'Unavailable'}
                </span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                Supports {provider.inventory_types.join(', ')}
              </p>
              {provider.reason && (
                <p className="mt-2 text-sm text-muted-foreground">{provider.reason}</p>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {generalWarnings.length ? (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent aria-live="polite" className="space-y-2 pt-4 text-sm text-amber-900">
            {generalWarnings.map((warning) => (
              <p key={warning}>{warning}</p>
            ))}
          </CardContent>
        </Card>
      ) : null}

      {!isLoading && response && flightNoticeMessages.length > 0 ? (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-sumi">Flight search notice</CardTitle>
          </CardHeader>
          <CardContent aria-live="polite" className="space-y-2 pt-0 text-sm text-sumi/80">
            {flightNoticeMessages.map((message) => (
              <p key={message}>{message}</p>
            ))}
          </CardContent>
        </Card>
      ) : null}

      {!isLoading && response && hasExplicitDegradedState ? (
        <Card className="border-amber-200 bg-amber-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-amber-900">Flight reliability degraded</CardTitle>
          </CardHeader>
          <CardContent aria-live="polite" className="space-y-2 pt-0 text-sm text-amber-900">
            {degradedProviders.map((provider) => (
              <p key={`${provider.provider}-${provider.reason}`}>
                {provider.label}: {provider.reason}
              </p>
            ))}
          </CardContent>
        </Card>
      ) : null}

      {errorMessage ? (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardContent className="pt-4 text-sm text-destructive">{errorMessage}</CardContent>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="border-primary/10 bg-white/80">
          <CardContent className="space-y-3 pt-4">
            <p className="text-sm font-medium text-primary">Searching live inventory…</p>
            <div data-testid="loading-state" className="h-28 animate-pulse rounded-2xl bg-muted/60" />
          </CardContent>
        </Card>
      ) : null}

      {!isLoading && !errorMessage && hasSearched && response && response.results.length === 0 ? (
        <Card className="border-border/80 bg-white/80">
          <CardContent className="pt-4 text-sm text-muted-foreground">
            No live results matched the current request. Try broadening dates, budget, or provider credentials.
          </CardContent>
        </Card>
      ) : null}

      {!isLoading && response ? (
        <div className="grid gap-8">
          {recommendationPackages.length ? (
            <section className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold text-sumi">Top Suggestions</h2>
                <span className="text-sm text-muted-foreground">{recommendationPackages.length} options</span>
              </div>
              <div className="grid gap-4">
                {recommendationPackages.map((suggestion) => (
                  <Card key={suggestion.bundle_id} className="border-primary/15 bg-primary/5">
                    <CardHeader className="gap-2 pb-2">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <CardTitle className="text-lg text-sumi">{suggestion.destination}</CardTitle>
                        <span className="rounded-full border border-primary/20 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-wide text-primary">
                          {suggestion.fallback_level === 'high-fit'
                            ? 'High fit'
                            : suggestion.fallback_level === 'partial-fit'
                              ? 'Partial fit'
                              : 'Fallback option'}
                        </span>
                      </div>
                      {suggestion.rationale_text && (
                        <p className="text-sm text-muted-foreground">{suggestion.rationale_text}</p>
                      )}
                    </CardHeader>
                    <CardContent className="space-y-3 pt-0">
                      {suggestion.reason_tags?.length ? (
                        <div className="flex flex-wrap gap-2">
                          {suggestion.reason_tags.map((tag) => (
                            <span
                              key={`${suggestion.bundle_id}-${tag}`}
                              className="rounded-full border border-border bg-background px-2.5 py-1 text-xs uppercase tracking-wide text-muted-foreground"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      ) : null}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          ) : null}
          <section className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl font-semibold text-sumi">Stay Results</h2>
              <span className="text-sm text-muted-foreground">
                {filteredStays.length} of {stayResults.length} results
              </span>
            </div>

            {stayResults.length > 0 && (
              <div className="rounded-xl border border-primary/10 bg-white/70 p-4 shadow-sm backdrop-blur flex flex-col md:flex-row md:items-center justify-between gap-6 animate-in fade-in slide-in-from-top-2 duration-300">
                <div className="flex flex-wrap items-center gap-6">
                  {/* Max Price Slider */}
                  <div className="flex flex-col gap-1.5 w-full md:w-56">
                    <label htmlFor="price-slider" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Max Price: {formatMoney(maxPrice, 'USD')}
                    </label>
                    <input
                      id="price-slider"
                      data-testid="stays-price-slider"
                      type="range"
                      min="0"
                      max={computedMaxPrice}
                      value={maxPrice}
                      onChange={(e) => setMaxPrice(Number(e.target.value))}
                      className="h-1.5 w-full accent-primary bg-muted rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  {/* Rating Filter Buttons */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Min Rating</span>
                    <div className="flex items-center gap-1.5">
                      {[0, 3, 4].map((threshold) => (
                        <button
                          key={threshold}
                          type="button"
                          className={`rounded-full px-3 py-1 text-xs font-semibold border transition duration-200 ${
                            ratingThreshold === threshold
                              ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                              : 'bg-background hover:bg-muted text-muted-foreground border-border'
                          }`}
                          onClick={() => setRatingThreshold(threshold)}
                        >
                          {threshold === 0 ? 'All' : `${threshold}.0+ Stars`}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Amenities filter checkboxes */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Amenities</span>
                    <div className="flex items-center gap-3">
                      {['wifi', 'pool', 'gym'].map((amenity) => {
                        const isSelected = selectedAmenities.includes(amenity)
                        return (
                          <label key={amenity} className="flex items-center gap-1.5 text-xs font-medium cursor-pointer text-muted-foreground select-none">
                            <input
                              type="checkbox"
                              data-testid={`amenity-${amenity}-checkbox`}
                              checked={isSelected}
                              onChange={() => {
                                setSelectedAmenities((prev) =>
                                  prev.includes(amenity)
                                    ? prev.filter((a) => a !== amenity)
                                    : [...prev, amenity]
                                )
                              }}
                              className="rounded border-border text-primary focus:ring-primary h-3.5 w-3.5 cursor-pointer"
                            />
                            <span className="capitalize">{amenity}</span>
                          </label>
                        )
                      })}
                    </div>
                  </div>
                </div>

                {/* Sorting Select */}
                <div className="flex flex-col gap-1.5 w-full md:w-auto">
                  <label htmlFor="sort-select" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Sort By
                  </label>
                  <select
                    id="sort-select"
                    data-testid="stays-sort-select"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'score' | 'price' | 'rating')}
                    className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm font-medium text-sumi focus:border-primary focus:outline-none cursor-pointer"
                  >
                    <option value="score">Recommendation Score</option>
                    <option value="price">Price: Low to High</option>
                    <option value="rating">Rating: High to Low</option>
                  </select>
                </div>
              </div>
            )}

            {filteredStays.length ? (
              <div className="grid gap-4">
                {filteredStays.map((result) => (
                  <ResultCard key={`${result.provider}-${result.title}`} result={result} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No stay results returned.</p>
            )}
          </section>

          <section className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl font-semibold text-sumi">Flight Results</h2>
              <span className="text-sm text-muted-foreground">{flightResults.length} results</span>
            </div>
            {flightResults.length ? (
              <div className="grid gap-4">
                {flightResults.map((result) => (
                  <ResultCard
                    key={result.normalized_offer_id ?? `${result.provider}-${result.title}-${result.departure_at}`}
                    result={result}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-2 text-sm text-muted-foreground">
                <p>{noFlightGuidance.explanation}</p>
                {noFlightGuidance.fallbackAttempts.length > 0 ? (
                  <p className="text-xs text-muted-foreground">
                    Fallbacks attempted: {noFlightGuidance.fallbackAttempts.join(', ')}
                  </p>
                ) : null}
                <ul className="list-disc space-y-1 pl-5">
                  {noFlightGuidance.steps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ul>
                {onNoFlightFollowUp && noFlightGuidance.followUpPrompt ? (
                  <button
                    type="button"
                    className="rounded-full border border-primary/20 bg-primary/5 px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary/10"
                    onClick={() => onNoFlightFollowUp(noFlightGuidance.followUpPrompt!)}
                  >
                    Continue in assistant chat
                  </button>
                ) : null}
              </div>
            )}
          </section>
        </div>
      ) : null}
    </div>
  )
}
