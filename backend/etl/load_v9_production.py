"""
MarketPulse V9 Production ETL Pipeline
Loads table_11_v9_flat.csv and table_38_v6.csv into PostgreSQL

Key Features:
- Auto-detects split point between demographics and spending
- Loads 3 tables: household_profiles, household_expenditures, retail_competition
- Uses v9 flat data (558 rows, clean, no negatives, full tail with mortgage/savings)
- Uses v6 retail data (8 real CBS store types)
"""

import sys
import io
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
import os

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import get_db


def load_table_11_v9(file_path: Path, engine):
    """
    Load Table 11 (v9 flat) and split into profiles + expenditures

    Split Logic:
    - Rows BEFORE "Consumption expenditures" = Demographics (profiles)
    - Rows FROM "Consumption expenditures" onwards = Spending (expenditures)
    """
    print(f"\n{'='*80}")
    print(f"📥 LOADING TABLE 11: {file_path.name}")
    print(f"{'='*80}")

    if not file_path.exists():
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    # Load CSV
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"✅ Loaded {len(df)} rows from {file_path.name}")

    # Find split point
    split_mask = df['Item_English'].str.contains('Consumption expenditures', case=False, na=False)

    if not split_mask.any():
        raise ValueError("CRITICAL: Could not find 'Consumption expenditures' split point!")

    split_idx = df.index[split_mask][0]  # Get first matching index (robust method)
    print(f"Split point detected at row {split_idx}: '{df.loc[split_idx, 'Item_English']}'")

    # SPLIT A: Demographics (rows before split)
    df_profiles = df.iloc[:split_idx].copy()
    df_profiles.columns = ['metric_name', 'q5_val', 'q4_val', 'q3_val', 'q2_val', 'q1_val', 'total_val']

    # Replace NaN with 0 for numeric columns
    numeric_cols = ['q5_val', 'q4_val', 'q3_val', 'q2_val', 'q1_val', 'total_val']
    df_profiles[numeric_cols] = df_profiles[numeric_cols].fillna(0)

    print(f"\n📊 PROFILES (Demographics):")
    print(f"   Rows: {len(df_profiles)}")
    print(f"   Sample metrics:")
    for idx, row in df_profiles.head(5).iterrows():
        print(f"     - {row['metric_name']}: Q5={row['q5_val']}, Q1={row['q1_val']}")

    # SPLIT B: Expenditures (rows from split onwards)
    df_exp = df.iloc[split_idx:].copy()
    df_exp.columns = ['item_name', 'q5_spend', 'q4_spend', 'q3_spend', 'q2_spend', 'q1_spend', 'total_spend']

    # Replace NaN with 0 for numeric columns
    spend_cols = ['q5_spend', 'q4_spend', 'q3_spend', 'q2_spend', 'q1_spend', 'total_spend']
    df_exp[spend_cols] = df_exp[spend_cols].fillna(0)

    # Drop duplicates (keep first occurrence)
    df_exp = df_exp.drop_duplicates(subset=['item_name'], keep='first')

    print(f"\n💰 EXPENDITURES (Spending):")
    print(f"   Rows: {len(df_exp)}")
    print(f"   Sample items:")
    for idx, row in df_exp.head(5).iterrows():
        print(f"     - {row['item_name']}: Total={row['total_spend']} NIS")

    # Verify critical items present
    mortgage = df_exp[df_exp['item_name'].str.contains('Mortgage', case=False, na=False)]
    savings = df_exp[df_exp['item_name'].str.contains('savings', case=False, na=False)]
    renovations = df_exp[df_exp['item_name'].str.contains('Renovation', case=False, na=False)]

    print(f"\n🔍 CRITICAL ITEMS VERIFICATION:")
    print(f"   Mortgage rows: {len(mortgage)} {'✅' if len(mortgage) > 0 else '❌'}")
    print(f"   Savings rows: {len(savings)} {'✅' if len(savings) > 0 else '❌'}")
    print(f"   Renovations rows: {len(renovations)} {'✅' if len(renovations) > 0 else '❌'}")

    if len(mortgage) > 0:
        mort_row = mortgage.iloc[0]
        print(f"   Mortgage: {mort_row['total_spend']} NIS (Q5={mort_row['q5_spend']}, Q1={mort_row['q1_spend']})")

    # Load to database
    print(f"\n💾 Writing to database...")
    with engine.begin() as conn:
        # Clear old data
        conn.execute(text("TRUNCATE TABLE household_profiles CASCADE;"))
        conn.execute(text("TRUNCATE TABLE household_expenditures CASCADE;"))

        # Insert new data
        df_profiles.to_sql('household_profiles', conn, if_exists='append', index=False)
        df_exp.to_sql('household_expenditures', conn, if_exists='append', index=False)

    print(f"✅ SUCCESS: Loaded {len(df_profiles)} profiles, {len(df_exp)} expenditures")

    return df_profiles, df_exp


