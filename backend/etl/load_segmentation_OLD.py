"""
PHASE 6: Universal Segmentation ETL Pipeline
Loads 14+ CBS demographic segmentation files into normalized star schema

Data Flow:
    Raw CBS Excel (ta2-ta13+)
    → Clean & Normalize (wide to long format)
    → dim_segment + fact_segment_expenditure tables

Segmentation Dimensions:
- Income Quintile/Decile
- Age Group
- Household Size
- Education Level
- Employment Status
- Religiosity Level
- Geographic (Sub-District)
- etc.
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

# ============================================================================
# CONFIGURATION: Segmentation File Mapping
# ============================================================================
SEGMENTATION_MAP: Dict[str, Tuple[str, int]] = {
    # Filename: (Segment Type, Sort Priority)
    'הוצאה לתצרוכת למשק בית עם מוצרים מפורטים.xlsx': ('Income Quintile', 1),  # Original Table 1.1
    'ta2.xlsx': ('Income Decile', 2),
    'ta3.xlsx': ('Gross Income Decile', 3),
    'ta4.xlsx': ('Household Size', 4),
    'ta5.xlsx': ('Age Group', 5),
    'ta6.xlsx': ('Composition Age', 6),
    'ta7.xlsx': ('Family Status', 7),
    'ta8.xlsx': ('Number of Children', 8),
    'ta9.xlsx': ('Number of Earners', 9),
    'ta10.xlsx': ('Sub-District', 10),
    'ta11.xlsx': ('Country of Birth', 11),
    'ta12.xlsx': ('Education Level', 12),
    'ta13.xlsx': ('Religiosity Level', 13),
}

# ============================================================================
# CRITICAL DATA INTEGRITY FIX - Keywords for Burn Rate Calculation
# ============================================================================
# These are the ONLY two aggregate summary rows needed for burn rate
AGGREGATE_INCOME_KEY = 'Net money income per household'
AGGREGATE_CONSUMPTION_KEY = 'Money expenditure per household'

# ============================================================================
# CORE CLEANING FUNCTION (from cbs_final_flat_fix.py)
# ============================================================================
def clean_cbs_value(val):
    """Clean CBS values - NO NEGATIVES, NO ERRORS"""
    if pd.isna(val):
        return None

    val_str = str(val).strip()

    # Skip error margin rows
    if '±' in val_str:
        return 'SKIP_ROW'

    # Handle suppressed/missing data
    if val_str in ['..', '-', '', 'nan']:
        return None

    # Remove CBS parentheses (low reliability indicator) and commas
    val_str = val_str.replace('(', '').replace(')', '').replace(',', '')

    try:
        result = float(val_str)
        # FIX NEGATIVES: Use absolute value (CBS statistical adjustment)
        return abs(result) if result < 0 else result
    except:
        return None


# ============================================================================
# SEGMENTATION FILE PROCESSOR
# ============================================================================
def process_segmentation_file(
    file_path: Path,
    segment_type: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Process a CBS segmentation file into normalized format.

    Returns:
        segments_df: DataFrame for dim_segment table
        expenditures_df: DataFrame for fact_segment_expenditure table
    """
    print(f"\n{'='*80}")
    print(f"Processing: {file_path.name}")
    print(f"Segment Type: {segment_type}")
    print(f"{'='*80}")

    if not file_path.exists():
        print(f"❌ FILE NOT FOUND: {file_path}")
        return pd.DataFrame(), pd.DataFrame()

    # Load raw Excel
    df_raw = pd.read_excel(file_path, header=None, engine='openpyxl')
    print(f"📊 Raw rows: {len(df_raw)}")

    # Find anchor row (contains quintile numbers 5, 4, 3, 2, 1 OR segment labels)
    anchor_row = None
    for idx, row in df_raw.iterrows():
        row_values = [str(x) for x in row.tolist() if pd.notna(x)]
        # Check for quintile pattern (5, 4, 3, 2, 1)
        if '5' in row_values and '4' in row_values and '3' in row_values and '2' in row_values and '1' in row_values:
            anchor_row = idx
            print(f"🎯 Anchor found at row {idx} (Quintile pattern)")
            break
        # Check for "Total" + year pattern
        if any('total' in str(x).lower() for x in row_values) and any('2022' in str(x) for x in row_values):
            anchor_row = idx
            print(f"🎯 Anchor found at row {idx} (Total/Year pattern)")
            break

    if anchor_row is None:
        print("❌ No anchor row found")
        return pd.DataFrame(), pd.DataFrame()

    # Reload with header
    df = pd.read_excel(file_path, header=anchor_row, engine='openpyxl')

    # Get segment column names (all columns except first item column)
    item_col = df.columns[0]
    segment_cols = df.columns[1:]

    print(f"📋 Found {len(segment_cols)} segment columns")
    print(f"   Sample segments: {list(segment_cols[:5])}")

    # Clean data
    cleaned_data = []
    stats = {'error': 0, 'empty': 0, 'no_total': 0, 'skipped': 0}

    for idx, row in df.iterrows():
        item_name = str(row[item_col]).strip() if pd.notna(row[item_col]) else None

        if not item_name or item_name == 'nan':
            stats['empty'] += 1
            continue

        # Skip error margin rows
        if '±' in item_name:
            stats['error'] += 1
            continue

        # Skip garbage headers (but NOT aggregate summary rows needed for burn rate)
        # Note: Must allow "Money expenditure per household" and "Net money income per household"
        if any(x in item_name.upper() for x in ['TABLE', 'PUBLICATION']):
            stats['skipped'] += 1
            continue

        # Skip specific header-like patterns (not aggregate metrics)
        if 'CONSUMPTION EXPENDITURE' in item_name.upper() or 'EXPENDITURE PER CAPITA' in item_name.upper():
            stats['skipped'] += 1
            continue

        # Skip numbered footnotes
        if item_name.startswith('(') and len(item_name) > 2 and item_name[1].isdigit():
            stats['skipped'] += 1
            continue

        # Extract and clean segment values
        row_data = {'item_name': item_name}
        skip_row = False

        for seg_col in segment_cols:
            cleaned_val = clean_cbs_value(row[seg_col])
            if cleaned_val == 'SKIP_ROW':
                skip_row = True
                stats['error'] += 1
                break
            row_data[seg_col] = cleaned_val

        if skip_row:
            continue

        # Check if row has meaningful data (at least one non-null value)
        if all(v is None or pd.isna(v) for k, v in row_data.items() if k != 'item_name'):
            stats['no_total'] += 1
            continue

        cleaned_data.append(row_data)

    df_cleaned = pd.DataFrame(cleaned_data)

    print(f"\n✅ Cleaned: {len(df_cleaned)} items")
    print(f"🗑️  Skipped: error={stats['error']}, empty={stats['empty']}, no_data={stats['no_total']}, garbage={stats['skipped']}")

    if df_cleaned.empty:
        return pd.DataFrame(), pd.DataFrame()

    # ========================================================================
    # NORMALIZATION: Wide → Long Format
    # ========================================================================

    # Melt DataFrame (un-pivot)
    df_long = pd.melt(
        df_cleaned,
        id_vars=['item_name'],
        value_vars=[col for col in df_cleaned.columns if col != 'item_name'],
        var_name='segment_value',
        value_name='expenditure_value'
    ).dropna(subset=['expenditure_value'])

    df_long['segment_type'] = segment_type
    df_long['file_source'] = file_path.name

    # Clean segment values (remove leading/trailing whitespace, fix encoding)
    df_long['segment_value'] = df_long['segment_value'].astype(str).str.strip()

    # ========================================================================
    # CRITICAL DATA INTEGRITY FIX: Flag income and consumption metrics
    # ========================================================================
    # These flags identify the TWO aggregate summary rows needed for burn rate
    df_long['is_income_metric'] = df_long['item_name'].str.contains(
        AGGREGATE_INCOME_KEY, case=False, na=False
    )
    df_long['is_consumption_metric'] = df_long['item_name'].str.contains(
        AGGREGATE_CONSUMPTION_KEY, case=False, na=False
    )

    # Assign segment order based on column position or segment value
    segment_order_map = {}
    for i, seg_col in enumerate(segment_cols, start=1):
        seg_val = str(seg_col).strip()
        # Try to extract numeric order from segment name
        if seg_val.startswith('Q') and seg_val[1].isdigit():
            # Quintile pattern: Q5, Q4, Q3, Q2, Q1
            order = int(seg_val[1])
        elif seg_val.isdigit():
            # Decile pattern: 10, 9, 8, ..., 1
            order = int(seg_val)
        else:
            # Default: use column position
            order = i
        segment_order_map[seg_val] = order

    df_long['segment_order'] = df_long['segment_value'].map(segment_order_map)

    # Create segments DataFrame for dim_segment table
    segments_df = df_long[['segment_type', 'segment_value', 'segment_order', 'file_source']].drop_duplicates()

    # Create expenditures DataFrame for fact_segment_expenditure table
    # (Note: segment_key will be assigned during database insertion via JOIN)
    # IMPORTANT: Include data integrity flags
    expenditures_df = df_long[['item_name', 'segment_type', 'segment_value', 'expenditure_value',
                                 'is_income_metric', 'is_consumption_metric']].copy()

    print(f"\n📦 Normalized Data:")
    print(f"   Unique segments: {len(segments_df)}")
    print(f"   Total expenditure records: {len(expenditures_df)}")
    print(f"   Income metric rows: {expenditures_df['is_income_metric'].sum()}")
    print(f"   Consumption metric rows: {expenditures_df['is_consumption_metric'].sum()}")

    return segments_df, expenditures_df


