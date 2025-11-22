"""
Extract Table 38: Food Expenditure by Store Type
Focus: Retail Battle - Store Competition Analysis

CBS Column Structure (Row 8 = Header):
- Column A (0): Category name (Hebrew)
- Column B (1): Other (אחר)
- Column C (2): Special shop (חנות מיוחדת) - wine/specialty stores
- Column D (3): Butcher (אטליז)
- Column E (4): Veg/Fruit shop (חנות ירקות ופירות)
- Column F (5): Online Supermarket (רשת מקוון)
- Column G (6): Supermarket Chain (רשתות סופרמרקט) ← MAIN RETAIL CHANNEL
- Column H (7): Market (שוק) - outdoor markets
- Column I (8): Grocery (מכולת) - corner stores
- Column J (9): Total (סך הכל)

Data Structure:
- Row N: Data row (spending amounts in NIS per household per month)
- Row N+1: Error margin row (with ± symbols) → SKIP

CBS Statistical Notation:
- ".." = Suppressed data (privacy/reliability) → Store as 0.0
- "(value)" = Low reliability → Extract value, keep as-is
- Negative = Statistical adjustment → Keep as-is
"""

import sys
import pandas as pd
from pathlib import Path
import logging

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_cbs_value(val):
    """
    Clean CBS statistical notation

    Returns: (cleaned_value, is_suppressed, is_low_reliability)
    """
    if pd.isna(val):
        return 0.0, False, False

    val_str = str(val).strip()

    # Handle ".." (suppressed data)
    if val_str == '..':
        return 0.0, True, False

    # Handle parentheses (low reliability indicator)
    is_low_reliability = '(' in val_str or ')' in val_str
    val_str = val_str.replace('(', '').replace(')', '')

    # Try to convert to float
    try:
        cleaned = float(val_str)
        return cleaned, False, is_low_reliability
    except:
        return 0.0, False, False


