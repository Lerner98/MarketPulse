"""
TEST SCRIPT - Read and Clean RAW CBS Excel Files
Following the cleaning methodology from the user's pipeline
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def clean_cbs_value(val):
    """
    Clean CBS values following the user's methodology:
    - Remove commas from numbers
    - Handle '..' (suppressed data) -> NaN or 0
    - Handle '-' (no data) -> NaN or 0
    - Handle '(value)' (low reliability) -> extract value
    - Strip ± symbols (standard error rows)
    """
    if pd.isna(val):
        return np.nan

    val_str = str(val).strip()

    # Filter noise: ± symbols indicate standard error rows
    if '±' in val_str:
        return 'SKIP_ROW'  # Signal to skip this row

    # Handle CBS placeholders
    if val_str == '..' or val_str == '-' or val_str == '':
        return np.nan

    # Remove parentheses (low reliability indicator)
    val_str = val_str.replace('(', '').replace(')', '')

    # Remove commas from numbers
    val_str = val_str.replace(',', '')

    # Try to convert to float
    try:
        return float(val_str)
    except:
        return np.nan


def test_table_11_quintile_expenditure():
    """
    TEST: Table 1.1 - Quintile Expenditure (NIS amounts)
    הוצאה לתצרוכת למשק בית עם מוצרים מפורטים
    """
    print("=" * 80)
    print("TEST 1: TABLE 1.1 - QUINTILE EXPENDITURE (NIS AMOUNTS)")
    print("=" * 80)

    project_root = Path(__file__).parent.parent.parent
    filepath = project_root / 'CBS Household Expenditure Data Strategy' / 'הוצאה לתצרוכת למשק בית עם מוצרים מפורטים.xlsx'

    if not filepath.exists():
        print(f"❌ FILE NOT FOUND: {filepath}")
        return

    print(f"✅ Found file: {filepath.name}\n")

    # Load ALL rows to find the anchor row with quintile numbers (5, 4, 3, 2, 1)
    df_raw = pd.read_excel(filepath, header=None, engine='openpyxl')
    print(f"📊 Loaded {len(df_raw)} raw rows from Excel\n")

    # Find anchor row (contains quintile numbers: 5, 4, 3, 2, 1)
    anchor_row_idx = None
    for idx, row in df_raw.iterrows():
        row_str = ' '.join([str(x) for x in row if pd.notna(x)])
        if '5' in row_str and '4' in row_str and '3' in row_str and '2' in row_str and '1' in row_str:
            # Check if it's the quintile header (not data)
            if 'quintile' in row_str.lower() or idx < 10:
                anchor_row_idx = idx
                print(f"🎯 ANCHOR ROW FOUND at index {idx}: {row.tolist()[:10]}")
                break

    if anchor_row_idx is None:
        print("❌ Could not find anchor row with quintile numbers!")
        return

    # Reload with correct header
    df = pd.read_excel(filepath, header=anchor_row_idx, engine='openpyxl')
    print(f"\n📋 Columns after anchor: {df.columns.tolist()[:10]}\n")

    # Clean data
    cleaned_rows = []
    skipped_error_rows = 0

    for idx, row in df.iterrows():
        # Get category name (first column)
        category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None

        if not category or category == 'nan':
            continue

        # Check if this is a standard error row (contains ±)
        if '±' in category:
            skipped_error_rows += 1
            continue

        # Extract quintile values (columns should be Q5, Q4, Q3, Q2, Q1, Total)
        # We need to identify which columns contain the quintile data
        values = []
        for i in range(1, min(8, len(row))):  # Check first 7 columns after category
            cleaned = clean_cbs_value(row.iloc[i])
            if cleaned == 'SKIP_ROW':
                break
            values.append(cleaned)

        if len(values) >= 6:  # Need at least Q5, Q4, Q3, Q2, Q1, Total
            cleaned_rows.append({
                'category': category,
                'Q5': values[0] if len(values) > 0 else np.nan,
                'Q4': values[1] if len(values) > 1 else np.nan,
                'Q3': values[2] if len(values) > 2 else np.nan,
                'Q2': values[3] if len(values) > 3 else np.nan,
                'Q1': values[4] if len(values) > 4 else np.nan,
                'Total': values[5] if len(values) > 5 else np.nan,
            })

    df_cleaned = pd.DataFrame(cleaned_rows)

    print(f"✅ CLEANED {len(df_cleaned)} data rows")
    print(f"🗑️  SKIPPED {skipped_error_rows} standard error rows (±)\n")

    # Show sample
    print("📊 SAMPLE DATA (first 10 rows):")
    print(df_cleaned.head(10).to_string(index=False))

    # Verify data types
    print(f"\n🔍 DATA TYPE VERIFICATION:")
    print(f"Q5 min: {df_cleaned['Q5'].min():.2f}, max: {df_cleaned['Q5'].max():.2f}")
    print(f"Q1 min: {df_cleaned['Q1'].min():.2f}, max: {df_cleaned['Q1'].max():.2f}")

    # Check if values are NIS amounts (should be > 10) or percentages (should be < 100)
    q5_mean = df_cleaned['Q5'].mean()
    if q5_mean > 100:
        print(f"✅ VALUES ARE NIS AMOUNTS (Q5 mean: {q5_mean:.2f} NIS)")
    else:
        print(f"⚠️  VALUES MIGHT BE PERCENTAGES (Q5 mean: {q5_mean:.2f})")

    return df_cleaned


def test_table_38_store_type():
    """
    TEST: Table 38 - Store Type Competition (PERCENTAGES or NIS?)
    הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות
    """
    print("\n\n" + "=" * 80)
    print("TEST 2: TABLE 38 - STORE TYPE COMPETITION")
    print("=" * 80)

    project_root = Path(__file__).parent.parent.parent
    filepath = project_root / 'CBS Household Expenditure Data Strategy' / 'הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות.xlsx'

    if not filepath.exists():
        print(f"❌ FILE NOT FOUND: {filepath}")
        return

    print(f"✅ Found file: {filepath.name}\n")

    # Load with header at row 7 (as determined earlier)
    df = pd.read_excel(filepath, header=7, engine='openpyxl')
    print(f"📊 Loaded {len(df)} rows from Excel")
    print(f"📋 Columns: {df.columns.tolist()}\n")

    # Clean data
    cleaned_rows = []
    skipped_error_rows = 0

    for idx, row in df.iterrows():
        category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None

        if not category or category == 'nan':
            continue

        # Skip error margin rows
        if '±' in category:
            skipped_error_rows += 1
            continue

        # Extract store type values (columns 1-9)
        values = []
        for i in range(1, 10):  # 8 store types + total
            if i >= len(row):
                break
            cleaned = clean_cbs_value(row.iloc[i])
            if cleaned == 'SKIP_ROW':
                break
            values.append(cleaned if pd.notna(cleaned) else 0.0)

        if len(values) >= 9:  # Need all 8 store types + total
            row_sum = sum(values[:8])
            total = values[8] if len(values) > 8 else row_sum

            cleaned_rows.append({
                'category': category,
                'other': values[0],
                'special_shop': values[1],
                'butcher': values[2],
                'veg_fruit_shop': values[3],
                'online_supermarket': values[4],
                'supermarket_chain': values[5],
                'market': values[6],
                'grocery': values[7],
                'total': total,
                'calculated_sum': row_sum,
            })

    df_cleaned = pd.DataFrame(cleaned_rows)

    print(f"✅ CLEANED {len(df_cleaned)} data rows")
    print(f"🗑️  SKIPPED {skipped_error_rows} standard error rows (±)\n")

    # Show sample
    print("📊 SAMPLE DATA (first 5 rows):")
    print(df_cleaned.head(5)[['category', 'special_shop', 'supermarket_chain', 'grocery', 'total']].to_string(index=False))

    # CRITICAL TEST: Check if values are percentages or NIS amounts
    print(f"\n🔍 DATA TYPE VERIFICATION:")
    print(f"Total column mean: {df_cleaned['total'].mean():.2f}")
    print(f"Total column max: {df_cleaned['total'].max():.2f}")
    print(f"Calculated sum (8 store types) mean: {df_cleaned['calculated_sum'].mean():.2f}")

    # Test case: Alcoholic beverages
    alc = df_cleaned[df_cleaned['category'].str.contains('lcoholic', case=False, na=False)]
    if not alc.empty:
        row = alc.iloc[0]
        print(f"\n🧪 TEST CASE: Alcoholic beverages")
        print(f"   special_shop: {row['special_shop']}")
        print(f"   supermarket_chain: {row['supermarket_chain']}")
        print(f"   grocery: {row['grocery']}")
        print(f"   total: {row['total']}")
        print(f"   calculated_sum: {row['calculated_sum']}")

        if abs(row['total'] - 100) < 5:
            print(f"\n✅ VALUES ARE PERCENTAGES (total ≈ 100)")
        elif row['total'] > 100:
            print(f"\n⚠️  VALUES MIGHT BE NIS AMOUNTS (total = {row['total']})")
        else:
            print(f"\n❓ UNCLEAR DATA TYPE (total = {row['total']})")

    return df_cleaned


def test_table_40_digital_matrix():
    """
    TEST: Table 40 - Digital Matrix (PERCENTAGES)
    אופן הרכישה - מטריצה דיגיטלית
    """
    print("\n\n" + "=" * 80)
    print("TEST 3: TABLE 40 - DIGITAL MATRIX (PURCHASE METHOD)")
    print("=" * 80)

    project_root = Path(__file__).parent.parent.parent
    filepath = project_root / 'CBS Household Expenditure Data Strategy' / 'אופן הרכישה - מטריצה דיגיטלית.xlsx'

    if not filepath.exists():
        print(f"❌ FILE NOT FOUND: {filepath}")
        return

    print(f"✅ Found file: {filepath.name}\n")

    # Load raw to find header
    df_raw = pd.read_excel(filepath, header=None, engine='openpyxl')
    print(f"📊 Loaded {len(df_raw)} raw rows\n")

    # Use header row 7 (common CBS format)
    df = pd.read_excel(filepath, header=7, engine='openpyxl')
    print(f"📋 Columns: {df.columns.tolist()[:10]}\n")

    # Clean and show sample
    cleaned_rows = []
    for idx, row in df.iterrows():
        category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
        if not category or category == 'nan' or '±' in category:
            continue

        # Extract purchase method percentages
        values = []
        for i in range(1, 4):  # Physical, Online Israel, Online Abroad
            cleaned = clean_cbs_value(row.iloc[i])
            values.append(cleaned if pd.notna(cleaned) else 0.0)

        if len(values) >= 3:
            total = sum(values)
            cleaned_rows.append({
                'category': category,
                'physical': values[0],
                'online_israel': values[1],
                'online_abroad': values[2],
                'total': total
            })

    df_cleaned = pd.DataFrame(cleaned_rows)
    print(f"✅ CLEANED {len(df_cleaned)} rows\n")
    print("📊 SAMPLE DATA:")
    print(df_cleaned.head(5).to_string(index=False))

    # Verify percentages
    print(f"\n🔍 DATA TYPE VERIFICATION:")
    print(f"Total mean: {df_cleaned['total'].mean():.2f}")
    if abs(df_cleaned['total'].mean() - 100) < 5:
        print(f"✅ VALUES ARE PERCENTAGES (totals ≈ 100%)")

    return df_cleaned


if __name__ == '__main__':
    # Run all tests
    df1 = test_table_11_quintile_expenditure()
    df2 = test_table_38_store_type()
    df3 = test_table_40_digital_matrix()

    print("\n\n" + "=" * 80)
    print("🎯 FINAL SUMMARY")
    print("=" * 80)
    print(f"Table 1.1: {len(df1) if df1 is not None else 0} categories extracted")
    print(f"Table 38: {len(df2) if df2 is not None else 0} categories extracted")
    print(f"Table 40: {len(df3) if df3 is not None else 0} categories extracted")