def load_table_38_v6(file_path: Path, engine):
    """
    Load Table 38 (v6 with 8 real CBS store types)
    """
    print(f"\n{'='*80}")
    print(f"📥 LOADING TABLE 38: {file_path.name}")
    print(f"{'='*80}")

    if not file_path.exists():
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    # Load CSV
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"✅ Loaded {len(df)} rows from {file_path.name}")

    # Map columns to database schema
    # The CSV has lowercase column names with _pct suffix for percentages
    df_clean = pd.DataFrame()
    df_clean['category'] = df['category']
    df_clean['other_pct'] = df['other_pct']
    df_clean['special_shop_pct'] = df['special_shop_pct']
    df_clean['butcher_pct'] = df['butcher_pct']
    df_clean['veg_fruit_shop_pct'] = df['veg_fruit_shop_pct']
    df_clean['online_supermarket_pct'] = df['online_supermarket_pct']
    df_clean['supermarket_chain_pct'] = df['supermarket_chain_pct']
    df_clean['market_pct'] = df['market_pct']
    df_clean['grocery_pct'] = df['grocery_pct']
    df_clean['total_pct'] = df['total']

    print(f"\n🏪 RETAIL COMPETITION:")
    print(f"   Categories: {len(df_clean)}")
    print(f"   Sample data:")
    for idx, row in df_clean.head(3).iterrows():
        print(f"     - {row['category']}: Supermarket={row['supermarket_chain_pct']}%, Market={row['market_pct']}%")

    # Verify alcoholic beverages test case
    alc_row = df_clean[df_clean['category'].str.contains('Alcoholic', case=False, na=False)]
    if len(alc_row) > 0:
        alc = alc_row.iloc[0]
        print(f"\n🧪 VERIFICATION: Alcoholic beverages")
        print(f"   Special_Shop: {alc['special_shop_pct']}% (expected 30.4)")
        print(f"   Supermarket_Chain: {alc['supermarket_chain_pct']}% (expected 51.1)")
        print(f"   Grocery: {alc['grocery_pct']}% (expected 11.4)")
        print(f"   Total: {alc['total_pct']}%")

    # Load to database
    print(f"\n💾 Writing to database...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE retail_competition CASCADE;"))
        df_clean.to_sql('retail_competition', conn, if_exists='append', index=False)

    print(f"✅ SUCCESS: Loaded {len(df_clean)} retail categories")

    return df_clean


def refresh_views(engine):
    """Refresh all materialized views"""
    print(f"\n{'='*80}")
    print(f"🔄 REFRESHING MATERIALIZED VIEWS")
    print(f"{'='*80}")

    with engine.begin() as conn:
        conn.execute(text("SELECT refresh_all_views();"))

    print(f"✅ All views refreshed")


def run_validation_queries(engine):
    """Run validation queries to verify data integrity"""
    print(f"\n{'='*80}")
    print(f"🔍 RUNNING VALIDATION QUERIES")
    print(f"{'='*80}")

    with engine.connect() as conn:
        # Query 1: Top 5 inequality gaps
        print(f"\n1️⃣ TOP 5 INEQUALITY GAPS (Q5/Q1 spending ratio):")
        result = conn.execute(text("""
            SELECT item_name, rich_spend, poor_spend, gap_ratio
            FROM vw_inequality_gap
            LIMIT 5;
        """))
        for row in result:
            print(f"   - {row[0][:50]:50s} | Q5: {row[1]:8.1f} | Q1: {row[2]:8.1f} | Gap: {row[3]:.2f}x")

        # Query 2: Burn rate
        print(f"\n2️⃣ BURN RATE (% of income consumed by spending):")
        result = conn.execute(text("SELECT * FROM vw_burn_rate;"))
        row = result.fetchone()
        if row:
            print(f"   Q5 (Rich): {row[0]:.1f}% | Q1 (Poor): {row[4]:.1f}%")

        # Query 3: Fresh food battle winners
        print(f"\n3️⃣ FRESH FOOD BATTLE (Traditional retail wins):")
        result = conn.execute(text("""
            SELECT category, traditional_retail_pct, supermarket_chain_pct
            FROM vw_fresh_food_battle
            WHERE winner = 'Traditional Wins'
            LIMIT 5;
        """))
        for row in result:
            print(f"   - {row[0]:40s} | Traditional: {row[1]:.1f}% | Supermarket: {row[2]:.1f}%")


def main():
    """Main ETL pipeline execution"""
    print(f"\n{'='*80}")
    print(f"MARKETPULSE V9 PRODUCTION ETL")
    print(f"{'='*80}")

    # Paths
    project_root = Path(__file__).parent.parent.parent

    # Table 11 from v9 flat (in data/raw)
    table_11_path = project_root / 'data' / 'raw' / 'table_11_v9_flat.csv'

    # Table 38 from existing extraction (in data/processed)
    table_38_path = project_root / 'data' / 'processed' / 'table_38_retail.csv'

    print(f"\nData files:")
    print(f"   Table 11: {table_11_path}")
    print(f"   Table 38: {table_38_path}")

    # Verify files exist
    if not table_11_path.exists():
        raise FileNotFoundError(f"Table 11 not found: {table_11_path}")
    if not table_38_path.exists():
        raise FileNotFoundError(f"Table 38 not found: {table_38_path}\n   Run: python backend/etl/extract_table_38.py")

    # Get database connection
    db = get_db()
    engine = db.engine
    print(f"\nDatabase connected")

    # Load data
    try:
        df_profiles, df_exp = load_table_11_v9(table_11_path, engine)
        df_retail = load_table_38_v6(table_38_path, engine)

        # Refresh materialized views
        refresh_views(engine)

        # Run validation queries
        run_validation_queries(engine)

        print(f"\n{'='*80}")
        print(f"🎉 ETL PIPELINE COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Profiles: {len(df_profiles)} rows")
        print(f"✅ Expenditures: {len(df_exp)} rows")
        print(f"✅ Retail: {len(df_retail)} rows")
        print(f"✅ Views: 3 materialized views refreshed")
        print(f"\n🔍 Next: Start backend API to serve insights")
        print(f"   cd backend")
        print(f"   uvicorn api.main:app --reload")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise


if __name__ == '__main__':
    main()
