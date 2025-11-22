"""
Refresh all materialized views after database update
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    print("Refreshing materialized views...")

    conn.execute(text('REFRESH MATERIALIZED VIEW vw_segment_burn_rate'))
    conn.commit()
    print("Refreshed: vw_segment_burn_rate")

    conn.execute(text('REFRESH MATERIALIZED VIEW vw_segment_inequality'))
    conn.commit()
    print("Refreshed: vw_segment_inequality")

    print("\nDone! All views refreshed.")
