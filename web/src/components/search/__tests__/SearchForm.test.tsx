import { fireEvent, render, screen } from '@testing-library/react'
import SearchForm from '../SearchForm'

describe('SearchForm', () => {
  it('submits canonical search payload from a travel prompt', () => {
    const onSearch = jest.fn()
    render(<SearchForm onSearch={onSearch} />)

    fireEvent.change(screen.getByLabelText(/travel prompt/i), {
      target: { value: 'Warm beach trip in June under 2500' },
    })
    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))

    expect(onSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        query: 'Warm beach trip in June under 2500',
        inventory: ['stay', 'flight'],
        travelers: expect.objectContaining({ adults: 2 }),
        stay_filters: expect.objectContaining({
          amenities: ['wifi'],
        }),
        flight_filters: expect.objectContaining({
          nonstop: false,
        }),
      })
    )
  })

  it('does not submit when the travel prompt is blank', () => {
    const onSearch = jest.fn()
    render(<SearchForm onSearch={onSearch} />)

    fireEvent.click(screen.getByRole('button', { name: /submit travel intent/i }))
    expect(onSearch).not.toHaveBeenCalled()
  })
})
