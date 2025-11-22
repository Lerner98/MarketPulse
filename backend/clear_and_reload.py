"""
Clear duplicate data and reload ETL once
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import subprocess
import sys

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("CLEARING DATABASE")
print("="*80)

with engine.begin() as conn:
    print("Truncating fact_segment_expenditure...")
    conn.execute(text("TRUNCATE fact_segment_expenditure CASCADE;"))

    print("Truncating dim_segment...")
    conn.execute(text("TRUNCATE dim_segment CASCADE;"))

    print("✅ Database cleared")

print("\n" + "="*80)
print("VERIFYING CLEARED STATE")
print("="*80)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM fact_segment_expenditure;"))
    count = result.scalar()
    print(f"fact_segment_expenditure: {count} records (should be 0)")

    result = conn.execute(text("SELECT COUNT(*) FROM dim_segment;"))
    count = result.scalar()
    print(f"dim_segment: {count} records (should be 0)")

print("\n" + "="*80)
print("RELOADING ETL - ONCE ONLY")
print("="*80)

subprocess.run(["python", "etl/load_segmentation.py"], cwd="backend")

print("\n" + "="*80)
print("FINAL VERIFICATION")
print("="*80)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM fact_segment_expenditure;"))
    count = result.scalar()
    print(f"fact_segment_expenditure: {count} records (should be 6,420)")

    result = conn.execute(text("""
        SELECT
            s.segment_type,
            COUNT(DISTINCT f.item_name) as unique_items,
            COUNT(*) as total_records
        FROM fact_segment_expenditure f
        JOIN dim_segment s ON f.segment_key = s.segment_key
        GROUP BY s.segment_type
        ORDER BY unique_items DESC;
    """))

    print("\nUnique items per segment type:")
    for row in result:
        print(f"  {row[0]}: {row[1]} unique items, {row[2]} total records")
