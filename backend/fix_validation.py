"""Quick script to update validation function"""
import sys
from pathlib import Path
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
from models.database import get_db

db = get_db()

fix_sql = """
CREATE OR REPLACE FUNCTION validate_cbs_schema()
RETURNS TABLE(
    check_name VARCHAR,
    status VARCHAR,
    details TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        'Column Count'::VARCHAR,
        CASE WHEN COUNT(*) = 12 THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        ('Expected 12 columns (10 CBS + 2 timestamps), found: ' || COUNT(*)::TEXT)::TEXT
    FROM information_schema.columns
    WHERE table_name = 'transactions';

    RETURN QUERY
    SELECT
        'Currency Check'::VARCHAR,
        CASE WHEN COUNT(*) = COUNT(*) FILTER (WHERE currency = 'ILS') THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        'All transactions should be in ILS'::TEXT
    FROM transactions;

    RETURN QUERY
    SELECT
        'Quintile Range'::VARCHAR,
        CASE WHEN MIN(income_quintile) >= 1 AND MAX(income_quintile) <= 5 THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        ('Quintile range: ' || MIN(income_quintile)::TEXT || ' to ' || MAX(income_quintile)::TEXT)::TEXT
    FROM transactions;

    RETURN QUERY
    SELECT
        'Hebrew Text'::VARCHAR,
        CASE WHEN COUNT(*) > 0 THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        ('Products with Hebrew characters: ' || COUNT(*)::TEXT)::TEXT
    FROM transactions
    WHERE product ~ '[\\u0590-\\u05FF]';
END;
$$ LANGUAGE plpgsql;
"""

with db.engine.begin() as connection:
    connection.execute(text(fix_sql))
    connection.commit()
    print("✓ Validation function updated")

    result = connection.execute(text("SELECT * FROM validate_cbs_schema()"))
    print("\n📊 VALIDATION RESULTS:")
    for row in result.fetchall():
        print(f"  {row[0]}: {row[1]} - {row[2]}")
