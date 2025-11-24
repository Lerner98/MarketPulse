import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  fetchInequalityGap,
  fetchBurnRate,
  fetchFreshFoodBattle,
  fetchRetailCompetition,
  fetchHouseholdProfiles,
  fetchExpenditures,
  InequalityGapResponse,
  BurnRateResponse,
  FreshFoodBattleResponse,
  RetailCompetitionResponse,
  HouseholdProfilesResponse,
  ExpendituresResponse,
} from '@/services/cbsApiV9';

/**
 * CBS Data Hooks V9 - Real Israeli Household Expenditure Data
 *
 * Data Source: CBS 2022 Survey
 * - 558 rows: 29 demographics + 528 spending categories + mortgage/savings
 * - 14 food categories × 8 store types
 */

// =============================================================================
// Strategic Insights Hooks (V9 Production)
// =============================================================================

/**
 * Fetch Inequality Gap Analysis
 * Shows spending disparity between Q5 (top 20%) and Q1 (bottom 20%)
 *
 * Example: "Housing: Q5 spends 3.2x more than Q1"
 */
export function useInequalityGap(): UseQueryResult<InequalityGapResponse, Error> {
  return useQuery({
    queryKey: ['v9-inequality-gap'],
    queryFn: fetchInequalityGap,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

/**
 * Fetch Burn Rate Analysis
 * Shows financial pressure: spending as % of income by quintile
 *
 * Example: "Q1 spends 166% of income (financial pressure), Q5 saves 25%"
 */
export function useBurnRate(): UseQueryResult<BurnRateResponse, Error> {
  return useQuery({
    queryKey: ['v9-burn-rate'],
    queryFn: fetchBurnRate,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch Fresh Food Battle Analysis
 * Shows retail competition: supermarkets vs traditional retail
 *
 * Example: "Meat: Butchers win 45%, Supermarkets 42%"
 */
export function useFreshFoodBattle(): UseQueryResult<FreshFoodBattleResponse, Error> {
  return useQuery({
    queryKey: ['v9-fresh-food-battle'],
    queryFn: fetchFreshFoodBattle,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch Full Retail Competition
 * All 14 food categories × 8 store types
 *
 * Store types: supermarket, market, grocery, butcher, special shop, veg/fruit, online, other
 */
export function useRetailCompetition(): UseQueryResult<RetailCompetitionResponse, Error> {
  return useQuery({
    queryKey: ['v9-retail-competition'],
    queryFn: fetchRetailCompetition,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch Household Profiles
 * 29 demographic metrics (age, household size, education, income, etc.)
 */
export function useHouseholdProfiles(): UseQueryResult<HouseholdProfilesResponse, Error> {
  return useQuery({
    queryKey: ['v9-household-profiles'],
    queryFn: fetchHouseholdProfiles,
    staleTime: 15 * 60 * 1000, // 15 minutes (demographics change less frequently)
    retry: 2,
  });
}

/**
 * Fetch Expenditure Categories
 * 528 spending categories with inequality index
 *
 * @param limit - Number of categories to return (default: 100)
 */
export function useExpenditures(limit: number = 100): UseQueryResult<ExpendituresResponse, Error> {
  return useQuery({
    queryKey: ['v9-expenditures', limit],
    queryFn: () => fetchExpenditures(limit),
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}
