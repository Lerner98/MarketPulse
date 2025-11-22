"""
Extract Geographic Region raw data from database to CSV
Purpose: Verify what the numeric codes actually represent before creating translation mappings
"""
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in environment")

engine = create_engine(DATABASE_URL)

print("Extracting Geographic Region segments from database...")

with engine.connect() as conn:
    # Extract all Geographic Region segments
    query = text("""
        SELECT segment_type, segment_value, segment_order
        FROM dim_segment
        WHERE segment_type = 'Geographic Region'
        ORDER BY segment_order
    """)
    df = pd.read_sql(query, conn)

    # Save to CSV with UTF-8 BOM for Excel compatibility
    output_file = 'geographic_segments_RAW.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\nExtracted {len(df)} Geographic Region segments")
    print(f"Saved to: {output_file}")
    print("\nData preview:")
    print(df.to_string())

print("\n✅ Extraction complete!")
