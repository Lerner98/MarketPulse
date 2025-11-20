// API Response Types
export interface HealthResponse {
  status: string
  message: string
  timestamp: string
}

export interface DashboardMetrics {
  total_revenue: number
  total_customers: number
  total_products: number
  avg_order_value: number
  total_transactions: number
  period_start?: string
  period_end?: string
}

export interface RevenueDataPoint {
  date: string
  revenue: number
  transactions?: number
}

export interface Customer {
  customer_id: string
  total_spent: number
  transaction_count: number
  first_purchase?: string
  last_purchase?: string
}

export interface Product {
  product_id: string
  product_name: string
  total_revenue: number
  units_sold: number
  avg_price: number
}

export interface SankeyNode {
  name: string
  category?: string
}

export interface SankeyLink {
  source: number | string
  target: number | string
  value: number
}

export interface SankeyData {
  nodes: SankeyNode[]
  links: SankeyLink[]
}

// API Hook Types
export interface UseFetchResult<T> {
  data: T | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export interface ApiError {
  message: string
  status?: number
  details?: unknown
}
