"""
Load Strategic CBS Data into PostgreSQL
Extracts from the 3 Excel files → Loads into database → Refreshes materialized views
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from extract_table_1_1 import load_table_1_1
from extract_table_40 import load_table_40
from extract_table_38 import load_table_38

from models.database import DatabaseManager
from sqlalchemy import text

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_quintile_expenditure(db_manager):
    """Load Table 1.1 into quintile_expenditure table"""
    logger.info("Loading quintile expenditure data...")

    df = load_table_1_1()

    session = db_manager.SessionLocal()
    try:
        # Clear existing data
        session.execute(text("TRUNCATE TABLE quintile_expenditure RESTART IDENTITY CASCADE"))

        # Insert new data
        for _, row in df.iterrows():
            query = text("""
                INSERT INTO quintile_expenditure (
                    category, quintile_1, quintile_2, quintile_3, quintile_4, quintile_5,
                    total_spending, avg_spending
                ) VALUES (
                    :category, :q1, :q2, :q3, :q4, :q5, :total, :avg
                )
            """)

            session.execute(query, {
                'category': row['category'],
                'q1': float(row['quintile_1']),
                'q2': float(row['quintile_2']),
                'q3': float(row['quintile_3']),
                'q4': float(row['quintile_4']),
                'q5': float(row['quintile_5']),
                'total': float(row['total_spending']),
                'avg': float(row['avg_spending'])
            })

        session.commit()
        logger.info(f"✅ Loaded {len(df)} quintile expenditure records")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to load quintile data: {e}")
        raise
    finally:
        session.close()


def load_purchase_methods(db_manager):
    """Load Table 40 into purchase_methods table"""
    logger.info("Loading purchase methods data...")

    df = load_table_40()

    session = db_manager.SessionLocal()
    try:
        # Clear existing data
        session.execute(text("TRUNCATE TABLE purchase_methods RESTART IDENTITY CASCADE"))

        # Insert new data
        for _, row in df.iterrows():
            query = text("""
                INSERT INTO purchase_methods (
                    category, physical_pct, online_israel_pct, online_abroad_pct
                ) VALUES (
                    :category, :physical, :israel, :abroad
                )
            """)

            session.execute(query, {
                'category': row['category'],
                'physical': float(row['physical_pct']),
                'israel': float(row['online_israel_pct']),
                'abroad': float(row['online_abroad_pct'])
            })

        session.commit()
        logger.info(f"✅ Loaded {len(df)} purchase method records")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to load purchase methods: {e}")
        raise
    finally:
        session.close()


def load_store_competition(db_manager):
    """Load Table 38 into store_competition table"""
    logger.info("Loading store competition data...")

    df = load_table_38()

    session = db_manager.SessionLocal()
    try:
        # Clear existing data
        session.execute(text("TRUNCATE TABLE store_competition RESTART IDENTITY CASCADE"))

        # Insert new data
        for _, row in df.iterrows():
            query = text("""
                INSERT INTO store_competition (
                    category, supermarket, local_market, butcher, bakery, other, total
                ) VALUES (
                    :category, :supermarket, :local, :butcher, :bakery, :other, :total
                )
            """)

            session.execute(query, {
                'category': row['category'],
                'supermarket': float(row['supermarket']),
                'local': float(row['local_market']),
                'butcher': float(row['butcher']),
                'bakery': float(row['bakery']),
                'other': float(row['other']),
                'total': float(row['total'])
            })

        session.commit()
        logger.info(f"✅ Loaded {len(df)} store competition records")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to load store competition: {e}")
        raise
    finally:
        session.close()


def refresh_materialized_views(db_manager):
    """Refresh all strategic materialized views"""
    logger.info("Refreshing materialized views...")

    session = db_manager.SessionLocal()
    try:
        session.execute(text("SELECT refresh_strategic_views()"))
        session.commit()
        logger.info("✅ Materialized views refreshed")

    except Exception as e:
        logger.error(f"❌ Failed to refresh views: {e}")
        raise
    finally:
        session.close()


def main():
    """Main loader pipeline"""
    print("=" * 70)
    print("STRATEGIC CBS DATA LOADER")
    print("Loading 3 datasets into PostgreSQL")
    print("=" * 70)

    db_manager = DatabaseManager()

    # Test connection
    if not db_manager.test_connection():
        logger.error("❌ Database connection failed!")
        return

    try:
        # Step 1: Load Table 1.1 (Quintile Expenditure)
        load_quintile_expenditure(db_manager)

        # Step 2: Load Table 40 (Purchase Methods)
        load_purchase_methods(db_manager)

        # Step 3: Load Table 38 (Store Competition)
        load_store_competition(db_manager)

        # Step 4: Refresh materialized views
        refresh_materialized_views(db_manager)

        print("\n" + "=" * 70)
        print("✅ ALL DATA LOADED SUCCESSFULLY")
        print("=" * 70)
        print("\nStrategic insights now available via API:")
        print("  GET /api/strategic/quintile-gap")
        print("  GET /api/strategic/digital-matrix")
        print("  GET /api/strategic/retail-battle")
        print("\nAPI will query materialized views for fast response times!")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        raise

    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
