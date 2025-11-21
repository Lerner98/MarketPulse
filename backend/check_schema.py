"""
Check database schema and search_path.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from models.database import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()

with db.engine.connect() as conn:
    # Check search_path
    result = conn.execute(text("SHOW search_path"))
    search_path = result.scalar()
    print(f"Search path: {search_path}")

    # Check if views exist in public schema
    result = conn.execute(text("""
        SELECT schemaname, matviewname
        FROM pg_matviews
        WHERE matviewname LIKE 'mv_%'
    """))

    views = result.fetchall()
    print(f"\nMaterialized views found: {len(views)}")
    for schema, view in views:
        print(f"  - {schema}.{view}")

    # Check table
    result = conn.execute(text("""
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE tablename = 'transactions'
    """))

    tables = result.fetchall()
    print(f"\nTransactions table: {tables}")
