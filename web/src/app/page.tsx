'use client'

import { useEffect, useState } from 'react'
import OrchestratorDashboard from '@/components/search/OrchestratorDashboard'
import ResultsDashboard from '@/components/search/ResultsDashboard'
import SearchForm from '@/components/search/SearchForm'
import {
  fetchProviderStatuses,
  orchestratorTurn,
  type ClarificationState,
  type OrchestratorTurnResponse,
  type ProviderStatus,
  type SearchRequest,
  type SearchResponse,
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

export interface ChatMessage {
  id: string
  sender: 'user' | 'assistant'
  text: string
  timestamp: Date
  response_type?: string
  candidate_destinations?: Array<Record<string, unknown>>
  packages?: Array<Record<string, unknown>>
  disclaimers?: string[]
  executed_agents?: string[]
}

export default function Home() {
  const [providerStatuses, setProviderStatuses] = useState<ProviderStatus[]>([])
  const [response, setResponse] = useState<OrchestratorTurnResponse | null>(null)
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)
  const [clarificationState, setClarificationState] = useState<ClarificationState | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const [assistantPromptOverride, setAssistantPromptOverride] = useState<string | null>(null)
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello! I am MiraiGo, your travel discovery companion. Describe where, when, and budget if known. We’ll ask one follow-up at a time to fill missing details.',
      timestamp: new Date(),
    },
  ])

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
    setAssistantPromptOverride(null)

    // Formulate a clean textual display of the user's action
    let userMsgText = request.query?.trim()
    if (request.clarification_answer?.answer_text?.trim()) {
      userMsgText = request.clarification_answer.answer_text.trim()
    } else if (request.recap_edit?.edited_value?.trim()) {
      userMsgText = `Update ${request.recap_edit.slot}: ${request.recap_edit.edited_value.trim()}`
    } else if (request.constraint_updates) {
      const updates = Object.entries(request.constraint_updates)
        .filter(([, val]) => val != null)
        .map(([k, v]) => {
          if (typeof v === 'object' && v !== null && 'start' in v) {
            const start = (v as { start: string }).start
            const end = (v as { end?: string }).end
            return `dates: ${start}${end ? ' to ' + end : ''}`
          }
          return `${k}: ${JSON.stringify(v)}`
        })
      if (updates.length) {
        userMsgText = `Constraint updates: ${updates.join(', ')}`
      }
    }

    if (!userMsgText) {
      userMsgText = 'Continuing planning with prior context.'
    }

    setChatHistory((prev) => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        sender: 'user',
        text: userMsgText!,
        timestamp: new Date(),
      },
    ])

    // Attach preserved clarification_state from prior turn for continuity
    const searchPayload: SearchRequest = clarificationState
      ? { ...request, clarification_state: clarificationState }
      : request

    try {
      const turn = await orchestratorTurn({
        session_id: sessionId,
        message: buildTurnMessage(request),
        search_payload: searchPayload,
      })
      setResponse(turn)
      if (turn.search_response) {
        setSearchResponse(turn.search_response)
        // Persist clarification_state for follow-up turns
        if (turn.search_response.clarification_state) {
          setClarificationState(turn.search_response.clarification_state)
        }
      }

      setChatHistory((prev) => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          sender: 'assistant',
          text: turn.markdown,
          timestamp: new Date(),
          response_type: turn.response_type,
          candidate_destinations: turn.candidate_destinations,
          packages: turn.packages,
          disclaimers: turn.disclaimers,
          executed_agents: turn.executed_agents,
        },
      ])
    } catch {
      setResponse(null)
      setSearchResponse(null)
      setErrorMessage('The orchestrator request failed. Please try again.')
      setChatHistory((prev) => [
        ...prev,
        {
          id: `assistant-error-${Date.now()}`,
          sender: 'assistant',
          text: 'The orchestrator request failed. Please try again.',
          timestamp: new Date(),
        },
      ])
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
          assistantPromptOverride={assistantPromptOverride}
          clarificationState={clarificationState}
          isSubmitting={isSubmitting}
          onSearch={handleSearch}
          preservedRequest={
            searchResponse?.applied_filters
              ? {
                  destination: searchResponse.applied_filters.destination || undefined,
                  origin: searchResponse.applied_filters.origin || undefined,
                  date_range: searchResponse.applied_filters.date_range || undefined,
                  trip_length_days: searchResponse.applied_filters.trip_length_days || undefined,
                  budget_range: searchResponse.applied_filters.budget_range || undefined,
                  travelers: searchResponse.applied_filters.travelers,
                  stay_filters: searchResponse.applied_filters.stay_filters,
                  flight_filters: searchResponse.applied_filters.flight_filters,
                }
              : null
          }
          chatHistory={chatHistory}
        />

        <OrchestratorDashboard
          errorMessage={errorMessage}
          isLoading={isSubmitting}
          providerStatuses={providerStatuses}
          response={response}
        />

        {searchResponse && (
          <ResultsDashboard
            response={searchResponse}
            providerStatuses={providerStatuses}
            isLoading={isSubmitting}
            onNoFlightFollowUp={(prompt) => setAssistantPromptOverride(prompt)}
          />
        )}
      </div>
    </main>
  )
}

