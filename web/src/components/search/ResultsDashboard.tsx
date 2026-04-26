'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { ProviderStatus, SearchResponse, SearchResult } from '@/lib/api'

interface ResultsDashboardProps {
  response: SearchResponse | null
  providerStatuses: ProviderStatus[]
  isLoading: boolean
  errorMessage?: string | null
}

function formatMoney(amount: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount)
}

function ResultCard({ result }: { result: SearchResult }) {
  const priceSummary = result.price_known
    ? formatMoney(result.total_price, result.currency)
    : result.price_label || 'Check partner site for pricing'

  return (
    <Card className="border-border/80 bg-white/90 shadow-sm">
      <CardHeader className="gap-3 border-b border-border/70">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1">
            <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-primary">
              {result.provider_label}
            </p>
            <CardTitle className="text-xl text-sumi">{result.title}</CardTitle>
            <p className="text-sm text-muted-foreground">{result.description}</p>
          </div>
          <div className="rounded-full border border-primary/15 bg-primary/5 px-3 py-1 text-sm font-semibold text-primary">
            Score {Math.round(result.score)}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-4 pt-4">
        <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          <span className="rounded-full bg-muted px-3 py-1 text-sumi">{priceSummary}</span>
          {result.inventory_type === 'stay' && result.location_label && (
            <span>{result.location_label}</span>
          )}
          {result.inventory_type === 'flight' && (
            <span>
              {result.origin_code} to {result.destination_code} • {result.stops === 0 ? 'Nonstop' : `${result.stops} stop${result.stops > 1 ? 's' : ''}`}
            </span>
          )}
        </div>
        {result.inventory_type === 'stay' && result.amenities.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {result.amenities.map((amenity) => (
              <span
                key={amenity}
                className="rounded-full border border-border bg-background px-2.5 py-1 text-xs uppercase tracking-wide text-muted-foreground"
              >
                {amenity}
              </span>
            ))}
          </div>
        )}
        {result.redirect_url ? (
          <a
            className="inline-flex w-fit rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition hover:bg-indigo-jp"
            href={result.redirect_url}
            rel="noreferrer"
            target="_blank"
          >
            {result.deep_link_label || 'Open provider link'}
          </a>
        ) : (
          <p className="text-sm text-muted-foreground">
            Direct booking link is not yet wired for this result.
          </p>
        )}
      </CardContent>
    </Card>
  )
}

export default function ResultsDashboard({
  response,
  providerStatuses,
  isLoading,
  errorMessage,
}: ResultsDashboardProps) {
  const stayResults = response?.results.filter((result) => result.inventory_type === 'stay') ?? []
  const flightResults = response?.results.filter((result) => result.inventory_type === 'flight') ?? []
  const providerList = response?.provider_status ?? providerStatuses
  const hasSearched = Boolean(response || errorMessage)
  const flightWarnings = response?.warnings.filter((warning) => warning.toLowerCase().includes('flight')) ?? []
  const generalWarnings = response?.warnings.filter((warning) => !warning.toLowerCase().includes('flight')) ?? []

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

      {!isLoading && response && flightWarnings.length > 0 ? (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-sumi">Flight search notice</CardTitle>
          </CardHeader>
          <CardContent aria-live="polite" className="space-y-2 pt-0 text-sm text-sumi/80">
            {flightWarnings.map((warning) => (
              <p key={warning}>{warning}</p>
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
          <section className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl font-semibold text-sumi">Stay Results</h2>
              <span className="text-sm text-muted-foreground">{stayResults.length} results</span>
            </div>
            {stayResults.length ? (
              <div className="grid gap-4">
                {stayResults.map((result) => (
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
                  <ResultCard key={`${result.provider}-${result.title}-${result.departure_at}`} result={result} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No flight results returned.</p>
            )}
          </section>
        </div>
      ) : null}
    </div>
  )
}
