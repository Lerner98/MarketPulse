import { useState, useEffect, useCallback } from 'react'
import type { UseFetchResult } from '@/types'

/**
 * Custom hook for fetching data from API
 * @param fetchFn - Async function that fetches data
 * @param dependencies - Dependencies array to trigger refetch
 * @returns Object with data, loading, error, and refetch function
 */
function useFetch<T>(
  fetchFn: () => Promise<T>,
  dependencies: unknown[] = []
): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await fetchFn()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An unknown error occurred'))
    } finally {
      setLoading(false)
    }
  }, [fetchFn])

  useEffect(() => {
    fetchData()
  }, [fetchData, ...dependencies])

  const refetch = useCallback(async () => {
    await fetchData()
  }, [fetchData])

  return { data, loading, error, refetch }
}

export default useFetch
