"""
Strategic CBS Analysis Endpoints - V9 Production API

This module provides curated strategic business insights derived from Israeli CBS
Household Expenditure Survey data. Unlike the flexible V10 segmentation API, these
endpoints serve pre-calculated strategic analyses optimized for business decision-making.

**Architecture:**
- **Tables**: household_profiles, household_expenditures, retail_competition
- **Materialized Views**: vw_inequality_gap, vw_burn_rate, vw_fresh_food_battle
- **Focus**: Pre-calculated quintile-based analysis (Q1-Q5 income groups)
- **Performance**: < 200ms response times via materialized views

**Key Strategic Insights:**

1. **Inequality Gap Analysis** - The Spending Divide
   - Identifies categories with highest Q5/Q1 spending ratios
   - Reveals luxury vs necessity goods
   - Business value: Product positioning, market segmentation

2. **Burn Rate Analysis** - Financial Pressure Indicator
   - Measures (Spending / Income) × 100% for each quintile
   - Identifies segments under financial stress
   - Business value: Credit risk, price sensitivity, target marketing

3. **Fresh Food Battle** - Traditional Retail vs Supermarket Competition
   - Compares traditional retail (markets, butchers) vs supermarket chains
   - Shows which categories favor which retail channel
   - Business value: Retail strategy, supply chain optimization

4. **Full Retail Competition** - 8 CBS Store Types
   - Complete breakdown across all store types
   - Business value: Channel strategy, competitive analysis

5. **Household Demographics** - Quintile Profiles
   - Demographics (age, education, income, household size) by quintile
   - Business value: Customer profiling, segmentation strategy

6. **Complete Expenditure Breakdown** - 500+ Categories
   - All spending categories with inequality indices
   - Business value: Category management, trend analysis

**Data Source:**
Israeli Central Bureau of Statistics (CBS) - Household Expenditure Survey 2022
- 500+ expenditure categories
- 5 income quintiles (Q1-Q5)
- 13 food categories for retail analysis
- Monthly spending data in ₪ (Israeli Shekels)

**Use Cases:**
- **Executive Dashboards**: High-level strategic KPIs
- **Market Research**: Competitive landscape analysis
- **Product Strategy**: Category performance and positioning
- **Economic Analysis**: Wealth inequality and consumer behavior

**Integration Notes:**
- All endpoints use dependency injection for database sessions
- Comprehensive error handling with HTTPException
- Auto-generated business insights for each endpoint
- OpenAPI documentation available at /docs
"""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/strategic", tags=["Strategic Insights V9"])


# =============================================================================
# Dependency Injection
# =============================================================================

def get_db_session():
    """Get database session"""
    from models.database import DatabaseManager

    db_manager = DatabaseManager()
    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()


# =============================================================================
# Pydantic Models
# =============================================================================

class InequalityGapItem(BaseModel):
    """Single spending category with inequality metrics"""
    item_name: str
    rich_spend: float = Field(..., description="Q5 (richest 20%) spending")
    poor_spend: float = Field(..., description="Q1 (poorest 20%) spending")
    gap_ratio: float = Field(..., description="Q5/Q1 spending ratio")
    total_spend: float


class InequalityGapResponse(BaseModel):
    """Inequality Gap Analysis - The Spending Divide"""
    top_gaps: List[InequalityGapItem] = Field(..., description="Top 10 categories with highest inequality")
    insight: str = Field(..., description="Business insight about inequality")


class BurnRateResponse(BaseModel):
    """Burn Rate Analysis - Financial Pressure Indicator"""
    q5_burn_rate_pct: float = Field(..., description="Q5 burn rate (%)")
    q4_burn_rate_pct: float
    q3_burn_rate_pct: float
    q2_burn_rate_pct: float
    q1_burn_rate_pct: float = Field(..., description="Q1 burn rate (%)")
    total_burn_rate_pct: float
    insight: str = Field(..., description="Business insight about financial pressure")


