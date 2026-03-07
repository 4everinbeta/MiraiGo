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

    expect(mockSearch).toHaveBeenCalledWith({ 
      q: 'Miami',
      date: undefined,
      qualities: []
    })
  })

  it('toggles date picker visibility when Add Dates is clicked', () => {
    render(<SearchForm onSearch={jest.fn()} />)
    const addDatesBtn = screen.getByRole('button', { name: /add dates/i })
    
    expect(screen.queryByText(/date range/i)).not.toBeInTheDocument()
    
    fireEvent.click(addDatesBtn)
    expect(screen.getAllByText(/date range/i).length).toBeGreaterThan(0)
  })

  it('toggles qualities visibility when Qualities is clicked', () => {
    render(<SearchForm onSearch={jest.fn()} />)
    const qualitiesBtn = screen.getByRole('button', { name: /qualities/i })
    
    expect(screen.queryByText(/desired qualities/i)).not.toBeInTheDocument()
    
    fireEvent.click(qualitiesBtn)
    expect(screen.getByText(/desired qualities/i)).toBeInTheDocument()
  })
})
