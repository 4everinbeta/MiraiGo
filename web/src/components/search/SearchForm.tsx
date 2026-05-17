'use client'

import { useMemo, useState } from 'react'
import { PencilLine } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import type {
  ClarificationRecapChip,
  ClarificationSlot,
  ClarificationState,
  DestinationSuggestion,
  InventoryType,
  SearchRequest,
} from '@/lib/api'

interface SearchFormProps {
  onSearch: (params: SearchRequest) => void
  isSubmitting?: boolean
  clarificationState?: ClarificationState | null
  preservedRequest?: Partial<SearchRequest> | null
}

const DEFAULT_AMENITIES = ['wifi']
const EMPTY_COPY_HEADING = 'Start with your travel intent'
const EMPTY_COPY_BODY =
  'Describe where, when, and budget if known. We’ll ask one follow-up at a time to fill missing details.'

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

export default function SearchForm({
  onSearch,
  isSubmitting = false,
  clarificationState = null,
  preservedRequest = null,
}: SearchFormProps) {
  const [query, setQuery] = useState('')
  const [answerText, setAnswerText] = useState('')
  const [editingSlot, setEditingSlot] = useState<ClarificationSlot | null>(null)
  const [editedValue, setEditedValue] = useState('')
  const [selectedSuggestionIds, setSelectedSuggestionIds] = useState<string[]>([])

  const activeQuestion = clarificationState?.next_question ?? null
  const destinationSuggestions = clarificationState?.destination_suggestions ?? []
  const recapChips = clarificationState?.recap.chips ?? []
  const canBegin = Boolean(query.trim())
  const canSubmitAnswer = Boolean(answerText.trim() && activeQuestion)
  const complete = Boolean(clarificationState?.all_critical_slots_resolved)
  const isDestinationQuestion = activeQuestion?.slot === 'destination'

  const activeChip = useMemo(
    () => recapChips.find((chip) => chip.slot === editingSlot) ?? null,
    [editingSlot, recapChips]
  )

  const selectedSuggestions = useMemo(() => {
    if (!destinationSuggestions.length || !selectedSuggestionIds.length) return []
    const selected = new Set(selectedSuggestionIds)
    return destinationSuggestions.filter((item) => selected.has(item.id))
  }, [destinationSuggestions, selectedSuggestionIds])

  const handleBegin = (event: React.FormEvent) => {
    event.preventDefault()
    if (!canBegin || isSubmitting) return
    onSearch(buildBaseRequest(query))
    setAnswerText('')
  }

  const handleAnswerSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    if (!activeQuestion || !canSubmitAnswer || isSubmitting) return

    onSearch({
      ...buildBaseRequest(query),
      clarification_answer: {
        slot: activeQuestion.slot,
        answer_text: answerText.trim(),
        explicit_unknown: false,
      },
    })
    setAnswerText('')
  }

  const markAnswerUnknown = () => {
    if (!activeQuestion || isSubmitting) return
    onSearch({
      ...buildBaseRequest(query),
      clarification_answer: {
        slot: activeQuestion.slot,
        explicit_unknown: true,
      },
    })
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
      ...buildBaseRequest(query),
      constraint_updates: {
        destination: destinationCandidates.length === 1 ? destinationCandidates[0] : undefined,
        destination_candidates: destinationCandidates,
        destination_selection_mode:
          destinationCandidates.length > 1 ? 'compare' : 'single',
        explicit_unknown_slots: [],
      },
    })
    setAnswerText('')
  }

  const startEditingChip = (chip: ClarificationRecapChip) => {
    setEditingSlot(chip.slot)
    setEditedValue(formatEditableDefault(chip))
  }

  const saveChipEdit = (event: React.FormEvent) => {
    event.preventDefault()
    if (!activeChip || !editedValue.trim() || isSubmitting) return

    onSearch({
      ...buildBaseRequest(query),
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
      ...buildBaseRequest(query),
      recap_edit: {
        slot: activeChip.slot,
        explicit_unknown: true,
      },
    })

    setEditingSlot(null)
    setEditedValue('')
  }

  const continueToRecommendations = () => {
    if (!complete || isSubmitting) return
    onSearch({
      ...buildBaseRequest(query),
      ...preservedRequest,
      query: query.trim() || preservedRequest?.query || undefined,
    })
  }

  return (
    <Card className="border-primary/10 bg-white/90 shadow-2xl shadow-primary/5 backdrop-blur">
      <CardHeader className="space-y-4 border-b border-primary/10 bg-gradient-to-r from-white via-sakura/40 to-white">
        <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-primary/70">
          Conversational Clarification
        </p>
        <CardTitle className="text-[28px] font-semibold leading-[1.2] text-sumi">
          Tell us your travel intent, then answer one follow-up at a time.
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-8 pt-8">
        <form className="space-y-4" onSubmit={handleBegin}>
          <label className="space-y-2 text-sm font-normal leading-[1.4] text-sumi">
            Travel prompt
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              rows={4}
              className="min-h-32 w-full rounded-lg border border-border bg-white px-3 py-2 text-base leading-[1.5] text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="I want a warm beach trip in June with a moderate budget."
            />
          </label>
          <div className="flex flex-wrap gap-2">
            <Button
              className="h-11 min-w-44 bg-primary text-white hover:bg-indigo-jp"
              disabled={!canBegin || isSubmitting}
              type="submit"
            >
              {isSubmitting ? 'Submitting…' : 'Submit travel intent'}
            </Button>
            {!clarificationState && (
              <p className="text-base font-normal leading-[1.5] text-muted-foreground">
                {EMPTY_COPY_BODY}
              </p>
            )}
          </div>
        </form>

        {!clarificationState && (
          <section className="rounded-2xl border border-border/80 bg-[#FEE2E2] p-6">
            <h2 className="text-[20px] font-semibold leading-[1.2] text-sumi">{EMPTY_COPY_HEADING}</h2>
            <p className="mt-2 text-base font-normal leading-[1.5] text-muted-foreground">{EMPTY_COPY_BODY}</p>
          </section>
        )}

        {activeQuestion && (
          <section className="space-y-4 rounded-2xl border border-primary/20 bg-[#FEE2E2] p-6">
            <h2 className="text-[20px] font-semibold leading-[1.2] text-sumi">{activeQuestion.prompt}</h2>
            {activeQuestion.helper_text ? (
              <p className="text-base font-normal leading-[1.5] text-muted-foreground">
                {activeQuestion.helper_text}
              </p>
            ) : null}
            {isDestinationQuestion && destinationSuggestions.length > 0 && (
              <div className="space-y-3 rounded-xl border border-primary/20 bg-white p-4">
                <p className="text-sm font-medium text-sumi">
                  Pick one or more options to narrow the location:
                </p>
                <div className="flex flex-wrap gap-2">
                  {destinationSuggestions.map((suggestion) => {
                    const selected = selectedSuggestionIds.includes(suggestion.id)
                    return (
                      <button
                        key={suggestion.id}
                        className={`rounded-full border px-3 py-1.5 text-sm transition ${
                          selected
                            ? 'border-primary bg-primary text-white'
                            : 'border-primary/25 bg-white text-sumi hover:border-primary/60'
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
                  <div className="flex flex-wrap gap-2">
                    {selectedSuggestions.map((suggestion) => (
                      <span
                        key={`selected-${suggestion.id}`}
                        className="rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary"
                      >
                        {suggestion.label}
                      </span>
                    ))}
                  </div>
                )}
                <div className="flex flex-wrap gap-2">
                  <Button
                    disabled={!selectedSuggestions.length || isSubmitting}
                    onClick={submitSelectedSuggestions}
                    type="button"
                  >
                    Use selected destinations
                  </Button>
                  <Button
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
            <form className="space-y-3" onSubmit={handleAnswerSubmit}>
              <label className="space-y-2 text-sm font-normal leading-[1.4] text-sumi">
                Your answer
                <Input
                  value={answerText}
                  onChange={(event) => setAnswerText(event.target.value)}
                  placeholder="Type your answer in plain language."
                />
              </label>
              <div className="flex flex-wrap gap-2">
                <Button disabled={!canSubmitAnswer || isSubmitting} type="submit">
                  {isSubmitting ? 'Saving…' : 'Submit answer'}
                </Button>
                <Button
                  aria-label="I don't know this yet"
                  disabled={isSubmitting}
                  onClick={markAnswerUnknown}
                  title="Set this clarification as unknown"
                  type="button"
                  variant="outline"
                >
                  I don&apos;t know this yet
                </Button>
              </div>
            </form>
          </section>
        )}

        {clarificationState && recapChips.length > 0 && (
          <section className="space-y-4 rounded-2xl border border-border/80 bg-[#FEE2E2] p-6">
            <h2 className="text-[20px] font-semibold leading-[1.2] text-sumi">Constraint recap</h2>
            <div className="flex flex-wrap gap-2">
              {recapChips.map((chip) => (
                <span
                  key={chip.slot}
                  className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-white px-3 py-2 text-sm font-normal leading-[1.4] text-sumi"
                >
                  <span>
                    {chip.label}: {chip.value_label}
                  </span>
                  {chip.editable && (
                    <Button
                      aria-label={`Edit ${chip.label}`}
                      className="h-11 min-w-11 px-3 text-primary"
                      disabled={isSubmitting}
                      onClick={() => startEditingChip(chip)}
                      title={`Edit ${chip.label}`}
                      type="button"
                      variant="ghost"
                    >
                      <PencilLine className="size-4" />
                      <span className="sm:hidden">Edit</span>
                    </Button>
                  )}
                </span>
              ))}
            </div>

            {activeChip && (
              <form
                className="space-y-3 rounded-xl border border-primary/20 bg-white p-4"
                onSubmit={saveChipEdit}
              >
                <label className="space-y-2 text-sm font-normal leading-[1.4] text-sumi">
                  {slotToInputLabel(activeChip)}
                  <Input
                    aria-label={slotToInputLabel(activeChip)}
                    onChange={(event) => setEditedValue(event.target.value)}
                    value={editedValue}
                  />
                </label>
                <div className="flex flex-wrap gap-2">
                  <Button
                    aria-label={`Save ${activeChip.label} edit`}
                    disabled={!editedValue.trim() || isSubmitting}
                    type="submit"
                  >
                    Save
                  </Button>
                  <Button
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
          </section>
        )}

        {complete && (
          <div className="flex justify-end border-t border-border/80 pt-4">
            <Button
              className="h-11 min-w-56 bg-primary text-white hover:bg-indigo-jp"
              disabled={isSubmitting}
              onClick={continueToRecommendations}
              type="button"
            >
              Continue to Recommendations
            </Button>
          </div>
        )}

        {clarificationState && !activeQuestion && !complete && (
          <section className="rounded-lg border border-destructive/30 bg-destructive/5 p-4">
            <p className="text-base font-normal leading-[1.5] text-destructive">
              We couldn’t process that answer. Rephrase it in plain language, or set the constraint manually in
              the recap chips and continue.
            </p>
          </section>
        )}
      </CardContent>
    </Card>
  )
}