class FreshFoodBattleItem(BaseModel):
    """Single category in fresh food battle"""
    category: str
    traditional_retail_pct: float = Field(..., description="Market + Grocery + Special Shop combined")
    supermarket_chain_pct: float
    traditional_advantage: float = Field(..., description="Advantage points for traditional retail")
    winner: str = Field(..., description="'Traditional Wins' or 'Supermarket Wins'")


class FreshFoodBattleResponse(BaseModel):
    """Fresh Food Battle - Traditional vs Supermarket Competition"""
    categories: List[FreshFoodBattleItem]
    insight: str = Field(..., description="Business insight about retail competition")


class RetailCompetitionItem(BaseModel):
    """Complete retail breakdown with 8 CBS store types"""
    category: str
    other_pct: float
    special_shop_pct: float
    butcher_pct: float
    veg_fruit_shop_pct: float
    online_supermarket_pct: float
    supermarket_chain_pct: float
    market_pct: float
    grocery_pct: float
    total_pct: float


class RetailCompetitionResponse(BaseModel):
    """Complete Retail Competition Data - 8 CBS Store Types"""
    categories: List[RetailCompetitionItem]
    insight: str


class HouseholdProfileItem(BaseModel):
    """Single demographic metric"""
    metric_name: str
    q5_val: float
    q4_val: float
    q3_val: float
    q2_val: float
    q1_val: float
    total_val: float


class HouseholdProfilesResponse(BaseModel):
    """Household Demographics by Quintile"""
    profiles: List[HouseholdProfileItem]
    insight: str


class ExpenditureItem(BaseModel):
    """Single expenditure category"""
    item_name: str
    q5_spend: float
    q4_spend: float
    q3_spend: float
    q2_spend: float
    q1_spend: float
    total_spend: float
    inequality_index: float


class ExpendituresResponse(BaseModel):
    """All Household Expenditures by Quintile"""
    expenditures: List[ExpenditureItem]
    total_categories: int
    insight: str


# =============================================================================
# Endpoint 1: Inequality Gap
# =============================================================================

@router.get(
    "/inequality-gap",
    response_model=InequalityGapResponse,
    summary="Inequality Gap Analysis - The Spending Divide",
    description="Shows which categories have the biggest spending gap between rich (Q5) and poor (Q1)"
)
def get_inequality_gap(db: Session = Depends(get_db_session)) -> InequalityGapResponse:
    """
    Top 10 categories with highest Q5/Q1 spending ratio.
    Uses materialized view vw_inequality_gap.
    """
    try:
        query = text("""
            SELECT item_name, rich_spend, poor_spend, gap_ratio, total_spend
            FROM vw_inequality_gap
            LIMIT 10;
        """)
        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inequality gap data not found. Run load_v9_production.py first."
            )

        items = [
            InequalityGapItem(
                item_name=row.item_name,
                rich_spend=float(row.rich_spend),
                poor_spend=float(row.poor_spend),
                gap_ratio=float(row.gap_ratio),
                total_spend=float(row.total_spend)
            )
            for row in results
        ]

        top_item = items[0]
        insight = (
            f"Highest inequality: {top_item.item_name} - "
            f"Q5 spends {top_item.gap_ratio:.1f}x more than Q1 "
            f"({top_item.rich_spend:.0f} NIS vs {top_item.poor_spend:.0f} NIS). "
            f"Premium products create massive wealth gaps."
        )

        return InequalityGapResponse(
            top_gaps=items,
            insight=insight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inequality gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch inequality gap: {str(e)}"
        )


# =============================================================================
# Endpoint 2: Burn Rate
# =============================================================================

