"""
Apply V10 Normalized Star Schema to PostgreSQL Database

This script:
1. Reads schema_v10_normalized.sql
2. Executes it against the database
3. Verifies tables were created successfully
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()


def apply_schema_v10():
    """Apply V10 normalized star schema to database"""
    print("\n" + "="*80)
    print("APPLYING V10 NORMALIZED STAR SCHEMA")
    print("="*80)

    # Get database connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return False

    engine = create_engine(DATABASE_URL)

    # Read schema file
    schema_file = Path(__file__).parent / 'models' / 'schema_v10_normalized.sql'

    if not schema_file.exists():
        print(f"❌ ERROR: Schema file not found: {schema_file}")
        return False

    print(f"\n📄 Reading schema from: {schema_file.name}")

    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Execute schema
    print("\n🔨 Executing SQL schema...")

    try:
        with engine.begin() as conn:
            # Execute entire schema as one transaction (handles multi-line functions)
            conn.execute(text(schema_sql))

        print(f"   ✅ Schema executed successfully")

    except Exception as e:
        print(f"❌ ERROR executing schema: {e}")
        return False

    # Verify tables were created
    print("\n🔍 Verifying table creation...")

    try:
        with engine.connect() as conn:
            # Check dim_segment
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = 'dim_segment'
            """)).scalar()

            if result > 0:
                print("   ✅ dim_segment table created")
            else:
                print("   ❌ dim_segment table NOT found")
                return False

            # Check fact_segment_expenditure
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = 'fact_segment_expenditure'
            """)).scalar()

            if result > 0:
                print("   ✅ fact_segment_expenditure table created")
            else:
                print("   ❌ fact_segment_expenditure table NOT found")
                return False

            # Check materialized views
            result = conn.execute(text("""
                SELECT COUNT(*) FROM pg_matviews
                WHERE matviewname IN ('vw_segment_inequality', 'vw_segment_burn_rate')
            """)).scalar()

            print(f"   ✅ {result} materialized views created")

            # Check functions
            result = conn.execute(text("""
                SELECT COUNT(*) FROM pg_proc
                WHERE proname IN ('refresh_all_segment_views', 'get_expenditure_by_segment_type', 'get_top_inequality_by_segment')
            """)).scalar()

            print(f"   ✅ {result} helper functions created")

            # Check sample data
            segment_count = conn.execute(text("SELECT COUNT(*) FROM dim_segment")).scalar()
            print(f"   ✅ Sample data: {segment_count} segments inserted")

    except Exception as e:
        print(f"❌ ERROR during verification: {e}")
        return False

    print("\n" + "="*80)
    print("✅ V10 SCHEMA APPLIED SUCCESSFULLY")
    print("="*80)
    print("\nNext steps:")
    print("1. Run ETL pipeline: python etl/load_segmentation.py")
    print("2. Verify data loading")
    print("3. Create API endpoints")
    print("4. Update frontend")

    return True


if __name__ == '__main__':
    success = apply_schema_v10()
    sys.exit(0 if success else 1)
