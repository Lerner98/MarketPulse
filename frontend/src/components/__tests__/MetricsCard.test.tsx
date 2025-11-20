import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MetricsCard from '../MetricsCard'

describe('MetricsCard', () => {
  it('renders title and value', () => {
    render(<MetricsCard title="Total Revenue" value="₪10,000" />)

    expect(screen.getByText('Total Revenue')).toBeInTheDocument()
    expect(screen.getByText('₪10,000')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(
      <MetricsCard
        title="Total Revenue"
        value="₪10,000"
        subtitle="All time"
      />
    )

    expect(screen.getByText('All time')).toBeInTheDocument()
  })

  it('renders trend when provided', () => {
    render(
      <MetricsCard
        title="Total Revenue"
        value="₪10,000"
        trend={{ value: 12.5, label: 'vs last month', isPositive: true }}
      />
    )

    expect(screen.getByText(/12.5%/)).toBeInTheDocument()
    expect(screen.getByText('vs last month')).toBeInTheDocument()
  })

  it('shows loading skeleton when loading is true', () => {
    const { container } = render(
      <MetricsCard title="Total Revenue" value="₪10,000" loading />
    )

    expect(screen.queryByText('Total Revenue')).not.toBeInTheDocument()
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    render(
      <MetricsCard
        title="Total Revenue"
        value="₪10,000"
        icon={<svg data-testid="test-icon" />}
      />
    )

    expect(screen.getByTestId('test-icon')).toBeInTheDocument()
  })
})
