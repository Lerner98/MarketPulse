"""
Update Table 38 Database Schema - Fix Column Mapping
Drops fake columns (bakery, local_market) and adds 8 real CBS columns
"""

import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import text

# Configure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(str(Path(__file__).parent.parent))
from models.database import get_db

def update_schema():
    """Update database schema for Table 38"""
    db = get_db()

    print("=" * 80)
    print("UPDATING TABLE 38 SCHEMA - CBS Store Type Competition")
    print("=" * 80)

    with db.engine.begin() as conn:
        # Check if table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'cbs_table_38_retail_battle'
            )
        """))
        table_exists = result.scalar()

        if not table_exists:
            print("\n📋 Creating new table cbs_table_38_retail_battle...")
            conn.execute(text("""
                CREATE TABLE cbs_table_38_retail_battle (
                    id SERIAL PRIMARY KEY,
                    category TEXT NOT NULL,
                    -- Spending amounts (NIS per household per month)
                    other NUMERIC DEFAULT 0,
                    special_shop NUMERIC DEFAULT 0,
                    butcher NUMERIC DEFAULT 0,
                    veg_fruit_shop NUMERIC DEFAULT 0,
                    online_supermarket NUMERIC DEFAULT 0,
                    supermarket_chain NUMERIC DEFAULT 0,
                    market NUMERIC DEFAULT 0,
                    grocery NUMERIC DEFAULT 0,
                    total NUMERIC DEFAULT 0,
                    -- Percentages (for analysis)
                    other_pct NUMERIC DEFAULT 0,
                    special_shop_pct NUMERIC DEFAULT 0,
                    butcher_pct NUMERIC DEFAULT 0,
                    veg_fruit_shop_pct NUMERIC DEFAULT 0,
                    online_supermarket_pct NUMERIC DEFAULT 0,
                    supermarket_chain_pct NUMERIC DEFAULT 0,
                    market_pct NUMERIC DEFAULT 0,
                    grocery_pct NUMERIC DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Table created successfully")
        else:
            print("\n📋 Table exists. Updating schema...")

            # Get current columns
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'cbs_table_38_retail_battle'
            """))
            current_columns = [row[0] for row in result]
            print(f"Current columns: {', '.join(current_columns)}")

            # Drop fake columns if they exist
            if 'bakery' in current_columns:
                print("\n🗑️  Dropping fake column: bakery")
                conn.execute(text("ALTER TABLE cbs_table_38_retail_battle DROP COLUMN IF EXISTS bakery"))

            if 'local_market' in current_columns:
                print("🗑️  Dropping fake column: local_market")
                conn.execute(text("ALTER TABLE cbs_table_38_retail_battle DROP COLUMN IF EXISTS local_market"))

            # Drop old 'supermarket' column if it exists (ambiguous name)
            if 'supermarket' in current_columns:
                print("🗑️  Dropping ambiguous column: supermarket")
                conn.execute(text("ALTER TABLE cbs_table_38_retail_battle DROP COLUMN IF EXISTS supermarket"))

            # Add new columns if they don't exist
            new_columns = [
                ('other', 'NUMERIC DEFAULT 0'),
                ('special_shop', 'NUMERIC DEFAULT 0'),
                ('butcher', 'NUMERIC DEFAULT 0'),
                ('veg_fruit_shop', 'NUMERIC DEFAULT 0'),
                ('online_supermarket', 'NUMERIC DEFAULT 0'),
                ('supermarket_chain', 'NUMERIC DEFAULT 0'),
                ('market', 'NUMERIC DEFAULT 0'),
                ('grocery', 'NUMERIC DEFAULT 0'),
                ('total', 'NUMERIC DEFAULT 0'),
                ('other_pct', 'NUMERIC DEFAULT 0'),
                ('special_shop_pct', 'NUMERIC DEFAULT 0'),
                ('butcher_pct', 'NUMERIC DEFAULT 0'),
                ('veg_fruit_shop_pct', 'NUMERIC DEFAULT 0'),
                ('online_supermarket_pct', 'NUMERIC DEFAULT 0'),
                ('supermarket_chain_pct', 'NUMERIC DEFAULT 0'),
                ('market_pct', 'NUMERIC DEFAULT 0'),
                ('grocery_pct', 'NUMERIC DEFAULT 0'),
            ]

            # Refresh column list
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'cbs_table_38_retail_battle'
            """))
            current_columns = [row[0] for row in result]

            for col_name, col_type in new_columns:
                if col_name not in current_columns:
                    print(f"➕ Adding column: {col_name}")
                    conn.execute(text(f"ALTER TABLE cbs_table_38_retail_battle ADD COLUMN {col_name} {col_type}"))

            print("✅ Schema updated successfully")

        # Clear old data
        print("\n🗑️  Clearing old data...")
        conn.execute(text("DELETE FROM cbs_table_38_retail_battle"))
        print("✅ Old data cleared")


