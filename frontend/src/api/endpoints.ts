import apiClient from './client'
import type {
  HealthResponse,
  DashboardMetrics,
  RevenueDataPoint,
  Customer,
  Product,
} from '@/types'

// Health check
export const getHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/api/health')
  return response.data
}

// Dashboard metrics
export const getDashboard = async (): Promise<DashboardMetrics> => {
  const response = await apiClient.get<DashboardMetrics>('/api/dashboard')
  return response.data
}

// Revenue data
export interface RevenueParams {
  start_date?: string
  end_date?: string
  grouping?: 'day' | 'week' | 'month'
  limit?: number
}

export const getRevenue = async (params?: RevenueParams): Promise<RevenueDataPoint[]> => {
  const response = await apiClient.get<RevenueDataPoint[]>('/api/revenue', { params })
  return response.data
}

// Customers
export interface CustomerParams {
  limit?: number
  offset?: number
  sort?: 'total_spent' | 'transaction_count'
  order?: 'asc' | 'desc'
}

export const getCustomers = async (params?: CustomerParams): Promise<Customer[]> => {
  const response = await apiClient.get<Customer[]>('/api/customers', { params })
  return response.data
}

// Products
export interface ProductParams {
  limit?: number
  offset?: number
  sort?: 'total_revenue' | 'units_sold'
  order?: 'asc' | 'desc'
}

export const getProducts = async (params?: ProductParams): Promise<Product[]> => {
  const response = await apiClient.get<Product[]>('/api/products', { params })
  return response.data
}
