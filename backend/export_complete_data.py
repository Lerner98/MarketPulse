import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import sys

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv()

# Connect to database
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Export ALL data from the database
with engine.connect() as conn:
    # Query ALL data from the database
    query = text("""
        SELECT
            s.segment_type,
            s.segment_value,
            s.segment_order,
            f.item_name,
            f.expenditure_value,
            f.is_income_metric,
            f.is_consumption_metric
        FROM fact_segment_expenditure f
        JOIN dim_segment s ON f.segment_key = s.segment_key
        ORDER BY s.segment_type, s.segment_order, f.item_name
    """)

    df = pd.read_sql(query, conn)

    # Save to CSV
    df.to_csv('COMPLETE_DATABASE_EXPORT.csv', index=False, encoding='utf-8-sig')

    print(f"Exported {len(df)} records to COMPLETE_DATABASE_EXPORT.csv")
    print(f"\nFirst 10 rows:")
    print(df.head(10))
    print(f"\nLast 10 rows:")
    print(df.tail(10))
    print(f"\nData types:")
    print(df.dtypes)