@router.get(
    "/burn-rate",
    response_model=BurnRateResponse,
    summary="Burn Rate Analysis - Financial Pressure",
    description="Shows what % of income is consumed by spending (financial pressure indicator)"
)
def get_burn_rate(db: Session = Depends(get_db_session)) -> BurnRateResponse:
    """
    Burn rate = (Spending / Income) * 100
    Uses materialized view vw_burn_rate.
    """
    try:
        query = text("""
            SELECT q5_burn_rate_pct, q4_burn_rate_pct, q3_burn_rate_pct,
                   q2_burn_rate_pct, q1_burn_rate_pct, total_burn_rate_pct
            FROM vw_burn_rate;
        """)
        result = db.execute(query).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Burn rate data not found. Run load_v9_production.py first."
            )

        q1_burn = float(result.q1_burn_rate_pct)
        q5_burn = float(result.q5_burn_rate_pct)

        if q1_burn > 100:
            financial_status = "CRISIS - Q1 spends MORE than income (debt spiral)"
        elif q1_burn > 90:
            financial_status = "CRITICAL PRESSURE - Q1 spends 90%+ of income"
        else:
            financial_status = f"High inequality - Q1 burn rate {q1_burn:.1f}% vs Q5 {q5_burn:.1f}%"

        insight = (
            f"Financial pressure analysis: Q1 (poorest) burn rate = {q1_burn:.1f}%, "
            f"Q5 (richest) burn rate = {q5_burn:.1f}%. "
            f"{financial_status}"
        )

        return BurnRateResponse(
            q5_burn_rate_pct=q5_burn,
            q4_burn_rate_pct=float(result.q4_burn_rate_pct),
            q3_burn_rate_pct=float(result.q3_burn_rate_pct),
            q2_burn_rate_pct=float(result.q2_burn_rate_pct),
            q1_burn_rate_pct=q1_burn,
            total_burn_rate_pct=float(result.total_burn_rate_pct),
            insight=insight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching burn rate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch burn rate: {str(e)}"
        )


# =============================================================================
# Endpoint 3: Fresh Food Battle
# =============================================================================

@router.get(
    "/fresh-food-battle",
    response_model=FreshFoodBattleResponse,
    summary="Fresh Food Battle - Traditional vs Supermarket",
    description="Categories where traditional retail (markets/grocery) beats supermarket chains"
)
def get_fresh_food_battle(db: Session = Depends(get_db_session)) -> FreshFoodBattleResponse:
    """
    Traditional retail = Market + Grocery + Special Shop
    Uses materialized view vw_fresh_food_battle.
    """
    try:
        query = text("""
            SELECT category, traditional_retail_pct, supermarket_chain_pct,
                   traditional_advantage, winner
            FROM vw_fresh_food_battle
            ORDER BY traditional_retail_pct DESC;
        """)
        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fresh food battle data not found. Run load_v9_production.py first."
            )

        items = [
            FreshFoodBattleItem(
                category=row.category,
                traditional_retail_pct=float(row.traditional_retail_pct),
                supermarket_chain_pct=float(row.supermarket_chain_pct),
                traditional_advantage=float(row.traditional_advantage),
                winner=row.winner
            )
            for row in results
        ]

        traditional_wins = [item for item in items if item.winner == 'Traditional Wins']
        supermarket_wins = [item for item in items if item.winner == 'Supermarket Wins']

        insight = (
            f"Retail battle: Traditional retail wins {len(traditional_wins)} categories, "
            f"supermarket chains win {len(supermarket_wins)}. "
            f"Fresh food favors traditional (markets/butchers), packaged goods favor supermarkets."
        )

        return FreshFoodBattleResponse(
            categories=items,
            insight=insight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fresh food battle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fresh food battle: {str(e)}"
        )


# =============================================================================
# Endpoint 4: Full Retail Competition (8 Store Types)
# =============================================================================

