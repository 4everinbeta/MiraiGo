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

  it('renders cards as external links when link is provided', () => {
    const resultsWithLink = [{ provider: 'Expedia', text: 'Hotel A', score: 10, link: 'https://expedia.com/test' }]
    render(<ResultsDashboard results={resultsWithLink} isLoading={false} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', 'https://expedia.com/test')
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('shows loading skeletons when isLoading is true', () => {
    render(<ResultsDashboard results={[]} isLoading={true} />)
    // Looking for skeleton containers (assuming we use a specific class or role)
    expect(screen.getByText(/seeking the future/i)).toBeInTheDocument()
    const skeletons = screen.getAllByTestId('loading-skeleton')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('shows progress for providers during loading', () => {
    render(<ResultsDashboard results={[]} isLoading={true} />)
    expect(screen.getByText(/Expedia/i)).toBeInTheDocument()
    expect(screen.getByText(/Booking.com/i)).toBeInTheDocument()
    expect(screen.getByText(/Airbnb/i)).toBeInTheDocument()
  })

  it('does not render when no results and not loading', () => {
    const { container } = render(<ResultsDashboard results={[]} isLoading={false} />)
    expect(container.firstChild).toBeNull()
  })
})
