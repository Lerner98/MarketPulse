"""
CBS Transaction Generator - PROPER Phase 2 Spec
===============================================
Generates transactions from CBS household expenditure data with CORRECT schema.

SCHEMA (10 columns ONLY):
1. transaction_id - Sequential (10000, 10001, ...)
2. customer_name - Hebrew name
3. product - Hebrew product name from CBS
4. category - Parent category name
5. amount - Amount in ILS
6. currency - Always "ILS"
7. transaction_date - YYYY-MM-DD format
8. status - completed/pending/cancelled
9. customer_city - Hebrew city
10. income_quintile - 1-5

NO emails, phones, payment methods, traffic sources, or device types.
This is household expenditure data, NOT e-commerce analytics data.
"""

import sys
import pandas as pd
import numpy as np
import random
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CBSProperTransactionGenerator:
    """
    Generate CBS household expenditure transactions with PROPER schema

    Follows Phase 2 specification:
    - 10 columns only
    - No e-commerce metadata
    - Pure household expenditure patterns
    """

    def __init__(self, cbs_categories: pd.DataFrame):
        """Initialize with CBS categories"""
        self.cbs_categories = cbs_categories
        logger.info(f"Initialized with {len(cbs_categories)} CBS categories")

        # Hebrew first names (common Israeli names)
        self.hebrew_first_names = [
            'דוד', 'שרה', 'משה', 'רחל', 'יוסף', 'מרים',
            'אברהם', 'לאה', 'יעקב', 'שושנה', 'יצחק', 'רבקה',
            'דניאל', 'חנה', 'שמואל', 'רות', 'אליהו', 'אסתר',
            'נתן', 'דבורה', 'יהושע', 'יעל', 'בנימין', 'נעמי',
            'עמית', 'תמר', 'אורי', 'נעמה', 'יונתן', 'מיכל'
        ]

        # Hebrew last names
        self.hebrew_last_names = [
            'כהן', 'לוי', 'מזרחי', 'פרץ', 'ביטון', 'אוחנה',
            'שלום', 'אסולין', 'אלמליח', 'אזולאי', 'חדד', 'בן דוד',
            'יוסף', 'אברהם', 'משה', 'דהן', 'עמר', 'ברוך',
            'מלכה', 'אטיאס', 'בוחבוט', 'אליהו', 'ממן', 'עובדיה'
        ]

        # Israeli cities with realistic distribution
        self.cities_distribution = {
            'תל אביב': 0.30,
            'ירושלים': 0.15,
            'חיפה': 0.12,
            'באר שבע': 0.08,
            'רחובות': 0.05,
            'פתח תקווה': 0.05,
            'ראשון לציון': 0.05,
            'נתניה': 0.05,
            'חולון': 0.05,
            'בני ברק': 0.05,
            'רמת גן': 0.05,
        }

        # Income quintile multipliers (relative to average spending)
        self.quintile_multipliers = {
            1: 0.60,  # Q1: Poorest 20%
            2: 0.80,  # Q2: Below average
            3: 1.00,  # Q3: Average
            4: 1.30,  # Q4: Above average
            5: 1.80,  # Q5: Richest 20%
        }

        # Status distribution
        self.status_weights = {
            'completed': 0.92,
            'pending': 0.05,
            'cancelled': 0.03
        }

        # Israeli holidays 2024 (for seasonality)
        self.holidays = {
            'rosh_hashanah': datetime(2024, 10, 3),
            'yom_kippur': datetime(2024, 10, 12),
            'sukkot': datetime(2024, 10, 17),
            'hanukkah': datetime(2024, 12, 26),
            'purim': datetime(2024, 3, 24),
            'passover': datetime(2024, 4, 23),
            'shavuot': datetime(2024, 6, 12),
        }

        # Map CBS categories to parent categories
        self.parent_categories = self._build_parent_categories()

    def _build_parent_categories(self) -> dict:
        """
        Map specific CBS products to parent categories

        CBS categories are hierarchical:
        - מזון ומשקאות (Food and beverages)
        - דיור (Housing)
        - תחבורה ותקשורת (Transportation and communication)
        - etc.
        """
        # Define parent categories based on common CBS structure
        categories = {}

        for idx, row in self.cbs_categories.iterrows():
            product_hebrew = row.get('category_hebrew', '')

            # Simple categorization based on keywords
            if any(word in product_hebrew for word in ['לחם', 'בשר', 'חלב', 'פירות', 'ירקות', 'אורז', 'קמח', 'שמן', 'סוכר', 'קפה', 'תה']):
                parent = 'מזון ומשקאות'
            elif any(word in product_hebrew for word in ['דיור', 'שכירות', 'ריהוט', 'מזגן']):
                parent = 'דיור'
            elif any(word in product_hebrew for word in ['רכב', 'דלק', 'תחבורה', 'טלפון', 'אינטרנט']):
                parent = 'תחבורה ותקשורת'
            elif any(word in product_hebrew for word in ['בגדים', 'נעליים', 'ביגוד']):
                parent = 'ביגוד והנעלה'
            elif any(word in product_hebrew for word in ['בריאות', 'תרופות', 'רופא']):
                parent = 'בריאות'
            elif any(word in product_hebrew for word in ['חינוך', 'לימודים', 'ספרים']):
                parent = 'חינוך ותרבות'
            else:
                parent = 'אחר'

            categories[product_hebrew] = parent

        return categories

    def generate_transactions(self, n_transactions: int = 10000) -> pd.DataFrame:
        """
        Generate n transactions with PROPER CBS schema

        Returns DataFrame with 10 columns:
        - transaction_id, customer_name, product, category, amount,
          currency, transaction_date, status, customer_city, income_quintile
        """
        logger.info(f"Generating {n_transactions:,} transactions...")

        transactions = []

        for i in range(n_transactions):
            if i % 1000 == 0 and i > 0:
                logger.info(f"  Generated {i:,} transactions...")

            # 1. Select income quintile (equal distribution)
            quintile = random.choice([1, 2, 3, 4, 5])

            # 2. Select random CBS category
            category_row = self.cbs_categories.sample(1).iloc[0]
            product_hebrew = category_row['category_hebrew']

            # 3. Get parent category
            parent_category = self.parent_categories.get(product_hebrew, 'אחר')

            # 4. Calculate amount based on CBS average + quintile + variance
            # Use average spending from CBS data
            base_amount = category_row['avg_spending']

            # Apply quintile multiplier
            quintile_mult = self.quintile_multipliers[quintile]
            amount = base_amount * quintile_mult

            # Add realistic variance (±30%)
            variance = random.uniform(0.70, 1.30)
            amount = amount * variance

            # Ensure minimum amount
            amount = max(amount, 10.0)

            # 5. Generate date with Israeli seasonality
            transaction_date = self._generate_date_with_seasonality()

            # 6. Select city (weighted distribution)
            city = self._select_city()

            # 7. Generate Hebrew customer name
            customer_name = self._generate_customer_name()

            # 8. Select status (weighted)
            status = random.choices(
                list(self.status_weights.keys()),
                weights=list(self.status_weights.values())
            )[0]

            # Create transaction with PROPER schema (10 columns only)
            transaction = {
                'transaction_id': 10000 + i,                          # Sequential
                'customer_name': customer_name,                       # Hebrew name
                'product': product_hebrew,                            # Product from CBS
                'category': parent_category,                          # Parent category
                'amount': round(amount, 2),                           # Amount in ILS
                'currency': 'ILS',                                    # Always ILS
                'transaction_date': transaction_date.strftime('%Y-%m-%d'),  # YYYY-MM-DD
                'status': status,                                     # completed/pending/cancelled
                'customer_city': city,                                # Hebrew city
                'income_quintile': quintile,                          # 1-5
            }

            transactions.append(transaction)

        df = pd.DataFrame(transactions)

        logger.info(f"[+] Generated {len(df):,} transactions")
        logger.info(f"    Date range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
        logger.info(f"    Total value: ILS {df[df['status']=='completed']['amount'].sum():,.2f}")
        logger.info(f"    Avg transaction: ILS {df[df['status']=='completed']['amount'].mean():.2f}")

        return df

    def _generate_date_with_seasonality(self) -> datetime:
        """Generate date with Israeli holiday seasonality"""
        # Random date in 2024
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        days = (end - start).days
        random_date = start + timedelta(days=random.randint(0, days))

        # Check if near holiday (boost probability)
        for holiday_name, holiday_date in self.holidays.items():
            days_to_holiday = abs((random_date.date() - holiday_date.date()).days)

            if days_to_holiday <= 7:  # Week before/after holiday
                # 60% chance to keep this date (higher near holidays)
                if random.random() < 0.6:
                    return random_date

        # Lower probability in summer (July-August)
        if random_date.month in [7, 8]:
            # 40% chance to regenerate (lower summer volume)
            if random.random() < 0.4:
                return self._generate_date_with_seasonality()

        return random_date

    def _select_city(self) -> str:
        """Select city based on weighted distribution"""
        cities = list(self.cities_distribution.keys())
        weights = list(self.cities_distribution.values())
        return random.choices(cities, weights=weights)[0]

    def _generate_customer_name(self) -> str:
        """Generate realistic Hebrew customer name"""
        first = random.choice(self.hebrew_first_names)
        last = random.choice(self.hebrew_last_names)
        return f"{first} {last}"


def main():
    """Run PROPER Phase 2 transaction generation"""
    print("=" * 70)
    print("CBS TRANSACTION GENERATION - PROPER PHASE 2 SCHEMA")
    print("Household Expenditure Data (NOT E-commerce Analytics)")
    print("=" * 70)
    print()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / 'data' / 'processed'

    # Load REAL CBS categories
    categories_file = processed_dir / 'cbs_categories_FIXED.csv'

    if not categories_file.exists():
        print(f"[ERROR] CBS categories not found: {categories_file}")
        print("        Run cbs_extractor_fixed.py first")
        return

    print(f"Loading CBS categories from: {categories_file.name}")
    df_categories = pd.read_csv(categories_file, encoding='utf-8-sig')
    print(f"[+] Loaded {len(df_categories)} CBS categories")
    print()

    # Initialize generator
    print("Initializing PROPER transaction generator...")
    generator = CBSProperTransactionGenerator(df_categories)
    print("[+] Generator initialized")
    print()

    # Generate transactions
    print("Generating 10,000 transactions with PROPER schema...")
    df_transactions = generator.generate_transactions(n_transactions=10000)
    print()

    # Validate schema
    print("=" * 70)
    print("SCHEMA VALIDATION")
    print("=" * 70)
    expected_columns = [
        'transaction_id', 'customer_name', 'product', 'category',
        'amount', 'currency', 'transaction_date', 'status',
        'customer_city', 'income_quintile'
    ]

    actual_columns = df_transactions.columns.tolist()

    print(f"Expected columns: {len(expected_columns)}")
    print(f"Actual columns:   {len(actual_columns)}")
    print()

    if actual_columns == expected_columns:
        print("[OK] Schema is CORRECT - 10 columns only")
    else:
        print("[ERROR] Schema mismatch!")
        print(f"Expected: {expected_columns}")
        print(f"Actual:   {actual_columns}")
        return

    print()
    print("Schema details:")
    for col in expected_columns:
        print(f"  {col}")
    print()

    # Show sample data
    print("=" * 70)
    print("SAMPLE TRANSACTIONS (First 5)")
    print("=" * 70)
    print(df_transactions.head(5).to_string())
    print()

    # Save transactions
    output_file = processed_dir / 'transactions_generated.csv'
    print(f"Saving transactions to: {output_file.name}")
    df_transactions.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"[+] Saved {len(df_transactions):,} transactions")
    print()

    print("=" * 70)
    print("PHASE 2 COMPLETE")
    print("=" * 70)
    print()
    print("Generated:")
    print(f"  - {len(df_transactions):,} transactions")
    print(f"  - Date range: {df_transactions['transaction_date'].min()} to {df_transactions['transaction_date'].max()}")
    print(f"  - Total revenue: ILS {df_transactions[df_transactions['status']=='completed']['amount'].sum():,.2f}")
    print(f"  - Avg transaction: ILS {df_transactions[df_transactions['status']=='completed']['amount'].mean():.2f}")
    print()
    print("Schema: 10 columns (CORRECT CBS household expenditure format)")
    print("  ✓ NO emails")
    print("  ✓ NO phones")
    print("  ✓ NO payment methods")
    print("  ✓ NO traffic sources")
    print("  ✓ NO device types")
    print()
    print("Next step: Phase 3 - Inject quality issues")
    print("  Run: python backend/etl/inject_quality_issues.py")
    print()


if __name__ == '__main__':
    main()
