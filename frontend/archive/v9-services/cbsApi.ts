/**
 * CBS API Service - Israeli Household Expenditure Data
 *
 * Connects to FastAPI backend CBS endpoints for real-time data
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CBSQuintile {
  income_quintile: number;
  transaction_count: number;
  total_spending: string;
  avg_transaction: string;
  median_transaction: string;
  unique_customers: number;
  spending_share_pct: string;
}

export interface CBSQuintileResponse {
  quintiles: CBSQuintile[];
  key_insight: string;
}

export interface CBSCategory {
  category: string;
  transaction_count: number;
  total_revenue: string;
  avg_transaction: string;
  unique_customers: number;
  unique_products: number;
  market_share_pct: string;
}

export interface CBSCategoryResponse {
  categories: CBSCategory[];
}

export interface CBSCity {
  city: string;
  transaction_count: number;
  total_revenue: string;
  avg_transaction: string;
  unique_customers: number;
  market_share_pct: string;
}

export interface CBSCityResponse {
  cities: CBSCity[];
}

export interface CBSDataQuality {
  completeness: string;
  uniqueness: string;
  validity: string;
  overall: string;
  assessment: string;
}

export interface CBSInsights {
  metadata: {
    report_date: string;
    data_period: string;
    total_transactions: number;
    data_quality_score: string;
  };
  data_summary: {
    total_customers: number;
    total_products: number;
    total_categories: number;
    cities_covered: number;
    currency: string;
  };
  quintile_analysis: {
    q1_avg: string;
    q5_avg: string;
    spending_ratio: string;
    key_finding: string;
  };
  top_categories: Array<{
    category: string;
    revenue: string;
    share: string;
  }>;
  top_cities: Array<{
    city: string;
    revenue: string;
  }>;
  business_recommendations: string[];
  pareto_analysis: {
    top_20_pct_products_revenue_share: string;
    top_20_pct_customers_revenue_share: string;
  };
  monthly_trend?: {
    [month: string]: string;
  };
}

/**
 * Fetch income quintile analysis
 */
export async function fetchQuintiles(): Promise<CBSQuintileResponse> {
  const response = await fetch(`${API_BASE_URL}/api/cbs/quintiles`);
  if (!response.ok) {
    throw new Error(`Failed to fetch quintiles: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch category performance
 */
export async function fetchCategories(): Promise<CBSCategoryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/cbs/categories`);
  if (!response.ok) {
    throw new Error(`Failed to fetch categories: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch city/geographic analysis
 */
export async function fetchCities(): Promise<CBSCityResponse> {
  const response = await fetch(`${API_BASE_URL}/api/cbs/cities`);
  if (!response.ok) {
    throw new Error(`Failed to fetch cities: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch data quality metrics
 */
export async function fetchDataQuality(): Promise<CBSDataQuality> {
  const response = await fetch(`${API_BASE_URL}/api/cbs/data-quality`);
  if (!response.ok) {
    throw new Error(`Failed to fetch data quality: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch complete business insights
 */
export async function fetchInsights(): Promise<CBSInsights> {
  const response = await fetch(`${API_BASE_URL}/api/cbs/insights`);
  if (!response.ok) {
    throw new Error(`Failed to fetch insights: ${response.statusText}`);
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

// =============================================================================
// Strategic CBS Endpoints (V2)
// =============================================================================

export interface QuintileGapItem {
  category: string;
  quintile_1: number;
  quintile_2: number;
  quintile_3: number;
  quintile_4: number;
  quintile_5: number;
  total_spending: number;
  avg_spending: number;
}

export interface QuintileGapResponse {
  ratio: number;
  q5_total: number;
  q1_total: number;
  insight: string;
  categories: QuintileGapItem[];
}

export interface DigitalMatrixItem {
  category: string;
  physical_pct: number;
  online_israel_pct: number;
  online_abroad_pct: number;
}

export interface DigitalMatrixResponse {
  top_israel_online: Array<{ category: string; online_israel_pct: number }>;
  top_abroad_online: Array<{ category: string; online_abroad_pct: number }>;
  most_physical: Array<{ category: string; physical_pct: number }>;
  categories: DigitalMatrixItem[];
}

export interface RetailBattleItem {
  category: string;
  // PERCENTAGES - Store type distribution (values already are %, sum to 100%)
  other: number;  // % of spending at "other" stores
  special_shop: number;  // % at wine/specialty shops (was wrongly called "local_market")
  butcher: number;  // % at butcher shops
  veg_fruit_shop: number;  // % at vegetable/fruit shops
  online_supermarket: number;  // % at online supermarkets
  supermarket_chain: number;  // % at supermarket chains (MAIN RETAIL CHANNEL)
  market: number;  // % at outdoor markets
  grocery: number;  // % at corner stores/grocery
  total: number;  // Should equal 100 (percentage sum)
  // DUPLICATE percentages (same as above - these are redundant)
  other_pct: number;
  special_shop_pct: number;
  butcher_pct: number;
  veg_fruit_shop_pct: number;
  online_supermarket_pct: number;
  supermarket_chain_pct: number;
  market_pct: number;
  grocery_pct: number;
}

export interface RetailBattleResponse {
  supermarket_chain_share: number;  // Main retail channel share
  market_share: number;  // Outdoor markets share
  grocery_share: number;  // Corner stores share
  special_shop_share: number;  // Wine/specialty shops share
  supermarket_wins: Array<{
    category: string;
    supermarket_chain_pct: number;
    market_pct: number;
    grocery_pct: number;
  }>;
  market_wins: Array<{
    category: string;
    market_pct: number;
    supermarket_chain_pct: number;
  }>;
  categories: RetailBattleItem[];
}

/**
 * Fetch Quintile Gap Analysis (The 2.62x Rule)
 */
export async function fetchQuintileGap(): Promise<QuintileGapResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/quintile-gap`);
  if (!response.ok) {
    throw new Error(`Failed to fetch quintile gap: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch Digital Opportunity Matrix
 */
export async function fetchDigitalMatrix(): Promise<DigitalMatrixResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/digital-matrix`);
  if (!response.ok) {
    throw new Error(`Failed to fetch digital matrix: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch Retail Battle Analysis
 */
export async function fetchRetailBattle(): Promise<RetailBattleResponse> {
  const response = await fetch(`${API_BASE_URL}/api/strategic/retail-battle`);
  if (!response.ok) {
    throw new Error(`Failed to fetch retail battle: ${response.statusText}`);
  }
  return response.json();
}
