"""
Pydantic models for MarketPulse API responses.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


# =============================================================================
# Health Check Models
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="API status: healthy, degraded, or unhealthy")
    timestamp: datetime = Field(..., description="Response timestamp")
    database: str = Field(..., description="Database connection status")
    version: str = Field(..., description="API version")


# =============================================================================
# Dashboard Models
# =============================================================================

class TopProductItem(BaseModel):
    """Top product item"""
    product_name: str
    total_revenue: float
    total_transactions: int


class RecentTrendItem(BaseModel):
    """Recent trend item"""
    date: str
    revenue: float
    transactions: int


class DashboardResponse(BaseModel):
    """Dashboard overview response"""
    total_revenue: float
    total_transactions: int
    average_order_value: float
    top_products: List[TopProductItem]
    recent_trends: List[RecentTrendItem]


# =============================================================================
# Revenue Models
# =============================================================================

class RevenueDayItem(BaseModel):
    """Revenue by day item"""
    date: str
    revenue: float
    transactions: int


class RevenueResponse(BaseModel):
    """Revenue analytics response"""
    total_revenue: float
    total_transactions: int
    average_order_value: float
    revenue_by_day: List[RevenueDayItem]


# =============================================================================
# Customer Models
# =============================================================================

class PaginationInfo(BaseModel):
    """Pagination information"""
    total: int
    page: int
    page_size: int
    total_pages: int


class CustomerItem(BaseModel):
    """Customer item"""
    customer_id: int
    email: str
    total_spent: float
    transaction_count: int
    average_order_value: float


class CustomersResponse(BaseModel):
    """Customer analytics response"""
    customers: List[CustomerItem]
    pagination: PaginationInfo


# =============================================================================
# Product Models
# =============================================================================

class ProductItem(BaseModel):
    """Product item"""
    product_id: int
    product_name: str
    total_revenue: float
    total_transactions: int
    average_price: float


class ProductsResponse(BaseModel):
    """Product analytics response"""
    products: List[ProductItem]
    pagination: PaginationInfo
