"""
CBS Data Loader - Load cleaned CBS transactions into PostgreSQL

This script:
1. Applies the schema_cbs.sql schema to the database
2. Loads all 10,000 transactions from transactions_cleaned.csv
3. Refreshes materialized views for performance
4. Runs validation checks
5. Reports data quality metrics

Usage:
    python backend/load_cbs_data.py
"""

import sys
import os
import pandas as pd
from pathlib import Path
from sqlalchemy import text
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from models.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup paths
project_root = Path(__file__).parent.parent
schema_file = project_root / 'backend' / 'models' / 'schema_cbs.sql'
data_file = project_root / 'data' / 'processed' / 'transactions_cleaned.csv'


def apply_schema(db):
    """Apply CBS schema to database"""
    logger.info("="*70)
    logger.info("STEP 1: APPLYING CBS SCHEMA")
    logger.info("="*70)

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    logger.info(f"Reading schema from: {schema_file}")
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Split into separate statements (handle multi-statement transactions)
    # PostgreSQL requires special handling for CREATE EXTENSION, DROP TABLE, etc.
    logger.info("Executing schema SQL...")

    try:
        with db.engine.begin() as connection:
            # Execute the entire schema as one transaction
            connection.execute(text(schema_sql))
            connection.commit()

        logger.info("✓ CBS schema applied successfully!")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to apply schema: {e}")
        raise


def load_transactions(db):
    """Load transactions from CSV into database"""
    logger.info("="*70)
    logger.info("STEP 2: LOADING CBS TRANSACTION DATA")
    logger.info("="*70)

    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")

    logger.info(f"Reading CSV from: {data_file}")
    df = pd.read_csv(data_file)
    logger.info(f"✓ Loaded {len(df):,} transactions from CSV")

    # Convert date column to proper format
    df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.date

    logger.info("Inserting transactions into database...")

    # Use bulk insert for performance
    records = df.to_dict('records')

    insert_sql = text("""
        INSERT INTO transactions (
            transaction_id,
            customer_name,
            product,
            category,
            amount,
            currency,
            transaction_date,
            status,
            customer_city,
            income_quintile
        ) VALUES (
            :transaction_id,
            :customer_name,
            :product,
            :category,
            :amount,
            :currency,
            :transaction_date,
            :status,
            :customer_city,
            :income_quintile
        )
        ON CONFLICT (transaction_id) DO NOTHING
    """)

    try:
        with db.engine.begin() as connection:
            # Insert in batches of 1000 for better performance
            batch_size = 1000
            total_inserted = 0

            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                connection.execute(insert_sql, batch)
                total_inserted += len(batch)

                if (i + batch_size) % 5000 == 0:
                    logger.info(f"  Inserted {total_inserted:,}/{len(records):,} transactions...")

            connection.commit()

        logger.info(f"✓ Successfully inserted {len(records):,} transactions!")
        logger.info("")
        return len(records)

    except Exception as e:
        logger.error(f"✗ Failed to load transactions: {e}")
        raise


def refresh_materialized_views(db):
    """Refresh all materialized views"""
    logger.info("="*70)
    logger.info("STEP 3: REFRESHING MATERIALIZED VIEWS")
    logger.info("="*70)

    try:
        with db.engine.begin() as connection:
            logger.info("Refreshing mv_daily_revenue...")
            connection.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_revenue"))

            logger.info("Refreshing mv_category_performance...")
            connection.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_performance"))

            logger.info("Refreshing mv_city_performance...")
            connection.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_city_performance"))

            logger.info("Refreshing mv_quintile_analysis...")
            connection.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_quintile_analysis"))

            connection.commit()

        logger.info("✓ All materialized views refreshed successfully!")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to refresh materialized views: {e}")
        logger.warning("This is expected if this is the first run (indexes don't exist yet)")
        logger.info("Attempting non-concurrent refresh...")

        try:
            with db.engine.begin() as connection:
                connection.execute(text("REFRESH MATERIALIZED VIEW mv_daily_revenue"))
                connection.execute(text("REFRESH MATERIALIZED VIEW mv_category_performance"))
                connection.execute(text("REFRESH MATERIALIZED VIEW mv_city_performance"))
                connection.execute(text("REFRESH MATERIALIZED VIEW mv_quintile_analysis"))
                connection.commit()

            logger.info("✓ Materialized views refreshed (non-concurrent mode)")
            logger.info("")
            return True
        except Exception as e2:
            logger.error(f"✗ Failed non-concurrent refresh: {e2}")
            return False


def run_validation_checks(db):
    """Run CBS schema validation checks"""
    logger.info("="*70)
    logger.info("STEP 4: RUNNING VALIDATION CHECKS")
    logger.info("="*70)

    try:
        with db.engine.begin() as connection:
            result = connection.execute(text("SELECT * FROM validate_cbs_schema()"))
            checks = result.fetchall()

        logger.info("\n📊 VALIDATION RESULTS:")
        logger.info("-" * 70)

        all_passed = True
        for check in checks:
            check_name, status, details = check
            symbol = "✓" if status == "PASS" else "✗"
            logger.info(f"{symbol} {check_name}: {status}")
            logger.info(f"   {details}")
            if status != "PASS":
                all_passed = False

        logger.info("-" * 70)
        if all_passed:
            logger.info("✓ All validation checks PASSED!")
        else:
            logger.warning("⚠ Some validation checks FAILED!")

        logger.info("")
        return all_passed

    except Exception as e:
        logger.error(f"✗ Failed to run validation checks: {e}")
        return False


