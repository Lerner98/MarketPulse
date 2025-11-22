"""
TEST ALL GEMINI CLEANING APPROACHES
Compare results and verify data integrity
"""

import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')


def test_approach_1_simple_clean():
    """Test: Simple cleaning (gemini_full_clean.py approach)"""
    print(f"\n{'='*80}")
    print("TEST 1: SIMPLE CLEAN (NO HIERARCHY)")
    print(f"{'='*80}")

    csv_path = Path(__file__).parent.parent / 'data' / 'raw' / 'gemini_full_clean_table_11.csv'

    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return None

    df = pd.read_csv(csv_path)

    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    # Check for negatives
    numeric_cols = ['Q5', 'Q4', 'Q3', 'Q2', 'Q1', 'Total']
    negatives = df[df[numeric_cols].lt(0).any(axis=1)]
    print(f"\n❌ Rows with negatives: {len(negatives)}")
    if len(negatives) > 0:
        print(negatives[['Item_English'] + numeric_cols].head())

    # Check for mortgage/savings
    critical_items = df[df['Item_English'].str.contains('Mortgage|Savings|Renovations', case=False, na=False)]
    print(f"\n✅ Critical items found: {len(critical_items)}")
    print(critical_items[['Item_English', 'Total']])

    # Test double-counting risk
    food_rows = df[df['Item_English'].str.contains('Food|Bread|Meat', case=False, na=False)]
    print(f"\n⚠️  Food-related rows (risk of double-counting): {len(food_rows)}")
    print(f"Total food spending if summed: {food_rows['Total'].sum():.2f}")

    return df


def test_approach_2_hierarchical():
    """Test: Hierarchical cleaning with levels"""
    print(f"\n{'='*80}")
    print("TEST 2: HIERARCHICAL CLEAN (WITH LEVELS)")
    print(f"{'='*80}")

    csv_path = Path(__file__).parent.parent / 'data' / 'raw' / 'gemini_hierarchical_table_11.csv'

    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return None

    df = pd.read_csv(csv_path)

    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    # Check hierarchy distribution
    print(f"\nHierarchy breakdown:")
    print(df['hierarchy_level'].value_counts().sort_index())

    # Check for negatives
    numeric_cols = ['Q5', 'Q4', 'Q3', 'Q2', 'Q1', 'Total']
    negatives = df[df[numeric_cols].lt(0).any(axis=1)]
    print(f"\n❌ Rows with negatives: {len(negatives)}")
    if len(negatives) > 0:
        print(negatives[['Item_English'] + numeric_cols].head())

    # Level 0 analysis (top sections - for dashboards)
    level_0 = df[df['hierarchy_level'] == 0]
    print(f"\n📊 Level 0 (Dashboard view - NO double-counting):")
    print(f"   Rows: {len(level_0)}")
    print(f"   Total spending if summed: {level_0['Total'].sum():.2f}")
    print("\nTop 10 sections:")
    print(level_0.nlargest(10, 'Total')[['Item_English', 'Total']])

    # Compare to full sum (should show double-counting)
    full_sum = df['Total'].sum()
    print(f"\n⚠️  DOUBLE-COUNTING TEST:")
    print(f"   Level 0 only sum: {level_0['Total'].sum():.2f}")
    print(f"   Full data sum: {full_sum:.2f}")
    print(f"   Difference: {full_sum - level_0['Total'].sum():.2f} (this is the double-count!)")

    return df


