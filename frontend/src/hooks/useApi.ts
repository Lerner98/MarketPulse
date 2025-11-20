import useFetch from './useFetch'
import {
  getHealth,
  getDashboard,
  getRevenue,
  getCustomers,
  getProducts,
  type RevenueParams,
  type CustomerParams,
  type ProductParams,
} from '@/api/endpoints'
import type {
  HealthResponse,
  DashboardMetrics,
  RevenueDataPoint,
  Customer,
  Product,
} from '@/types'

// Health check hook
export const useHealth = () => {
  return useFetch<HealthResponse>(getHealth)
}

// Dashboard metrics hook
export const useDashboard = () => {
  return useFetch<DashboardMetrics>(getDashboard)
}

// Revenue data hook
export const useRevenue = (params?: RevenueParams) => {
  return useFetch<RevenueDataPoint[]>(
    () => getRevenue(params),
    [params]
  )
}

// Customers hook
export const useCustomers = (params?: CustomerParams) => {
  return useFetch<Customer[]>(
    () => getCustomers(params),
    [params]
  )
}

// Products hook
export const useProducts = (params?: ProductParams) => {
  return useFetch<Product[]>(
    () => getProducts(params),
    [params]
  )
}
