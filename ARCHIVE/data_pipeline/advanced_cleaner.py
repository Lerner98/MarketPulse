"""
Advanced E-commerce Data Cleaning and ETL Pipeline
Showcases professional data processing and cleaning skills

Features:
- Comprehensive data quality assessment
- Advanced cleaning techniques (outlier detection, email/phone validation)
- Duplicate detection using multiple strategies
- Missing value imputation
- Data profiling and quality reporting
- Hebrew text handling (UTF-8)
- Secure database loading

Author: MarketPulse Team
Created: 2025-11-20
"""

import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy import text

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import DatabaseManager  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedEcommerceDataCleaner:
    """
    Advanced E-commerce transaction data cleaner with comprehensive
    data quality assessment and cleaning capabilities.
    """

    # Email validation regex
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    # Israeli phone number pattern
    PHONE_PATTERN = re.compile(r"^05\d{1}-?\d{3}-?\d{4}$")

    # Valid statuses
    VALID_STATUSES = {"completed", "pending", "cancelled"}

    # Valid payment methods
    VALID_PAYMENT_METHODS = {
        "credit_card",
        "paypal",
        "bank_transfer",
        "cash_on_delivery",
        "bit",
        "apple_pay",
        "google_pay",
    }

    # Valid device types
    VALID_DEVICE_TYPES = {"mobile", "desktop", "tablet"}

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize the advanced data cleaner."""
        self.db_manager = db_manager or DatabaseManager()
        self.stats = {
            "total_records": 0,
            "duplicates_removed": 0,
            "outliers_detected": 0,
            "malformed_emails_fixed": 0,
            "malformed_phones_fixed": 0,
            "missing_values_imputed": 0,
            "invalid_records_removed": 0,
            "final_records": 0,
        }
        self.quality_report = {}

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with proper UTF-8 encoding for Hebrew support."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Loading data from {file_path}")

        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")

            if df.empty:
                raise ValueError("CSV file is empty")

            self.stats["total_records"] = len(df)
            logger.info(f"Loaded {len(df):,} records from CSV")

            return df

        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

    def assess_data_quality(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive data quality assessment.
        Returns detailed quality metrics.
        """
        logger.info("Assessing data quality...")

        quality_report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": {},
            "duplicate_rows": 0,
            "data_types": {},
            "unique_counts": {},
        }

        # Missing values per column
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / len(df)) * 100
            quality_report["missing_values"][col] = {
                "count": int(missing_count),
                "percentage": round(missing_pct, 2),
            }

        # Duplicate rows
        quality_report["duplicate_rows"] = int(df.duplicated().sum())

        # Data types
        quality_report["data_types"] = {
            col: str(dtype) for col, dtype in df.dtypes.items()
        }

        # Unique value counts
        for col in df.columns:
            quality_report["unique_counts"][col] = int(df[col].nunique())

        self.quality_report = quality_report
        return quality_report

    def print_quality_report(self):
        """Print formatted data quality report."""
        print("\n" + "=" * 60)
        print("DATA QUALITY ASSESSMENT REPORT")
        print("=" * 60)

        print(f"\nDataset Dimensions:")
        print(f"  Rows: {self.quality_report['total_rows']:,}")
        print(f"  Columns: {self.quality_report['total_columns']}")

        print(f"\nDuplicate Rows: {self.quality_report['duplicate_rows']:,}")

        print(f"\nMissing Values:")
        for col, info in self.quality_report["missing_values"].items():
            if info["count"] > 0:
                print(f"  {col}: {info['count']:,} ({info['percentage']:.2f}%)")

        print("\n" + "=" * 60)

    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate and attempt to fix malformed email addresses.
        Returns (is_valid, fixed_email).
        """
        if pd.isna(email) or not email or not isinstance(email, str):
            return False, None

        email = email.strip()

        # Already valid
        if self.EMAIL_PATTERN.match(email):
            return True, email

        # Common fixes
        # Fix: Multiple @@ -> single @
        if "@@" in email:
            fixed = email.replace("@@", "@")
            if self.EMAIL_PATTERN.match(fixed):
                return True, fixed

        # Fix: Missing @ (e.g., "usergmail.com" -> "user@gmail.com")
        if "@" not in email and "gmail.com" in email:
            fixed = email.replace("gmail.com", "@gmail.com")
            if self.EMAIL_PATTERN.match(fixed):
                return True, fixed

        # Cannot fix
        return False, None

    def validate_phone(self, phone: str) -> Tuple[bool, Optional[str]]:
        """
        Validate and attempt to fix Israeli phone numbers.
        Returns (is_valid, fixed_phone).
        """
        if pd.isna(phone) or not phone or not isinstance(phone, str):
            return False, None

        phone = phone.strip()

        # Already valid
        if self.PHONE_PATTERN.match(phone):
            return True, phone

        # Fix: Remove all non-digits and re-format
        digits_only = re.sub(r"[^\d]", "", phone)

        # Israeli mobile: 10 digits starting with 05
        if len(digits_only) == 10 and digits_only.startswith("05"):
            fixed = f"{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
            return True, fixed

        # Cannot fix
        return False, None

    def detect_outliers_iqr(
        self, df: pd.DataFrame, column: str, multiplier: float = 3.0
    ) -> pd.Series:
        """
        Detect outliers using IQR (Interquartile Range) method.
        Returns boolean mask where True = outlier.
        """
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        return outliers

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive data cleaning pipeline.
        """
        logger.info("Starting advanced data cleaning pipeline...")

        df_clean = df.copy()

        # Step 1: Normalize column names
        logger.info("Step 1: Normalizing column names")
        df_clean.columns = df_clean.columns.str.lower().str.strip()

        # Step 2: Remove exact duplicates
        logger.info("Step 2: Removing exact duplicate rows")
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        duplicates_removed = initial_count - len(df_clean)
        self.stats["duplicates_removed"] = duplicates_removed
        logger.info(f"  Removed {duplicates_removed:,} exact duplicates")

        # Step 3: Fix malformed emails
        logger.info("Step 3: Validating and fixing email addresses")
        email_fixes = 0
        invalid_emails = 0

        def fix_email(email):
            nonlocal email_fixes, invalid_emails
            is_valid, fixed = self.validate_email(email)
            if is_valid and fixed != email:
                email_fixes += 1
            elif not is_valid:
                invalid_emails += 1
                return None
            return fixed if fixed else email

        df_clean["customer_email"] = df_clean["customer_email"].apply(fix_email)
        self.stats["malformed_emails_fixed"] = email_fixes
        logger.info(f"  Fixed {email_fixes:,} malformed emails")
        logger.info(f"  Set {invalid_emails:,} invalid emails to NULL")

        # Step 4: Fix malformed phone numbers
        logger.info("Step 4: Validating and fixing phone numbers")
        phone_fixes = 0
        invalid_phones = 0

        def fix_phone(phone):
            nonlocal phone_fixes, invalid_phones
            is_valid, fixed = self.validate_phone(phone)
            if is_valid and fixed != phone:
                phone_fixes += 1
            elif not is_valid:
                invalid_phones += 1
                return None
            return fixed if fixed else phone

        df_clean["customer_phone"] = df_clean["customer_phone"].apply(fix_phone)
        self.stats["malformed_phones_fixed"] = phone_fixes
        logger.info(f"  Fixed {phone_fixes:,} malformed phone numbers")
        logger.info(f"  Set {invalid_phones:,} invalid phones to NULL")

        # Step 5: Detect and handle price outliers
        logger.info("Step 5: Detecting price outliers")
        outlier_mask = self.detect_outliers_iqr(df_clean, "amount", multiplier=3.0)
        outlier_count = outlier_mask.sum()
        self.stats["outliers_detected"] = outlier_count

        if outlier_count > 0:
            logger.info(
                f"  Detected {outlier_count:,} price outliers "
                f"({(outlier_count/len(df_clean))*100:.2f}%)"
            )
            # Cap outliers at reasonable bounds
            Q1 = df_clean["amount"].quantile(0.25)
            Q3 = df_clean["amount"].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3.0 * IQR
            upper_bound = Q3 + 3.0 * IQR

            df_clean.loc[outlier_mask, "amount"] = df_clean.loc[
                outlier_mask, "amount"
            ].clip(lower=lower_bound, upper=upper_bound)
            logger.info(f"  Capped outliers to reasonable bounds")

        # Step 6: Handle missing values
        logger.info("Step 6: Handling missing values")

        # Impute missing cities with most common city
        if df_clean["customer_city"].isna().any():
            most_common_city = df_clean["customer_city"].mode()[0]
            missing_cities = df_clean["customer_city"].isna().sum()
            df_clean["customer_city"].fillna(most_common_city, inplace=True)
            self.stats["missing_values_imputed"] += missing_cities
            logger.info(
                f"  Imputed {missing_cities:,} missing cities "
                f"with '{most_common_city}'"
            )

        # Impute missing device types with most common
        if df_clean["device_type"].isna().any():
            most_common_device = df_clean["device_type"].mode()[0]
            missing_devices = df_clean["device_type"].isna().sum()
            df_clean["device_type"].fillna(most_common_device, inplace=True)
            self.stats["missing_values_imputed"] += missing_devices
            logger.info(
                f"  Imputed {missing_devices:,} missing device types "
                f"with '{most_common_device}'"
            )

        # Step 7: Data type enforcement
        logger.info("Step 7: Enforcing data types")

        # Convert timestamp to datetime
        df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"], errors="coerce")

        # Convert numeric fields
        df_clean["amount"] = pd.to_numeric(df_clean["amount"], errors="coerce")
        df_clean["quantity"] = pd.to_numeric(
            df_clean["quantity"], errors="coerce"
        ).astype("Int64")

        # Normalize categorical fields
        df_clean["status"] = df_clean["status"].str.lower().str.strip()
        df_clean["payment_method"] = df_clean["payment_method"].str.lower().str.strip()
        df_clean["device_type"] = df_clean["device_type"].str.lower().str.strip()

        # Trim text fields
        for col in [
            "customer_name",
            "product_name",
            "product_category",
            "customer_city",
            "traffic_source",
        ]:
            df_clean[col] = df_clean[col].str.strip()

        # Step 8: Validate and remove invalid records
        logger.info("Step 8: Removing invalid records")

        initial_count = len(df_clean)

        # Remove records with critical missing values
        df_clean = df_clean.dropna(
            subset=[
                "transaction_id",
                "timestamp",
                "customer_name",
                "product_name",
                "amount",
                "status",
            ]
        )

        # Remove records with invalid amounts
        df_clean = df_clean[df_clean["amount"] > 0]

        # Remove records with invalid quantities
        df_clean = df_clean[df_clean["quantity"] > 0]

        # Validate status
        df_clean = df_clean[df_clean["status"].isin(self.VALID_STATUSES)]

        # Validate payment method
        df_clean = df_clean[df_clean["payment_method"].isin(self.VALID_PAYMENT_METHODS)]

        # Validate device type
        df_clean = df_clean[df_clean["device_type"].isin(self.VALID_DEVICE_TYPES)]

        invalid_removed = initial_count - len(df_clean)
        self.stats["invalid_records_removed"] = invalid_removed
        logger.info(f"  Removed {invalid_removed:,} invalid records")

        self.stats["final_records"] = len(df_clean)

        logger.info(f"Data cleaning complete: {len(df_clean):,} clean records")

        return df_clean

    def save_cleaned_data(self, df: pd.DataFrame, output_path: str):
        """Save cleaned data to CSV."""
        logger.info(f"Saving cleaned data to {output_path}")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info("Cleaned data saved successfully")

    def load_to_database(self, df: pd.DataFrame):
        """Load cleaned data into PostgreSQL database."""
        logger.info("Loading data into database...")

        try:
            with self.db_manager.get_session() as session:
                # Clear existing data
                logger.info("Clearing existing transactions...")
                session.execute(
                    text("TRUNCATE TABLE transactions RESTART IDENTITY CASCADE")
                )
                session.commit()

                # Insert new data
                logger.info(f"Inserting {len(df):,} transactions...")

                # Convert DataFrame to records for insertion
                records = df.to_dict("records")

                # Batch insert for performance
                batch_size = 1000
                for i in range(0, len(records), batch_size):
                    batch = records[i : i + batch_size]

                    for record in batch:
                        session.execute(
                            text(
                                """
                                INSERT INTO transactions (
                                    transaction_id, timestamp, customer_name,
                                    customer_email, customer_phone,
                                    customer_city, product_name,
                                    product_category, quantity, amount,
                                    status, payment_method, traffic_source,
                                    device_type
                                ) VALUES (
                                    :transaction_id, :timestamp,
                                    :customer_name, :customer_email,
                                    :customer_phone, :customer_city,
                                    :product_name, :product_category,
                                    :quantity, :amount, :status,
                                    :payment_method, :traffic_source,
                                    :device_type
                                )
                            """
                            ),
                            record,
                        )

                    session.commit()

                    if (i + batch_size) % 5000 == 0:
                        logger.info(f"  Inserted {i + batch_size:,} records...")

                logger.info(
                    f"Successfully loaded {len(records):,} records " f"into database"
                )

        except Exception as e:
            logger.error(f"Failed to load data to database: {e}")
            raise

    def print_cleaning_summary(self):
        """Print comprehensive cleaning summary."""
        print("\n" + "=" * 60)
        print("DATA CLEANING SUMMARY")
        print("=" * 60)
        print(f"\nInput:")
        print(f"  Total records: {self.stats['total_records']:,}")

        print(f"\nCleaning Operations:")
        print(f"  Duplicates removed: " f"{self.stats['duplicates_removed']:,}")
        print(f"  Malformed emails fixed: " f"{self.stats['malformed_emails_fixed']:,}")
        print(f"  Malformed phones fixed: " f"{self.stats['malformed_phones_fixed']:,}")
        print(f"  Price outliers detected: " f"{self.stats['outliers_detected']:,}")
        print(f"  Missing values imputed: " f"{self.stats['missing_values_imputed']:,}")
        print(
            f"  Invalid records removed: " f"{self.stats['invalid_records_removed']:,}"
        )

        print(f"\nOutput:")
        print(f"  Clean records: {self.stats['final_records']:,}")

        data_quality = (self.stats["final_records"] / self.stats["total_records"]) * 100
        print(f"  Data quality: {data_quality:.2f}%")

        print("\n" + "=" * 60)

    def run_pipeline(
        self, input_path: str, output_path: str, load_to_db: bool = True
    ) -> pd.DataFrame:
        """
        Run the complete data processing pipeline.

        Args:
            input_path: Path to input CSV file
            output_path: Path to save cleaned CSV
            load_to_db: Whether to load into database

        Returns:
            Cleaned DataFrame
        """
        print("\n" + "=" * 60)
        print("ADVANCED DATA PROCESSING PIPELINE")
        print("=" * 60)

        # Load data
        df = self.load_csv(input_path)

        # Assess quality
        self.assess_data_quality(df)
        self.print_quality_report()

        # Clean data
        df_clean = self.clean_data(df)

        # Save cleaned data
        self.save_cleaned_data(df_clean, output_path)

        # Load to database
        if load_to_db:
            self.load_to_database(df_clean)

        # Print summary
        self.print_cleaning_summary()

        print("\n[+] Pipeline completed successfully!")

        return df_clean


def main():
    """Execute the data processing pipeline."""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / "data" / "raw" / "transactions.csv"
    output_file = project_root / "data" / "processed" / "transactions_clean.csv"

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Initialize cleaner
    cleaner = AdvancedEcommerceDataCleaner()

    # Run pipeline
    df_clean = cleaner.run_pipeline(
        input_path=str(input_file), output_path=str(output_file), load_to_db=True
    )

    print(f"\nCleaned data shape: {df_clean.shape}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()
