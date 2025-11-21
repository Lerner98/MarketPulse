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
