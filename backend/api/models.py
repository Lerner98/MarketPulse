"""
Pydantic models for API request/response validation.

These models define the structure and validation rules for all API endpoints,
ensuring type safety and automatic documentation in FastAPI.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Health Check Models
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status", examples=["healthy"])
    timestamp: datetime = Field(..., description="Current server timestamp")
    database: str = Field(..., description="Database connection status", examples=["connected"])
    version: str = Field(default="1.0.0", description="API version")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2025-11-20T12:00:00Z",
                "database": "connected",
                "version": "1.0.0"
            }
        }
    )


# =============================================================================
# Dashboard Models
# =============================================================================

class TopProductItem(BaseModel):
    """Individual product in top products list."""

    product: str = Field(..., description="Product name", examples=["מחשב נייד"])
    revenue: Decimal = Field(..., description="Total revenue for product", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product": "מחשב נייד",
                "revenue": 5234567.89
            }
        }
    )


class RecentTrendItem(BaseModel):
    """Daily revenue trend data point."""

    transaction_date: date = Field(..., description="Transaction date", alias="date")
    revenue: Decimal = Field(..., description="Total revenue for date", ge=0)
    transaction_count: int = Field(..., description="Number of transactions", ge=0)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "date": "2025-11-20",
                "revenue": 123456.78,
                "transaction_count": 87
            }
        }
    )


class DashboardResponse(BaseModel):
    """Aggregated dashboard metrics."""

    total_revenue: Decimal = Field(..., description="Total revenue across all transactions", ge=0)
    total_transactions: int = Field(..., description="Total transaction count", ge=0)
    avg_order_value: Decimal = Field(..., description="Average transaction amount", ge=0)
    completed_transactions: int = Field(..., description="Number of completed transactions", ge=0)
    pending_transactions: int = Field(..., description="Number of pending transactions", ge=0)
    cancelled_transactions: int = Field(..., description="Number of cancelled transactions", ge=0)
    top_products: List[TopProductItem] = Field(
        ...,
        description="Top 5 products by revenue",
        max_length=5
    )
    recent_trend: List[RecentTrendItem] = Field(
        ...,
        description="Last 7 days revenue trend",
        max_length=7
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_revenue": 15234567.89,
                "total_transactions": 10000,
                "avg_order_value": 1523.46,
                "completed_transactions": 3313,
                "pending_transactions": 3388,
                "cancelled_transactions": 3299,
                "top_products": [
                    {"product": "מחשב נייד", "revenue": 5234567.89},
                    {"product": "טלפון סלולרי", "revenue": 4123456.78}
                ],
                "recent_trend": [
                    {"date": "2025-11-20", "revenue": 123456.78, "transaction_count": 87}
                ]
            }
        }
    )


# =============================================================================
# Revenue Models
# =============================================================================

class RevenueDayItem(BaseModel):
    """Daily revenue aggregation."""

    transaction_date: date = Field(..., description="Transaction date", alias="date")
    total_revenue: Decimal = Field(..., description="Total revenue for date", ge=0)
    transaction_count: int = Field(..., description="Number of transactions", ge=0)
    avg_transaction_value: Decimal = Field(..., description="Average transaction value", ge=0)
    unique_customers: int = Field(..., description="Unique customers on this date", ge=0)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "transaction_date": "2025-11-20",
                "total_revenue": 123456.78,
                "transaction_count": 87,
                "avg_transaction_value": 1419.04,
                "unique_customers": 65
            }
        }
    )


class RevenueResponse(BaseModel):
    """Revenue analytics response."""

    data: List[RevenueDayItem] = Field(..., description="Daily revenue data")
    total_revenue: Decimal = Field(..., description="Sum of all revenue in period", ge=0)
    total_transactions: int = Field(..., description="Total transactions in period", ge=0)
    avg_daily_revenue: Decimal = Field(..., description="Average daily revenue", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "transaction_date": "2025-11-20",
                        "total_revenue": 123456.78,
                        "transaction_count": 87,
                        "avg_transaction_value": 1419.04,
                        "unique_customers": 65
                    }
                ],
                "total_revenue": 15234567.89,
                "total_transactions": 10000,
                "avg_daily_revenue": 41736.35
            }
        }
    )


# =============================================================================
# Customer Models
# =============================================================================

class CustomerItem(BaseModel):
    """Individual customer analytics."""

    customer_name: str = Field(..., description="Customer name", max_length=255)
    transaction_count: int = Field(..., description="Total transactions by customer", ge=0)
    total_spent: Decimal = Field(..., description="Total amount spent", ge=0)
    avg_transaction: Decimal = Field(..., description="Average transaction amount", ge=0)
    first_purchase: date = Field(..., description="Date of first purchase")
    last_purchase: date = Field(..., description="Date of most recent purchase")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_name": "אבי כהן",
                "transaction_count": 15,
                "total_spent": 12345.67,
                "avg_transaction": 823.04,
                "first_purchase": "2024-06-15",
                "last_purchase": "2025-11-18"
            }
        }
    )


class PaginationInfo(BaseModel):
    """Pagination metadata."""

    limit: int = Field(..., description="Number of results per page", ge=1, le=100)
    offset: int = Field(..., description="Number of results to skip", ge=0)
    total: int = Field(..., description="Total number of results available", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "limit": 10,
                "offset": 0,
                "total": 5432
            }
        }
    )


class CustomersResponse(BaseModel):
    """Customer analytics response with pagination."""

    customers: List[CustomerItem] = Field(..., description="Customer data")
    pagination: PaginationInfo = Field(..., description="Pagination information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customers": [
                    {
                        "customer_name": "אבי כהן",
                        "transaction_count": 15,
                        "total_spent": 12345.67,
                        "avg_transaction": 823.04,
                        "first_purchase": "2024-06-15",
                        "last_purchase": "2025-11-18"
                    }
                ],
                "pagination": {
                    "limit": 10,
                    "offset": 0,
                    "total": 5432
                }
            }
        }
    )


# =============================================================================
# Product Models
# =============================================================================

class ProductItem(BaseModel):
    """Individual product performance metrics."""

    product: str = Field(..., description="Product name", max_length=255)
    total_transactions: int = Field(..., description="Number of transactions", ge=0)
    total_revenue: Decimal = Field(..., description="Total revenue generated", ge=0)
    avg_price: Decimal = Field(..., description="Average price per transaction", ge=0)
    unique_customers: int = Field(..., description="Number of unique customers", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product": "מחשב נייד",
                "total_transactions": 2134,
                "total_revenue": 5234567.89,
                "avg_price": 2453.21,
                "unique_customers": 1876
            }
        }
    )


class ProductsResponse(BaseModel):
    """Product performance response."""

    products: List[ProductItem] = Field(..., description="Product performance data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "products": [
                    {
                        "product": "מחשב נייד",
                        "total_transactions": 2134,
                        "total_revenue": 5234567.89,
                        "avg_price": 2453.21,
                        "unique_customers": 1876
                    },
                    {
                        "product": "טלפון סלולרי",
                        "total_transactions": 1987,
                        "total_revenue": 4123456.78,
                        "avg_price": 2076.89,
                        "unique_customers": 1654
                    }
                ]
            }
        }
    )


# =============================================================================
# Error Models
# =============================================================================

class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Machine-readable error code", examples=["VALIDATION_ERROR"])
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {"field": "limit", "error": "Must be between 1 and 100"},
                "timestamp": "2025-11-20T12:00:00Z"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail = Field(..., description="Error information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": "2025-11-20T12:00:00Z"
                }
            }
        }
    )
