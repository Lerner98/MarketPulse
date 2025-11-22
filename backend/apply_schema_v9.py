"""
Apply V9 Production Schema to Database
"""
import sys
import io
from pathlib import Path
from sqlalchemy import text

# Fix Windows console encoding for emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(str(Path(__file__).parent))

from models.database import get_db

def apply_schema():
    """Read and execute schema_v9_production.sql"""
    schema_file = Path(__file__).parent / 'models' / 'schema_v9_production.sql'

    print(f"Reading schema: {schema_file}")

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    # Get database connection
    db = get_db()
    print(f"Connected to database")

    # Execute schema SQL file
    print(f"Executing schema...")
    db.execute_sql_file(str(schema_file))

    print(f"Schema applied successfully!")

    # Verify tables created
    print(f"\nVerifying tables...")
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
              AND table_name IN ('household_profiles', 'household_expenditures', 'retail_competition')
            ORDER BY table_name;
        """))

        tables = [row[0] for row in result]

        if len(tables) == 3:
            print(f"All 3 tables created:")
            for table in tables:
                print(f"   - {table}")
        else:
            print(f"Expected 3 tables, found {len(tables)}")
            for table in tables:
                print(f"   - {table}")

if __name__ == '__main__':
    try:
        apply_schema()
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise
