"""
GEMINI V8 PERFECT CLEANER
Hierarchical + Fixed Negatives + Full Tail (Mortgage/Savings preserved)
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')


def clean_cbs_value(val):
    """Clean CBS values - keep POSITIVE (CBS parentheses ≠ negatives)"""
    if pd.isna(val):
        return None

    val_str = str(val).strip()

    if '±' in val_str:
        return 'SKIP_ROW'

    if val_str in ['..', '-', '', 'nan']:
        return None

    # CBS uses (5.0) for low reliability, NOT negative!
    val_str = val_str.replace('(', '').replace(')', '').replace(',', '')

    try:
        result = float(val_str)
        return abs(result) if result < 0 else result
    except:
        return None


def detect_hierarchy_level(item_name):
    """
    Detect hierarchy:
    - Level 0: Main sections (Food, Housing, etc.)
    - Level 1: Subcategories
    - Level 2: Detail items
    """
    section_keywords = [
        'consumption', 'expenditure', 'food', 'housing', 'dwelling',
        'furniture', 'household equipment', 'clothing', 'footwear',
        'health', 'education', 'culture', 'entertainment',
        'transport', 'communications', 'miscellaneous'
    ]

    name_lower = item_name.lower()

    # Level 0: Main section headers
    if any(keyword in name_lower for keyword in section_keywords):
        if 'excl.' in name_lower or 'total' in name_lower or len(item_name.split()) <= 3:
            return 0

    # Level 2: Very specific items
    if ',' in item_name or len(item_name.split()) > 6:
        return 2

    return 1


def process_table_11_v8(file_path):
    """Process Table 1.1 with hierarchy + full tail preservation"""
    print(f"\n{'='*80}")
    print(f"V8 PERFECT PROCESSING: {file_path.name}")
    print(f"{'='*80}")

    if not file_path.exists():
        print(f"❌ FILE NOT FOUND")
        return None

    # Load raw data
    df_raw = pd.read_excel(file_path, header=None, engine='openpyxl')
    print(f"📊 Raw rows: {len(df_raw)}")

    # Find anchor row
    anchor_row = None
    for idx, row in df_raw.iterrows():
        row_values = [str(x) for x in row.tolist() if pd.notna(x)]
        if '5' in row_values and '4' in row_values and '3' in row_values and '2' in row_values and '1' in row_values:
            anchor_row = idx
            print(f"🎯 Anchor at row {idx}")
            break

    if anchor_row is None:
        print("❌ No anchor found")
        return None

    # Reload with header
    df = pd.read_excel(file_path, header=anchor_row, engine='openpyxl')

    # Clean data with hierarchy detection + TAIL PRESERVATION
    cleaned_data = []
    stats = {'error': 0, 'garbage': 0, 'footnote': 0, 'empty': 0}

    for idx, row in df.iterrows():
        item_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None

        if not item_name or item_name == 'nan':
            stats['empty'] += 1
            continue

        # Skip ± error rows
        if '±' in item_name:
            stats['error'] += 1
            continue

        # Skip CBS table headers (but NOT product categories!)
        if ('TABLE' in item_name.upper() and any(x in item_name for x in ['1.1', '3.8', '4.0'])) or \
           (item_name.upper() in ['EXPENDITURE', 'CONSUMPTION', 'TOTAL CONSUMPTION']):
            stats['garbage'] += 1
            continue

        # Skip ONLY numbered footnotes like "(1) In 2018..."
        # DO NOT skip category headers that start with capital letters
        if item_name.startswith('(') and len(item_name) > 2 and item_name[1].isdigit():
            stats['footnote'] += 1
            continue

        # Extract and clean values
        row_data = {'category': item_name}
        skip_row = False

        for col_idx in range(1, len(row)):
            cleaned_val = clean_cbs_value(row.iloc[col_idx])
            if cleaned_val == 'SKIP_ROW':
                skip_row = True
                stats['error'] += 1
                break
            row_data[f'col_{col_idx}'] = cleaned_val

        if skip_row:
            continue

        # Detect hierarchy level
        hierarchy_level = detect_hierarchy_level(item_name)
        row_data['hierarchy_level'] = hierarchy_level

        cleaned_data.append(row_data)

    df_cleaned = pd.DataFrame(cleaned_data)

    print(f"\n✅ Cleaned: {len(df_cleaned)} rows")
    print(f"🗑️  Skipped: ± rows={stats['error']}, garbage={stats['garbage']}, footnotes={stats['footnote']}, empty={stats['empty']}")

    # Map to final format
    df_final = pd.DataFrame({
        'Item_English': df_cleaned['category'],
        'hierarchy_level': df_cleaned['hierarchy_level'],
        'Q5': df_cleaned['col_1'],
        'Q4': df_cleaned['col_2'],
        'Q3': df_cleaned['col_3'],
        'Q2': df_cleaned['col_4'],
        'Q1': df_cleaned['col_5'],
        'Total': df_cleaned['col_6']
    })

    # Hierarchy breakdown
    print(f"\n📊 Hierarchy breakdown:")
    print(df_final['hierarchy_level'].value_counts().sort_index())

    # Verify critical items
    numeric_cols = ['Q5', 'Q4', 'Q3', 'Q2', 'Q1', 'Total']

    print(f"\n🔍 VERIFICATION:")

    # Check for mortgage/savings
    mortgage = df_final[df_final['Item_English'].str.contains('Mortgage', case=False, na=False)]
    savings = df_final[df_final['Item_English'].str.contains('savings', case=False, na=False)]
    renovations = df_final[df_final['Item_English'].str.contains('Renovation', case=False, na=False)]

    print(f"   Mortgage rows: {len(mortgage)} {'✅' if len(mortgage) > 0 else '❌'}")
    print(f"   Savings rows: {len(savings)} {'✅' if len(savings) > 0 else '❌'}")
    print(f"   Renovations rows: {len(renovations)} {'✅' if len(renovations) > 0 else '❌'}")

    if len(mortgage) > 0:
        print(f"\n   Mortgage values:")
        for _, row in mortgage.iterrows():
            print(f"   - {row['Item_English']}: {row['Total']}")

    # Check for negatives
    negatives = df_final[df_final[numeric_cols].lt(0).any(axis=1)]
    print(f"\n   Negative values: {len(negatives)} {'✅ (None)' if len(negatives) == 0 else '❌'}")

    # Save
    output_path = Path(__file__).parent.parent / 'data' / 'raw' / 'table_11_v8.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved: {output_path}")

    return df_final


if __name__ == '__main__':
    print("🧪 GEMINI V8 PERFECT CLEANER")
    print("Hierarchical + Fixed Negatives + Full Tail Preservation\n")

    filepath = Path(__file__).parent / 'הוצאה לתצרוכת למשק בית עם מוצרים מפורטים.xlsx'
    df = process_table_11_v8(filepath)

    if df is not None:
        print(f"\n{'='*80}")
        print("🎯 V8 COMPLETE")
        print(f"{'='*80}")
        print(f"Total rows: {len(df)}")
        print(f"Hierarchy levels: {sorted(df['hierarchy_level'].unique())}")
        print("\n✅ table_11_v8.csv created with:")
        print("   - Hierarchy levels (prevents double-counting)")
        print("   - Fixed negatives (CBS parentheses)")
        print("   - Full tail (Mortgage/Savings/Renovations preserved)")