def load_table_38():
    """
    Load Table 38: הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות
    Returns: DataFrame with food expenditure by store type (8 store types)
    """
    logger.info("Loading Table 38 (Store Type)...")

    project_root = Path(__file__).parent.parent.parent
    filepath = project_root / 'CBS Household Expenditure Data Strategy' / 'הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות.xlsx'

    if not filepath.exists():
        raise FileNotFoundError(f"CBS Excel file not found: {filepath}")

    # Load with header row 7 (0-indexed row 7 = visual row 8)
    df = pd.read_excel(filepath, header=7, engine='openpyxl')
    df = df.dropna(how='all')

    logger.info(f"Loaded {len(df)} rows from CBS Excel")
    logger.info(f"Columns: {df.columns.tolist()}")

    # Extract store type data
    stores = []
    skipped_rows = 0

    for idx, row in df.iterrows():
        # Category is in column 0 (English name or Hebrew)
        category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None

        if not category or category == 'nan':
            continue

        # Skip error margin rows (contain ± symbol)
        if '±' in category:
            skipped_rows += 1
            continue

        # Skip metadata rows
        if category.lower() in ['total', 'sum', 'סך הכל']:
            continue

        # Extract 8 store types from columns B-I (indices 1-8)
        # Plus total from column J (index 9)
        try:
            # Columns B-I: 8 store types
            vals = []
            suppressed_flags = []
            low_reliability_flags = []

            for i in range(1, 9):  # Columns B-I (indices 1-8)
                val = row.iloc[i] if i < len(row) else None
                cleaned, is_suppressed, is_low_reliability = clean_cbs_value(val)
                vals.append(cleaned)
                suppressed_flags.append(is_suppressed)
                low_reliability_flags.append(is_low_reliability)

            # Column J: Total (index 9)
            total_val = row.iloc[9] if len(row) > 9 else None
            total, _, _ = clean_cbs_value(total_val)

            # If total is 0 or missing, calculate from individual values
            if total == 0 or total < sum(vals):
                total = sum(vals)

            # Skip if no meaningful data (total < 1 NIS)
            if total < 1:
                continue

            # Calculate percentages (within each row, should sum to ~100%)
            other_pct = (vals[0] / total * 100) if total > 0 else 0
            special_shop_pct = (vals[1] / total * 100) if total > 0 else 0
            butcher_pct = (vals[2] / total * 100) if total > 0 else 0
            veg_fruit_shop_pct = (vals[3] / total * 100) if total > 0 else 0
            online_supermarket_pct = (vals[4] / total * 100) if total > 0 else 0
            supermarket_chain_pct = (vals[5] / total * 100) if total > 0 else 0
            market_pct = (vals[6] / total * 100) if total > 0 else 0
            grocery_pct = (vals[7] / total * 100) if total > 0 else 0

            stores.append({
                'category': category,
                # Spending amounts (NIS per household per month)
                'other': vals[0],                        # Column B
                'special_shop': vals[1],                 # Column C
                'butcher': vals[2],                      # Column D
                'veg_fruit_shop': vals[3],              # Column E
                'online_supermarket': vals[4],           # Column F
                'supermarket_chain': vals[5],            # Column G ← CRITICAL!
                'market': vals[6],                       # Column H
                'grocery': vals[7],                      # Column I
                'total': total,                          # Column J
                # Percentages (for analysis)
                'other_pct': round(other_pct, 1),
                'special_shop_pct': round(special_shop_pct, 1),
                'butcher_pct': round(butcher_pct, 1),
                'veg_fruit_shop_pct': round(veg_fruit_shop_pct, 1),
                'online_supermarket_pct': round(online_supermarket_pct, 1),
                'supermarket_chain_pct': round(supermarket_chain_pct, 1),
                'market_pct': round(market_pct, 1),
                'grocery_pct': round(grocery_pct, 1),
            })
        except Exception as e:
            logger.warning(f"Failed to process row {idx} ({category}): {e}")
            continue

    df_clean = pd.DataFrame(stores)
    logger.info(f"Extracted {len(df_clean)} categories with store type data")
    logger.info(f"Skipped {skipped_rows} error margin rows")

    return df_clean


def analyze_retail_competition(df):
    """
    Analyze Retail Battle: Store Competition
    """
    # Calculate market shares (aggregate spending across all categories)
    total_supermarket_chain = df['supermarket_chain'].sum()
    total_market = df['market'].sum()
    total_grocery = df['grocery'].sum()
    total_special_shop = df['special_shop'].sum()
    total_butcher = df['butcher'].sum()
    total_veg_fruit = df['veg_fruit_shop'].sum()
    total_online = df['online_supermarket'].sum()
    total_other = df['other'].sum()

    grand_total = (total_supermarket_chain + total_market + total_grocery +
                   total_special_shop + total_butcher + total_veg_fruit +
                   total_online + total_other)

    supermarket_chain_share = (total_supermarket_chain / grand_total * 100) if grand_total > 0 else 0
    market_share = (total_market / grand_total * 100) if grand_total > 0 else 0
    grocery_share = (total_grocery / grand_total * 100) if grand_total > 0 else 0
    special_shop_share = (total_special_shop / grand_total * 100) if grand_total > 0 else 0

    # Find categories where supermarket chain loses to outdoor markets
    df_analysis = df.copy()
    supermarket_loses = df_analysis[df_analysis['market_pct'] > df_analysis['supermarket_chain_pct']].sort_values('market_pct', ascending=False)

    # Find categories where supermarket chain dominates
    supermarket_wins = df_analysis.sort_values('supermarket_chain_pct', ascending=False)

    return {
        'supermarket_chain_share': supermarket_chain_share,
        'market_share': market_share,
        'grocery_share': grocery_share,
        'special_shop_share': special_shop_share,
        'supermarket_loses': supermarket_loses.head(5)[['category', 'supermarket_chain_pct', 'market_pct']].to_dict('records'),
        'supermarket_wins': supermarket_wins.head(5)[['category', 'supermarket_chain_pct', 'market_pct', 'grocery_pct']].to_dict('records')
    }


