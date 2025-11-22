"""
DATABASE FIX: Update dim_segment to use Hebrew names instead of numeric codes
This is the "GODLY STABILITY" fix that corrects the database at the source
"""
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Load the verified mapping (Single Source of Truth)
mapping_file = 'data/geographic_segment_map.csv'
df_map = pd.read_csv(mapping_file, encoding='utf-8-sig')

print("=== VERIFIED GEOGRAPHIC MAPPING ===")
print(df_map.to_string(index=False))

# Create mapping dictionary
code_to_hebrew = dict(zip(df_map['segment_code'].astype(str), df_map['hebrew_name']))

print("\n=== FIXING DATABASE ===")

with engine.connect() as conn:
    # Check current state
    result = conn.execute(text("""
        SELECT segment_key, segment_value
        FROM dim_segment
        WHERE segment_type = 'Geographic Region'
        ORDER BY segment_order
    """)).fetchall()

    print(f"\n📊 Found {len(result)} Geographic Region segments")
    print("\nCURRENT (BROKEN) VALUES:")
    for row in result:
        segment_key, segment_value = row
        print(f"  Key {segment_key}: '{segment_value}'")

    # Update each segment with correct Hebrew name
    print("\n🔧 APPLYING FIX...")
    updated_count = 0

    for row in result:
        segment_key, old_value = row

        # Look up correct Hebrew name
        if old_value in code_to_hebrew:
            new_value = code_to_hebrew[old_value]

            # Update database
            conn.execute(
                text("""
                    UPDATE dim_segment
                    SET segment_value = :new_value
                    WHERE segment_key = :segment_key
                """),
                {"new_value": new_value, "segment_key": segment_key}
            )

            print(f"  ✅ Updated key {segment_key}: '{old_value}' → '{new_value}'")
            updated_count += 1
        else:
            print(f"  ⚠️  No mapping for '{old_value}' (key {segment_key})")

    # Commit changes
    conn.commit()

    print(f"\n✅ Updated {updated_count} segments")

    # Verify fix
    print("\n🔍 VERIFICATION - Updated values:")
    result_after = conn.execute(text("""
        SELECT segment_key, segment_value
        FROM dim_segment
        WHERE segment_type = 'Geographic Region'
        ORDER BY segment_order
    """)).fetchall()

    for row in result_after:
        segment_key, segment_value = row
        print(f"  Key {segment_key}: '{segment_value}'")

print("\n✅ DATABASE FIX COMPLETE!")
print("The API will now return Hebrew names directly.")
print("Frontend translation layer is no longer needed (but kept as defensive backup).")
