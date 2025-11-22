"""
PHASE 6: V10 Segmentation API Endpoints
Flexible endpoints for normalized star schema (dim_segment + fact_segment_expenditure)

Endpoints:
- GET /api/v10/segments/types - List all available segment types
- GET /api/v10/segments/{segment_type}/values - Get segment values for a type
- GET /api/v10/segmentation/{segment_type} - Get expenditure data by segment type
- GET /api/v10/inequality/{segment_type} - Get inequality analysis for a segment type
- GET /api/v10/burn-rate - Get burn rate analysis (Income Quintile only)
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text, create_engine
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in environment")

engine = create_engine(DATABASE_URL)
logger = logging.getLogger(__name__)

# =============================================================================
# Pydantic Models
# =============================================================================

class SegmentTypeItem(BaseModel):
    """Segment type information"""
    segment_type: str = Field(..., description="Type of demographic segmentation (e.g., 'Income Quintile', 'Age Group')")
    count: int = Field(..., description="Number of segments in this type")
    example_values: List[str] = Field(..., description="Sample segment values")

class SegmentTypeResponse(BaseModel):
    """Response for segment types endpoint"""
    total_types: int
    segment_types: List[SegmentTypeItem]

class SegmentValueItem(BaseModel):
    """Individual segment value"""
    segment_value: str
    segment_order: Optional[int]

class SegmentValuesResponse(BaseModel):
    """Response for segment values endpoint"""
    segment_type: str
    total_values: int
    values: List[SegmentValueItem]

class ExpenditureItem(BaseModel):
    """Individual expenditure record"""
    item_name: str
    segment_value: str
    expenditure_value: float

class SegmentationResponse(BaseModel):
    """Response for segmentation endpoint"""
    segment_type: str
    total_items: int
    total_records: int
    expenditures: List[ExpenditureItem]

class InequalityItem(BaseModel):
    """Inequality analysis item"""
    item_name: str
    high_segment: str
    high_spend: float
    low_segment: str
    low_spend: float
    inequality_ratio: float
    avg_spend: float

class InequalityResponse(BaseModel):
    """Response for inequality endpoint"""
    segment_type: str
    total_items: int
    top_inequality: List[InequalityItem]
    insight: str

class BurnRateItem(BaseModel):
    """Burn rate analysis item"""
    segment_value: str
    income: float
    spending: float
    burn_rate_pct: float
    surplus_deficit: float
    financial_status: str

class BurnRateResponse(BaseModel):
    """Response for burn rate endpoint"""
    total_segments: int
    burn_rates: List[BurnRateItem]
    insight: str

# =============================================================================
# Router
# =============================================================================

router = APIRouter(prefix="/api/v10", tags=["V10 Segmentation"])

# =============================================================================
# Endpoints
# =============================================================================

@router.get(
    "/segments/types",
    response_model=SegmentTypeResponse,
    summary="List all segment types",
    description="Get all available demographic segmentation types with actual expenditure data"
)
def get_segment_types():
    """
    List all available segment types with counts and examples.
    Only returns segment types that have actual expenditure data.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                WITH ranked_segments AS (
                    SELECT DISTINCT
                        s.segment_type,
                        s.segment_value,
                        s.segment_order,
                        ROW_NUMBER() OVER (PARTITION BY s.segment_type ORDER BY s.segment_order) as rn
                    FROM dim_segment s
                    INNER JOIN fact_segment_expenditure f ON s.segment_key = f.segment_key
                )
                SELECT
                    segment_type,
                    COUNT(*) as count,
                    ARRAY_AGG(segment_value) as examples
                FROM ranked_segments
                WHERE rn <= 3
                GROUP BY segment_type
                ORDER BY segment_type
            """)).fetchall()

            segment_types = [
                SegmentTypeItem(
                    segment_type=row[0],
                    count=row[1],
                    example_values=row[2] if row[2] else []
                )
                for row in result
            ]

            return SegmentTypeResponse(
                total_types=len(segment_types),
                segment_types=segment_types
            )

    except Exception as e:
        logger.error(f"Error fetching segment types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch segment types: {str(e)}"
        )


@router.get(
    "/segments/{segment_type}/values",
    response_model=SegmentValuesResponse,
    summary="Get segment values for a type",
    description="Get all segment values for a specific segment type (e.g., all quintiles for 'Income Quintile')"
)
def get_segment_values(segment_type: str):
    """
    Get all segment values for a specific segment type.

    Args:
        segment_type: The segment type (e.g., "Income Quintile", "Age Group")
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT segment_value, segment_order
                    FROM dim_segment
                    WHERE segment_type = :segment_type
                    ORDER BY segment_order
                """),
                {"segment_type": segment_type}
            ).fetchall()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Segment type '{segment_type}' not found"
                )

            values = [
                SegmentValueItem(
                    segment_value=row[0],
                    segment_order=row[1]
                )
                for row in result
            ]

            return SegmentValuesResponse(
                segment_type=segment_type,
                total_values=len(values),
                values=values
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching segment values: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch segment values: {str(e)}"
        )


@router.get(
    "/segmentation/{segment_type}",
    response_model=SegmentationResponse,
    summary="Get expenditure data by segment type",
    description="Get all expenditure records for a specific segment type with optional limit"
)
def get_segmentation_data(
    segment_type: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of expenditure records to return")
):
    """
    Get expenditure data for a specific segment type.

    Args:
        segment_type: The segment type (e.g., "Income Quintile", "Age Group")
        limit: Maximum number of expenditure records to return
    """
    try:
        with engine.connect() as conn:
            # Verify segment type exists
            type_check = conn.execute(
                text("SELECT COUNT(*) FROM dim_segment WHERE segment_type = :segment_type"),
                {"segment_type": segment_type}
            ).scalar()

            if type_check == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Segment type '{segment_type}' not found"
                )

            # Get expenditure data
            result = conn.execute(
                text("""
                    SELECT
                        f.item_name,
                        s.segment_value,
                        f.expenditure_value
                    FROM fact_segment_expenditure f
                    JOIN dim_segment s ON f.segment_key = s.segment_key
                    WHERE s.segment_type = :segment_type
                    ORDER BY f.item_name, s.segment_order
                    LIMIT :limit
                """),
                {"segment_type": segment_type, "limit": limit}
            ).fetchall()

            expenditures = [
                ExpenditureItem(
                    item_name=row[0],
                    segment_value=row[1],
                    expenditure_value=float(row[2])
                )
                for row in result
            ]

            # Count distinct items
            distinct_items = conn.execute(
                text("""
                    SELECT COUNT(DISTINCT f.item_name)
                    FROM fact_segment_expenditure f
                    JOIN dim_segment s ON f.segment_key = s.segment_key
                    WHERE s.segment_type = :segment_type
                """),
                {"segment_type": segment_type}
            ).scalar()

            return SegmentationResponse(
                segment_type=segment_type,
                total_items=distinct_items,
                total_records=len(expenditures),
                expenditures=expenditures
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching segmentation data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch segmentation data: {str(e)}"
        )


@router.get(
    "/inequality/{segment_type}",
    response_model=InequalityResponse,
    summary="Get inequality analysis",
    description="Get inequality gap analysis for a specific segment type (spending disparity between highest and lowest segments)"
)
def get_inequality_analysis(
    segment_type: str,
    limit: int = Query(10, ge=1, le=100, description="Number of top inequality items to return")
):
    """
    Get inequality analysis showing spending gaps between segments.

    Args:
        segment_type: The segment type (e.g., "Income Quintile", "Age Group")
        limit: Number of top inequality items to return
    """
    try:
        with engine.connect() as conn:
            # Verify segment type exists
            type_check = conn.execute(
                text("SELECT COUNT(*) FROM dim_segment WHERE segment_type = :segment_type"),
                {"segment_type": segment_type}
            ).scalar()

            if type_check == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Segment type '{segment_type}' not found"
                )

            # Get inequality data from materialized view
            result = conn.execute(
                text("""
                    SELECT
                        item_name,
                        high_segment,
                        high_spend,
                        low_segment,
                        low_spend,
                        inequality_ratio,
                        avg_spend
                    FROM vw_segment_inequality
                    WHERE segment_type = :segment_type
                    ORDER BY inequality_ratio DESC
                    LIMIT :limit
                """),
                {"segment_type": segment_type, "limit": limit}
            ).fetchall()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No inequality data found for segment type '{segment_type}'"
                )

            inequality_items = [
                InequalityItem(
                    item_name=row[0],
                    high_segment=row[1],
                    high_spend=float(row[2]),
                    low_segment=row[3],
                    low_spend=float(row[4]),
                    inequality_ratio=float(row[5]),
                    avg_spend=float(row[6])
                )
                for row in result
            ]

            # Generate insight
            top_item = inequality_items[0]
            insight = (
                f"The highest inequality is in '{top_item.item_name}' where "
                f"{top_item.high_segment} spends {top_item.inequality_ratio:.1f}x more than "
                f"{top_item.low_segment} (₪{top_item.high_spend:.2f} vs ₪{top_item.low_spend:.2f})"
            )

            return InequalityResponse(
                segment_type=segment_type,
                total_items=len(inequality_items),
                top_inequality=inequality_items,
                insight=insight
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inequality analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch inequality analysis: {str(e)}"
        )


@router.get(
    "/burn-rate",
    response_model=BurnRateResponse,
    summary="Get burn rate analysis",
    description="Get financial pressure analysis (spending as % of income) for any segment type"
)
def get_burn_rate_analysis(
    segment_type: str = Query("Income Quintile", description="Segment type to analyze (e.g., 'Income Quintile', 'Geographic Region', 'Work Status')")
):
    """
    Get burn rate analysis showing financial pressure for each segment.

    Burn rate = (Spending / Income) × 100%
    - > 100%: Financial pressure (deficit)
    - 90-100%: Break-even
    - 75-90%: Low savings
    - < 75%: Healthy savings
    """
    try:
        with engine.connect() as conn:
            # Get burn rate data from materialized view - FILTERED by segment_type
            result = conn.execute(text("""
                SELECT
                    segment_value,
                    income,
                    spending,
                    burn_rate_pct,
                    surplus_deficit,
                    financial_status
                FROM vw_segment_burn_rate
                WHERE segment_type = :segment_type
                ORDER BY burn_rate_pct DESC
            """), {"segment_type": segment_type}).fetchall()

            if not result:
                # If view is empty, return empty result with helpful message
                return BurnRateResponse(
                    total_segments=0,
                    burn_rates=[],
                    insight="No burn rate data available. Ensure income and consumption expenditure data is loaded."
                )

            burn_rate_items = [
                BurnRateItem(
                    segment_value=row[0],
                    income=float(row[1]),
                    spending=float(row[2]),
                    burn_rate_pct=float(row[3]),
                    surplus_deficit=float(row[4]),
                    financial_status=row[5]
                )
                for row in result
            ]

            # Generate insight
            highest = burn_rate_items[0]
            lowest = burn_rate_items[-1]
            insight = (
                f"Financial pressure: {highest.segment_value} has {highest.burn_rate_pct:.1f}% burn rate "
                f"({highest.financial_status}), while {lowest.segment_value} has {lowest.burn_rate_pct:.1f}% "
                f"({lowest.financial_status})"
            )

            return BurnRateResponse(
                total_segments=len(burn_rate_items),
                burn_rates=burn_rate_items,
                insight=insight
            )

    except Exception as e:
        logger.error(f"Error fetching burn rate analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch burn rate analysis: {str(e)}"
        )
