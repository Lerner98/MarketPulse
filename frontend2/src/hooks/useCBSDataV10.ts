import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  fetchSegmentTypes,
  fetchSegmentValues,
  fetchSegmentationData,
  fetchInequalityAnalysis,
  fetchBurnRateAnalysis,
  fetchBusinessIntelligence,
  SegmentTypesResponse,
  SegmentValuesResponse,
  SegmentationResponse,
  InequalityResponse,
  BurnRateResponse,
  BusinessIntelligenceResponse,
} from '@/services/cbsApiV10';

/**
 * CBS Data Hooks V10 - Normalized Star Schema Architecture
 *
 * Key Innovation: Dynamic segmentation - same hooks work for ANY demographic dimension
 * - Income Quintile
 * - Age Group
 * - Education Level
 * - Religiosity
 * - Geographic (Sub-District)
 * - etc.
 *
 * Architecture:
 * - dim_segment (Dimension: WHO)
 * - fact_segment_expenditure (Fact: WHAT + HOW MUCH)
 */

// =============================================================================
// Segment Discovery Hooks
// =============================================================================

/**
 * Fetch all available segment types
 *
 * Returns list of demographic dimensions available in the database
 * Example: ["Income Quintile", "Age Group", "Education Level"]
 *
 * Use this to populate the master segment selector dropdown
 */
export function useSegmentTypes(): UseQueryResult<SegmentTypesResponse, Error> {
  return useQuery({
    queryKey: ['v10-segment-types'],
    queryFn: fetchSegmentTypes,
    staleTime: 15 * 60 * 1000, // 15 minutes (segment types rarely change)
    retry: 2,
  });
}

/**
 * Fetch segment values for a specific segment type
 *
 * @param segmentType - The segment type (e.g., "Income Quintile")
 *
 * Returns all segment values (e.g., Q1, Q2, Q3, Q4, Q5 for Income Quintile)
 * Sorted by segment_order for proper display
 */
export function useSegmentValues(
  segmentType: string | null
): UseQueryResult<SegmentValuesResponse, Error> {
  return useQuery({
    queryKey: ['v10-segment-values', segmentType],
    queryFn: () => fetchSegmentValues(segmentType!),
    enabled: !!segmentType, // Only fetch when segmentType is selected
    staleTime: 15 * 60 * 1000,
    retry: 2,
  });
}

// =============================================================================
// Expenditure Data Hooks
// =============================================================================

/**
 * Fetch expenditure data for a specific segment type
 *
 * @param segmentType - The segment type (e.g., "Income Quintile", "Age Group")
 * @param limit - Number of expenditure records to return (default: 100)
 *
 * Returns expenditure records grouped by the selected demographic dimension
 *
 * Example:
 * - segmentType="Income Quintile" → Shows spending across Q1-Q5
 * - segmentType="Age Group" → Shows spending across 18-24, 25-34, etc.
 */
export function useSegmentationData(
  segmentType: string | null,
  limit: number = 100
): UseQueryResult<SegmentationResponse, Error> {
  return useQuery({
    queryKey: ['v10-segmentation-data', segmentType, limit],
    queryFn: () => fetchSegmentationData(segmentType!, limit),
    enabled: !!segmentType,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}

// =============================================================================
// Business Intelligence Hooks
// =============================================================================

/**
 * Fetch inequality analysis for a specific segment type
 *
 * @param segmentType - The segment type (e.g., "Income Quintile", "Age Group")
 * @param limit - Number of top inequality items to return (default: 10)
 *
 * Returns spending gap between highest and lowest segments
 *
 * Example Insights:
 * - Income Quintile: "Q5 spends 28.7x more on Income Tax than Q1"
 * - Age Group: "65+ spends 5.2x more on Healthcare than 18-24"
 * - Education: "PhD holders spend 12.3x more on Books than High School"
 */
export function useInequalityAnalysis(
  segmentType: string | null,
  limit: number = 10
): UseQueryResult<InequalityResponse, Error> {
  return useQuery({
    queryKey: ['v10-inequality-analysis', segmentType, limit],
    queryFn: () => fetchInequalityAnalysis(segmentType!, limit),
    enabled: !!segmentType,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch burn rate analysis for any segment type
 *
 * @param segmentType - The segment type (e.g., "Income Quintile", "Geographic Region")
 *
 * Returns financial pressure metrics: spending as % of income
 *
 * Burn Rate Categories:
 * - > 100%: Financial Pressure (Deficit)
 * - 90-100%: Break-Even
 * - 75-90%: Low Savings
 * - < 75%: Healthy Savings
 */
export function useBurnRateAnalysis(
  segmentType: string | null
): UseQueryResult<BurnRateResponse, Error> {
  return useQuery({
    queryKey: ['v10-burn-rate-analysis', segmentType],
    queryFn: () => fetchBurnRateAnalysis(segmentType!),
    enabled: !!segmentType,
    staleTime: 10 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch comprehensive business intelligence for a segment type
 *
 * @param segmentType - The segment type (e.g., "Work Status", "Income Quintile")
 *
 * Returns corporate-grade metrics:
 * - Market Sizing: Total addressable market (TAM) per segment
 * - Customer Profiles: Demographics, financial health, lifecycle stage
 * - Category Opportunities: Top categories by market size
 * - Strategic Recommendations: Actionable business insights
 *
 * Example Use Cases:
 * - Work Status: Employees ₪440B market vs Pensioners ₪94B
 * - Income Quintile: Q5 premium segments vs Q1 value segments
 * - Geographic: City market opportunities and demographic targeting
 */
export function useBusinessIntelligence(
  segmentType: string | null
): UseQueryResult<BusinessIntelligenceResponse, Error> {
  return useQuery({
    queryKey: ['v10-business-intelligence', segmentType],
    queryFn: () => fetchBusinessIntelligence(segmentType!),
    enabled: !!segmentType,
    staleTime: 15 * 60 * 1000, // 15 minutes (strategic data changes infrequently)
    retry: 2,
  });
}
