"""
FIXED CBS Extractor - Properly extracts REAL product expenditure data
Based on correct methodology for messy Israeli government Excel files
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import re

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_header_row(df):
    """
    Detect the real header row in CBS Excel
    Header row usually contains mostly strings, not NaN or numbers
    """
    for i, row in df.iterrows():
        # Count how many cells look like column labels (strings)
        string_count = row.apply(lambda x: isinstance(x, str)).sum()
        if string_count >= (len(row) * 0.5):
            logger.info(f"Found header row at index {i}")
            return i
    logger.warning("Could not find header row, using row 0")
    return 0


def remove_footnotes(df):
    """
    Remove footnote rows (contain parentheses with numbers like (1))
    """
    # Remove rows where first column contains footnote markers
    df = df[~df.iloc[:,0].astype(str).str.contains(r"\(\d+\)", na=False)]
    # Remove rows with "Note" or "הערה"
    df = df[~df.iloc[:,0].astype(str).str.contains("^(\\(|Note|הערה)", na=False)]
    return df


def normalize_column_names(df):
    """
    Normalize column names (remove special chars, lowercase)
    """
    df.columns = (
        df.columns.astype(str)
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\wא-ת]", "", regex=True)
        .str.lower()
    )
    return df


def convert_numeric_columns(df):
    """
    Convert numeric columns from strings to actual numbers
    """
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return df


def load_and_clean_cbs(filepath):
    """
    Full pipeline to load and clean CBS Excel file
    """
    logger.info(f"Loading {filepath.name}...")

    # Load without header first
    df_raw = pd.read_excel(filepath, header=None, engine='openpyxl')
    logger.info(f"Raw shape: {df_raw.shape}")

    # Find header row
    header_row = find_header_row(df_raw)

    # Re-load with correct header
    df = pd.read_excel(filepath, header=header_row, engine='openpyxl')
    logger.info(f"Shape after header detection: {df.shape}")

    # Remove empty rows
    df = df.dropna(how='all')

    # Remove footnotes
    df = remove_footnotes(df)

    # Normalize column names
    df = normalize_column_names(df)

    # Convert numeric columns
    df = convert_numeric_columns(df)

    logger.info(f"Final cleaned shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)[:5]}...")

    return df


def extract_product_categories(df):
    """
    Extract product categories with spending amounts by quintile
    """
    categories = []

    # Assuming structure:
    # Col 0: English product name
    # Cols 1-5: Quintile spending (Q5, Q4, Q3, Q2, Q1)

    for idx, row in df.iterrows():
        # Skip if first column is empty or looks like a header
        first_col = str(row.iloc[0]).strip()

        if not first_col or first_col == 'nan' or first_col == 'NULL':
            continue

        # Skip if it's a statistical metadata row
        skip_words = ['average', 'total', 'households', 'persons', 'income',
                      'expenditure', 'payment', 'age', 'earners', 'schooling',
                      'median', 'gross', 'net', 'compulsory', 'transfer']
        if any(word in first_col.lower() for word in skip_words):
            continue

        # Skip rows that are just error margins (start with ±)
        if first_col.startswith('±') or first_col.startswith('NULL'):
            continue

        # Try to extract spending amounts (should be in columns 1-5)
        try:
            # Get quintile values (Q5, Q4, Q3, Q2, Q1)
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

            # Only keep if we have at least some valid spending data
            if sum(amounts) > 0:
                categories.append({
                    'category_english': first_col,
                    'quintile_5': amounts[0] if len(amounts) > 0 else 0.0,
                    'quintile_4': amounts[1] if len(amounts) > 1 else 0.0,
                    'quintile_3': amounts[2] if len(amounts) > 2 else 0.0,
                    'quintile_2': amounts[3] if len(amounts) > 3 else 0.0,
                    'quintile_1': amounts[4] if len(amounts) > 4 else 0.0,
                    'avg_spending': np.mean(amounts)
                })
        except Exception as e:
            # Skip problematic rows
            continue

    logger.info(f"Extracted {len(categories)} product categories")
    return pd.DataFrame(categories)


def main():
    """Run the fixed extraction"""
    print("=" * 70)
    print("FIXED CBS DATA EXTRACTION")
    print("Extracting REAL product expenditure categories")
    print("=" * 70)
    print()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    cbs_data_dir = project_root / 'CBS Household Expenditure Data Strategy'
    output_dir = project_root / 'data' / 'processed'

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load and clean the main expenditure file
    filepath = cbs_data_dir / 'הוצאות לתצרוכת למשק בית מוצרים מפורטים.xlsx'

    df_clean = load_and_clean_cbs(filepath)

    # Extract product categories
    df_categories = extract_product_categories(df_clean)

    print(f"\n[+] Extracted {len(df_categories)} product categories")
    print(f"\nFirst 10 categories:")
    print(df_categories.head(10)[['category_english', 'avg_spending']])

    print(f"\nLast 10 categories:")
    print(df_categories.tail(10)[['category_english', 'avg_spending']])

    # Validate - make sure we got REAL products
    print(f"\n=== VALIDATION ===")
    print(f"Total categories: {len(df_categories)}")
    print(f"Categories with spending > 0: {(df_categories['avg_spending'] > 0).sum()}")
    print(f"Average spending range: ILS {df_categories['avg_spending'].min():.2f} - ILS {df_categories['avg_spending'].max():.2f}")

    # Check for product keywords (should find food items, etc.)
    food_keywords = ['bread', 'rice', 'meat', 'milk', 'fruit', 'vegetable']
    has_food = df_categories['category_english'].str.lower().str.contains('|'.join(food_keywords), case=False, na=False).any()
    print(f"Contains food products: {has_food}")

    # Save
    output_file = output_dir / 'cbs_categories_REAL.csv'
    df_categories.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n[+] Saved to {output_file.name}")


if __name__ == '__main__':
    main()