def test_data_integrity():
    """Test: Compare both approaches for data integrity"""
    print(f"\n{'='*80}")
    print("TEST 3: DATA INTEGRITY COMPARISON")
    print(f"{'='*80}")

    simple_path = Path(__file__).parent.parent / 'data' / 'raw' / 'gemini_full_clean_table_11.csv'
    hier_path = Path(__file__).parent.parent / 'data' / 'raw' / 'gemini_hierarchical_table_11.csv'

    if not simple_path.exists() or not hier_path.exists():
        print("❌ Missing files for comparison")
        return

    df_simple = pd.read_csv(simple_path)
    df_hier = pd.read_csv(hier_path)

    print(f"Simple clean rows: {len(df_simple)}")
    print(f"Hierarchical rows: {len(df_hier)}")
    print(f"Difference: {len(df_simple) - len(df_hier)} rows")

    # Check if hierarchical has LESS footnote garbage
    simple_tail = df_simple.tail(10)['Item_English'].tolist()
    hier_tail = df_hier.tail(10)['Item_English'].tolist()

    print(f"\n📋 TAIL COMPARISON (checking for footnote garbage):")
    print("\nSimple clean tail:")
    for item in simple_tail:
        print(f"  - {item}")

    print("\nHierarchical tail:")
    for item in hier_tail:
        print(f"  - {item}")

    # Find critical items in both
    critical_keywords = ['Mortgage', 'Savings', 'Renovations', 'Insurance']

    print(f"\n🔍 CRITICAL ITEMS CHECK:")
    for keyword in critical_keywords:
        simple_count = len(df_simple[df_simple['Item_English'].str.contains(keyword, case=False, na=False)])
        hier_count = len(df_hier[df_hier['Item_English'].str.contains(keyword, case=False, na=False)])

        status = "✅" if simple_count == hier_count else "❌"
        print(f"  {status} {keyword}: Simple={simple_count}, Hierarchical={hier_count}")


def test_table_38_integrity():
    """Test: Verify Table 38 (retail battle) data"""
    print(f"\n{'='*80}")
    print("TEST 4: TABLE 38 (RETAIL BATTLE) INTEGRITY")
    print(f"{'='*80}")

    csv_path = Path(__file__).parent.parent / 'data' / 'raw' / 'gemini_full_clean_table_38.csv'

    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return None

    df = pd.read_csv(csv_path)

    print(f"Total categories: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    # Check for negatives (should be NONE after fix)
    store_cols = ['Other', 'Special_Shop', 'Butcher', 'Veg_Fruit_Shop',
                  'Online_Supermarket', 'Supermarket_Chain', 'Market', 'Grocery']
    negatives = df[df[store_cols].lt(0).any(axis=1)]
    print(f"\n❌ Categories with negatives: {len(negatives)}")
    if len(negatives) > 0:
        print(negatives[['Category'] + store_cols])

    # Verify percentages sum to 100
    df['row_sum'] = df[store_cols].sum(axis=1)
    not_100 = df[~df['row_sum'].between(98, 102)]
    print(f"\n❌ Categories NOT summing to ~100%: {len(not_100)}")
    if len(not_100) > 0:
        print(not_100[['Category', 'row_sum']])

    # Verify alcoholic beverages test case
    alc = df[df['Category'].str.contains('lcoholic', case=False, na=False)]
    if not alc.empty:
        row = alc.iloc[0]
        print(f"\n🧪 ALCOHOLIC BEVERAGES VERIFICATION:")
        print(f"   Special_Shop: {row['Special_Shop']}% (expected: 30.4)")
        print(f"   Supermarket_Chain: {row['Supermarket_Chain']}% (expected: 51.1)")
        print(f"   Grocery: {row['Grocery']}% (expected: 11.4)")
        print(f"   Total: {row['Total']}% (expected: 100.0)")

        if abs(row['Special_Shop'] - 30.4) < 1 and abs(row['Supermarket_Chain'] - 51.1) < 1 and abs(row['Grocery'] - 11.4) < 1:
            print(f"   ✅ VERIFICATION PASSED!")
        else:
            print(f"   ❌ VERIFICATION FAILED!")

    return df


if __name__ == '__main__':
    print("🧪 COMPREHENSIVE GEMINI APPROACH TESTING")
    print("Testing ALL cleaning methods to verify data integrity\n")

    # Run all tests
    df1 = test_approach_1_simple_clean()
    df2 = test_approach_2_hierarchical()
    test_data_integrity()
    df38 = test_table_38_integrity()

    print(f"\n{'='*80}")
    print("🎯 FINAL RECOMMENDATIONS")
    print(f"{'='*80}")

    if df1 is not None and df2 is not None:
        print("\n📊 FOR DASHBOARD (prevents double-counting):")
        print("   USE: gemini_hierarchical_table_11.csv with hierarchy_level = 0")
        print("   Rows: ~30 top sections")
        print("   No parent+child overlap")

        print("\n📊 FOR DETAILED ANALYSIS:")
        print("   USE: gemini_hierarchical_table_11.csv with all levels")
        print("   Filter by hierarchy_level as needed")

        print("\n📊 FOR TABLE 38 (RETAIL BATTLE):")
        print("   USE: gemini_full_clean_table_38.csv")
        print("   All percentages, no hierarchy needed")