def main():
    """Extract and analyze Table 38"""
    print("=" * 80)
    print("TABLE 38: RETAIL BATTLE ANALYSIS - CBS Store Type Competition")
    print("=" * 80)

    df = load_table_38()

    print(f"\n✅ Extracted {len(df)} food categories")
    print(f"\n📊 Sample store distribution (first 5 categories):")
    print(df.head(5)[['category', 'supermarket_chain', 'market', 'grocery', 'special_shop']])

    # Verify critical test case: Alcoholic beverages
    alcoholic = df[df['category'].str.contains('lcoholic', case=False, na=False)]
    if not alcoholic.empty:
        print(f"\n🧪 VERIFICATION TEST CASE: Alcoholic Beverages")
        print(alcoholic[['category', 'special_shop', 'supermarket_chain', 'grocery', 'total']].to_string(index=False))
        print(f"\nPercentages:")
        print(alcoholic[['category', 'special_shop_pct', 'supermarket_chain_pct', 'grocery_pct']].to_string(index=False))

        # Expected values from user's screenshot:
        # special_shop = 30.4%, supermarket_chain = 51.1%, grocery = 11.4%
        row = alcoholic.iloc[0]
        print(f"\n🎯 EXPECTED (from CBS screenshot): special_shop=30.4%, supermarket_chain=51.1%, grocery=11.4%")
        print(f"🎯 ACTUAL: special_shop={row['special_shop_pct']}%, supermarket_chain={row['supermarket_chain_pct']}%, grocery={row['grocery_pct']}%")

        # Verification
        if abs(row['special_shop_pct'] - 30.4) < 1 and abs(row['supermarket_chain_pct'] - 51.1) < 1 and abs(row['grocery_pct'] - 11.4) < 1:
            print("✅ VERIFICATION PASSED: ETL matches CBS data!")
        else:
            print("❌ VERIFICATION FAILED: ETL output does NOT match CBS data!")

    # Analyze competition
    analysis = analyze_retail_competition(df)

    print(f"\n=== RETAIL MARKET SHARES (Aggregate) ===")
    print(f"Supermarket Chain: {analysis['supermarket_chain_share']:.1f}%")
    print(f"Outdoor Market: {analysis['market_share']:.1f}%")
    print(f"Grocery/Corner Store: {analysis['grocery_share']:.1f}%")
    print(f"Special Shop (Wine/Specialty): {analysis['special_shop_share']:.1f}%")

    print(f"\n=== Top 5: Where Supermarket Chains DOMINATE ===")
    for item in analysis['supermarket_wins']:
        print(f"  {item['category']}: Supermarket {item['supermarket_chain_pct']:.1f}% vs Market {item['market_pct']:.1f}%")

    print(f"\n=== Top 5: Where Outdoor Markets WIN ===")
    for item in analysis['supermarket_loses']:
        print(f"  {item['category']}: Market {item['market_pct']:.1f}% vs Supermarket {item['supermarket_chain_pct']:.1f}%")

    # Save
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'table_38_retail.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n[+] Saved to {output_file}")

    # Verify percentages sum to ~100%
    print(f"\n🔍 Data Quality Check:")
    df['pct_sum'] = (df['other_pct'] + df['special_shop_pct'] + df['butcher_pct'] +
                     df['veg_fruit_shop_pct'] + df['online_supermarket_pct'] +
                     df['supermarket_chain_pct'] + df['market_pct'] + df['grocery_pct'])

    outliers = df[~df['pct_sum'].between(98, 102)]
    if len(outliers) > 0:
        print(f"⚠️  {len(outliers)} categories have percentages NOT summing to 100%:")
        print(outliers[['category', 'pct_sum']])
    else:
        print(f"✅ All {len(df)} categories have percentages summing to ~100%")


if __name__ == '__main__':
    main()
