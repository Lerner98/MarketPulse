/**
 * CBS API Client V10 - Normalized Star Schema
 *
 * Data Architecture:
 * - dim_segment: Dimension table (WHO - all demographic types)
 * - fact_segment_expenditure: Fact table (WHAT + HOW MUCH)
 *
 * Key Feature: Dynamic segmentation - same API serves Income, Age, Education, etc.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// =============================================================================
// TypeScript Interfaces
// =============================================================================

export interface SegmentTypeItem {
  segment_type: string;
  count: number;
  example_values: string[];
}

export interface SegmentTypesResponse {
  total_types: number;
  segment_types: SegmentTypeItem[];
}

export interface SegmentValueItem {
  segment_value: string;
  segment_order: number | null;
}

export interface SegmentValuesResponse {
  segment_type: string;
  total_values: number;
  values: SegmentValueItem[];
}

export interface ExpenditureItem {
  item_name: string;
  segment_value: string;
  expenditure_value: number;
}

export interface SegmentationResponse {
  segment_type: string;
  total_items: number;
  total_records: number;
  expenditures: ExpenditureItem[];
}

export interface InequalityItem {
  item_name: string;
  high_segment: string;
  high_spend: number;
  low_segment: string;
  low_spend: number;
  inequality_ratio: number;
  avg_spend: number;
}

export interface InequalityResponse {
  segment_type: string;
  total_items: number;
  top_inequality: InequalityItem[];
  insight: string;
}

export interface BurnRateItem {
  segment_value: string;
  income: number;
  spending: number;
  burn_rate_pct: number;
  surplus_deficit: number;
  financial_status: string;
}

export interface BurnRateResponse {
  total_segments: number;
  burn_rates: BurnRateItem[];
  insight: string;
}

export interface SegmentProfile {
  segment_value: string;
  segment_name: string;
  total_households: number;
  monthly_spending_per_hh: number;
  annual_market_size_b: number;
  market_share_pct: number;
  monthly_income: number;
  monthly_spending: number;
  savings_rate_pct: number;
  monthly_surplus_deficit: number;
  financial_status: string;
  avg_age: number;
  avg_household_size: number;
  lifecycle_stage: string;
}

export interface CategoryOpportunity {
  category_name: string;
  annual_market_b: number;
  employee_spending: number;
  self_employed_spending: number;
  pensioner_spending: number;
  employee_premium_ratio: number;
  market_maturity: string;
}

export interface BusinessIntelligenceResponse {
  segment_type: string;
  total_market_b: number;
  segment_profiles: SegmentProfile[];
  top_categories: CategoryOpportunity[];
  executive_summary: string;
}

// =============================================================================
// API Client Functions
// =============================================================================

/**
 * Fetch all available segment types
 * Returns list of demographic segmentation types (Income Quintile, Age Group, etc.)
 */
export async function fetchSegmentTypes(): Promise<SegmentTypesResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v10/segments/types`);

  if (!response.ok) {
    throw new Error(`Failed to fetch segment types: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch segment values for a specific segment type
 * @param segmentType - The segment type (e.g., "Income Quintile", "Age Group")
 */
export async function fetchSegmentValues(segmentType: string): Promise<SegmentValuesResponse> {
  const encodedType = encodeURIComponent(segmentType);
  const response = await fetch(`${API_BASE_URL}/api/v10/segments/${encodedType}/values`);

  if (!response.ok) {
    throw new Error(`Failed to fetch segment values for "${segmentType}": ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch expenditure data for a specific segment type
 * @param segmentType - The segment type (e.g., "Income Quintile", "Age Group")
 * @param limit - Number of expenditure records to return (default: 100)
 */
export async function fetchSegmentationData(
  segmentType: string,
  limit: number = 100
): Promise<SegmentationResponse> {
  const encodedType = encodeURIComponent(segmentType);
  const response = await fetch(
    `${API_BASE_URL}/api/v10/segmentation/${encodedType}?limit=${limit}`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch segmentation data for "${segmentType}": ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch inequality analysis for a specific segment type
 * Shows spending disparity between highest and lowest segments
 * @param segmentType - The segment type (e.g., "Income Quintile", "Age Group")
 * @param limit - Number of top inequality items to return (default: 10)
 */
export async function fetchInequalityAnalysis(
  segmentType: string,
  limit: number = 10
): Promise<InequalityResponse> {
  const encodedType = encodeURIComponent(segmentType);
  const response = await fetch(
    `${API_BASE_URL}/api/v10/inequality/${encodedType}?limit=${limit}`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch inequality analysis for "${segmentType}": ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch burn rate analysis for any segment type
 * Shows financial pressure: spending as % of income
 * @param segmentType - The segment type (e.g., "Income Quintile", "Geographic Region")
 */
export async function fetchBurnRateAnalysis(segmentType: string): Promise<BurnRateResponse> {
  const encodedType = encodeURIComponent(segmentType);
  const response = await fetch(`${API_BASE_URL}/api/v10/burn-rate?segment_type=${encodedType}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch burn rate analysis for "${segmentType}": ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch comprehensive business intelligence for a segment type
 * Returns market sizing, customer profiles, category opportunities, and strategic recommendations
 * @param segmentType - The segment type (e.g., "Work Status", "Income Quintile")
 */
export async function fetchBusinessIntelligence(segmentType: string): Promise<BusinessIntelligenceResponse> {
  const encodedType = encodeURIComponent(segmentType);
  const response = await fetch(`${API_BASE_URL}/api/v10/business-intelligence/${encodedType}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch business intelligence for "${segmentType}": ${response.statusText}`);
  }

  return response.json();
}