# ============================================================================
# DATABASE LOADER
# ============================================================================
def load_to_database(segments_df: pd.DataFrame, expenditures_df: pd.DataFrame, engine):
    """
    Load normalized data into dim_segment and fact_segment_expenditure tables.
    """
    print(f"\n{'='*80}")
    print("DATABASE LOADING")
    print(f"{'='*80}")

    with engine.begin() as conn:
        # ====================================================================
        # STEP 1: Insert segments into dim_segment (with conflict handling)
        # ====================================================================
        print("\n[1/3] Inserting segments into dim_segment...")

        for _, row in segments_df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO dim_segment (segment_type, segment_value, segment_order, file_source)
                    VALUES (:segment_type, :segment_value, :segment_order, :file_source)
                    ON CONFLICT (segment_type, segment_value) DO UPDATE
                    SET segment_order = EXCLUDED.segment_order,
                        file_source = EXCLUDED.file_source;
                """),
                {
                    'segment_type': row['segment_type'],
                    'segment_value': row['segment_value'],
                    'segment_order': row['segment_order'],
                    'file_source': row['file_source']
                }
            )

        print(f"   ✅ Inserted/Updated {len(segments_df)} segments")

        # ====================================================================
        # STEP 2: Insert expenditures into fact_segment_expenditure
        # ====================================================================
        print("\n[2/3] Inserting expenditures into fact_segment_expenditure...")

        inserted_count = 0
        for _, row in expenditures_df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO fact_segment_expenditure
                        (item_name, segment_key, expenditure_value, is_income_metric, is_consumption_metric)
                    SELECT
                        :item_name,
                        s.segment_key,
                        :expenditure_value,
                        :is_income_metric,
                        :is_consumption_metric
                    FROM dim_segment s
                    WHERE s.segment_type = :segment_type
                      AND s.segment_value = :segment_value;
                """),
                {
                    'item_name': row['item_name'],
                    'segment_type': row['segment_type'],
                    'segment_value': row['segment_value'],
                    'expenditure_value': float(row['expenditure_value']),
                    'is_income_metric': bool(row['is_income_metric']),
                    'is_consumption_metric': bool(row['is_consumption_metric'])
                }
            )
            inserted_count += 1

            if inserted_count % 1000 == 0:
                print(f"   Progress: {inserted_count}/{len(expenditures_df)} records...")

        print(f"   ✅ Inserted {inserted_count} expenditure records")

        # ====================================================================
        # STEP 3: Refresh materialized views
        # ====================================================================
        print("\n[3/3] Refreshing materialized views...")
        conn.execute(text("SELECT refresh_all_segment_views();"))
        print("   ✅ Views refreshed")

    print(f"\n{'='*80}")
    print("✅ DATABASE LOADING COMPLETE")
    print(f"{'='*80}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("\n" + "="*80)
    print("PHASE 6: UNIVERSAL SEGMENTATION ETL PIPELINE")
    print("="*80)

    # Setup database connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return

    engine = create_engine(DATABASE_URL)

    # Base directory for CBS files
    cbs_data_dir = Path(__file__).parent.parent.parent / 'CBS Household Expenditure Data Strategy'

    # Process each segmentation file
    all_segments = []
    all_expenditures = []

    for filename, (segment_type, priority) in SEGMENTATION_MAP.items():
        file_path = cbs_data_dir / filename

        if not file_path.exists():
            print(f"\n⚠️  SKIPPING: {filename} (file not found)")
            continue

        segments_df, expenditures_df = process_segmentation_file(file_path, segment_type)

        if not segments_df.empty and not expenditures_df.empty:
            all_segments.append(segments_df)
            all_expenditures.append(expenditures_df)

    # Combine all DataFrames
    if all_segments and all_expenditures:
        combined_segments = pd.concat(all_segments, ignore_index=True).drop_duplicates()
        combined_expenditures = pd.concat(all_expenditures, ignore_index=True)

        print(f"\n{'='*80}")
        print("PIPELINE SUMMARY")
        print(f"{'='*80}")
        print(f"Total unique segments: {len(combined_segments)}")
        print(f"Total expenditure records: {len(combined_expenditures)}")
        print(f"\nSegment types processed:")
        for seg_type in combined_segments['segment_type'].unique():
            count = len(combined_segments[combined_segments['segment_type'] == seg_type])
            print(f"  - {seg_type}: {count} segments")

        # Load into database
        load_to_database(combined_segments, combined_expenditures, engine)

    else:
        print("\n❌ No data processed - check file paths and formats")

    print("\n" + "="*80)
    print("✅ PHASE 6 ETL PIPELINE COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
