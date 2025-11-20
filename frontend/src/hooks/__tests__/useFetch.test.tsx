import { describe, it, expect, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import useFetch from '../useFetch'

describe('useFetch', () => {
  it('returns loading state initially', () => {
    const fetchFn = vi.fn().mockResolvedValue({ data: 'test' })
    const { result } = renderHook(() => useFetch(fetchFn))

    expect(result.current.loading).toBe(true)
    expect(result.current.data).toBe(null)
    expect(result.current.error).toBe(null)
  })

  it('returns data on successful fetch', async () => {
    const mockData = { id: 1, name: 'Test' }
    const fetchFn = vi.fn().mockResolvedValue(mockData)
    const { result } = renderHook(() => useFetch(fetchFn))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockData)
    expect(result.current.error).toBe(null)
    expect(fetchFn).toHaveBeenCalledTimes(1)
  })

  it('returns error on failed fetch', async () => {
    const mockError = new Error('Fetch failed')
    const fetchFn = vi.fn().mockRejectedValue(mockError)
    const { result } = renderHook(() => useFetch(fetchFn))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toBe(null)
    expect(result.current.error).toEqual(mockError)
  })

  it('refetches data when refetch is called', async () => {
    const mockData1 = { id: 1 }
    const mockData2 = { id: 2 }
    const fetchFn = vi
      .fn()
      .mockResolvedValueOnce(mockData1)
      .mockResolvedValueOnce(mockData2)

    const { result } = renderHook(() => useFetch(fetchFn))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockData1)

    await result.current.refetch()

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockData2)
    expect(fetchFn).toHaveBeenCalledTimes(2)
  })

  it('handles non-Error objects as errors', async () => {
    const fetchFn = vi.fn().mockRejectedValue('String error')
    const { result } = renderHook(() => useFetch(fetchFn))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeInstanceOf(Error)
    expect(result.current.error?.message).toBe('An unknown error occurred')
  })
})
