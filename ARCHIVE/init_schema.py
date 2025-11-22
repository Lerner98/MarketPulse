"""Initialize database schema from SQL file."""

import sys
from pathlib import Path

from sqlalchemy import text

sys.path.append(str(Path(__file__).parent))

from models.database import DatabaseManager

def main():
    """Initialize database schema."""
    print("Initializing database schema...")

    # Read schema file
    schema_file = Path(__file__).parent / "models" / "schema_advanced.sql"

    if not schema_file.exists():
        print(f"Error: Schema file not found: {schema_file}")
        return

    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Execute schema
    db = DatabaseManager()

    try:
        with db.get_session() as session:
            # Execute entire schema as one statement (handles $$ properly)
            print("Executing schema...")
            session.execute(text(schema_sql))
            session.commit()

        print("[+] Database schema initialized successfully!")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
