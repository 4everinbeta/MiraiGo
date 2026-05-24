'use client'

import { useEffect, useState } from 'react'
import OrchestratorDashboard from '@/components/search/OrchestratorDashboard'
import SearchForm from '@/components/search/SearchForm'
import {
  fetchProviderStatuses,
  orchestratorTurn,
  type OrchestratorTurnResponse,
  type ProviderStatus,
  type SearchRequest,
} from '@/lib/api'

const SESSION_STORAGE_KEY = 'miraigo.orchestrator.session'

function ensureSessionId(): string {
  if (typeof window === 'undefined') {
    return 'server-session'
  }

  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY)
  if (existing) return existing

  const created =
    typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
      ? crypto.randomUUID()
      : `session-${Date.now()}`
  window.localStorage.setItem(SESSION_STORAGE_KEY, created)
  return created
}

function buildTurnMessage(request: SearchRequest): string {
  const parts: string[] = []
  if (request.query?.trim()) {
    parts.push(request.query.trim())
  }
  if (request.clarification_answer?.answer_text?.trim()) {
    parts.push(request.clarification_answer.answer_text.trim())
  }
  if (request.recap_edit?.edited_value?.trim()) {
    parts.push(`Update ${request.recap_edit.slot}: ${request.recap_edit.edited_value.trim()}`)
  }
  if (request.constraint_updates) {
    const updates = Object.entries(request.constraint_updates)
      .filter(([, value]) => value != null)
      .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
    if (updates.length) {
      parts.push(`Constraint updates -> ${updates.join(', ')}`)
    }
  }
  return parts.join('\n').trim() || 'Continue planning with prior context.'
}

export default function Home() {
  const [providerStatuses, setProviderStatuses] = useState<ProviderStatus[]>([])
  const [response, setResponse] = useState<OrchestratorTurnResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')

  useEffect(() => {
    setSessionId(ensureSessionId())
  }, [])

  useEffect(() => {
    let active = true
    const loadProviders = async () => {
      try {
        const providers = await fetchProviderStatuses()
        if (active) setProviderStatuses(providers)
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
    if (!sessionId) return
    setIsSubmitting(true)
    setErrorMessage(null)
    try {
      const turn = await orchestratorTurn({
        session_id: sessionId,
        message: buildTurnMessage(request),
      })
      setResponse(turn)
    } catch {
      setResponse(null)
      setErrorMessage('The orchestrator request failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(43,58,103,0.08),_transparent_35%),linear-gradient(180deg,_#fff_0%,_#fff7f8_100%)] text-foreground">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-14">
        <header className="space-y-6">
          <div className="inline-flex rounded-full border border-primary/15 bg-white/70 px-4 py-1 text-[11px] font-semibold uppercase tracking-[0.32em] text-primary">
            MiraiGo Multi-Agent
          </div>
          <div className="grid gap-6 md:grid-cols-[1.3fr_0.9fr] md:items-end">
            <div className="space-y-4">
              <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-sumi lg:text-6xl">
                Plan trips through a Groq-powered orchestration flow with deterministic pricing adapters.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-muted-foreground">
                Your prompt is sent to the orchestrator each turn, state is persisted by session, and the frontend renders questions, destination ideas, package pricing, and itinerary narratives.
              </p>
            </div>
          </div>
        </header>

        <SearchForm
          clarificationState={null}
          isSubmitting={isSubmitting}
          preservedRequest={null}
          onSearch={handleSearch}
        />

        <OrchestratorDashboard
          errorMessage={errorMessage}
          isLoading={isSubmitting}
          providerStatuses={providerStatuses}
          response={response}
        />
      </div>
    </main>
  )
}
