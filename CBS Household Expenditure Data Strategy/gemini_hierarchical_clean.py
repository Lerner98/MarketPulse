"""
GEMINI HIERARCHICAL CLEANING PIPELINE
Preserves CBS data structure with hierarchy levels to prevent double-counting
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')


def clean_cbs_value(val):
    """Sanitize CBS values - keep values POSITIVE (CBS parentheses ≠ negatives)"""
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


def detect_hierarchy_level(item_name, prev_total):
    """
    Detect if row is:
    - Level 0: Main section header (e.g., "Food", "Housing")
    - Level 1: Subcategory (e.g., "Bread", "Meat")
    - Level 2: Detail item (e.g., "White bread", "Beef")

    Heuristics:
    - Section headers have LARGE totals (> 1000 NIS typically)
    - Detail items have smaller totals
    - ALL CAPS or specific keywords indicate headers
    """
    # Check for section header keywords
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

    # Level 2: Very specific items (long names with commas or detailed descriptions)
    if ',' in item_name or len(item_name.split()) > 6:
        return 2

    # Default: Level 1 (subcategories)
    return 1


def process_hierarchical_cbs(file_path, header_row=None):
    """
    Process CBS file preserving hierarchical structure
    """
    print(f"\n{'='*80}")
    print(f"HIERARCHICAL PROCESSING: {file_path.name}")
    print(f"{'='*80}")

    if not file_path.exists():
        print(f"❌ FILE NOT FOUND")
        return None

    # Load raw data
    df_raw = pd.read_excel(file_path, header=None, engine='openpyxl')
    print(f"📊 Raw rows: {len(df_raw)}")

    # Find anchor row
    anchor_row = None
    if header_row is None:
        for idx, row in df_raw.iterrows():
            row_values = [str(x) for x in row.tolist() if pd.notna(x)]
            if '5' in row_values and '4' in row_values and '3' in row_values and '2' in row_values and '1' in row_values:
                anchor_row = idx
                print(f"🎯 Anchor at row {idx}")
                break
    else:
        anchor_row = header_row

    if anchor_row is None:
        print("❌ No anchor found")
        return None

    # Reload with header
    df = pd.read_excel(file_path, header=anchor_row, engine='openpyxl')

    # Clean data with hierarchy detection
    cleaned_data = []
    stats = {'error': 0, 'garbage': 0, 'footnote': 0, 'empty': 0}
    prev_total = 0

    for idx, row in df.iterrows():
        item_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None

        if not item_name or item_name == 'nan':
            stats['empty'] += 1
            continue

        # Skip ± error rows
        if '±' in item_name:
            stats['error'] += 1
            continue

        # Skip CBS table headers
        if ('TABLE' in item_name.upper() and any(x in item_name for x in ['1.1', '3.8', '4.0'])) or \
           (item_name.upper() in ['EXPENDITURE', 'CONSUMPTION', 'TOTAL CONSUMPTION']):
            stats['garbage'] += 1
            continue

        # Skip footnotes (only numbered footnotes like "(1) In 2018...")
        if (item_name.startswith('(') and len(item_name) > 2 and item_name[1].isdigit()) or \
           (item_name.lower().startswith('from ') and 'chain' in item_name.lower()):
            stats['footnote'] += 1
            continue

        # Skip orphan footnote fragments (no capital letter start)
        if len(item_name) > 0 and not item_name[0].isupper() and not item_name[0].isdigit():
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
        total_val = row_data.get('col_6', 0) or 0  # Total is usually col 6
        hierarchy_level = detect_hierarchy_level(item_name, prev_total)
        row_data['hierarchy_level'] = hierarchy_level
        prev_total = total_val

        cleaned_data.append(row_data)

    df_cleaned = pd.DataFrame(cleaned_data)

    print(f"\n✅ Cleaned: {len(df_cleaned)} rows")
    print(f"🗑️  Skipped: ± rows={stats['error']}, garbage={stats['garbage']}, footnotes={stats['footnote']}, empty={stats['empty']}")
    print(f"\n📊 Hierarchy breakdown:")
    print(df_cleaned['hierarchy_level'].value_counts().sort_index())

    return df_cleaned


def clean_table_11_hierarchical():
    """Clean Table 1.1 with hierarchy preservation"""
    filepath = Path(__file__).parent / 'הוצאה לתצרוכת למשק בית עם מוצרים מפורטים.xlsx'
    df = process_hierarchical_cbs(filepath)

    if df is None:
        return None

    # Map to quintiles
    df_final = pd.DataFrame({
        'Item_English': df['category'],
        'hierarchy_level': df['hierarchy_level'],
        'Q5': df['col_1'],
        'Q4': df['col_2'],
        'Q3': df['col_3'],
        'Q2': df['col_4'],
        'Q1': df['col_5'],
        'Total': df['col_6']
    })

    # Show sample by hierarchy
    print("\n📊 SAMPLE BY HIERARCHY LEVEL:")
    for level in sorted(df_final['hierarchy_level'].unique()):
        print(f"\n--- Level {level} ---")
        sample = df_final[df_final['hierarchy_level'] == level].head(3)
        print(sample[['Item_English', 'Total']].to_string(index=False))

    # Save
    output_path = Path(__file__).parent.parent / 'data' / 'raw' / 'gemini_hierarchical_table_11.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved: {output_path}")

    return df_final


if __name__ == '__main__':
    print("🧪 GEMINI HIERARCHICAL CLEANING PIPELINE")
    print("Preserves CBS structure with hierarchy levels\n")

    df = clean_table_11_hierarchical()

    if df is not None:
        print(f"\n{'='*80}")
        print("🎯 FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Total rows: {len(df)}")
        print(f"Level 0 (sections): {len(df[df['hierarchy_level'] == 0])}")
        print(f"Level 1 (subcategories): {len(df[df['hierarchy_level'] == 1])}")
        print(f"Level 2 (details): {len(df[df['hierarchy_level'] == 2])}")
        print("\n✅ Use 'hierarchy_level' to filter for visualization:")
        print("   - Level 0 only: Top-level overview (prevents double-counting)")
        print("   - Level 1: Category breakdown")
        print("   - Level 2: Detailed items")