def load_data():
    """Load corrected CSV into database"""
    db = get_db()

    print("\n📊 Loading corrected CBS data...")

    # Load CSV
    csv_path = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'table_38_retail.csv'
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} categories from CSV")

    # Insert into database
    with db.engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO cbs_table_38_retail_battle (
                    category, other, special_shop, butcher, veg_fruit_shop,
                    online_supermarket, supermarket_chain, market, grocery, total,
                    other_pct, special_shop_pct, butcher_pct, veg_fruit_shop_pct,
                    online_supermarket_pct, supermarket_chain_pct, market_pct, grocery_pct
                ) VALUES (
                    :category, :other, :special_shop, :butcher, :veg_fruit_shop,
                    :online_supermarket, :supermarket_chain, :market, :grocery, :total,
                    :other_pct, :special_shop_pct, :butcher_pct, :veg_fruit_shop_pct,
                    :online_supermarket_pct, :supermarket_chain_pct, :market_pct, :grocery_pct
                )
            """), {
                'category': row['category'],
                'other': float(row['other']),
                'special_shop': float(row['special_shop']),
                'butcher': float(row['butcher']),
                'veg_fruit_shop': float(row['veg_fruit_shop']),
                'online_supermarket': float(row['online_supermarket']),
                'supermarket_chain': float(row['supermarket_chain']),
                'market': float(row['market']),
                'grocery': float(row['grocery']),
                'total': float(row['total']),
                'other_pct': float(row['other_pct']),
                'special_shop_pct': float(row['special_shop_pct']),
                'butcher_pct': float(row['butcher_pct']),
                'veg_fruit_shop_pct': float(row['veg_fruit_shop_pct']),
                'online_supermarket_pct': float(row['online_supermarket_pct']),
                'supermarket_chain_pct': float(row['supermarket_chain_pct']),
                'market_pct': float(row['market_pct']),
                'grocery_pct': float(row['grocery_pct']),
            })

    print(f"✅ Loaded {len(df)} categories into database")


def verify_data():
    """Verify the loaded data"""
    db = get_db()

    print("\n🧪 VERIFICATION TEST: Alcoholic Beverages")
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT category, special_shop_pct, supermarket_chain_pct, grocery_pct
            FROM cbs_table_38_retail_battle
            WHERE category ILIKE '%alcoholic%'
        """))

        row = result.fetchone()
        if row:
            print(f"Category: {row[0]}")
            print(f"Special Shop: {row[1]}%")
            print(f"Supermarket Chain: {row[2]}%")
            print(f"Grocery: {row[3]}%")

            # Expected values from CBS screenshot
            if abs(float(row[1]) - 30.4) < 1 and abs(float(row[2]) - 51.1) < 1 and abs(float(row[3]) - 11.4) < 1:
                print("\n✅ VERIFICATION PASSED: Database matches CBS data!")
            else:
                print("\n❌ VERIFICATION FAILED: Database does NOT match CBS data!")
                print(f"Expected: special_shop=30.4%, supermarket_chain=51.1%, grocery=11.4%")
        else:
            print("❌ Alcoholic beverages not found in database")

    # Count total rows
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM cbs_table_38_retail_battle"))
        count = result.scalar()
        print(f"\n📊 Total categories in database: {count}")


if __name__ == '__main__':
    try:
        update_schema()
        load_data()
        verify_data()
        print("\n" + "=" * 80)
        print("✅ TABLE 38 SCHEMA UPDATE COMPLETE")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
