"""
Find which row contains the actual region names
"""
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

CBS_DIR = r"C:\Users\guyle\Desktop\Base\Projects\MarketPulse\CBS Household Expenditure Data Strategy"
FILE_NAME = "WorkStatus-IncomeSource.xlsx"
FILE_PATH = os.path.join(CBS_DIR, FILE_NAME)

print("Testing different header rows to find region names...\n")

# Try reading with different header rows
for header_row in range(0, 12):
    df = pd.read_excel(FILE_PATH, header=header_row)
    cols = df.columns.tolist()

    print(f"=== HEADER_ROW={header_row} ===")
    print(f"Columns: {cols[:10]}")

    # Check if we see region names
    has_regions = any('Tel Aviv' in str(col) or 'Haifa' in str(col) or 'Jerusalem' in str(col) for col in cols)
    if has_regions:
        print("✅ FOUND REGION NAMES!")
        print(f"All columns: {cols}")
    print()
