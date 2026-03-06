import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Home from '../app/page'
import useSWR from 'swr'

// Mock SWR
jest.mock('swr')
const mockedUseSWR = useSWR as jest.Mock

describe('Home Page Integration', () => {
  it('renders initial state', () => {
    mockedUseSWR.mockReturnValue({ data: null, error: null, isLoading: false })
    render(<Home />)
    expect(screen.getAllByText(/Mirai/i).length).toBeGreaterThan(0)
    expect(screen.getByPlaceholderText(/where do you want to go/i)).toBeInTheDocument()
  })

  it('performs search and displays results', async () => {
    const mockResults = {
      results: [
        { provider: 'Expedia', text: 'Miami Beach Resort', score: 100 }
      ]
    }

    // Initial state
    mockedUseSWR.mockReturnValue({ data: null, error: null, isLoading: false })
    
    const { rerender } = render(<Home />)
    
    const input = screen.getByPlaceholderText(/where do you want to go/i)
    const button = screen.getByRole('button', { name: /search/i })

    // Simulate user typing and clicking search
    fireEvent.change(input, { target: { value: 'Miami' } })
    fireEvent.click(button)

    // Update mock for the second render after state change
    mockedUseSWR.mockReturnValue({ data: mockResults, error: null, isLoading: false })
    
    rerender(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Miami Beach Resort')).toBeInTheDocument()
      expect(screen.getByText(/Expedia/i)).toBeInTheDocument()
    })
  })
})
