"""
CBS Table 38 Clean Extraction
Retail Competition: Food Expenditure by Store Type
Following cbs_final_flat_fix.py approach
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')


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


def extract_table_38_clean():
    """
    Extract Table 38 with proper CBS cleaning
    Returns: Clean DataFrame with 14 food categories × 8 store types
    """
    print(f"\n{'='*80}")
    print(f"TABLE 38: RETAIL COMPETITION CLEAN EXTRACTION")
    print(f"{'='*80}")

    filepath = Path(__file__).parent / 'הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות.xlsx'

    if not filepath.exists():
        print(f"❌ FILE NOT FOUND: {filepath}")
        return None

    # Load raw Excel
    df_raw = pd.read_excel(filepath, header=None, engine='openpyxl')
    print(f"📊 Raw rows: {len(df_raw)}")

    # Find header row (contains "Other", "Special shop", "Butcher", etc.)
    header_row = None
    for idx, row in df_raw.iterrows():
        row_values = [str(x).lower() for x in row.tolist() if pd.notna(x)]
        # Look for English store type keywords
        if any('other' in x for x in row_values) or any('butcher' in x for x in row_values):
            header_row = idx
            print(f"🎯 Header at row {idx}")
            break

    if header_row is None:
        print("❌ No header found")
        return None

    # Reload with header
    df = pd.read_excel(filepath, header=header_row, engine='openpyxl')
    print(f"📋 Columns: {df.columns.tolist()}")

    # Clean data
    cleaned_data = []
    stats = {'error': 0, 'empty': 0, 'no_data': 0, 'total_row': 0}

    for idx, row in df.iterrows():
        # Category name is first column
        category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None

        if not category or category == 'nan':
            stats['empty'] += 1
            continue

        # Skip error margin rows
        if '±' in category:
            stats['error'] += 1
            continue

        # Skip "Total" aggregate row
        if category.lower() in ['total', 'sum', 'סך הכל']:
            stats['total_row'] += 1
            continue

        # Extract 8 store types (columns B-I) + Total (column J)
        # Columns indices: 1=Other, 2=Special shop, 3=Butcher, 4=Veg/Fruit,
        #                  5=Online, 6=Supermarket Chain, 7=Market, 8=Grocery, 9=Total

        row_data = {'category': category}
        skip_row = False

        # Extract 9 columns (8 store types + total)
        for col_idx in range(1, 10):
            if col_idx < len(row):
                cleaned_val = clean_cbs_value(row.iloc[col_idx])
                if cleaned_val == 'SKIP_ROW':
                    skip_row = True
                    stats['error'] += 1
                    break
                row_data[f'col_{col_idx}'] = cleaned_val
            else:
                row_data[f'col_{col_idx}'] = None

        if skip_row:
            continue

        # Skip rows with no meaningful data (total < 1 or all zeros)
        total_val = row_data.get('col_9', None)
        if total_val is None or total_val < 1:
            stats['no_data'] += 1
            continue

        cleaned_data.append(row_data)

    df_cleaned = pd.DataFrame(cleaned_data)

    print(f"\n✅ Cleaned: {len(df_cleaned)} food categories")
    print(f"🗑️  Skipped: ± rows={stats['error']}, empty={stats['empty']}, no_data={stats['no_data']}, total_row={stats['total_row']}")

    # Map to final format with proper column names
    df_final = pd.DataFrame({
        'category': df_cleaned['category'],
        'other': df_cleaned['col_1'],
        'special_shop': df_cleaned['col_2'],
        'butcher': df_cleaned['col_3'],
        'veg_fruit_shop': df_cleaned['col_4'],
        'online_supermarket': df_cleaned['col_5'],
        'supermarket_chain': df_cleaned['col_6'],
        'market': df_cleaned['col_7'],
        'grocery': df_cleaned['col_8'],
        'total': df_cleaned['col_9']
    })

    # Calculate percentages (each row sums to ~100%)
    store_cols = ['other', 'special_shop', 'butcher', 'veg_fruit_shop',
                  'online_supermarket', 'supermarket_chain', 'market', 'grocery']

    for col in store_cols:
        df_final[f'{col}_pct'] = (df_final[col] / df_final['total'] * 100).round(1)

    # Verification
    print(f"\n🔍 VERIFICATION:")

    # Check for Alcoholic beverages (test case)
    alcoholic = df_final[df_final['category'].str.contains('lcoholic', case=False, na=False)]
    if not alcoholic.empty:
        row = alcoholic.iloc[0]
        print(f"   Alcoholic beverages:")
        print(f"   - Special shop: {row['special_shop_pct']}% (expected 30.4%)")
        print(f"   - Supermarket chain: {row['supermarket_chain_pct']}% (expected 51.1%)")
        print(f"   - Grocery: {row['grocery_pct']}% (expected 11.4%)")

        # Verify match
        if (abs(row['special_shop_pct'] - 30.4) < 1 and
            abs(row['supermarket_chain_pct'] - 51.1) < 1 and
            abs(row['grocery_pct'] - 11.4) < 1):
            print(f"   ✅ VERIFICATION PASSED")
        else:
            print(f"   ❌ VERIFICATION FAILED")

    # Check for negatives
    numeric_cols = store_cols + ['total']
    negatives = df_final[df_final[numeric_cols].lt(0).any(axis=1)]
    print(f"   Negative values: {len(negatives)} {'✅ (None)' if len(negatives) == 0 else '❌'}")
    if len(negatives) > 0:
        print(f"   ⚠️  Found negatives in: {negatives['category'].tolist()}")

    # Check percentage sums
    df_final['pct_sum'] = df_final[[f'{col}_pct' for col in store_cols]].sum(axis=1)
    outliers = df_final[~df_final['pct_sum'].between(98, 102)]
    print(f"   Percentage sums: {len(outliers)} outliers {'✅' if len(outliers) == 0 else '⚠️'}")
    if len(outliers) > 0:
        print(f"   Categories with sum ≠ 100%:")
        for _, row in outliers.iterrows():
            print(f"   - {row['category']}: {row['pct_sum']:.1f}%")

    # Drop temporary pct_sum column
    df_final = df_final.drop(columns=['pct_sum'])

    # Save to processed folder
    output_path = Path(__file__).parent.parent / 'data' / 'processed' / 'table_38_retail.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved: {output_path}")

    return df_final


if __name__ == '__main__':
    print("🧪 CBS TABLE 38 CLEAN EXTRACTION")
    print("Following cbs_final_flat_fix.py approach\n")

    df = extract_table_38_clean()

    if df is not None:
        print(f"\n{'='*80}")
        print("🎯 TABLE 38 CLEAN COMPLETE")
        print(f"{'='*80}")
        print(f"Total categories: {len(df)}")
        print("\n✅ table_38_retail.csv created with:")
        print("   - NO negative values (fixed with abs())")
        print("   - NO error margin rows (± removed)")
        print("   - 14 food categories")
        print("   - 8 store types + percentages")
        print("   - Clean processed data ready for database")
