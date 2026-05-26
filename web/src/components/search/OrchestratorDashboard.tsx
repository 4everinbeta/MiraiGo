'use client'

import { useState } from 'react'
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
  const [expanded, setExpanded] = useState(false)
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

      {!isLoading && response ? (
        <div className="space-y-4">
          <Card className="border-primary/10 bg-white/90">
            <CardHeader className="space-y-2 pb-2 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg text-sumi">
                  Agent Execution Traces & Diagnostics
                </CardTitle>
                <p className="text-xs text-muted-foreground">
                  Executed Agents: {response.executed_agents.join(' → ')} · Type: {response.response_type}
                </p>
              </div>
              <button
                onClick={() => setExpanded(!expanded)}
                type="button"
                className="rounded-lg border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-semibold text-primary hover:bg-primary/10 transition cursor-pointer"
              >
                {expanded ? 'Hide Traces' : 'Show Traces'}
              </button>
            </CardHeader>
            <CardContent
              className="space-y-4 pt-0"
              style={{ display: expanded ? 'block' : 'none' }}
            >
              <div className="rounded-xl border border-border/70 bg-background p-4">
                <p className="whitespace-pre-wrap text-sm leading-6 text-sumi">{response.markdown}</p>
              </div>

              {response.open_questions.length > 0 ? (
                <div>
                  <p className="text-sm font-medium text-sumi">Open questions</p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                    {response.open_questions.map((question) => (
                      <li key={question}>{question}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {response.candidate_destinations.length > 0 ? (
                <div>
                  <p className="text-sm font-medium text-sumi">Destination ideas</p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                    {response.candidate_destinations.map((candidate, index) => (
                      <li key={`${renderDestinationLabel(candidate)}-${index}`}>
                        {renderDestinationLabel(candidate)}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {response.packages.length > 0 ? (
                <div>
                  <p className="text-sm font-medium text-sumi">Packages</p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                    {response.packages.map((pkg, index) => (
                      <li key={`${renderPackageLabel(pkg)}-${index}`}>{renderPackageLabel(pkg)}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {response.disclaimers.length > 0 ? (
                <div>
                  <p className="text-sm font-medium text-sumi">Disclaimers</p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                    {response.disclaimers.map((disclaimer) => (
                      <li key={disclaimer}>{disclaimer}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </CardContent>
          </Card>
        </div>
      ) : null}

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
