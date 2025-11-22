"""
Read specific cell C6 from WorkStatus-IncomeSource.xlsx
"""
import pandas as pd
import openpyxl
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

CBS_DIR = r"C:\Users\guyle\Desktop\Base\Projects\MarketPulse\CBS Household Expenditure Data Strategy"
FILE_NAME = "WorkStatus-IncomeSource.xlsx"
FILE_PATH = os.path.join(CBS_DIR, FILE_NAME)

print(f"Reading cell C6 from: {FILE_NAME}\n")

# Method 1: Using openpyxl (direct cell access)
print("=== METHOD 1: openpyxl ===")
wb = openpyxl.load_workbook(FILE_PATH)
ws = wb.active
cell_value = ws['C6'].value
print(f"Cell C6 value: '{cell_value}'")
print(f"Type: {type(cell_value)}")

# Method 2: Using pandas (row/column indexing)
print("\n=== METHOD 2: pandas ===")
df = pd.read_excel(FILE_PATH, header=None)
# C6 = Row 5 (0-indexed), Column 2 (C = 2)
pandas_value = df.iloc[5, 2]
print(f"Row 5, Column 2 (C6) value: '{pandas_value}'")
print(f"Type: {type(pandas_value)}")

# Show surrounding cells for context
print("\n=== SURROUNDING CELLS (Row 5, Columns A-G) ===")
for col_idx in range(7):
    col_letter = chr(65 + col_idx)  # A=65, B=66, etc.
    value = df.iloc[5, col_idx]
    print(f"{col_letter}6: '{value}'")
