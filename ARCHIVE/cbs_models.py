"""
Pydantic models for CBS (Israeli Household Expenditure) API endpoints.

These models define Israeli-specific analytics including income quintile analysis,
geographic segmentation, and category performance based on CBS data structure.
"""

from decimal import Decimal
from typing import List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Quintile Analysis Models
# =============================================================================


class QuintileItem(BaseModel):
    """Income quintile analytics."""

    income_quintile: int = Field(
        ..., description="Quintile number (1=lowest, 5=highest)", ge=1, le=5
    )
    transaction_count: int = Field(..., description="Number of transactions", ge=0)
    total_spending: Decimal = Field(..., description="Total spending in quintile", ge=0)
    avg_transaction: Decimal = Field(..., description="Average transaction amount", ge=0)
    median_transaction: Decimal = Field(
        ..., description="Median transaction amount", ge=0
    )
    unique_customers: int = Field(..., description="Unique customers in quintile", ge=0)
    spending_share_pct: Decimal = Field(
        ..., description="Percentage of total spending", ge=0, le=100
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "income_quintile": 5,
                "transaction_count": 2046,
                "total_spending": 330531.30,
                "avg_transaction": 161.55,
                "median_transaction": 143.28,
                "unique_customers": 1543,
                "spending_share_pct": 28.26,
            }
        }
    )


class QuintileResponse(BaseModel):
    """Quintile analysis response."""

    quintiles: List[QuintileItem] = Field(..., description="Quintile data", max_length=5)
    key_insight: str = Field(..., description="Business insight summary")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quintiles": [
                    {
                        "income_quintile": 5,
                        "transaction_count": 2046,
                        "total_spending": 330531.30,
                        "avg_transaction": 161.55,
                        "median_transaction": 143.28,
                        "unique_customers": 1543,
                        "spending_share_pct": 28.26,
                    }
                ],
                "key_insight": "High-income households (Q5) spend 1.72x more per transaction than low-income (Q1)",
            }
        }
    )


# =============================================================================
# Category Analysis Models
# =============================================================================


class CategoryItem(BaseModel):
    """Category performance metrics."""

    category: str = Field(..., description="CBS category name", max_length=255)
    transaction_count: int = Field(..., description="Number of transactions", ge=0)
    total_revenue: Decimal = Field(..., description="Total revenue", ge=0)
    avg_transaction: Decimal = Field(..., description="Average transaction amount", ge=0)
    unique_customers: int = Field(..., description="Unique customers", ge=0)
    unique_products: int = Field(..., description="Unique products in category", ge=0)
    market_share_pct: Decimal = Field(
        ..., description="Market share percentage", ge=0, le=100
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "מזון ומשקאות",
                "transaction_count": 1390,
                "total_revenue": 219410.68,
                "avg_transaction": 157.85,
                "unique_customers": 876,
                "unique_products": 25,
                "market_share_pct": 17.2,
            }
        }
    )


class CategoryResponse(BaseModel):
    """Category performance response."""

    categories: List[CategoryItem] = Field(..., description="Category performance data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "categories": [
                    {
                        "category": "מזון ומשקאות",
                        "transaction_count": 1390,
                        "total_revenue": 219410.68,
                        "avg_transaction": 157.85,
                        "unique_customers": 876,
                        "unique_products": 25,
                        "market_share_pct": 17.2,
                    }
                ]
            }
        }
    )


# =============================================================================
# Geographic Analysis Models
# =============================================================================


class CityItem(BaseModel):
    """City performance metrics."""

    customer_city: str = Field(..., description="City name", max_length=255)
    transaction_count: int = Field(..., description="Number of transactions", ge=0)
    total_revenue: Decimal = Field(..., description="Total revenue", ge=0)
    avg_transaction: Decimal = Field(..., description="Average transaction amount", ge=0)
    unique_customers: int = Field(..., description="Unique customers", ge=0)
    market_share_pct: Decimal = Field(
        ..., description="Market share percentage", ge=0, le=100
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_city": "תל אביב",
                "transaction_count": 3211,
                "total_revenue": 378923.96,
                "avg_transaction": 128.46,
                "unique_customers": 2143,
                "market_share_pct": 32.4,
            }
        }
    )


class CityResponse(BaseModel):
    """City performance response."""

    cities: List[CityItem] = Field(..., description="City performance data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cities": [
                    {
                        "customer_city": "תל אביב",
                        "transaction_count": 3211,
                        "total_revenue": 378923.96,
                        "avg_transaction": 128.46,
                        "unique_customers": 2143,
                        "market_share_pct": 32.4,
                    }
                ]
            }
        }
    )


# =============================================================================
# Data Quality Models
# =============================================================================


class DataQualityResponse(BaseModel):
    """Data quality metrics response."""

    completeness: Decimal = Field(
        ..., description="Completeness score (0-100)", ge=0, le=100
    )
    uniqueness: Decimal = Field(..., description="Uniqueness score (0-100)", ge=0, le=100)
    validity: Decimal = Field(..., description="Validity score (0-100)", ge=0, le=100)
    overall: Decimal = Field(..., description="Overall quality score (0-100)", ge=0, le=100)
    assessment: str = Field(..., description="Quality assessment text")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "completeness": 100.00,
                "uniqueness": 100.00,
                "validity": 100.00,
                "overall": 100.00,
                "assessment": "EXCELLENT",
            }
        }
    )


# =============================================================================
# Business Insights Models
# =============================================================================


class BusinessInsightsResponse(BaseModel):
    """Complete business insights export."""

    metadata: Dict[str, Any] = Field(..., description="Metadata about insights")
    data_summary: Dict[str, Any] = Field(..., description="Overall data summary")
    income_quintile_analysis: Dict[str, Any] = Field(..., description="Quintile insights")
    top_categories: Dict[str, Decimal] = Field(..., description="Top categories by revenue")
    top_products: Dict[str, Decimal] = Field(..., description="Top products by revenue")
    top_cities: Dict[str, Any] = Field(..., description="Top cities with metrics")
    monthly_trend: Dict[int, Decimal] = Field(..., description="Monthly spending trends")
    seasonal_insights: Dict[str, Any] = Field(..., description="Seasonal patterns")
    pareto_analysis: Dict[str, Any] = Field(..., description="80/20 rule analysis")
    business_recommendations: List[str] = Field(
        ..., description="Strategic recommendations"
    )
    key_metrics: Dict[str, Any] = Field(..., description="Key business metrics")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "generated_at": "2024-11-20T12:00:00",
                    "data_source": "Israeli Central Bureau of Statistics",
                    "analysis_period": "2024",
                    "version": "1.0",
                },
                "data_summary": {
                    "total_transactions": 10000,
                    "total_volume": 1272842.90,
                    "average_transaction": 127.28,
                },
                "income_quintile_analysis": {
                    "quintile_5": {
                        "total_spending": 330531.30,
                        "avg_transaction": 161.55,
                        "percentage_of_total": 28.26,
                    }
                },
            }
        }
    )
