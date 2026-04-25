import { fireEvent, render, screen } from '@testing-library/react'
import type { ClarificationState } from '@/lib/api'
import SearchForm from '../SearchForm'

function buildClarificationState(
  overrides: Partial<ClarificationState> = {}
): ClarificationState {
  return {
    destination: {
      slot: 'destination',
      value_label: null,
      confidence: 0.1,
      ambiguous: true,
      explicit_unknown: false,
      source: 'extracted',
    },
    timeline: {
      slot: 'timeline',
      value_label: 'June 2026',
      confidence: 0.9,
      ambiguous: false,
      explicit_unknown: false,
      source: 'user',
    },
    trip_length: {
      slot: 'trip_length',
      value_label: '7 days',
      confidence: 0.9,
      ambiguous: false,
      explicit_unknown: false,
      source: 'user',
    },
    budget: {
      slot: 'budget',
      value_label: '$2,500',
      confidence: 0.8,
      ambiguous: false,
      explicit_unknown: false,
      source: 'extracted',
    },
    next_question: {
      slot: 'destination',
      prompt: 'Where do you want to travel?',
      helper_text: 'City, country, or a broad region all work.',
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
          slot: 'timeline',
          label: 'Timeline',
          value_label: 'June 2026',
          editable: true,
          explicit_unknown: false,
        },
      ],
      continue_label: 'Continue to Recommendations',
    },
    all_critical_slots_resolved: false,
    ...overrides,
  }
}

describe('ClarificationFlow', () => {
  it('renders one active clarification prompt at a time', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState()}
      />
    )

    const prompts = screen.getAllByRole('heading', {
      name: /where do you want to travel\?/i,
    })

    expect(prompts).toHaveLength(1)
    expect(
      screen.queryByText(/no active clarification question/i)
    ).not.toBeInTheDocument()
  })

  it('renders editable recap chips and sends recap_edit payload on chip edit', () => {
    const onSearch = jest.fn()
    render(
      <SearchForm
        onSearch={onSearch}
        clarificationState={buildClarificationState()}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /edit destination/i }))
    fireEvent.change(screen.getByLabelText(/update destination/i), {
      target: { value: 'Japan' },
    })
    fireEvent.click(screen.getByRole('button', { name: /save destination edit/i }))

    expect(onSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        recap_edit: {
          slot: 'destination',
          edited_value: 'Japan',
          explicit_unknown: false,
        },
      })
    )
  })

  it('shows exact continue CTA label when clarification is complete', () => {
    render(
      <SearchForm
        onSearch={jest.fn()}
        clarificationState={buildClarificationState({
          next_question: null,
          all_critical_slots_resolved: true,
        })}
      />
    )

    expect(
      screen.getByRole('button', { name: 'Continue to Recommendations' })
    ).toBeInTheDocument()
  })
})
