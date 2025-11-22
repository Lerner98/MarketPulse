"""Create strategic CBS schema in PostgreSQL"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

from models.database import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()

if not db.test_connection():
    print("[ERROR] Cannot connect to database")
    sys.exit(1)

session = db.SessionLocal()

try:
    # Read and execute schema
    schema_path = Path(__file__).parent / 'models' / 'schema_strategic.sql'
    schema_sql = schema_path.read_text(encoding='utf-8')

    # Execute the entire schema
    session.execute(text(schema_sql))
    session.commit()

    print("[SUCCESS] Strategic schema created successfully!")

except Exception as e:
    session.rollback()
    print(f"[ERROR] Failed to create schema: {e}")
    sys.exit(1)

finally:
    session.close()
    db.close()
