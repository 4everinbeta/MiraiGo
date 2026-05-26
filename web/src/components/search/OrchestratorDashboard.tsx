'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { OrchestratorTurnResponse, ProviderStatus } from '@/lib/api'

interface OrchestratorDashboardProps {
  response: OrchestratorTurnResponse | null
  providerStatuses: ProviderStatus[]
  isLoading: boolean
  errorMessage?: string | null
}

function renderDestinationLabel(candidate: Record<string, unknown>): string {
  const destination = candidate.destination
  return typeof destination === 'string' ? destination : 'Suggested destination'
}

function renderPackageLabel(pkg: Record<string, unknown>): string {
  const destination = pkg.destination
  const totalPrice = pkg.total_price
  if (typeof destination === 'string' && typeof totalPrice === 'number') {
    return `${destination} — ${totalPrice}`
  }
  return typeof destination === 'string' ? destination : 'Priced package'
}

export default function OrchestratorDashboard({
  response,
  providerStatuses,
  isLoading,
  errorMessage,
}: OrchestratorDashboardProps) {
  const hasSearched = Boolean(response || errorMessage)

  return (
    <div className="space-y-8">
      <Card className="border-primary/10 bg-white/80 shadow-sm">
        <CardHeader className="border-b border-primary/10">
          <CardTitle className="text-lg text-sumi">Provider Availability</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 pt-4 md:grid-cols-3">
          {providerStatuses.map((provider) => (
            <div key={provider.provider} className="rounded-2xl border border-border/70 bg-background p-4">
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
              {provider.reason && <p className="mt-2 text-sm text-muted-foreground">{provider.reason}</p>}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Error messages are now fully unified inside the premium SearchForm Chat Hub */}

      {isLoading ? (
        <Card className="border-primary/10 bg-white/80">
          <CardContent className="space-y-3 pt-4">
            <p className="text-sm font-medium text-primary">Orchestrating your trip…</p>
            <div data-testid="loading-state" className="h-28 animate-pulse rounded-2xl bg-muted/60" />
          </CardContent>
        </Card>
      ) : null}

      {/* Conversational responses are now fully unified inside the premium SearchForm Chat Hub */}

      {!isLoading && !errorMessage && hasSearched && !response ? (
        <Card className="border-border/80 bg-white/80">
          <CardContent className="pt-4 text-sm text-muted-foreground">
            No orchestrator response was returned for this turn.
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
