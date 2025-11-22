"""
Extract Table 1.1: Household Expenditure by Income Quintile
Focus: Get the 1.76x Rule data (Q5 vs Q1 spending patterns)
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_header_row(df):
    """Detect the real header row in CBS Excel"""
    for i, row in df.iterrows():
        string_count = row.apply(lambda x: isinstance(x, str)).sum()
        if string_count >= (len(row) * 0.5):
            logger.info(f"Found header row at index {i}")
            return i
    return 0


def remove_footnotes(df):
    """Remove footnote rows"""
    df = df[~df.iloc[:,0].astype(str).str.contains(r"\(\d+\)", na=False)]
    df = df[~df.iloc[:,0].astype(str).str.contains("^(\\(|Note|הערה)", na=False)]
    return df


def load_table_1_1():
    """
    Load Table 1.1: הוצאה לתצרוכת למשק בית עם מוצרים מפורטים
    Returns: Clean DataFrame with category expenditure by quintile
    """
    logger.info("Loading Table 1.1 (Quintile Expenditure)...")

    project_root = Path(__file__).parent.parent.parent
    filepath = project_root / 'CBS Household Expenditure Data Strategy' / 'הוצאה לתצרוכת למשק בית עם מוצרים מפורטים.xlsx'

    # Load raw
    df_raw = pd.read_excel(filepath, header=None, engine='openpyxl')
    logger.info(f"Raw shape: {df_raw.shape}")

    # Find header
    header_row = find_header_row(df_raw)

    # Reload with header
    df = pd.read_excel(filepath, header=header_row, engine='openpyxl')

    # Clean
    df = df.dropna(how='all')
    df = remove_footnotes(df)

    # Extract meaningful categories with quintile data
    categories = []

    for idx, row in df.iterrows():
        first_col = str(row.iloc[0]).strip()

        # Skip empty or invalid rows
        if not first_col or first_col == 'nan':
            continue

        # Skip metadata rows
        skip_words = ['average', 'total', 'households', 'persons', 'income',
                      'median', 'gross', 'net', 'compulsory']
        if any(word in first_col.lower() for word in skip_words):
            continue

        # Extract quintile spending (columns 1-5)
        try:
            amounts = []
            for i in range(1, 6):
                if i < len(row):
                    val = row.iloc[i]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        amounts.append(float(val))
                    else:
                        amounts.append(0.0)
                else:
                    amounts.append(0.0)

            # Only keep if we have spending data
            if sum(amounts) > 0:
                categories.append({
                    'category': first_col,
                    'quintile_5': amounts[0],  # Highest income
                    'quintile_4': amounts[1],
                    'quintile_3': amounts[2],
                    'quintile_2': amounts[3],
                    'quintile_1': amounts[4],  # Lowest income
                    'total_spending': sum(amounts),
                    'avg_spending': np.mean(amounts)
                })
        except:
            continue

    df_clean = pd.DataFrame(categories)
    logger.info(f"Extracted {len(df_clean)} categories with quintile data")

    return df_clean


def calculate_quintile_gap(df):
    """
    Calculate the 1.76x Rule: Q5 vs Q1 spending ratio
    """
    q5_total = df['quintile_5'].sum()
    q1_total = df['quintile_1'].sum()

    ratio = q5_total / q1_total if q1_total > 0 else 0

    return {
        'ratio': round(ratio, 2),
        'q5_total': q5_total,
        'q1_total': q1_total,
        'insight': f"High-income households (Q5) spend {ratio:.2f}x more than low-income (Q1)"
    }


def main():
    """Extract and analyze Table 1.1"""
    print("=" * 70)
    print("TABLE 1.1: QUINTILE EXPENDITURE ANALYSIS")
    print("=" * 70)

    # Extract data
    df = load_table_1_1()

    print(f"\nExtracted {len(df)} categories")
    print(f"\nSample categories:")
    print(df.head(10)[['category', 'quintile_5', 'quintile_1', 'avg_spending']])

    # Calculate the 1.76x Rule
    gap_analysis = calculate_quintile_gap(df)

    print(f"\n=== THE 1.76x RULE ===")
    print(f"Q5 Total Spending: ₪{gap_analysis['q5_total']:,.0f}")
    print(f"Q1 Total Spending: ₪{gap_analysis['q1_total']:,.0f}")
    print(f"Spending Ratio: {gap_analysis['ratio']}x")
    print(f"\nInsight: {gap_analysis['insight']}")

    # Save
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'table_1_1_quintiles.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n[+] Saved to {output_file.name}")


if __name__ == '__main__':
    main()
