"""
Advanced E-commerce Data Generator for MarketPulse
Generates realistic Israeli e-commerce data with intentional quality issues
to showcase advanced data processing and cleaning skills.
"""

import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)


class IsraeliEcommerceDataGenerator:
    """Generate realistic Israeli e-commerce transaction data."""

    def __init__(self):
        # Hebrew first names (common Israeli names)
        self.hebrew_first_names = [
            "דוד",
            "משה",
            "יוסף",
            "אברהם",
            "שרה",
            "רחל",
            "לאה",
            "מרים",
            "יעקב",
            "יצחק",
            "דניאל",
            "מיכאל",
            "גבריאל",
            "נועה",
            "תמר",
            "שירה",
            "עדי",
            "רועי",
            "יונתן",
            "אלי",
            "עומר",
            "טל",
            "מאיה",
            "ליאור",
            "שני",
            "אורי",
            "עידו",
            "נטע",
            "ענבל",
            "יובל",
            "איתי",
            "רונן",
            "גיא",
            "חן",
            "ניר",
            "קרן",
            "דנה",
            "מור",
            "אסף",
            "נדב",
            "רותם",
            "הדס",
            "ליהי",
            "איל",
            "ערן",
            "מתן",
        ]

        # Hebrew last names
        self.hebrew_last_names = [
            "כהן",
            "לוי",
            "מזרחי",
            "פרץ",
            "ביטון",
            "אוחנה",
            "שלום",
            "אסולין",
            "אלמליח",
            "אזולאי",
            "חדד",
            "בן דוד",
            "יוסף",
            "אברהם",
            "משה",
            "דהן",
            "עמר",
            "ברוך",
            "מלכה",
            "אטיאס",
            "בוחבוט",
            "אליהו",
            "ממן",
            "עובדיה",
            "זוהר",
            "צדוק",
            "נחום",
            "בר",
            "שפירא",
            "רוזן",
            "גולדברג",
            "כץ",
            "פרידמן",
            "שטרן",
            "ברקוביץ",
            "ליברמן",
            "אבוטבול",
            "מושיאשוילי",
            "אוחיון",
            "סבן",
            "חביב",
            "גבאי",
        ]

        # Israeli cities
        self.israeli_cities = [
            "תל אביב",
            "ירושלים",
            "חיפה",
            "ראשון לציון",
            "פתח תקווה",
            "אשדוד",
            "נתניה",
            "באר שבע",
            "בני ברק",
            "חולון",
            "רמת גן",
            "בת ים",
            "אשקלון",
            "רחובות",
            "הרצליה",
            "כפר סבא",
            "חדרה",
            "מודיעין",
            "נצרת",
            "לוד",
            "רעננה",
            "רמלה",
            "גבעתיים",
        ]

        # Product categories with Hebrew names
        self.product_categories = {
            "אלקטרוניקה": [  # Electronics
                "אייפון 15 פרו",
                "סמסונג גלקסי S24",
                "אוזניות בלוטוס",
                "מחשב נייד דל",
                "טאבלט אייפד",
                "שעון חכם",
                "רמקול JBL",
                "מסך מחשב 27 אינץ'",
                "מקלדת אלחוטית",
                "עכבר גיימינג",
            ],
            "אופנה": [  # Fashion
                "חולצת פולו",
                "מכנסי ג'ינס",
                "נעלי נייק",
                "תיק יד",
                "שמלת ערב",
                "ז'קט עור",
                "משקפי שמש",
                "חגורה",
                "כובע",
                "צעיף קשמיר",
            ],
            "בית וגן": [  # Home & Garden
                "מזרון אורתופדי",
                "ספה תלת מושבית",
                "שולחן אוכל",
                "כורסא",
                "מנורת עמידה",
                "וילון",
                "שטיח פרסי",
                "כלי מטבח",
                "סט מצעים",
                "כלי אמבטיה",
            ],
            "ספורט": [  # Sports
                "נעלי ריצה",
                "אופני הרים",
                "מזרן יוגה",
                "משקולות",
                "כדורגל",
                "בגד ים",
                "תיק ספורט",
                "בקבוק מים",
                "שעון ספורט",
                "רולרבליידס",
            ],
            "קוסמטיקה": [  # Cosmetics
                "בושם שאנל",
                "קרם פנים",
                "שפתון",
                "מסקרה",
                "אייליינר",
                "קרם ידיים",
                "שמפו",
                "מרכך שיער",
                "סבון פנים",
                "קרם גוף",
            ],
            "ספרים": [  # Books
                "הארי פוטר",
                "שלושת המוסקטרים",
                "אלכימאי",
                "1984",
                "חוות החיות",
                "נסיך קטן",
                "מאה שנות בדידות",
                "זקן והים",
                "גטסבי הגדול",
                "להרוג זמיר",
            ],
            "משחקים": [  # Games & Toys
                "פלייסטיישן 5",
                "משחק לגו",
                "פאזל",
                "בובה ברבי",
                "משחק קופסה",
                "רובוט שלט רחוק",
                "קלפים",
                "כדור טניס שולחן",
                "משחק דמקה",
                "סט ציור",
            ],
        }

        # Traffic sources
        self.traffic_sources = [
            "Google Ads",
            "Facebook",
            "Instagram",
            "Organic Search",
            "Email Campaign",
            "Direct",
            "Referral",
            "Twitter",
            "TikTok",
            "YouTube Ads",
        ]

        # Payment methods
        self.payment_methods = [
            "credit_card",
            "paypal",
            "bank_transfer",
            "cash_on_delivery",
            "bit",
            "apple_pay",
            "google_pay",
        ]

        # Device types
        self.device_types = ["mobile", "desktop", "tablet"]

        # Status weights (most completed, some pending/cancelled)
        self.status_weights = {"completed": 0.75, "pending": 0.15, "cancelled": 0.10}

    def generate_customer_name(self) -> str:
        """Generate realistic Hebrew customer name."""
        first = random.choice(self.hebrew_first_names)
        last = random.choice(self.hebrew_last_names)
        return f"{first} {last}"

    def generate_email(self, name: str) -> str:
        """Generate email from customer name (with some data quality issues)."""
        # Convert Hebrew to transliteration (simplified)
        domains = ["gmail.com", "walla.co.il", "hotmail.com", "012.net.il"]

        # 5% chance of malformed email (data quality issue)
        if random.random() < 0.05:
            return random.choice(
                [
                    "invalid.email",  # Missing @
                    "@missingusername.com",  # Missing username
                    f"user@",  # Missing domain
                    f"user{random.randint(1, 1000)}@@double.com",  # Double @
                ]
            )

        # Normal email
        username = f"user{random.randint(1000, 99999)}"
        return f"{username}@{random.choice(domains)}"

    def generate_phone(self) -> str:
        """Generate Israeli phone number (with some quality issues)."""
        # 3% chance of malformed phone
        if random.random() < 0.03:
            return random.choice(
                [
                    "050-INVALID",  # Invalid characters
                    "05",  # Too short
                    "050-123-456-789-000",  # Too long
                    "",  # Missing
                ]
            )

        # Israeli mobile format: 05X-XXX-XXXX
        prefix = random.choice(["050", "052", "053", "054", "055", "058"])
        middle = random.randint(100, 999)
        last = random.randint(1000, 9999)

        # 10% chance of inconsistent formatting
        if random.random() < 0.1:
            return f"{prefix}{middle}{last}"  # No dashes

        return f"{prefix}-{middle}-{last}"

    def generate_transaction_amount(self, category: str, date: datetime) -> float:
        """Generate realistic transaction amount with seasonal variations."""
        # Base prices by category
        base_prices = {
            "אלקטרוניקה": (500, 5000),
            "אופנה": (80, 800),
            "בית וגן": (150, 3000),
            "ספורט": (100, 1500),
            "קוסמטיקה": (50, 500),
            "ספרים": (30, 150),
            "משחקים": (60, 1200),
        }

        min_price, max_price = base_prices.get(category, (50, 500))
        base_amount = random.uniform(min_price, max_price)

        # Seasonal multipliers
        month = date.month
        seasonal_multiplier = 1.0

        # Holiday seasons (November-December) - higher spending
        if month in [11, 12]:
            seasonal_multiplier = 1.3
        # Summer sale (July-August) - lower prices
        elif month in [7, 8]:
            seasonal_multiplier = 0.85

        amount = base_amount * seasonal_multiplier

        # Add some random variation
        amount *= random.uniform(0.9, 1.1)

        return round(amount, 2)

    def introduce_duplicates(
        self, df: pd.DataFrame, duplicate_rate: float = 0.02
    ) -> pd.DataFrame:
        """Introduce duplicate transactions (data quality issue)."""
        n_duplicates = int(len(df) * duplicate_rate)
        if n_duplicates > 0:
            duplicate_rows = df.sample(n=n_duplicates)
            df = pd.concat([df, duplicate_rows], ignore_index=True)
        return df

    def introduce_missing_values(
        self, df: pd.DataFrame, missing_rate: float = 0.03
    ) -> pd.DataFrame:
        """Introduce missing values in various columns."""
        columns_to_affect = ["customer_city", "phone", "device_type"]

        for col in columns_to_affect:
            n_missing = int(len(df) * missing_rate)
            missing_indices = random.sample(range(len(df)), n_missing)
            df.loc[missing_indices, col] = None

        return df

    def introduce_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Introduce price outliers (data entry errors)."""
        # 0.5% extremely high prices (typo: extra zero)
        n_high_outliers = int(len(df) * 0.005)
        high_indices = random.sample(range(len(df)), n_high_outliers)
        df.loc[high_indices, "amount"] *= 10

        # 0.3% extremely low prices (typo: missing zero)
        n_low_outliers = int(len(df) * 0.003)
        low_indices = random.sample(range(len(df)), n_low_outliers)
        df.loc[low_indices, "amount"] /= 10

        return df

    def generate_quarterly_pattern(
        self, start_date: datetime, end_date: datetime, n_transactions: int
    ) -> List[datetime]:
        """Generate timestamps with realistic quarterly patterns."""
        dates = []
        days_range = (end_date - start_date).days

        # Define quarterly business cycles
        for _ in range(n_transactions):
            random_days = random.randint(0, days_range)
            date = start_date + timedelta(days=random_days)

            # Increase probability at quarter ends
            if date.month % 3 == 0:  # March, June, September, December
                # 30% higher transaction volume at quarter end
                if random.random() < 0.3:
                    dates.append(date)

            dates.append(date)

        # Trim to exact count
        return random.sample(dates, n_transactions)

    def generate_dataset(
        self,
        n_transactions: int = 15000,
        start_date: str = "2023-01-01",
        end_date: str = "2024-12-31",
    ) -> pd.DataFrame:
        """Generate complete realistic dataset."""
        print(f"[*] Generating {n_transactions:,} transactions...")

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Generate dates with quarterly patterns
        dates = self.generate_quarterly_pattern(start_dt, end_dt, n_transactions)

        transactions = []

        for i, date in enumerate(dates):
            if i % 1000 == 0:
                print(f"  Generated {i:,} transactions...")

            # Select category and product
            category = random.choice(list(self.product_categories.keys()))
            product_name = random.choice(self.product_categories[category])

            # Generate customer info
            customer_name = self.generate_customer_name()
            customer_email = self.generate_email(customer_name)
            customer_phone = self.generate_phone()
            customer_city = random.choice(self.israeli_cities)

            # Generate transaction details
            amount = self.generate_transaction_amount(category, date)
            quantity = random.choices([1, 2, 3, 4, 5], weights=[60, 20, 10, 7, 3])[0]
            total_amount = amount * quantity

            # Select status based on weights
            status = random.choices(
                list(self.status_weights.keys()),
                weights=list(self.status_weights.values()),
            )[0]

            # Other attributes
            traffic_source = random.choice(self.traffic_sources)
            payment_method = random.choice(self.payment_methods)
            device_type = random.choices(self.device_types, weights=[60, 30, 10])[0]

            transaction = {
                "transaction_id": str(uuid.uuid4()),
                "timestamp": date.strftime("%Y-%m-%d %H:%M:%S"),
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "customer_city": customer_city,
                "product_name": product_name,
                "product_category": category,
                "quantity": quantity,
                "amount": total_amount,
                "status": status,
                "payment_method": payment_method,
                "traffic_source": traffic_source,
                "device_type": device_type,
            }

            transactions.append(transaction)

        df = pd.DataFrame(transactions)

        print(f"[+] Generated {len(df):,} base transactions")

        # Introduce data quality issues
        print("[*] Introducing data quality issues...")
        df = self.introduce_duplicates(df, duplicate_rate=0.02)
        print(f"  Added ~{int(n_transactions * 0.02):,} duplicates")

        df = self.introduce_missing_values(df, missing_rate=0.03)
        print(f"  Added ~{int(n_transactions * 0.03):,} missing values")

        df = self.introduce_outliers(df)
        print("  Added price outliers")

        # Shuffle the data
        df = df.sample(frac=1).reset_index(drop=True)

        print(f"[+] Final dataset: {len(df):,} transactions")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Categories: {df['product_category'].nunique()}")
        print(f"   Customers: {df['customer_name'].nunique()}")

        return df


def main():
    """Generate and save the dataset."""
    print("=" * 60)
    print("MarketPulse Advanced Data Generator")
    print("=" * 60)
    print()

    generator = IsraeliEcommerceDataGenerator()

    # Generate dataset
    df = generator.generate_dataset(
        n_transactions=15000, start_date="2023-01-01", end_date="2024-12-31"
    )

    # Save to CSV
    output_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "transactions.csv"

    print()
    print(f"[*] Saving to {output_file}...")
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print()
    print("=" * 60)
    print("[+] Data Generation Complete!")
    print("=" * 60)
    print()
    print("[*] Dataset Summary:")
    print(f"   Total transactions: {len(df):,}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"   Total revenue: ILS {df[df['status']=='completed']['amount'].sum():,.2f}")
    print(
        f"   Avg order value: ILS {df[df['status']=='completed']['amount'].mean():,.2f}"
    )
    print(f"   Unique customers: {df['customer_name'].nunique():,}")
    print(f"   Product categories: {df['product_category'].nunique()}")
    print()
    print("[*] Data Quality Issues (intentional for cleaning demo):")
    print(f"   Duplicates: ~{int(15000 * 0.02):,}")
    print(f"   Missing values: ~{int(15000 * 0.03):,}")
    print(f"   Malformed emails: ~{int(15000 * 0.05):,}")
    print(f"   Malformed phones: ~{int(15000 * 0.03):,}")
    print(f"   Price outliers: ~{int(15000 * 0.008):,}")
    print()
    print("Next step: Run data cleaning pipeline")
    print("  cd backend")
    print("  python data_pipeline/cleaner.py")


if __name__ == "__main__":
    main()
