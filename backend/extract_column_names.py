"""
Extract actual column names from WorkStatus-IncomeSource.xlsx
to understand what segment codes are being used
"""
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

CBS_DIR = r"C:\Users\guyle\Desktop\Base\Projects\MarketPulse\CBS Household Expenditure Data Strategy"
FILE_NAME = "WorkStatus-IncomeSource.xlsx"
FILE_PATH = os.path.join(CBS_DIR, FILE_NAME)

print(f"Reading: {FILE_PATH}\n")

# The ETL config says header_row=10 (0-indexed = row 9)
# Let's check what pandas reads with header=10
df = pd.read_excel(FILE_PATH, header=10)

print("=== COLUMN NAMES (What ETL sees as segment values) ===")
for i, col in enumerate(df.columns):
    print(f"Column {i}: '{col}' (type: {type(col).__name__})")

print(f"\n=== FIRST 5 ROWS OF DATA ===")
print(df.head().to_string())
