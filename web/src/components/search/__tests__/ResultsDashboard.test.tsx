import { render, screen } from '@testing-library/react'
import ResultsDashboard from '../ResultsDashboard'

describe('ResultsDashboard', () => {
  const mockResults = [
    { provider: 'Expedia', text: 'Hotel A', score: 10 },
    { provider: 'Booking.com', text: 'Hotel B', score: 20 },
  ]

  it('renders a list of results', () => {
    render(<ResultsDashboard results={mockResults} isLoading={false} />)
    expect(screen.getByText('Hotel A')).toBeInTheDocument()
    expect(screen.getByText('Hotel B')).toBeInTheDocument()
    expect(screen.getByText('Expedia')).toBeInTheDocument()
    expect(screen.getByText('Booking.com')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(<ResultsDashboard results={[]} isLoading={true} />)
    expect(screen.getByText(/seeking the future/i)).toBeInTheDocument()
  })

  it('does not render when no results and not loading', () => {
    const { container } = render(<ResultsDashboard results={[]} isLoading={false} />)
    expect(container.firstChild).toBeNull()
  })
})
