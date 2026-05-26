'use client'

import { useMemo, useState, useRef, useEffect } from 'react'
import { PencilLine } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import type { ChatMessage } from '@/app/page'
import type {
  ClarificationRecapChip,
  ClarificationSlot,
  ClarificationState,
  DestinationSuggestion,
  InventoryType,
  SearchDateRange,
  SearchRequest,
} from '@/lib/api'

interface SearchFormProps {
  onSearch: (params: SearchRequest) => void
  isSubmitting?: boolean
  clarificationState?: ClarificationState | null
  preservedRequest?: Partial<SearchRequest> | null
  assistantPromptOverride?: string | null
  chatHistory?: ChatMessage[]
}

const DEFAULT_AMENITIES = ['wifi']
const EMPTY_COPY_HEADING = 'Start with your travel intent'
const EMPTY_COPY_BODY =
  'Describe where, when, and budget if known. We’ll ask one follow-up at a time to fill missing details.'
const FLIGHT_REQUIREMENT_GUIDANCE: Record<string, string> = {
  origin: 'Add your departure origin to unlock airfare recommendations.',
  date_range: 'Add a travel date range (start and optional end date) to unlock airfare recommendations.',
  destination: 'Confirm your destination to unlock airfare recommendations.',
}

function buildBaseRequest(query: string): Omit<
  SearchRequest,
  'clarification_answer' | 'recap_edit' | 'constraint_updates'
> {
  const inventory: InventoryType[] = ['stay', 'flight']
  return {
    query: query.trim() || undefined,
    inventory,
    travelers: {
      adults: 2,
      children: 0,
      infants: 0,
    },
    stay_filters: {
      amenities: DEFAULT_AMENITIES,
    },
    flight_filters: {
      nonstop: false,
    },
    currency_code: 'USD',
    limit_per_provider: 5,
  }
}

function slotToInputLabel(chip: ClarificationRecapChip) {
  return `Update ${chip.label}`
}

function formatEditableDefault(chip: ClarificationRecapChip) {
  const normalized = chip.value_label.toLowerCase()
  if (normalized === 'missing' || normalized === "i don't know") {
    return ''
  }
  return chip.value_label
}

const EMPTY_SUGGESTIONS: DestinationSuggestion[] = []
const EMPTY_CHIPS: ClarificationRecapChip[] = []

