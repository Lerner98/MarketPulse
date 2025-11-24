"""
V10 Data Loader - Load CBS data from complete CSV export
Loads 2024-11-22_complete_database_export_6420_records.csv into V10 normalized schema
"""

import pandas as pd
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Path to CSV export
CSV_PATH = Path(__file__).parent.parent / "data" / "v10_exports" / "2024-11-22_complete_database_export_6420_records.csv"

def load_csv_to_v10():
    """Load complete CSV export into V10 normalized schema"""

    print("=" * 80)
    print("V10 DATA LOADER - Loading from CSV Export")
    print("=" * 80)

    # Read CSV
    print(f"\nReading CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows from CSV")

    # Show columns
    print(f"\nCSV Columns: {list(df.columns)}")

    # Clear existing data
    print("\nClearing existing V10 data...")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM fact_segment_expenditure"))
        conn.execute(text("DELETE FROM dim_segment WHERE segment_type NOT IN ('Income Quintile', 'Age Group')"))
        print("Cleared fact_segment_expenditure and non-sample segments from dim_segment")

    # Load segments
    print("\nLoading segments into dim_segment...")
    segments = df[['segment_type', 'segment_value', 'segment_order']].drop_duplicates()

    segment_count = 0
    with engine.begin() as conn:
        for _, row in segments.iterrows():
            # Use segment_order from CSV
            segment_order = int(row['segment_order']) if pd.notna(row['segment_order']) else None

            conn.execute(text("""
                INSERT INTO dim_segment (segment_type, segment_value, segment_order, file_source)
                VALUES (:segment_type, :segment_value, :segment_order, 'csv_export_2024-11-22')
                ON CONFLICT (segment_type, segment_value) DO UPDATE
                SET segment_order = EXCLUDED.segment_order
            """), {
                'segment_type': row['segment_type'],
                'segment_value': str(row['segment_value']),
                'segment_order': segment_order
            })
            segment_count += 1

    print(f"Loaded {segment_count} segments")

    # Load expenditures
    print("\nLoading expenditure data into fact_segment_expenditure...")

    expenditure_count = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            # Get segment_key
            segment_key_result = conn.execute(text("""
                SELECT segment_key FROM dim_segment
                WHERE segment_type = :segment_type AND segment_value = :segment_value
            """), {
                'segment_type': row['segment_type'],
                'segment_value': str(row['segment_value'])
            }).fetchone()

            if not segment_key_result:
                print(f"WARNING: No segment found for {row['segment_type']} / {row['segment_value']}")
                continue

            segment_key = segment_key_result[0]

            # Insert expenditure
            conn.execute(text("""
                INSERT INTO fact_segment_expenditure (
                    segment_key, item_name, expenditure_value,
                    is_income_metric, is_consumption_metric
                )
                VALUES (:segment_key, :item_name, :expenditure_value, :is_income, :is_consumption)
            """), {
                'segment_key': segment_key,
                'item_name': row['item_name'],
                'expenditure_value': float(row['expenditure_value']),
                'is_income': bool(row['is_income_metric']),
                'is_consumption': bool(row['is_consumption_metric'])
            })
            expenditure_count += 1

            if expenditure_count % 500 == 0:
                print(f"  Loaded {expenditure_count:,} expenditure records...")

    print(f"Loaded {expenditure_count:,} total expenditure records")

    # Refresh materialized views
    print("\nRefreshing materialized views...")
    with engine.begin() as conn:
        conn.execute(text("REFRESH MATERIALIZED VIEW vw_segment_inequality"))
        conn.execute(text("REFRESH MATERIALIZED VIEW vw_segment_burn_rate"))
        print("Materialized views refreshed")

    # Verify load
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    with engine.connect() as conn:
        # Count segments
        segment_types = conn.execute(text("""
            SELECT segment_type, COUNT(*)
            FROM dim_segment
            GROUP BY segment_type
            ORDER BY segment_type
        """)).fetchall()

        print("\nSegments loaded:")
        for st in segment_types:
            print(f"  {st[0]}: {st[1]} values")

        # Count expenditures
        total_exp = conn.execute(text("SELECT COUNT(*) FROM fact_segment_expenditure")).scalar()
        print(f"\nTotal expenditure records: {total_exp:,}")

        # Check inequality view
        ineq_count = conn.execute(text("SELECT COUNT(*) FROM vw_segment_inequality")).scalar()
        print(f"Inequality view records: {ineq_count:,}")

        # Check burn rate view
        burn_count = conn.execute(text("SELECT COUNT(*) FROM vw_segment_burn_rate")).scalar()
        print(f"Burn rate view records: {burn_count:,}")

        # Show top inequality for Work Status
        print("\nTop 3 inequality categories for Work Status (after fix):")
        work_ineq = conn.execute(text("""
            SELECT item_name, high_segment, low_segment, inequality_ratio
            FROM vw_segment_inequality
            WHERE segment_type = 'Work Status'
            ORDER BY inequality_ratio DESC
            LIMIT 3
        """)).fetchall()

        for row in work_ineq:
            print(f"  {row[0][:40]:40s} | {row[1]:15s} vs {row[2]:15s} | {row[3]:.1f}x")

    print("\n" + "=" * 80)
    print("LOAD COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        load_csv_to_v10()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
