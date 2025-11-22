"""
Run all verification queries requested by user
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

queries = {
    "1. Segment breakdown": """
        SELECT segment_type, COUNT(*)
        FROM dim_segment
        GROUP BY segment_type
        ORDER BY segment_type;
    """,

    "2. Records per segment type": """
        SELECT s.segment_type, COUNT(*) as records
        FROM fact_segment_expenditure f
        JOIN dim_segment s ON f.segment_key = s.segment_key
        GROUP BY s.segment_type
        ORDER BY records DESC;
    """,

    "3. CBS test case - Q1 income (MUST be 7510)": """
        SELECT f.expenditure_value
        FROM fact_segment_expenditure f
        JOIN dim_segment s ON f.segment_key = s.segment_key
        WHERE s.segment_type = 'Income Quintile'
        AND s.segment_value = '1'
        AND f.item_name LIKE '%Net money income per household%';
    """,

    "4. CBS test case - Q5 spending (MUST be 20076)": """
        SELECT f.expenditure_value
        FROM fact_segment_expenditure f
        JOIN dim_segment s ON f.segment_key = s.segment_key
        WHERE s.segment_type = 'Income Quintile'
        AND s.segment_value = '5'
        AND f.item_name LIKE '%Money expenditure per household%';
    """,

    "5. Burn rate values (Q1 should be ~146%, Q5 should be ~60%)": """
        SELECT segment_value, burn_rate_pct
        FROM vw_segment_burn_rate
        ORDER BY segment_value;
    """
}

print("=" * 80)
print("DATABASE VERIFICATION QUERIES")
print("=" * 80)

with engine.connect() as conn:
    for title, query in queries.items():
        print(f"\n{title}")
        print("-" * 80)
        result = conn.execute(text(query))
        rows = result.fetchall()

        if not rows:
            print("NO RESULTS")
        else:
            for row in rows:
                print(row)