def calculate_data_quality(db):
    """Calculate and report data quality metrics"""
    logger.info("="*70)
    logger.info("STEP 5: DATA QUALITY METRICS")
    logger.info("="*70)

    try:
        with db.engine.begin() as connection:
            result = connection.execute(text("SELECT * FROM calculate_data_quality()"))
            metrics = result.fetchone()

        completeness, uniqueness, validity, overall = metrics

        logger.info("\n📊 DATA QUALITY SCORES:")
        logger.info("-" * 70)
        logger.info(f"  Completeness:  {completeness:.2f}%")
        logger.info(f"  Uniqueness:    {uniqueness:.2f}%")
        logger.info(f"  Validity:      {validity:.2f}%")
        logger.info(f"  Overall Score: {overall:.2f}%")
        logger.info("-" * 70)

        if overall >= 95:
            logger.info("✓ EXCELLENT data quality!")
        elif overall >= 85:
            logger.info("✓ GOOD data quality")
        elif overall >= 70:
            logger.info("⚠ ACCEPTABLE data quality")
        else:
            logger.warning("✗ POOR data quality - review data issues")

        logger.info("")
        return overall

    except Exception as e:
        logger.error(f"✗ Failed to calculate data quality: {e}")
        return None


def verify_data_loaded(db):
    """Verify data was loaded correctly"""
    logger.info("="*70)
    logger.info("STEP 6: VERIFICATION QUERIES")
    logger.info("="*70)

    try:
        with db.engine.begin() as connection:
            # Total transactions
            result = connection.execute(text("SELECT COUNT(*) FROM transactions"))
            total = result.scalar()
            logger.info(f"✓ Total transactions: {total:,}")

            # Total volume
            result = connection.execute(text("SELECT SUM(amount) FROM transactions WHERE status='completed'"))
            volume = result.scalar()
            logger.info(f"✓ Total volume: ILS {volume:,.2f}")

            # Date range
            result = connection.execute(text("SELECT MIN(transaction_date), MAX(transaction_date) FROM transactions"))
            min_date, max_date = result.fetchone()
            logger.info(f"✓ Date range: {min_date} to {max_date}")

            # Categories
            result = connection.execute(text("SELECT COUNT(DISTINCT category) FROM transactions"))
            categories = result.scalar()
            logger.info(f"✓ Unique categories: {categories}")

            # Cities
            result = connection.execute(text("SELECT COUNT(DISTINCT customer_city) FROM transactions"))
            cities = result.scalar()
            logger.info(f"✓ Unique cities: {cities}")

            # Products
            result = connection.execute(text("SELECT COUNT(DISTINCT product) FROM transactions"))
            products = result.scalar()
            logger.info(f"✓ Unique products: {products}")

            # Top 5 cities
            result = connection.execute(text("""
                SELECT customer_city, SUM(amount) as total
                FROM transactions
                WHERE status='completed'
                GROUP BY customer_city
                ORDER BY total DESC
                LIMIT 5
            """))
            logger.info("\n📊 TOP 5 CITIES BY SPENDING:")
            for i, (city, total) in enumerate(result.fetchall(), 1):
                logger.info(f"   {i}. {city}: ILS {total:,.2f}")

            # Quintile distribution
            result = connection.execute(text("""
                SELECT income_quintile, COUNT(*) as count, AVG(amount) as avg_amount
                FROM transactions
                GROUP BY income_quintile
                ORDER BY income_quintile
            """))
            logger.info("\n📊 INCOME QUINTILE DISTRIBUTION:")
            for q, count, avg in result.fetchall():
                logger.info(f"   Q{q}: {count:,} transactions (Avg: ILS {avg:.2f})")

        logger.info("")
        logger.info("✓ Data verification complete!")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        return False


def main():
    """Main execution function"""
    logger.info("="*70)
    logger.info("CBS DATA LOADER")
    logger.info("MarketPulse - Israeli Household Expenditure Analysis")
    logger.info("="*70)
    logger.info("")

    try:
        # Initialize database connection
        logger.info("Initializing database connection...")
        db = get_db()

        if not db.test_connection():
            logger.error("✗ Database connection failed!")
            logger.error("Please ensure PostgreSQL is running and DATABASE_URL is correct")
            return False

        logger.info("✓ Database connection successful!")
        logger.info("")

        # Step 1: Apply schema
        apply_schema(db)

        # Step 2: Load transactions
        records_loaded = load_transactions(db)

        # Step 3: Refresh materialized views
        refresh_materialized_views(db)

        # Step 4: Run validation checks
        validation_passed = run_validation_checks(db)

        # Step 5: Calculate data quality
        quality_score = calculate_data_quality(db)

        # Step 6: Verify data
        verify_data_loaded(db)

        # Final summary
        logger.info("="*70)
        logger.info("LOAD COMPLETE - SUMMARY")
        logger.info("="*70)
        logger.info(f"✓ Transactions loaded: {records_loaded:,}")
        logger.info(f"✓ Schema validation: {'PASSED' if validation_passed else 'FAILED'}")
        logger.info(f"✓ Data quality score: {quality_score:.2f}%")
        logger.info("")
        logger.info("Next Steps:")
        logger.info("  1. Update API endpoints to query CBS schema")
        logger.info("  2. Add /api/insights endpoint to serve business_insights.json")
        logger.info("  3. Test API endpoints with real data")
        logger.info("  4. Update frontend to display EDA insights")
        logger.info("="*70)

        return True

    except Exception as e:
        logger.error(f"✗ Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
