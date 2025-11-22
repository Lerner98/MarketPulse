"""
CBS-specific API endpoints for Israeli Household Expenditure Analytics.

These endpoints serve insights from the EDA analysis including:
- Income quintile analysis
- Category performance
- Geographic (city) analysis
- Data quality metrics
- Business insights export
"""

import json
import logging
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.cbs_models import (
    QuintileResponse,
    QuintileItem,
    CategoryResponse,
    CategoryItem,
    CityResponse,
    CityItem,
    DataQualityResponse,
    BusinessInsightsResponse,
)


# Dependency injection function
def get_db_session():
    """Get database session for dependency injection."""
    from models.database import DatabaseManager

    db_manager = DatabaseManager()
    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/cbs", tags=["CBS Analytics"])


# =============================================================================
# Income Quintile Analysis
# =============================================================================


@router.get(
    "/quintiles",
    response_model=QuintileResponse,
    summary="Get income quintile analysis",
    description="Israeli household spending patterns by income quintile (Q1-Q5)",
)
def get_quintile_analysis(db: Session = Depends(get_db_session)) -> QuintileResponse:
    """
    Income quintile analysis using mv_quintile_analysis materialized view.

    Returns spending patterns across 5 income quintiles:
    - Q1: Lowest 20% of income households
    - Q2-Q4: Middle income groups
    - Q5: Highest 20% of income households

    Includes transaction counts, spending totals, averages, and market share.
    """
    try:
        query = text(
            """
            SELECT
                income_quintile,
                transaction_count,
                total_spending,
                avg_transaction,
                median_transaction,
                unique_customers,
                spending_share_pct
            FROM mv_quintile_analysis
            ORDER BY income_quintile
        """
        )

        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No quintile data available",
            )

        quintiles = [
            QuintileItem(
                income_quintile=row.income_quintile,
                transaction_count=row.transaction_count,
                total_spending=Decimal(str(row.total_spending)),
                avg_transaction=Decimal(str(row.avg_transaction)),
                median_transaction=Decimal(str(row.median_transaction)),
                unique_customers=row.unique_customers,
                spending_share_pct=Decimal(str(row.spending_share_pct)),
            )
            for row in results
        ]

        # Calculate key insight (Q5 vs Q1 ratio)
        q5_avg = quintiles[4].avg_transaction
        q1_avg = quintiles[0].avg_transaction
        ratio = q5_avg / q1_avg

        key_insight = (
            f"High-income households (Q5) spend {ratio:.2f}x more per "
            f"transaction than low-income (Q1). Q5 accounts for "
            f"{quintiles[4].spending_share_pct:.1f}% of total spending."
        )

        return QuintileResponse(quintiles=quintiles, key_insight=key_insight)

    except SQLAlchemyError as e:
        logger.error(f"Quintile query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quintile data",
        )


# =============================================================================
# Category Performance
# =============================================================================


@router.get(
    "/categories",
    response_model=CategoryResponse,
    summary="Get category performance",
    description="Israeli household spending by CBS product categories",
)
def get_category_performance(db: Session = Depends(get_db_session)) -> CategoryResponse:
    """
    Category performance using mv_category_performance materialized view.

    Returns metrics for all CBS categories including:
    - מזון ומשקאות (Food & Beverages)
    - דיור (Housing)
    - תחבורה ותקשורת (Transportation & Communication)
    - And other official CBS categories

    Sorted by total revenue descending.
    """
    try:
        query = text(
            """
            SELECT
                category,
                transaction_count,
                total_revenue,
                avg_transaction,
                unique_customers,
                unique_products,
                market_share_pct
            FROM mv_category_performance
            ORDER BY total_revenue DESC
        """
        )

        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No category data available",
            )

        categories = [
            CategoryItem(
                category=row.category,
                transaction_count=row.transaction_count,
                total_revenue=Decimal(str(row.total_revenue)),
                avg_transaction=Decimal(str(row.avg_transaction)),
                unique_customers=row.unique_customers,
                unique_products=row.unique_products,
                market_share_pct=Decimal(str(row.market_share_pct)),
            )
            for row in results
        ]

        return CategoryResponse(categories=categories)

    except SQLAlchemyError as e:
        logger.error(f"Category query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category data",
        )


