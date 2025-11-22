"""
Strategic CBS Analysis Endpoints - PostgreSQL Version
Queries materialized views for fast response times
"""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/strategic", tags=["Strategic Insights"])


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

class QuintileGapItem(BaseModel):
    """Single category with quintile breakdown"""
    category: str
    quintile_1: float
    quintile_2: float
    quintile_3: float
    quintile_4: float
    quintile_5: float
    total_spending: float
    avg_spending: float


class QuintileGapResponse(BaseModel):
    """The 2.62x Rule - Income inequality analysis"""
    ratio: float = Field(..., description="Q5/Q1 spending ratio")
    q5_total: float = Field(..., description="Total Q5 spending")
    q1_total: float = Field(..., description="Total Q1 spending")
    insight: str = Field(..., description="Business insight text")
    categories: List[QuintileGapItem]


class DigitalMatrixItem(BaseModel):
    """Single category with purchase method breakdown"""
    category: str
    physical_pct: float
    online_israel_pct: float
    online_abroad_pct: float


class DigitalMatrixResponse(BaseModel):
    """Digital Opportunity Matrix"""
    top_israel_online: List[Dict[str, Any]]
    top_abroad_online: List[Dict[str, Any]]
    most_physical: List[Dict[str, Any]]
    categories: List[DigitalMatrixItem]


class RetailBattleItem(BaseModel):
    """Single food category with store type breakdown - 8 CBS store types"""
    category: str
    # Spending amounts (NIS per household per month)
    other: float
    special_shop: float  # Was wrongly called "local_market"
    butcher: float
    veg_fruit_shop: float
    online_supermarket: float
    supermarket_chain: float  # MAIN RETAIL CHANNEL
    market: float  # Outdoor markets
    grocery: float  # Corner stores
    total: float
    # Percentages
    other_pct: float
    special_shop_pct: float
    butcher_pct: float
    veg_fruit_shop_pct: float
    online_supermarket_pct: float
    supermarket_chain_pct: float
    market_pct: float
    grocery_pct: float


class RetailBattleResponse(BaseModel):
    """Retail Competition Analysis - 8 CBS store types"""
    supermarket_chain_share: float  # Main retail channel share
    market_share: float  # Outdoor markets share
    grocery_share: float  # Corner stores share
    special_shop_share: float  # Wine/specialty shops share
    supermarket_wins: List[Dict[str, Any]]  # Where supermarket chains dominate
    market_wins: List[Dict[str, Any]]  # Where outdoor markets win
    categories: List[RetailBattleItem]


# =============================================================================
# Endpoint 1: The 2.62x Rule (Quintile Gap)
# =============================================================================

@router.get(
    "/quintile-gap",
    response_model=QuintileGapResponse,
    summary="The 2.62x Rule - Income inequality in spending",
    description="High-income households (Q5) spend 2.62x more than low-income (Q1)"
)
def get_quintile_gap(db: Session = Depends(get_db_session)) -> QuintileGapResponse:
    """
    Analyze spending inequality across income quintiles.
    Uses materialized view vw_quintile_gap for fast queries.
    """
    try:
        # Get the ratio from materialized view
        gap_query = text("""
            SELECT q5_total, q1_total, spending_ratio
            FROM vw_quintile_gap
        """)
        gap_result = db.execute(gap_query).fetchone()

        if not gap_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quintile gap data not found. Run load_strategic_data.py first."
            )

        # Get all categories
        categories_query = text("""
            SELECT category, quintile_1, quintile_2, quintile_3, quintile_4, quintile_5,
                   total_spending, avg_spending
            FROM quintile_expenditure
            ORDER BY total_spending DESC
        """)
        categories_results = db.execute(categories_query).fetchall()

        categories = [
            QuintileGapItem(
                category=row.category,
                quintile_1=float(row.quintile_1),
                quintile_2=float(row.quintile_2),
                quintile_3=float(row.quintile_3),
                quintile_4=float(row.quintile_4),
                quintile_5=float(row.quintile_5),
                total_spending=float(row.total_spending),
                avg_spending=float(row.avg_spending)
            )
            for row in categories_results
        ]

        ratio = float(gap_result.spending_ratio)

        return QuintileGapResponse(
            ratio=ratio,
            q5_total=float(gap_result.q5_total),
            q1_total=float(gap_result.q1_total),
            insight=f"High-income households (Q5) spend {ratio}x more than low-income (Q1). Allocate 40% of marketing budget to Q4-Q5 for highest ROI.",
            categories=categories
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quintile gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch quintile gap data: {str(e)}"
        )


# =============================================================================
# Endpoint 2: Digital Opportunity Matrix
# =============================================================================

