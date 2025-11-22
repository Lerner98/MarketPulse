"""
Quick script to refresh materialized views for testing.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from models.database import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()

print("Refreshing materialized views...")

with db.engine.begin() as conn:
    # Check if views exist
    views = ['mv_quintile_analysis', 'mv_category_performance', 'mv_city_performance', 'mv_daily_revenue']

    for view in views:
        try:
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM pg_matviews
                    WHERE matviewname = '{view}'
                )
            """))
            exists = result.scalar()

            if exists:
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                print(f"✓ Refreshed {view}")
            else:
                print(f"✗ View {view} does not exist")
        except Exception as e:
            print(f"✗ Error with {view}: {e}")

print("\nDone!")
