import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ErrorMessage from '../ErrorMessage'

describe('ErrorMessage', () => {
  it('renders error message', () => {
    render(<ErrorMessage message="Test error" />)

    expect(screen.getByText('Error')).toBeInTheDocument()
    expect(screen.getByText('Test error')).toBeInTheDocument()
  })

  it('renders retry button when onRetry is provided', () => {
    const onRetry = vi.fn()
    render(<ErrorMessage message="Test error" onRetry={onRetry} />)

    expect(screen.getByText('Try again')).toBeInTheDocument()
  })

  it('does not render retry button when onRetry is not provided', () => {
    render(<ErrorMessage message="Test error" />)

    expect(screen.queryByText('Try again')).not.toBeInTheDocument()
  })

  it('calls onRetry when retry button is clicked', async () => {
    const onRetry = vi.fn()
    const user = userEvent.setup()

    render(<ErrorMessage message="Test error" onRetry={onRetry} />)

    await user.click(screen.getByText('Try again'))

    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('applies custom className', () => {
    const { container } = render(
      <ErrorMessage message="Test error" className="custom-class" />
    )

    expect(container.firstChild).toHaveClass('custom-class')
  })
})