export default function SearchForm({
  onSearch,
  isSubmitting = false,
  clarificationState = null,
  preservedRequest = null,
  assistantPromptOverride = null,
  chatHistory = [],
}: SearchFormProps) {
  const [query, setQuery] = useState('')
  const [editingSlot, setEditingSlot] = useState<ClarificationSlot | null>(null)
  const [editedValue, setEditedValue] = useState('')
  const [selectedSuggestionIds, setSelectedSuggestionIds] = useState<string[]>([])
  const activeQuestion = clarificationState?.next_question ?? null
  const destinationSuggestions = clarificationState?.destination_suggestions ?? EMPTY_SUGGESTIONS
  const recapChips = clarificationState?.recap.chips ?? EMPTY_CHIPS
  const canSubmit = Boolean(query.trim())
  const complete = Boolean(clarificationState?.all_critical_slots_resolved)
  const pendingFlightRequirements = clarificationState?.flight_requirements_pending ?? []
  const continueBlocked = complete && pendingFlightRequirements.length > 0
  const continueBlockReason =
    clarificationState?.continue_block_reason ??
    (continueBlocked
      ? `Continue needs ${pendingFlightRequirements.join(', ')} before flight recommendations can load.`
      : null)
  const remediationRequirement = continueBlocked ? pendingFlightRequirements[0] ?? null : null
  const remediationQuestion =
    remediationRequirement === 'origin'
      ? {
          slot: 'origin' as const,
          prompt: 'What airport or city are you flying from?',
          helper: 'Reply with city or airport code, for example Denver or DEN.',
        }
      : remediationRequirement === 'date_range'
      ? {
          slot: 'date_range' as const,
          prompt: 'What travel dates should I use?',
          helper: 'Reply YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD.',
        }
      : null
  const isDestinationQuestion = activeQuestion?.slot === 'destination'
  const pendingRequirementGuidance = pendingFlightRequirements.map(
    (requirement) =>
      FLIGHT_REQUIREMENT_GUIDANCE[requirement] ??
      `Provide ${requirement.replace('_', ' ')} to unlock airfare recommendations.`
  )
  const assistantFollowUpPrompt =
    activeQuestion?.prompt ??
    remediationQuestion?.prompt ??
    assistantPromptOverride ??
    (continueBlocked ? 'Let’s unlock airfare results.' : null)
  const assistantFollowUpHelper = activeQuestion?.helper_text ?? remediationQuestion?.helper ?? null
  const showAssistantFollowUp = Boolean(activeQuestion || continueBlocked || assistantPromptOverride)

  const activeChip = useMemo(
    () => recapChips.find((chip) => chip.slot === editingSlot) ?? null,
    [editingSlot, recapChips]
  )

  const chatEndRef = useRef<HTMLDivElement>(null)

  const messages = useMemo(() => {
    if (chatHistory && chatHistory.length > 0) {
      return chatHistory
    }
    const list: ChatMessage[] = [
      {
        id: 'welcome',
        sender: 'assistant' as const,
        text: 'Hello! I am MiraiGo, your travel discovery companion. Describe where, when, and budget if known. We’ll ask one follow-up at a time to fill missing details.',
        timestamp: new Date(),
      },
    ]
    if (showAssistantFollowUp && assistantFollowUpPrompt) {
      list.push({
        id: 'fallback-question',
        sender: 'assistant' as const,
        text: assistantFollowUpPrompt,
        timestamp: new Date(),
      })
    }
    return list
  }, [chatHistory, showAssistantFollowUp, assistantFollowUpPrompt])

  useEffect(() => {
    if (typeof chatEndRef.current?.scrollIntoView === 'function') {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages.length])

  const selectedSuggestions = useMemo(() => {
    if (!destinationSuggestions.length || !selectedSuggestionIds.length) return []
    const selected = new Set(selectedSuggestionIds)
    return destinationSuggestions.filter((item) => selected.has(item.id))
  }, [destinationSuggestions, selectedSuggestionIds])

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    if (!canSubmit || isSubmitting) return

    const trimmedInput = query.trim()
    if (activeQuestion) {
      onSearch({
        ...buildTurnPayload(),
        clarification_answer: {
          slot: activeQuestion.slot,
          answer_text: trimmedInput,
          explicit_unknown: false,
        },
      })
      setQuery('')
      return
    }

    if (continueBlocked && remediationQuestion?.slot === 'origin') {
      onSearch({
        ...buildTurnPayload(),
        constraint_updates: {
          origin: trimmedInput,
        },
      })
      setQuery('')
      return
    }

    if (continueBlocked && remediationQuestion?.slot === 'date_range') {
      const parsed = parseDateRangeAnswer(trimmedInput)
      if (!parsed) return
      onSearch({
        ...buildTurnPayload(),
        constraint_updates: {
          date_range: parsed,
        },
      })
      setQuery('')
      return
    }

    if (assistantPromptOverride) {
      onSearch({
        ...buildTurnPayload(),
        query: trimmedInput,
      })
      setQuery('')
      return
    }

    // Default: initial travel prompt submission
    onSearch(buildBaseRequest(trimmedInput))
    setQuery('')
  }

  const buildTurnPayload = (): SearchRequest => ({
    ...buildBaseRequest(query),
    ...preservedRequest,
    query: query.trim() || preservedRequest?.query || undefined,
    clarification_state: clarificationState ?? preservedRequest?.clarification_state ?? undefined,
  })

  const parseDateRangeAnswer = (answer: string): SearchDateRange | null => {
    const normalized = answer.trim()
    const spanMatch = normalized.match(
      /^(\d{4}-\d{2}-\d{2})\s*(?:to|through|-)\s*(\d{4}-\d{2}-\d{2})$/i
    )
    if (spanMatch) {
      return { start: spanMatch[1], end: spanMatch[2] }
    }
    const singleMatch = normalized.match(/^(\d{4}-\d{2}-\d{2})$/)
    if (singleMatch) {
      return { start: singleMatch[1] }
    }
    return null
  }

  const markAnswerUnknown = () => {
    if (!activeQuestion || isSubmitting) return
    onSearch({
      ...buildTurnPayload(),
      clarification_answer: {
        slot: activeQuestion.slot,
        explicit_unknown: true,
      },
    })
    setQuery('')
  }

  const toggleSuggestion = (suggestion: DestinationSuggestion) => {
    setSelectedSuggestionIds((prev) => {
      if (prev.includes(suggestion.id)) {
        return prev.filter((item) => item !== suggestion.id)
      }
      return [...prev, suggestion.id]
    })
  }

  const submitSelectedSuggestions = () => {
    if (!selectedSuggestions.length || isSubmitting) return
    const destinationCandidates = selectedSuggestions.map((item) => item.label)
    onSearch({
      ...buildTurnPayload(),
      constraint_updates: {
        destination: destinationCandidates.length === 1 ? destinationCandidates[0] : undefined,
        destination_candidates: destinationCandidates,
        destination_selection_mode:
          destinationCandidates.length > 1 ? 'compare' : 'single',
        explicit_unknown_slots: [],
      },
    })
    setQuery('')
  }

  const startEditingChip = (chip: ClarificationRecapChip) => {
    setEditingSlot(chip.slot)
    setEditedValue(formatEditableDefault(chip))
  }

  const saveChipEdit = (event: React.FormEvent) => {
    event.preventDefault()
    if (!activeChip || !editedValue.trim() || isSubmitting) return

    onSearch({
      ...buildTurnPayload(),
      recap_edit: {
        slot: activeChip.slot,
        edited_value: editedValue.trim(),
        explicit_unknown: false,
      },
    })

    setEditingSlot(null)
    setEditedValue('')
  }

  const markChipUnknown = () => {
    if (!activeChip || isSubmitting) return

    onSearch({
      ...buildTurnPayload(),
      recap_edit: {
        slot: activeChip.slot,
        explicit_unknown: true,
      },
    })

    setEditingSlot(null)
    setEditedValue('')
  }

  const continueToRecommendations = () => {
    if (!complete || continueBlocked || isSubmitting) return
    onSearch(buildTurnPayload())
  }

  const promptLabel = showAssistantFollowUp ? 'Your answer' : 'Travel prompt'
  const promptPlaceholder = assistantFollowUpHelper || 'I want a warm beach trip in June with a moderate budget.'
  const promptAriaLabel = showAssistantFollowUp ? 'Your answer' : 'Travel prompt'
  const buttonLabel = isSubmitting
    ? 'Submitting…'
    : showAssistantFollowUp
    ? 'Submit answer'
    : 'Submit travel intent'

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1.3fr_0.7fr] gap-6 items-start">
      {/* Main Column: Chat Interface */}
      <Card className="border-primary/10 bg-white/95 shadow-2xl shadow-primary/5 backdrop-blur-md rounded-3xl overflow-hidden flex flex-col h-[750px]">
        {/* Chat Header */}
        <CardHeader className="space-y-2 border-b border-primary/10 bg-gradient-to-r from-sakura/20 via-sakura/5 to-white py-4 px-6 shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-full bg-gradient-to-tr from-primary to-indigo-jp flex items-center justify-center text-white font-bold shadow-lg shadow-primary/20">
                MG
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary/70">
                  MiraiGo Discovery Hub
                </p>
                <CardTitle className="text-xl font-bold leading-tight text-sumi">
                  Discovery Assistant
                </CardTitle>
              </div>
            </div>
            
            {/* System Status in header */}
            <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800 animate-fade-in">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Global Live Pricing
            </div>
          </div>
        </CardHeader>

        {/* Scrollable Message Thread */}
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-transparent to-sakura/5 scrollbar-thin scrollbar-thumb-primary/10">
          {messages.map((msg, index) => {
            const isLast = index === messages.length - 1
            const isAssistant = msg.sender === 'assistant'
            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] ${
                  isAssistant ? 'self-start' : 'self-end ml-auto flex-row-reverse'
                }`}
              >
                {isAssistant && (
                  <div className="size-8 rounded-full bg-indigo-50 border border-primary/10 flex items-center justify-center text-xs font-bold text-primary shadow-sm shrink-0">
                    A
                  </div>
                )}
                <div className="space-y-3 w-full">
                  <div
                    className={`rounded-2xl px-4 py-3 text-base shadow-sm ${
                      isAssistant
                        ? 'bg-white border border-primary/5 text-sumi rounded-tl-none'
                        : 'bg-gradient-to-r from-primary to-indigo-jp text-white rounded-tr-none'
                    }`}
                  >
                    {isAssistant ? (
                      <div className="space-y-4">
                        <p className="whitespace-pre-wrap text-sm leading-6">
                          {msg.text}
                        </p>

                        {/* Interactive Destination Picker */}
                        {isLast && isDestinationQuestion && destinationSuggestions.length > 0 && (
                          <div className="space-y-3 mt-4 rounded-xl border border-primary/10 bg-sakura/5 p-4 animate-fade-in">
                            <p className="text-xs font-semibold uppercase tracking-wider text-sumi/70">
                              Pick one or more options to narrow location:
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {destinationSuggestions.map((suggestion) => {
                                const selected = selectedSuggestionIds.includes(suggestion.id)
                                return (
                                  <button
                                    key={suggestion.id}
                                    className={`rounded-full border px-3 py-1.5 text-sm transition-all duration-300 ${
                                      selected
                                        ? 'border-primary bg-primary text-white shadow-md shadow-primary/20 scale-[1.03]'
                                        : 'border-primary/25 bg-white text-sumi hover:border-primary/50 hover:bg-primary/5'
                                    }`}
                                    onClick={() => toggleSuggestion(suggestion)}
                                    type="button"
                                  >
                                    {suggestion.label}
                                  </button>
                                )
                              })}
                            </div>
                            {selectedSuggestions.length > 0 && (
                              <div className="flex flex-wrap gap-2 pt-2 border-t border-primary/5">
                                {selectedSuggestions.map((suggestion) => (
                                  <span
                                    key={`selected-${suggestion.id}`}
                                    className="rounded-full border border-primary/20 bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary"
                                  >
                                    {suggestion.label}
                                  </span>
                                ))}
                              </div>
                            )}
                            <div className="flex flex-wrap gap-2 pt-2">
                              <Button
                                size="sm"
                                disabled={!selectedSuggestions.length || isSubmitting}
                                onClick={submitSelectedSuggestions}
                                type="button"
                                className="bg-primary hover:bg-indigo-jp text-white font-medium"
                              >
                                Use selected destinations
                              </Button>
                              <Button
                                size="sm"
                                disabled={isSubmitting}
                                onClick={markAnswerUnknown}
                                type="button"
                                variant="outline"
                              >
                                Don&apos;t care — show popular beach picks
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap text-sm leading-6 text-white font-medium">
                        {msg.text}
                      </p>
                    )}
                  </div>
                  <span className="text-[10px] text-muted-foreground block px-1">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            )
          })}
          {isSubmitting && (
            <div className="flex gap-3 max-w-[80%] items-center animate-pulse">
              <div className="size-8 rounded-full bg-indigo-50 border border-primary/10 flex items-center justify-center text-xs font-bold text-primary shrink-0">
                A
              </div>
              <div className="bg-white border border-primary/5 rounded-2xl px-4 py-3 rounded-tl-none text-sm text-muted-foreground flex items-center gap-2">
                <span className="flex gap-1">
                  <span className="size-1.5 bg-primary/60 rounded-full animate-bounce"></span>
                  <span className="size-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span className="size-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                </span>
                MiraiGo is searching live prices...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </CardContent>

        {/* Input area */}
        <div className="border-t border-primary/10 bg-white p-4 shrink-0">
          <form className="space-y-3" onSubmit={handleSubmit}>
            {showAssistantFollowUp && (
              <div className="mb-4 space-y-2 p-4 bg-sakura/5 rounded-2xl border border-primary/10 animate-fade-in" data-testid="assistant-thread">
                {activeQuestion && (
                  <h2 className="text-[18px] font-bold leading-snug text-sumi">
                    {activeQuestion.prompt}
                  </h2>
                )}
                {remediationQuestion && (
                  <h2 className="text-[18px] font-bold leading-snug text-sumi">
                    {remediationQuestion.prompt}
                  </h2>
                )}
                {assistantFollowUpHelper ? (
                  <p className="text-sm text-muted-foreground">
                    {assistantFollowUpHelper}
                  </p>
                ) : null}
                {continueBlocked && continueBlockReason ? (
                  <p className="text-sm font-semibold text-destructive" role="status">
                    {continueBlockReason}
                  </p>
                ) : null}
                {continueBlocked && pendingRequirementGuidance.length > 0 && (
                  <ul className="list-disc pl-5 space-y-1 text-sm text-sumi/90">
                    {pendingRequirementGuidance.map((guidance) => (
                      <li key={guidance}>{guidance}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
            <label htmlFor="travel-prompt" className="block text-sm font-normal leading-[1.4] text-sumi mb-2">
              {promptLabel}
            </label>
            <div className="relative rounded-2xl border border-primary/15 bg-white shadow-sm focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all duration-300">
              <textarea
                id="travel-prompt"
                name="travel-prompt"
                aria-label={promptAriaLabel}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                rows={2}
                className="w-full rounded-2xl bg-white pl-4 pr-14 py-3 text-base text-sumi placeholder:text-muted-foreground focus:outline-none resize-none min-h-16"
                placeholder={promptPlaceholder}
                disabled={isSubmitting}
              />
              <div className="absolute right-3 bottom-3">
                <Button
                  size="icon"
                  className="h-10 w-10 rounded-xl bg-primary hover:bg-indigo-jp text-white shadow-md shadow-primary/25 transition-all duration-300"
                  disabled={!canSubmit || isSubmitting}
                  type="submit"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="size-4 animate-fade-in"
                  >
                    <path d="m22 2-7 20-4-9-9-4Z" />
                    <path d="M22 2 11 13" />
                  </svg>
                  <span className="sr-only">{buttonLabel}</span>
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 items-center justify-between">
              <div className="flex gap-2">
                {activeQuestion ? (
                  <Button
                    aria-label="I don't know this yet"
                    disabled={isSubmitting}
                    onClick={markAnswerUnknown}
                    title="Set this clarification as unknown"
                    type="button"
                    variant="outline"
                    size="sm"
                    className="rounded-full"
                  >
                    I don&apos;t know this yet
                  </Button>
                ) : null}
              </div>
              
              {!clarificationState && (
                <p className="text-xs text-muted-foreground italic">
                  {EMPTY_COPY_BODY}
                </p>
              )}
            </div>
          </form>
        </div>
      </Card>

      {/* Side Column: Trip Parameters Panel */}
      <div className="space-y-6">
        <Card className="border-primary/10 bg-white/95 shadow-lg rounded-3xl overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-sakura/5 to-white border-b border-primary/5 py-4 px-6">
            <CardTitle className="text-base font-bold text-sumi flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="size-4 text-primary"
              >
                <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                <line x1="16" x2="16" y1="2" y2="6" />
                <line x1="8" x2="8" y1="2" y2="6" />
                <line x1="3" x2="21" y1="10" y2="10" />
                <path d="m9 16 2 2 4-4" />
              </svg>
              Active Trip Parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-6">
            {clarificationState && recapChips.length > 0 ? (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {recapChips.map((chip) => (
                    <span
                      key={chip.slot}
                      className="inline-flex items-center gap-2 rounded-full border border-primary/10 bg-primary/5 pl-3 pr-1 py-1.5 text-xs font-semibold text-sumi transition-all duration-300 hover:bg-primary/10"
                    >
                      <span>
                        {chip.label}: {chip.value_label}
                      </span>
                      {chip.editable && (
                        <Button
                          aria-label={`Edit ${chip.label}`}
                          className="h-7 w-7 rounded-full p-0 text-primary hover:bg-primary/15"
                          disabled={isSubmitting}
                          onClick={() => startEditingChip(chip)}
                          title={`Edit ${chip.label}`}
                          type="button"
                          variant="ghost"
                        >
                          <PencilLine className="size-3" />
                          <span className="sr-only">Edit</span>
                        </Button>
                      )}
                    </span>
                  ))}
                </div>

                {activeChip && (
                  <form
                    className="space-y-3 rounded-2xl border border-primary/15 bg-sakura/5 p-4 animate-fade-in"
                    onSubmit={saveChipEdit}
                  >
                    <label className="block text-xs font-bold uppercase tracking-wider text-sumi/80">
                      {slotToInputLabel(activeChip)}
                      <Input
                        aria-label={slotToInputLabel(activeChip)}
                        onChange={(event) => setEditedValue(event.target.value)}
                        value={editedValue}
                        className="mt-1 bg-white border-primary/10 focus:border-primary"
                        placeholder="Type value..."
                      />
                    </label>
                    <div className="flex flex-wrap gap-1.5">
                      <Button
                        size="sm"
                        aria-label={`Save ${activeChip.label} edit`}
                        disabled={!editedValue.trim() || isSubmitting}
                        type="submit"
                        className="bg-primary hover:bg-indigo-jp text-white font-medium"
                      >
                        Save
                      </Button>
                      <Button
                        size="sm"
                        aria-label={`Mark ${activeChip.label} unknown`}
                        disabled={isSubmitting}
                        onClick={markChipUnknown}
                        title={`Mark ${activeChip.label} as unknown`}
                        type="button"
                        variant="outline"
                      >
                        I don&apos;t know
                      </Button>
                      <Button
                        size="sm"
                        disabled={isSubmitting}
                        onClick={() => setEditingSlot(null)}
                        type="button"
                        variant="ghost"
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                )}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground italic">
                No active parameters yet. Submit your travel intent to start discovery.
              </p>
            )}

            {complete && (
              <div className="pt-4 border-t border-primary/10 space-y-4">
                {continueBlocked ? (
                  <div className="rounded-xl bg-amber-50 border border-amber-200 p-3 text-xs text-amber-800 space-y-2">
                    <p className="font-semibold flex items-center gap-1.5">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="size-3.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>
                      Airfare Prerequisites Pending
                    </p>
                    <p className="text-amber-700/90">{continueBlockReason}</p>
                  </div>
                ) : null}
                
                <Button
                  className="w-full h-11 bg-primary text-white hover:bg-indigo-jp shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2"
                  disabled={isSubmitting || continueBlocked}
                  onClick={continueToRecommendations}
                  type="button"
                >
                  Continue to Recommendations
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="2.5" stroke="currentColor" className="size-4"><path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" /></svg>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