@router.get(
    "/digital-matrix",
    response_model=DigitalMatrixResponse,
    summary="Digital Opportunity Matrix - E-commerce vs Physical",
    description="Which products are bought online (Israel vs Abroad) vs physical stores"
)
def get_digital_matrix(db: Session = Depends(get_db_session)) -> DigitalMatrixResponse:
    """
    Analyze digital penetration across product categories.
    Uses materialized view vw_digital_matrix.
    """
    try:
        # Get all categories from materialized view
        query = text("""
            SELECT category, physical_pct, online_israel_pct, online_abroad_pct, total_online_pct
            FROM vw_digital_matrix
            ORDER BY online_israel_pct DESC
        """)
        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Digital matrix data not found. Run load_strategic_data.py first."
            )

        # Build response lists
        all_categories = []
        for row in results:
            all_categories.append(DigitalMatrixItem(
                category=row.category,
                physical_pct=float(row.physical_pct),
                online_israel_pct=float(row.online_israel_pct),
                online_abroad_pct=float(row.online_abroad_pct)
            ))

        # Top 5 for each dimension
        sorted_by_israel = sorted(all_categories, key=lambda x: x.online_israel_pct, reverse=True)[:5]
        sorted_by_abroad = sorted(all_categories, key=lambda x: x.online_abroad_pct, reverse=True)[:5]
        sorted_by_physical = sorted(all_categories, key=lambda x: x.physical_pct, reverse=True)[:5]

        top_israel = [{"category": c.category, "online_israel_pct": c.online_israel_pct} for c in sorted_by_israel]
        top_abroad = [{"category": c.category, "online_abroad_pct": c.online_abroad_pct} for c in sorted_by_abroad]
        most_physical = [{"category": c.category, "physical_pct": c.physical_pct} for c in sorted_by_physical]

        return DigitalMatrixResponse(
            top_israel_online=top_israel,
            top_abroad_online=top_abroad,
            most_physical=most_physical,
            categories=all_categories
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching digital matrix: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch digital matrix data: {str(e)}"
        )


# =============================================================================
# Endpoint 3: Retail Battle
# =============================================================================

@router.get(
    "/retail-battle",
    response_model=RetailBattleResponse,
    summary="Retail Battle - Store Competition Analysis (8 CBS store types)",
    description="Food expenditure breakdown by store type - Supermarket Chain vs Market vs Grocery etc."
)
def get_retail_battle(db: Session = Depends(get_db_session)) -> RetailBattleResponse:
    """
    Analyze retail competition for food categories.
    Uses Table 38 data with 8 real CBS store types.
    """
    try:
        # Get all categories with 8 store types
        query = text("""
            SELECT
                category,
                other, special_shop, butcher, veg_fruit_shop,
                online_supermarket, supermarket_chain, market, grocery, total,
                other_pct, special_shop_pct, butcher_pct, veg_fruit_shop_pct,
                online_supermarket_pct, supermarket_chain_pct, market_pct, grocery_pct
            FROM cbs_table_38_retail_battle
            ORDER BY supermarket_chain_pct DESC
        """)
        results = db.execute(query).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retail battle data not found. Run update_table_38_schema.py first."
            )

        # Build category list
        categories = []
        for row in results:
            categories.append(RetailBattleItem(
                category=row.category,
                other=float(row.other),
                special_shop=float(row.special_shop),
                butcher=float(row.butcher),
                veg_fruit_shop=float(row.veg_fruit_shop),
                online_supermarket=float(row.online_supermarket),
                supermarket_chain=float(row.supermarket_chain),
                market=float(row.market),
                grocery=float(row.grocery),
                total=float(row.total),
                other_pct=float(row.other_pct),
                special_shop_pct=float(row.special_shop_pct),
                butcher_pct=float(row.butcher_pct),
                veg_fruit_shop_pct=float(row.veg_fruit_shop_pct),
                online_supermarket_pct=float(row.online_supermarket_pct),
                supermarket_chain_pct=float(row.supermarket_chain_pct),
                market_pct=float(row.market_pct),
                grocery_pct=float(row.grocery_pct),
            ))

        # Calculate market shares (aggregate spending)
        total_supermarket_chain = sum(c.supermarket_chain for c in categories)
        total_market = sum(c.market for c in categories)
        total_grocery = sum(c.grocery for c in categories)
        total_special_shop = sum(c.special_shop for c in categories)
        total_butcher = sum(c.butcher for c in categories)
        total_veg_fruit = sum(c.veg_fruit_shop for c in categories)
        total_online = sum(c.online_supermarket for c in categories)
        total_other = sum(c.other for c in categories)

        grand_total = (total_supermarket_chain + total_market + total_grocery + total_special_shop +
                       total_butcher + total_veg_fruit + total_online + total_other)

        supermarket_chain_share = round((total_supermarket_chain / grand_total * 100), 1) if grand_total > 0 else 0
        market_share = round((total_market / grand_total * 100), 1) if grand_total > 0 else 0
        grocery_share = round((total_grocery / grand_total * 100), 1) if grand_total > 0 else 0
        special_shop_share = round((total_special_shop / grand_total * 100), 1) if grand_total > 0 else 0

        # Find where supermarket chains WIN (dominate)
        supermarket_wins = [
            {
                "category": c.category,
                "supermarket_chain_pct": round(c.supermarket_chain_pct, 1),
                "market_pct": round(c.market_pct, 1),
                "grocery_pct": round(c.grocery_pct, 1)
            }
            for c in sorted(categories, key=lambda x: x.supermarket_chain_pct, reverse=True)
        ][:5]

        # Find where outdoor MARKETS win
        market_wins = [
            {
                "category": c.category,
                "market_pct": round(c.market_pct, 1),
                "supermarket_chain_pct": round(c.supermarket_chain_pct, 1)
            }
            for c in sorted(categories, key=lambda x: x.market_pct, reverse=True)
            if c.market_pct > c.supermarket_chain_pct
        ][:5]

        return RetailBattleResponse(
            supermarket_chain_share=supermarket_chain_share,
            market_share=market_share,
            grocery_share=grocery_share,
            special_shop_share=special_shop_share,
            supermarket_wins=supermarket_wins,
            market_wins=market_wins,
            categories=categories
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching retail battle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch retail battle data: {str(e)}"
        )
