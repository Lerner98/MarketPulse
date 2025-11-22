// TypeScript interfaces matching backend data models

export interface DashboardMetrics {
  totalRevenue: number;
  transactionCount: number;
  averageOrderValue: number;
  topProduct: string;
}

export interface RevenueData {
  date: string;
  revenue: number;
  hebrewDate: string;
  dayName: string;
}

export interface CustomerData {
  id: string;
  name: string;
  totalSpent: number;
  transactionCount: number;
  lastPurchaseDate: string;
  city: string;
}

export interface ProductData {
  id: string;
  name: string;
  category: string;
  unitsSold: number;
  revenue: number;
  trend: 'up' | 'down' | 'stable';
}

export interface CategoryBreakdown {
  category: string;
  value: number;
  percentage: number;
}

export interface SankeyNode {
  name: string;
}

export interface SankeyLink {
  source: number;
  target: number;
  value: number;
}

export interface CustomerJourneyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

export interface ErrorState {
  message: string;
  retryFn?: () => void;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}
