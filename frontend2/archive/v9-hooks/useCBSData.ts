import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  fetchQuintiles,
  fetchCategories,
  fetchCities,
  fetchDataQuality,
  fetchInsights,
  fetchQuintileGap,
  fetchDigitalMatrix,
  fetchRetailBattle,
  CBSQuintileResponse,
  CBSCategoryResponse,
  CBSCityResponse,
  CBSDataQuality,
  CBSInsights,
  QuintileGapResponse,
  DigitalMatrixResponse,
  RetailBattleResponse,
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

// =============================================================================
// Strategic Insights Hooks (V2)
// =============================================================================

/**
 * Fetch Quintile Gap Analysis - The 2.62x Rule
 * High-income households (Q5) spend 2.62x more than low-income (Q1)
 */
export function useQuintileGap(): UseQueryResult<QuintileGapResponse, Error> {
  return useQuery({
    queryKey: ['strategic-quintile-gap'],
    queryFn: fetchQuintileGap,
    staleTime: 10 * 60 * 1000, // 10 minutes (strategic data changes less frequently)
    retry: 2,
  });
}

/**
 * Fetch Digital Opportunity Matrix
 * E-commerce penetration analysis (Israel online, abroad online, physical)
 */
export function useDigitalMatrix(): UseQueryResult<DigitalMatrixResponse, Error> {
  return useQuery({
    queryKey: ['strategic-digital-matrix'],
    queryFn: fetchDigitalMatrix,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch Retail Battle Analysis
 * Store type competition (supermarket vs local market vs butcher/bakery)
 */
export function useRetailBattle(): UseQueryResult<RetailBattleResponse, Error> {
  return useQuery({
    queryKey: ['strategic-retail-battle'],
    queryFn: fetchRetailBattle,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}
