/**
 * CBS API Service V9 - Real CBS Household Expenditure Data
 *
 * V9 Production Pipeline:
 * - Table 11: 558 rows (29 demographics + 528 spending categories + mortgage/savings)
 * - Table 38: 14 food categories × 8 store types
 *
 * Data Source: Israeli Central Bureau of Statistics (CBS) 2022 Survey
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// =============================================================================
// V9 Strategic Endpoints - Real CBS Data
// =============================================================================

/**
 * Inequality Gap Analysis
 * Shows spending disparity between Q5 (top 20%) and Q1 (bottom 20%)
 */
export interface InequalityGapItem {
  item_name: string;
  rich_spend: number;  // Q5 spending (NIS/month)
  poor_spend: number;  // Q1 spending (NIS/month)
  gap_ratio: number;   // Q5/Q1 ratio (inequality index)
  total_spend: number; // Average spending (NIS/month)
}

export interface InequalityGapResponse {
  top_inequality: InequalityGapItem[];  // Top 10 categories with highest gap
  insight: string;
}

/**
 * Burn Rate Analysis
 * Shows financial pressure: spending as % of income by quintile
 */
export interface BurnRateResponse {
  q1_burn_rate: number;  // % (e.g., 166.4% = spending MORE than income)
  q5_burn_rate: number;  // % (e.g., 74.8% = saving 25% of income)
  avg_burn_rate: number; // Average across all quintiles
  insight: string;
  pressure_segments: Array<{
    quintile: string;
    burn_rate: number;
    interpretation: string;
  }>;
}

/**
 * Fresh Food Battle
 * Shows retail competition: supermarkets vs traditional retail (markets/butchers)
 */
export interface FreshFoodBattleItem {
  category: string;
  supermarket_chain_pct: number;  // % at big chains
  traditional_pct: number;         // % at markets/butchers/specialty
  winner: string;                  // "Supermarket" or "Traditional"
}

export interface FreshFoodBattleResponse {
  supermarket_dominance: FreshFoodBattleItem[];  // Where chains win
  traditional_strongholds: FreshFoodBattleItem[]; // Where specialty wins
  insight: string;
  aggregate_shares: {
    supermarket_total: number;
    traditional_total: number;
  };
}

/**
 * Retail Competition (Full Breakdown)
 * 8 store types: supermarket, market, grocery, butcher, special shop, veg/fruit, online, other
 */
export interface RetailCompetitionItem {
  category: string;
  other_pct: number;
  special_shop_pct: number;
  butcher_pct: number;
  veg_fruit_shop_pct: number;
  online_supermarket_pct: number;
  supermarket_chain_pct: number;
  market_pct: number;
  grocery_pct: number;
}

export interface RetailCompetitionResponse {
  categories: RetailCompetitionItem[];
  total_categories: number;
}

/**
 * Household Profiles
 * 29 demographic metrics (age, household size, education, income, etc.)
 */
export interface HouseholdProfileItem {
  metric_name: string;
  q5_val: number;   // Top 20% income
  q1_val: number;   // Bottom 20% income
  total_val: number; // Average
}

export interface HouseholdProfilesResponse {
  profiles: HouseholdProfileItem[];
  total_metrics: number;
}

/**
 * Expenditure Categories
 * 528 spending categories with inequality index
 */
export interface ExpenditureItem {
  item_name: string;
  q5_spend: number;
  q1_spend: number;
  total_spend: number;
  inequality_index: number;  // Q5/Q1 ratio (auto-calculated in DB)
}

export interface ExpendituresResponse {
  expenditures: ExpenditureItem[];
  total_categories: number;
  limit_applied: number;
}

// =============================================================================
// API Fetch Functions
// =============================================================================

/**
 * Fetch Inequality Gap Analysis
 * Example: "Housing & Utilities: Q5 spends 3.2x more than Q1"
 */
export async function fetchInequalityGap(): Promise<InequalityGapResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/inequality-gap`);
  if (!response.ok) {
    throw new Error(`Failed to fetch inequality gap: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch Burn Rate Analysis
 * Example: "Q1 spends 166% of income (financial pressure), Q5 spends 75% (saving 25%)"
 */
export async function fetchBurnRate(): Promise<BurnRateResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/burn-rate`);
  if (!response.ok) {
    throw new Error(`Failed to fetch burn rate: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch Fresh Food Battle Analysis
 * Example: "Meat: Butchers win 45%, Supermarkets 42%"
 */
export async function fetchFreshFoodBattle(): Promise<FreshFoodBattleResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/fresh-food-battle`);
  if (!response.ok) {
    throw new Error(`Failed to fetch fresh food battle: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch Full Retail Competition
 * All 14 food categories × 8 store types
 */
export async function fetchRetailCompetition(): Promise<RetailCompetitionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/retail-competition`);
  if (!response.ok) {
    throw new Error(`Failed to fetch retail competition: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch Household Profiles
 * 29 demographic metrics
 */
export async function fetchHouseholdProfiles(): Promise<HouseholdProfilesResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/household-profiles`);
  if (!response.ok) {
    throw new Error(`Failed to fetch household profiles: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch Expenditure Categories
 * @param limit - Number of categories to return (default: 100)
 */
export async function fetchExpenditures(limit: number = 100): Promise<ExpendituresResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/expenditures?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch expenditures: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error('Backend is not healthy');
  }
  return response.json();
}