# =============================================================================
# Geographic (City) Analysis
# =============================================================================


@router.get(
    "/cities",
    response_model=CityResponse,
    summary="Get city performance",
    description="Israeli household spending by geographic location (cities)",
)
def get_city_performance(db: Session = Depends(get_db_session)) -> CityResponse:
    """
    City performance using mv_city_performance materialized view.

    Returns metrics for all Israeli cities in the dataset:
    - תל אביב (Tel Aviv)
    - ירושלים (Jerusalem)
    - חיפה (Haifa)
    - And other major Israeli cities

    Sorted by total revenue descending.
    """
    try:
        query = text(
            """
            SELECT
                customer_city,
                transaction_count,
                total_revenue,
                avg_transaction,
                unique_customers,
                market_share_pct
            FROM mv_city_performance
            ORDER BY total_revenue DESC
        """
        )

        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No city data available",
            )

        cities = [
            CityItem(
                customer_city=row.customer_city,
                transaction_count=row.transaction_count,
                total_revenue=Decimal(str(row.total_revenue)),
                avg_transaction=Decimal(str(row.avg_transaction)),
                unique_customers=row.unique_customers,
                market_share_pct=Decimal(str(row.market_share_pct)),
            )
            for row in results
        ]

        return CityResponse(cities=cities)

    except SQLAlchemyError as e:
        logger.error(f"City query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve city data",
        )


# =============================================================================
# Data Quality Metrics
# =============================================================================


@router.get(
    "/data-quality",
    response_model=DataQualityResponse,
    summary="Get data quality metrics",
    description="CBS data quality scores (completeness, uniqueness, validity)",
)
def get_data_quality(db: Session = Depends(get_db_session)) -> DataQualityResponse:
    """
    Data quality metrics using calculate_data_quality() function.

    Returns:
    - Completeness: % of records with all required fields
    - Uniqueness: % of records with unique transaction IDs
    - Validity: % of records within expected ranges
    - Overall: Weighted average score

    Quality assessment:
    - 95-100: EXCELLENT
    - 85-94: GOOD
    - 70-84: ACCEPTABLE
    - <70: POOR
    """
    try:
        query = text("SELECT * FROM calculate_data_quality()")
        result = db.execute(query).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate data quality",
            )

        completeness, uniqueness, validity, overall = result

        # Determine assessment
        if overall >= 95:
            assessment = "EXCELLENT"
        elif overall >= 85:
            assessment = "GOOD"
        elif overall >= 70:
            assessment = "ACCEPTABLE"
        else:
            assessment = "POOR"

        return DataQualityResponse(
            completeness=Decimal(str(completeness)),
            uniqueness=Decimal(str(uniqueness)),
            validity=Decimal(str(validity)),
            overall=Decimal(str(overall)),
            assessment=assessment,
        )

    except SQLAlchemyError as e:
        logger.error(f"Data quality query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve data quality metrics",
        )


# =============================================================================
# Business Insights Export
# =============================================================================


@router.get(
    "/insights",
    response_model=BusinessInsightsResponse,
    summary="Get complete business insights",
    description="Complete CBS analysis export including all EDA insights",
)
def get_business_insights() -> BusinessInsightsResponse:
    """
    Complete business insights from EDA analysis.

    Returns the full business_insights.json export including:
    - Metadata and data summary
    - Income quintile analysis (Q1-Q5)
    - Top categories, products, and cities
    - Monthly and seasonal trends
    - Pareto analysis (80/20 rule)
    - Strategic business recommendations
    - Key market metrics

    This endpoint serves pre-computed insights from the EDA phase.
    """
    try:
        # Load business_insights.json
        project_root = Path(__file__).parent.parent.parent
        insights_file = project_root / "data" / "processed" / "business_insights.json"

        if not insights_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business insights file not found",
            )

        with open(insights_file, "r", encoding="utf-8") as f:
            insights_data = json.load(f)

        return BusinessInsightsResponse(**insights_data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse business insights JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid business insights data format",
        )
    except Exception as e:
        logger.error(f"Failed to load business insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load business insights",
        )
