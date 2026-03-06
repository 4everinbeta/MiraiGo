import { render, screen, fireEvent } from '@testing-library/react'
import SearchForm from '../SearchForm'

describe('SearchForm', () => {
  it('updates natural language input on change', () => {
    render(<SearchForm onSearch={jest.fn()} />)
    const input = screen.getByPlaceholderText(/where do you want to go/i)
    fireEvent.change(input, { target: { value: 'Beach trip to Miami' } })
    expect(input).toHaveValue('Beach trip to Miami')
  })

  it('calls onSearch with query when form is submitted', () => {
    const mockSearch = jest.fn()
    render(<SearchForm onSearch={mockSearch} />)
    const input = screen.getByPlaceholderText(/where do you want to go/i)
    const button = screen.getByRole('button', { name: /search/i })

    fireEvent.change(input, { target: { value: 'Miami' } })
    fireEvent.click(button)

    expect(mockSearch).toHaveBeenCalledWith({ q: 'Miami' })
  })
})
