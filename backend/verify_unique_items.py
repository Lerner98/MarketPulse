"""
Verify unique items per segment type
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("FINAL VERIFICATION - UNIQUE ITEMS PER SEGMENT TYPE")
print("="*80)

with engine.connect() as conn:
    # Total count
    result = conn.execute(text("SELECT COUNT(*) FROM fact_segment_expenditure;"))
    total = result.scalar()
    print(f"\nTotal records in database: {total}")
    print(f"Expected: 6,420")
    print(f"Status: {'PASS' if total == 6420 else 'FAIL'}")

    # Unique items per segment type
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

    print("\n" + "="*80)
    print("UNIQUE ITEMS PER SEGMENT TYPE")
    print("="*80)
    print(f"{'Segment Type':<30} {'Unique Items':<15} {'Total Records':<15}")
    print("-"*80)

    for row in result:
        print(f"{row[0]:<30} {row[1]:<15} {row[2]:<15}")
