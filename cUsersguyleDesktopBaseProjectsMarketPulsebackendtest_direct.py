"""Direct test without TestClient to verify database works."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from models.database import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()

# Test direct database query
with db.get_session() as session:
    result = session.execute(text("""
        SELECT income_quintile, transaction_count
        FROM mv_quintile_analysis
        ORDER BY income_quintile
    """))
    rows = result.fetchall()
    print(f"✓ Found {len(rows)} quintiles in database:")
    for row in rows:
        print(f"  Q{row[0]}: {row[1]} transactions")

print("\n✓ Direct database query works!")
