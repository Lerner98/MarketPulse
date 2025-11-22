"""
E-commerce Data Cleaning and ETL Pipeline
Implements secure data validation, cleaning, and loading to PostgreSQL

Security features:
- Input validation for all fields
- SQL injection prevention via prepared statements
- Data type enforcement
- Duplicate detection and handling
- Hebrew character support (UTF-8)

Author: MarketPulse Team
Created: 2025-11-20
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import DatabaseManager  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EcommerceDataCleaner:
    """
    E-commerce transaction data cleaner and validator

    Responsibilities:
    1. Load CSV data with proper encoding (UTF-8 for Hebrew support)
    2. Validate data types and formats
    3. Clean and normalize data
    4. Detect and handle duplicates
    5. Load data into PostgreSQL using secure methods
    """

    # Valid status values (whitelist approach for security)
    VALID_STATUSES = {"completed", "pending", "cancelled"}

    # Valid currency codes
    VALID_CURRENCIES = {"ILS", "USD", "EUR"}

    # Valid product names (Hebrew)
    VALID_PRODUCTS = {
        "מחשב נייד",  # Laptop
        "טלפון סלולרי",  # Mobile phone
        "אוזניות",  # Headphones
        "מקלדת",  # Keyboard
        "עכבר",  # Mouse
    }

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize the data cleaner

        Args:
            db_manager: Database manager instance (creates new if not provided)
        """
        self.db_manager = db_manager or DatabaseManager()
        self.stats = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "duplicates_removed": 0,
            "records_loaded": 0,
        }

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV file with proper encoding for Hebrew support

        Args:
            file_path: Path to CSV file

        Returns:
            Pandas DataFrame

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Loading data from {file_path}")

        try:
            # Load with UTF-8-sig encoding to handle BOM and Hebrew characters
            df = pd.read_csv(file_path, encoding="utf-8-sig")

            if df.empty:
                raise ValueError("CSV file is empty")

            self.stats["total_records"] = len(df)
            logger.info(f"Loaded {len(df)} records from CSV")

            return df

        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

    def validate_record(self, row: pd.Series) -> Tuple[bool, Optional[str]]:
        """
        Validate a single transaction record

        Security: Whitelist validation for all fields

        Args:
            row: Pandas Series representing a transaction

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check transaction_id
        if pd.isna(row["transaction_id"]):
            return False, "Missing transaction_id"
        if not isinstance(row["transaction_id"], (int, np.integer)):
            return False, "Invalid transaction_id type"
        if row["transaction_id"] < 0:
            return False, "Negative transaction_id"

        # Check customer_name
        if pd.isna(row["customer_name"]) or not row["customer_name"].strip():
            return False, "Missing customer_name"
        if len(row["customer_name"]) > 255:
            return False, "Customer name too long"

        # Check product (whitelist validation)
        if pd.isna(row["product"]):
            return False, "Missing product"
        if row["product"] not in self.VALID_PRODUCTS:
            return False, f"Invalid product: {row['product']}"

        # Check amount
        if pd.isna(row["amount"]):
            return False, "Missing amount"
        try:
            amount = float(row["amount"])
            if amount < 0:
                return False, "Negative amount"
            if amount > 1000000:  # Reasonable upper limit
                return False, "Amount exceeds maximum"
        except (ValueError, TypeError):
            return False, "Invalid amount format"

        # Check currency (whitelist validation)
        if pd.isna(row["currency"]):
            return False, "Missing currency"
        if row["currency"] not in self.VALID_CURRENCIES:
            return False, f"Invalid currency: {row['currency']}"

        # Check date
        if pd.isna(row["date"]):
            return False, "Missing date"
        try:
            date_obj = pd.to_datetime(row["date"])
            # Validate date range (not in future, not too old)
            if date_obj > datetime.now():
                return False, "Future date not allowed"
            if date_obj.year < 2020:
                return False, "Date too old"
        except Exception:
            return False, "Invalid date format"

        # Check status (whitelist validation)
        if pd.isna(row["status"]):
            return False, "Missing status"
        if row["status"] not in self.VALID_STATUSES:
            return False, f"Invalid status: {row['status']}"

        return True, None

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize transaction data

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data cleaning process")

        df_clean = df.copy()

        # Normalize column names (lowercase, strip whitespace)
        df_clean.columns = df_clean.columns.str.lower().str.strip()

        # Convert transaction_id to integer
        df_clean["transaction_id"] = pd.to_numeric(
            df_clean["transaction_id"], errors="coerce"
        ).astype("Int64")

        # Clean customer names (strip whitespace, normalize)
        df_clean["customer_name"] = df_clean["customer_name"].astype(str).str.strip()

        # Clean product names (strip whitespace)
        df_clean["product"] = df_clean["product"].astype(str).str.strip()

        # Convert amount to float with 2 decimal places
        df_clean["amount"] = pd.to_numeric(df_clean["amount"], errors="coerce").round(2)

        # Normalize currency (uppercase)
        df_clean["currency"] = df_clean["currency"].astype(str).str.upper().str.strip()

        # Convert date to datetime
        df_clean["date"] = pd.to_datetime(df_clean["date"], errors="coerce")

        # Normalize status (lowercase)
        df_clean["status"] = df_clean["status"].astype(str).str.lower().str.strip()

        # Validate each record
        valid_mask = df_clean.apply(lambda row: self.validate_record(row)[0], axis=1)

        # Separate valid and invalid records
        df_valid = df_clean[valid_mask].copy()
        df_invalid = df_clean[~valid_mask].copy()

        self.stats["valid_records"] = len(df_valid)
        self.stats["invalid_records"] = len(df_invalid)

        if len(df_invalid) > 0:
            logger.warning(f"Found {len(df_invalid)} invalid records")
            # Log first few invalid records for debugging
            for idx, row in df_invalid.head(5).iterrows():
                is_valid, error = self.validate_record(row)
                logger.warning(f"Invalid record {idx}: {error}")

        logger.info(f"Data cleaning complete: {len(df_valid)} valid records")

        return df_valid

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate transactions

        Duplicates are identified by transaction_id

        Args:
            df: DataFrame to deduplicate

        Returns:
            Deduplicated DataFrame
        """
        logger.info("Checking for duplicates")

        initial_count = len(df)

        # Remove duplicates based on transaction_id (keep first occurrence)
        df_dedup = df.drop_duplicates(subset=["transaction_id"], keep="first")

        duplicates_removed = initial_count - len(df_dedup)
        self.stats["duplicates_removed"] = duplicates_removed

        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate records")
        else:
            logger.info("No duplicates found")

        return df_dedup

    def load_to_database(self, df: pd.DataFrame, batch_size: int = 1000):
        """
        Load cleaned data to PostgreSQL database

        Security: Uses SQLAlchemy prepared statements (no raw SQL)

        Args:
            df: Cleaned DataFrame to load
            batch_size: Number of records to insert per batch
        """
        if df.empty:
            logger.warning("No data to load to database")
            return

        logger.info(f"Loading {len(df)} records to database")

        try:
            # Rename columns to match database schema
            df_to_load = df.copy()
            df_to_load = df_to_load.rename(columns={"date": "transaction_date"})

            with self.db_manager.get_session():
                # Use pandas to_sql with SQLAlchemy for secure insertion
                # This uses prepared statements internally
                df_to_load.to_sql(
                    "transactions",
                    con=self.db_manager.engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=batch_size,
                )

                self.stats["records_loaded"] = len(df)
                logger.info(f"Successfully loaded {len(df)} records to database")

        except Exception as e:
            logger.error(f"Failed to load data to database: {e}")
            raise

    def run_pipeline(
        self, input_file: str, output_file: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Run complete ETL pipeline

        Args:
            input_file: Path to input CSV file
            output_file: Optional path to save cleaned CSV

        Returns:
            Dictionary with pipeline statistics
        """
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)

        # Step 1: Load data
        df_raw = self.load_csv(input_file)

        # Step 2: Clean data
        df_clean = self.clean_data(df_raw)

        # Step 3: Remove duplicates
        df_dedup = self.remove_duplicates(df_clean)

        # Step 4: Save cleaned data (optional)
        if output_file:
            df_dedup.to_csv(output_file, index=False, encoding="utf-8-sig")
            logger.info(f"Cleaned data saved to {output_file}")

        # Step 5: Load to database
        self.load_to_database(df_dedup)

        # Print statistics
        logger.info("=" * 60)
        logger.info("ETL Pipeline Complete")
        logger.info("=" * 60)
        logger.info(f"Total records: {self.stats['total_records']}")
        logger.info(f"Valid records: {self.stats['valid_records']}")
        logger.info(f"Invalid records: {self.stats['invalid_records']}")
        logger.info(f"Duplicates removed: {self.stats['duplicates_removed']}")
        logger.info(f"Records loaded to DB: {self.stats['records_loaded']}")
        logger.info("=" * 60)

        return self.stats


def main():
    """Main entry point for ETL pipeline"""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / "data" / "raw" / "transactions.csv"
    output_file = project_root / "data" / "processed" / "transactions_clean.csv"
    schema_file = project_root / "backend" / "models" / "schema.sql"

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Initialize database
        db = DatabaseManager()

        # Test connection
        if not db.test_connection():
            logger.error(
                "Database connection failed. Please check your connection settings."
            )
            return

        # Check if schema already initialized
        with db.engine.connect():
            from sqlalchemy import inspect  # noqa: E402

            inspector = inspect(db.engine)
            if "transactions" not in inspector.get_table_names():
                # Initialize schema
                if schema_file.exists():
                    logger.info("Initializing database schema")
                    db.execute_sql_file(str(schema_file))
                else:
                    logger.warning(f"Schema file not found: {schema_file}")
            else:
                logger.info("Database schema already initialized")

        # Run ETL pipeline
        cleaner = EcommerceDataCleaner(db)
        cleaner.run_pipeline(str(input_file), str(output_file))

        # Success
        logger.info("ETL pipeline completed successfully!")

    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
