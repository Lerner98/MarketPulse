"""
Strategic CBS Analysis Endpoints - The 3 Core Insights
1. The 2.62x Rule (Quintile Gap) - Table 1.1
2. Digital Opportunity Matrix - Table 40
3. Retail Battle - Table 38
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/strategic", tags=["Strategic Insights"])


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
    """Single food category with store type breakdown"""
    category: str
    supermarket: float
    local_market: float
    butcher: float
    bakery: float
    other: float
    total: float


class RetailBattleResponse(BaseModel):
    """Retail Competition Analysis"""
    supermarket_share: float
    local_share: float
    butcher_share: float
    supermarket_loses: List[Dict[str, Any]]
    categories: List[RetailBattleItem]


# =============================================================================
# Helper Functions - Load data from CSV (cached in production)
# =============================================================================

def load_quintile_data():
    """Load Table 1.1 data"""
    import pandas as pd

    project_root = Path(__file__).parent.parent.parent
    csv_path = project_root / 'data' / 'processed' / 'table_1_1_quintiles.csv'

    if not csv_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table 1.1 data not found. Run extract_table_1_1.py first."
        )

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    return df


def load_digital_data():
    """Load Table 40 data"""
    import pandas as pd

    project_root = Path(__file__).parent.parent.parent
    csv_path = project_root / 'data' / 'processed' / 'table_40_digital.csv'

    if not csv_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table 40 data not found. Run extract_table_40.py first."
        )

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    return df


def load_retail_data():
    """Load Table 38 data"""
    import pandas as pd

    project_root = Path(__file__).parent.parent.parent
    csv_path = project_root / 'data' / 'processed' / 'table_38_retail.csv'

    if not csv_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table 38 data not found. Run extract_table_38.py first."
        )

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    return df


# =============================================================================
# Endpoint 1: The 2.62x Rule (Quintile Gap)
# =============================================================================

@router.get(
    "/quintile-gap",
    response_model=QuintileGapResponse,
    summary="The 2.62x Rule - Income inequality in spending",
    description="High-income households (Q5) spend 2.62x more than low-income (Q1)"
)
def get_quintile_gap() -> QuintileGapResponse:
    """
    Analyze spending inequality across income quintiles.

    Returns:
    - Spending ratio (Q5/Q1)
    - Category-by-category breakdown
    - Business insight
    """
    df = load_quintile_data()

    # Calculate the ratio
    q5_total = df['quintile_5'].sum()
    q1_total = df['quintile_1'].sum()
    ratio = round(q5_total / q1_total, 2) if q1_total > 0 else 0

    # Build category list
    categories = []
    for _, row in df.iterrows():
        categories.append(QuintileGapItem(
            category=row['category'],
            quintile_1=float(row['quintile_1']),
            quintile_2=float(row['quintile_2']),
            quintile_3=float(row['quintile_3']),
            quintile_4=float(row['quintile_4']),
            quintile_5=float(row['quintile_5']),
            total_spending=float(row['total_spending']),
            avg_spending=float(row['avg_spending'])
        ))

    return QuintileGapResponse(
        ratio=ratio,
        q5_total=q5_total,
        q1_total=q1_total,
        insight=f"High-income households (Q5) spend {ratio}x more than low-income (Q1). Allocate 40% of marketing budget to Q4-Q5 for highest ROI.",
        categories=categories
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
def get_digital_matrix() -> DigitalMatrixResponse:
    """
    Analyze digital penetration across product categories.

    Returns:
    - Top Israel online categories
    - Top Abroad online categories
    - Most physical categories
    - Full category breakdown
    """
    df = load_digital_data()

    # Sort by online Israel percentage
    df_sorted_israel = df.sort_values('online_israel_pct', ascending=False)
    df_sorted_abroad = df.sort_values('online_abroad_pct', ascending=False)
    df_sorted_physical = df.sort_values('physical_pct', ascending=False)

    # Top 5 each
    top_israel = df_sorted_israel.head(5)[['category', 'online_israel_pct']].to_dict('records')
    top_abroad = df_sorted_abroad.head(5)[['category', 'online_abroad_pct']].to_dict('records')
    most_physical = df_sorted_physical.head(5)[['category', 'physical_pct']].to_dict('records')

    # Build category list
    categories = []
    for _, row in df.iterrows():
        categories.append(DigitalMatrixItem(
            category=row['category'],
            physical_pct=float(row['physical_pct']),
            online_israel_pct=float(row['online_israel_pct']),
            online_abroad_pct=float(row['online_abroad_pct'])
        ))

    return DigitalMatrixResponse(
        top_israel_online=top_israel,
        top_abroad_online=top_abroad,
        most_physical=most_physical,
        categories=categories
    )


# =============================================================================
# Endpoint 3: Retail Battle
# =============================================================================

@router.get(
    "/retail-battle",
    response_model=RetailBattleResponse,
    summary="Retail Battle - Supermarket vs Local Market competition",
    description="Food expenditure breakdown by store type - who wins fresh vs packaged"
)
def get_retail_battle() -> RetailBattleResponse:
    """
    Analyze retail competition for food categories.

    Returns:
    - Market share by store type
    - Categories where supermarkets lose to local markets
    - Full category breakdown
    """
    df = load_retail_data()

    # Calculate market shares
    total_supermarket = df['supermarket'].sum()
    total_local = df['local_market'].sum()
    total_butcher = df['butcher'].sum()
    grand_total = total_supermarket + total_local + total_butcher

    supermarket_share = round((total_supermarket / grand_total * 100), 1) if grand_total > 0 else 0
    local_share = round((total_local / grand_total * 100), 1) if grand_total > 0 else 0
    butcher_share = round((total_butcher / grand_total * 100), 1) if grand_total > 0 else 0

    # Find where supermarkets lose
    df['supermarket_pct'] = df['supermarket'] / df['total'] * 100
    df['local_pct'] = df['local_market'] / df['total'] * 100

    loses_to_local = df[df['local_pct'] > df['supermarket_pct']].sort_values('local_pct', ascending=False)
    loses_list = loses_to_local.head(5)[['category', 'supermarket_pct', 'local_pct']].to_dict('records')

    # Build category list
    categories = []
    for _, row in df.iterrows():
        categories.append(RetailBattleItem(
            category=row['category'],
            supermarket=float(row['supermarket']),
            local_market=float(row['local_market']),
            butcher=float(row['butcher']),
            bakery=float(row['bakery']),
            other=float(row['other']),
            total=float(row['total'])
        ))

    return RetailBattleResponse(
        supermarket_share=supermarket_share,
        local_share=local_share,
        butcher_share=butcher_share,
        supermarket_loses=loses_list,
        categories=categories
    )
