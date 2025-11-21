import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  fetchQuintiles,
  fetchCategories,
  fetchCities,
  fetchDataQuality,
  fetchInsights,
  CBSQuintileResponse,
  CBSCategoryResponse,
  CBSCityResponse,
  CBSDataQuality,
  CBSInsights,
} from '@/services/cbsApi';

/**
 * Fetch income quintile analysis (Q1-Q5)
 */
export function useQuintiles(): UseQueryResult<CBSQuintileResponse, Error> {
  return useQuery({
    queryKey: ['cbs-quintiles'],
    queryFn: fetchQuintiles,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

/**
 * Fetch category performance
 */
export function useCategories(): UseQueryResult<CBSCategoryResponse, Error> {
  return useQuery({
    queryKey: ['cbs-categories'],
    queryFn: fetchCategories,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch city/geographic analysis
 */
export function useCities(): UseQueryResult<CBSCityResponse, Error> {
  return useQuery({
    queryKey: ['cbs-cities'],
    queryFn: fetchCities,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch data quality metrics
 */
export function useDataQuality(): UseQueryResult<CBSDataQuality, Error> {
  return useQuery({
    queryKey: ['cbs-data-quality'],
    queryFn: fetchDataQuality,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

/**
 * Fetch complete business insights
 */
export function useInsights(): UseQueryResult<CBSInsights, Error> {
  return useQuery({
    queryKey: ['cbs-insights'],
    queryFn: fetchInsights,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}
