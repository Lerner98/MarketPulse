"""
Business Intelligence API - Corporate-Grade Metrics
Transforms CBS household data into actionable business insights

Key Metrics:
- Total Addressable Market (TAM)
- Customer Lifetime Value indicators (savings rate, disposable income)
- Market opportunity by category
- Demographic profiling for targeting
- Financial health indicators
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

class SegmentProfile(BaseModel):
    """Complete business profile for a demographic segment"""
    segment_value: str
    segment_name: str  # Translated name

    # Market Sizing
    total_households: int = Field(..., description="Total households in Israel")
    monthly_spending_per_hh: float = Field(..., description="Average monthly spending per household")
    annual_market_size_b: float = Field(..., description="Total addressable market in billions")
    market_share_pct: float = Field(..., description="% of total market")

    # Financial Health
    monthly_income: float
    monthly_spending: float
    savings_rate_pct: float = Field(..., description="(Income - Spending) / Income * 100")
    monthly_surplus_deficit: float = Field(..., description="Disposable income or deficit")
    financial_status: str = Field(..., description="Healthy Savings / Tight Budget / Deficit")

    # Demographics
    avg_age: float
    avg_household_size: float
    lifecycle_stage: str = Field(..., description="Young Families / Established / Retirees")

class CategoryOpportunity(BaseModel):
    """Market opportunity analysis for a spending category"""
    category_name: str
    annual_market_b: float = Field(..., description="Total annual market in billions")
    employee_spending: float
    self_employed_spending: float
    pensioner_spending: float
    employee_premium_ratio: float = Field(..., description="How much more employees spend vs pensioners")
    market_maturity: str = Field(..., description="Growth / Mature / Declining")

class BusinessIntelligenceResponse(BaseModel):
    """Complete business intelligence for a segment type"""
    segment_type: str
    total_market_b: float = Field(..., description="Combined market size across all segments")
    segment_profiles: List[SegmentProfile]
    top_opportunities: List[CategoryOpportunity]
    executive_summary: str = Field(..., description="1-paragraph business recommendation")

# =============================================================================
# Router
# =============================================================================

router = APIRouter(prefix="/api/v10/business-intelligence", tags=["Business Intelligence"])

# =============================================================================
# Helper Functions
# =============================================================================

def calculate_financial_status(savings_rate: float) -> str:
    """Determine financial health category"""
    if savings_rate > 5:
        return "חיסכון בריא (Healthy Savings)"
    elif savings_rate > 0:
        return "תקציב צמוד (Tight Budget)"
    elif savings_rate > -10:
        return "גירעון קל (Mild Deficit)"
    else:
        return "מצוקה כלכלית (Financial Stress)"

def determine_lifecycle(age: float, household_size: float) -> str:
    """Classify lifecycle stage for targeting"""
    if age < 35 and household_size > 2.5:
        return "משפחות צעירות (Young Families)"
    elif age < 50 and household_size > 3:
        return "משפחות מבוססות (Established Families)"
    elif age < 65:
        return "בוגרים (Empty Nesters)"
    else:
        return "פנסיונרים (Retirees)"

def assess_market_maturity(employee_ratio: float) -> str:
    """Assess if category is growing or mature"""
    if employee_ratio > 3:
        return "צמיחה (Growth - Employee Premium)"
    elif employee_ratio > 1.5:
        return "בשלה (Mature - Stable)"
    else:
        return "דועכת (Declining - Pensioner Shift)"

# =============================================================================
# Endpoints
# =============================================================================

@router.get(
    "/{segment_type}",
    response_model=BusinessIntelligenceResponse,
    summary="Get complete business intelligence for segment type",
    description="Returns TAM, customer profiles, market opportunities, and executive summary"
)
def get_business_intelligence(segment_type: str):
    """
    Corporate-grade business intelligence combining:
    - Market sizing (TAM)
    - Customer profiling (demographics, financial health)
    - Category opportunities (where to compete)
    - Strategic recommendations
    """
    try:
        with engine.connect() as conn:
            # Get comprehensive segment profiles
            segment_data = conn.execute(text("""
                SELECT
                    s.segment_value,
                    MAX(CASE WHEN f.item_name = 'Consumption expenditures - total' THEN f.expenditure_value END) as spending,
                    MAX(CASE WHEN f.is_income_metric = TRUE THEN f.expenditure_value END) as income,
                    MAX(CASE WHEN f.item_name LIKE '%Households in population%' THEN f.expenditure_value END) as households_k,
                    MAX(CASE WHEN f.item_name LIKE '%Average persons in household%' THEN f.expenditure_value END) as avg_persons,
                    MAX(CASE WHEN f.item_name = 'Average age of economic head of household' THEN f.expenditure_value END) as avg_age
                FROM fact_segment_expenditure f
                JOIN dim_segment s ON f.segment_key = s.segment_key
                WHERE s.segment_type = :segment_type
                GROUP BY s.segment_value, s.segment_order
                ORDER BY s.segment_order
            """), {"segment_type": segment_type}).fetchall()

            if not segment_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No data found for segment type '{segment_type}'"
                )

            # Calculate total market
            total_market = sum(
                float(row[1] or 0) * float(row[3] or 0) * 1000 * 12
                for row in segment_data
            ) / 1e9

            # Build segment profiles
            profiles = []
            segment_translations = {
                '1,176': 'פנסיונרים',
                '3,713': 'שכירים',
                '589': 'עצמאיים'
            }

            for row in segment_data:
                spending = float(row[1] or 0)
                income = float(row[2] or 0)
                households = float(row[3] or 0) * 1000 if row[3] else 0

                annual_market = spending * households * 12 / 1e9
                savings_rate = ((income - spending) / income * 100) if income > 0 else 0

                profiles.append(SegmentProfile(
                    segment_value=row[0],
                    segment_name=segment_translations.get(row[0], row[0]),
                    total_households=int(households),
                    monthly_spending_per_hh=spending,
                    annual_market_size_b=round(annual_market, 2),
                    market_share_pct=round(annual_market / total_market * 100, 1) if total_market > 0 else 0,
                    monthly_income=income,
                    monthly_spending=spending,
                    savings_rate_pct=round(savings_rate, 1),
                    monthly_surplus_deficit=round(income - spending, 0),
                    financial_status=calculate_financial_status(savings_rate),
                    avg_age=float(row[5] or 0),
                    avg_household_size=float(row[4] or 0),
                    lifecycle_stage=determine_lifecycle(float(row[5] or 0), float(row[4] or 0))
                ))

            # Get top category opportunities
            opportunities_data = conn.execute(text("""
                WITH category_spending AS (
                    SELECT
                        f.item_name,
                        MAX(CASE WHEN s.segment_value = '3,713' THEN f.expenditure_value END) as employees,
                        MAX(CASE WHEN s.segment_value = '3,713' THEN
                            (SELECT f2.expenditure_value FROM fact_segment_expenditure f2
                             JOIN dim_segment s2 ON f2.segment_key = s2.segment_key
                             WHERE s2.segment_value = '3,713' AND f2.item_name LIKE '%Households in population%' LIMIT 1)
                        END) as emp_households,
                        MAX(CASE WHEN s.segment_value = '589' THEN f.expenditure_value END) as self_emp,
                        MAX(CASE WHEN s.segment_value = '1,176' THEN f.expenditure_value END) as pensioners
                    FROM fact_segment_expenditure f
                    JOIN dim_segment s ON f.segment_key = s.segment_key
                    WHERE s.segment_type = :segment_type
                      AND f.item_name NOT LIKE '%income%'
                      AND f.item_name NOT LIKE '%payment%'
                      AND f.item_name NOT LIKE '%tax%'
                      AND f.item_name NOT LIKE '%Average%'
                      AND f.item_name NOT LIKE '%Median%'
                      AND f.item_name NOT LIKE '%Households%'
                      AND f.item_name NOT LIKE 'From %'
                      AND f.item_name NOT LIKE '%total%'
                    GROUP BY f.item_name
                    HAVING MAX(CASE WHEN s.segment_value = '3,713' THEN f.expenditure_value END) > 500
                )
                SELECT * FROM category_spending
                ORDER BY employees DESC
                LIMIT 10
            """), {"segment_type": segment_type}).fetchall()

            opportunities = []
            for row in opportunities_data:
                emp_spending = float(row[1] or 0)
                emp_households = float(row[2] or 0) * 1000 if row[2] else 0
                annual_market = emp_spending * emp_households * 12 / 1e9

                pen_spending = float(row[4] or 0)
                premium_ratio = emp_spending / pen_spending if pen_spending > 0 else 0

                opportunities.append(CategoryOpportunity(
                    category_name=row[0],
                    annual_market_b=round(annual_market, 2),
                    employee_spending=emp_spending,
                    self_employed_spending=float(row[3] or 0),
                    pensioner_spending=pen_spending,
                    employee_premium_ratio=round(premium_ratio, 1),
                    market_maturity=assess_market_maturity(premium_ratio)
                ))

            # Generate executive summary
            largest_segment = max(profiles, key=lambda p: p.annual_market_size_b)
            healthiest_segment = max(profiles, key=lambda p: p.savings_rate_pct)
            top_category = opportunities[0] if opportunities else None

            executive_summary = (
                f"שוק ישראלי בהיקף ₪{total_market:.1f}B שנתי. "
                f"{largest_segment.segment_name} הם הסגמנט הגדול ביותר (₪{largest_segment.annual_market_size_b:.1f}B, "
                f"{largest_segment.market_share_pct:.0f}% מהשוק) עם שיעור חיסכון של {healthiest_segment.savings_rate_pct:.1f}%. "
            )

            if top_category:
                executive_summary += (
                    f"הזדמנות מובילה: {top_category.category_name} (₪{top_category.annual_market_b:.1f}B), "
                    f"עם פרמיה של {top_category.employee_premium_ratio:.1f}x לשכירים. "
                )

            executive_summary += "המלצה: התמקדות בשכירים למוצרי פרימיום, פנסיונרים למוצרי ערך."

            return BusinessIntelligenceResponse(
                segment_type=segment_type,
                total_market_b=round(total_market, 2),
                segment_profiles=profiles,
                top_opportunities=opportunities,
                executive_summary=executive_summary
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating business intelligence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate business intelligence: {str(e)}"
        )
