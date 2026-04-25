import { render, screen } from '@testing-library/react'
import type { ClarificationState } from '@/lib/api'

function ClarificationPreview({ state }: { state: ClarificationState }) {
  return (
    <section>
      <h2>{state.next_question?.prompt ?? 'No active clarification question'}</h2>
      <ul>
        {state.recap.chips.map((chip) => (
          <li key={chip.slot}>
            {chip.label}: {chip.value_label}
          </li>
        ))}
      </ul>
    </section>
  )
}

describe('ClarificationFlow contract scaffold', () => {
  it('renders active question and recap chip values from typed clarification state', () => {
    const clarificationState: ClarificationState = {
      destination: {
        slot: 'destination',
        value_label: null,
        confidence: 0.2,
        ambiguous: false,
        explicit_unknown: false,
        source: 'extracted',
      },
      timeline: {
        slot: 'timeline',
        value_label: 'June',
        confidence: 0.9,
        ambiguous: false,
        explicit_unknown: false,
        source: 'user',
      },
      trip_length: {
        slot: 'trip_length',
        value_label: "I don't know",
        confidence: 1,
        ambiguous: false,
        explicit_unknown: true,
        source: 'user',
      },
      budget: {
        slot: 'budget',
        value_label: '$2500',
        confidence: 0.8,
        ambiguous: false,
        explicit_unknown: false,
        source: 'extracted',
      },
      next_question: {
        slot: 'destination',
        prompt: 'Where do you want to travel?',
        helper_text: 'City, country, or broader region all work.',
      },
      recap: {
        chips: [
          {
            slot: 'destination',
            label: 'Destination',
            value_label: 'Missing',
            editable: true,
            explicit_unknown: false,
          },
          {
            slot: 'trip_length',
            label: 'Trip Length',
            value_label: "I don't know",
            editable: true,
            explicit_unknown: true,
          },
        ],
        continue_label: 'Continue to Recommendations',
      },
      all_critical_slots_resolved: false,
    }

    render(<ClarificationPreview state={clarificationState} />)
    expect(screen.getByText('Where do you want to travel?')).toBeInTheDocument()
    expect(screen.getByText(/Destination: Missing/)).toBeInTheDocument()
    expect(screen.getByText(/Trip Length: I don't know/)).toBeInTheDocument()
  })
})
