"""Test validation function"""
import sys
from pathlib import Path
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))

from models.database import get_db

db = get_db()

with db.engine.begin() as connection:
    result = connection.execute(text("SELECT * FROM validate_cbs_schema()"))
    print("\n📊 CBS SCHEMA VALIDATION RESULTS:")
    print("-" * 70)
    for row in result.fetchall():
        symbol = "✓" if row[1] == "PASS" else "✗"
        print(f"{symbol} {row[0]}: {row[1]}")
        print(f"   {row[2]}")
    print("-" * 70)