@router.get(
    "/retail-competition",
    response_model=RetailCompetitionResponse,
    summary="Complete Retail Competition - 8 CBS Store Types",
    description="Full breakdown of food expenditure by all 8 CBS store types"
)
def get_retail_competition(db: Session = Depends(get_db_session)) -> RetailCompetitionResponse:
    """
    Get all retail competition data with 8 CBS store types.
    """
    try:
        query = text("""
            SELECT category, other_pct, special_shop_pct, butcher_pct, veg_fruit_shop_pct,
                   online_supermarket_pct, supermarket_chain_pct, market_pct, grocery_pct, total_pct
            FROM retail_competition
            ORDER BY supermarket_chain_pct DESC;
        """)
        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retail competition data not found. Run load_v9_production.py first."
            )

        items = [
            RetailCompetitionItem(
                category=row.category,
                other_pct=float(row.other_pct),
                special_shop_pct=float(row.special_shop_pct),
                butcher_pct=float(row.butcher_pct),
                veg_fruit_shop_pct=float(row.veg_fruit_shop_pct),
                online_supermarket_pct=float(row.online_supermarket_pct),
                supermarket_chain_pct=float(row.supermarket_chain_pct),
                market_pct=float(row.market_pct),
                grocery_pct=float(row.grocery_pct),
                total_pct=float(row.total_pct)
            )
            for row in results
        ]

        insight = f"Complete retail breakdown for {len(items)} food categories across 8 CBS store types."

        return RetailCompetitionResponse(
            categories=items,
            insight=insight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching retail competition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch retail competition: {str(e)}"
        )


# =============================================================================
# Endpoint 5: Household Profiles (Demographics)
# =============================================================================

@router.get(
    "/household-profiles",
    response_model=HouseholdProfilesResponse,
    summary="Household Demographics by Quintile",
    description="Demographics: household size, income, age, education by income quintile"
)
def get_household_profiles(db: Session = Depends(get_db_session)) -> HouseholdProfilesResponse:
    """
    Get all household demographic profiles.
    """
    try:
        query = text("""
            SELECT metric_name, q5_val, q4_val, q3_val, q2_val, q1_val, total_val
            FROM household_profiles
            ORDER BY metric_name;
        """)
        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Household profiles not found. Run load_v9_production.py first."
            )

        items = [
            HouseholdProfileItem(
                metric_name=row.metric_name,
                q5_val=float(row.q5_val),
                q4_val=float(row.q4_val),
                q3_val=float(row.q3_val),
                q2_val=float(row.q2_val),
                q1_val=float(row.q1_val),
                total_val=float(row.total_val)
            )
            for row in results
        ]

        insight = f"Complete demographic breakdown with {len(items)} metrics across 5 income quintiles."

        return HouseholdProfilesResponse(
            profiles=items,
            insight=insight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching household profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch household profiles: {str(e)}"
        )


# =============================================================================
# Endpoint 6: All Expenditures
# =============================================================================

@router.get(
    "/expenditures",
    response_model=ExpendituresResponse,
    summary="All Household Expenditures by Quintile",
    description="Complete spending breakdown for 500+ categories with inequality index"
)
def get_expenditures(
    db: Session = Depends(get_db_session),
    limit: int = 100
) -> ExpendituresResponse:
    """
    Get all household expenditures with optional limit.
    """
    try:
        query = text(f"""
            SELECT item_name, q5_spend, q4_spend, q3_spend, q2_spend, q1_spend,
                   total_spend, inequality_index
            FROM household_expenditures
            ORDER BY total_spend DESC
            LIMIT :limit;
        """)
        results = db.execute(query, {"limit": limit}).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expenditures not found. Run load_v9_production.py first."
            )

        items = [
            ExpenditureItem(
                item_name=row.item_name,
                q5_spend=float(row.q5_spend),
                q4_spend=float(row.q4_spend),
                q3_spend=float(row.q3_spend),
                q2_spend=float(row.q2_spend),
                q1_spend=float(row.q1_spend),
                total_spend=float(row.total_spend),
                inequality_index=float(row.inequality_index)
            )
            for row in results
        ]

        # Get total count
        count_query = text("SELECT COUNT(*) FROM household_expenditures;")
        total_count = db.execute(count_query).scalar()

        insight = f"Showing top {len(items)} of {total_count} expenditure categories by total spending."

        return ExpendituresResponse(
            expenditures=items,
            total_categories=total_count,
            insight=insight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching expenditures: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch expenditures: {str(e)}"
        )
