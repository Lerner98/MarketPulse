"""
Extract Table 40: Purchase Method Analysis (Online vs Physical)
Focus: Digital Opportunity Matrix - Israel vs Abroad online purchases
"""

import sys
import pandas as pd
from pathlib import Path
import logging

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_header_row(df):
    """Detect the real header row"""
    for i, row in df.iterrows():
        string_count = row.apply(lambda x: isinstance(x, str)).sum()
        if string_count >= (len(row) * 0.5):
            return i
    return 0


def load_table_40():
    """
    Load Table 40: רכישות מוצרים נבחרים לפי אופן
    Returns: DataFrame with online vs physical purchase breakdown
    """
    logger.info("Loading Table 40 (Purchase Method)...")

    project_root = Path(__file__).parent.parent.parent
    filepath = project_root / 'CBS Household Expenditure Data Strategy' / 'רכישות מוצרים נבחרים לפי אופן.xlsx'

    # Load with header row 7
    df = pd.read_excel(filepath, header=7, engine='openpyxl')
    df = df.dropna(how='all')

    # Extract purchase method data
    purchases = []

    for idx, row in df.iterrows():
        # Category is in column 1 (Hebrew)
        category = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None

        if not category or category == 'nan':
            continue

        # Skip metadata rows and bad data
        if '±' in category or '..' in category:
            continue
        if category in ['אחוזים', 'Percentages', '2022']:
            continue

        # Extract percentages from columns 3-5 (Physical, Online Israel, Online Abroad)
        try:
            vals = []
            for i in range(3, 6):  # Columns 3, 4, 5
                val = row.iloc[i] if i < len(row) else 0
                if pd.notna(val) and isinstance(val, (int, float)):
                    vals.append(float(val))
                else:
                    vals.append(0.0)

            # Only keep if we have data
            if sum(vals) > 10:  # At least 10% total
                physical_pct = vals[0]
                online_israel_pct = vals[1]
                online_abroad_pct = vals[2]

                purchases.append({
                    'category': category,
                    'physical_pct': physical_pct,
                    'online_israel_pct': online_israel_pct,
                    'online_abroad_pct': online_abroad_pct
                })
        except:
            continue

    df_clean = pd.DataFrame(purchases)
    logger.info(f"Extracted {len(df_clean)} categories with purchase method data")

    return df_clean


def analyze_digital_penetration(df):
    """
    Create Digital Opportunity Matrix
    """
    # Sort by online Israel percentage
    df_sorted = df.sort_values('online_israel_pct', ascending=False)

    insight = {
        'top_israel_online': df_sorted.head(3)[['category', 'online_israel_pct']].to_dict('records'),
        'top_abroad_online': df.sort_values('online_abroad_pct', ascending=False).head(3)[['category', 'online_abroad_pct']].to_dict('records'),
        'most_physical': df.sort_values('physical_pct', ascending=False).head(3)[['category', 'physical_pct']].to_dict('records')
    }

    return insight


def main():
    """Extract and analyze Table 40"""
    print("=" * 70)
    print("TABLE 40: DIGITAL OPPORTUNITY MATRIX")
    print("=" * 70)

    df = load_table_40()

    print(f"\nExtracted {len(df)} categories")
    print(f"\nSample purchase methods:")
    print(df.head(10)[['category', 'online_israel_pct', 'online_abroad_pct', 'physical_pct']])

    # Analyze digital penetration
    analysis = analyze_digital_penetration(df)

    print(f"\n=== DIGITAL INSIGHTS ===")
    print(f"\nTop Israel Online Categories:")
    for item in analysis['top_israel_online']:
        print(f"  {item['category']}: {item['online_israel_pct']:.1f}%")

    print(f"\nTop Abroad Online Categories:")
    for item in analysis['top_abroad_online']:
        print(f"  {item['category']}: {item['online_abroad_pct']:.1f}%")

    # Save
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed'
    output_file = output_dir / 'table_40_digital.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n[+] Saved to {output_file.name}")


if __name__ == '__main__':
    main()
