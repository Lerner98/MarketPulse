"""
Extract Geographic Region data from WorkStatus-IncomeSource.xlsx
Purpose: Verify actual CBS codes vs expected region names
"""
import pandas as pd
import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Path to CBS file
CBS_DIR = r"C:\Users\guyle\Desktop\Base\Projects\MarketPulse\CBS Household Expenditure Data Strategy"
FILE_NAME = "WorkStatus-IncomeSource.xlsx"
FILE_PATH = os.path.join(CBS_DIR, FILE_NAME)

print(f"Reading: {FILE_PATH}\n")

# Read Excel with proper encoding
df = pd.read_excel(FILE_PATH, sheet_name=0, header=None)

print("=== FIRST 20 ROWS (to find header structure) ===")
print(df.head(20).to_string())

print("\n\n=== EXTRACTING GEOGRAPHIC COLUMNS ===")
# According to docs, header_row should be at row 10 (0-indexed = row 9)
# Let's check rows 8-12 to find the actual header row

for i in range(8, 13):
    print(f"\nRow {i}: {df.iloc[i].tolist()}")
