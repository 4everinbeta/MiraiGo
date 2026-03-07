import { render, screen, fireEvent } from '@testing-library/react'
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
    // Multiple matches now (filter button and card title)
    expect(screen.getAllByText(/Expedia/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Booking.com/i).length).toBeGreaterThan(0)
  })

  it('renders cards as external links when link is provided', () => {
    const resultsWithLink = [{ provider: 'Expedia', text: 'Hotel A', score: 10, link: 'https://expedia.com/test' }]
    render(<ResultsDashboard results={resultsWithLink} isLoading={false} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', 'https://expedia.com/test')
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('filters results by provider', () => {
    const results = [
      { provider: 'Expedia', text: 'Expedia Result', score: 10 },
      { provider: 'Booking.com', text: 'Booking Result', score: 20 },
    ]
    render(<ResultsDashboard results={results} isLoading={false} />)
    
    const bookingFilter = screen.getByLabelText(/Booking.com/i)
    fireEvent.click(bookingFilter)
    
    expect(screen.getByText('Booking Result')).toBeInTheDocument()
    expect(screen.queryByText('Expedia Result')).not.toBeInTheDocument()
  })

  it('shows loading skeletons when isLoading is true', () => {
    render(<ResultsDashboard results={[]} isLoading={true} />)
    expect(screen.getByText(/seeking the future/i)).toBeInTheDocument()
    const skeletons = screen.getAllByTestId('loading-skeleton')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('shows progress for providers during loading', () => {
    render(<ResultsDashboard results={[]} isLoading={true} />)
    expect(screen.getAllByText(/Expedia/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Booking.com/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Airbnb/i).length).toBeGreaterThan(0)
  })

  it('does not render when no results and not loading', () => {
    const { container } = render(<ResultsDashboard results={[]} isLoading={false} />)
    expect(container.firstChild).toBeNull()
  })
})
