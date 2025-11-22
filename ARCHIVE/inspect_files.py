import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).parent.parent.parent
cbs_dir = project_root / 'CBS Household Expenditure Data Strategy'

# Inspect Table 40
print("=" * 70)
print("TABLE 40 STRUCTURE")
print("=" * 70)
filepath40 = cbs_dir / 'רכישות מוצרים נבחרים לפי אופן.xlsx'
df40 = pd.read_excel(filepath40, header=7, nrows=20)
print(f"Columns: {df40.columns.tolist()}")
print(f"\nFirst 10 rows:")
print(df40.iloc[:10, :6])

print("\n" + "=" * 70)
print("TABLE 38 STRUCTURE")
print("=" * 70)
filepath38 = cbs_dir / 'הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות.xlsx'
df38 = pd.read_excel(filepath38, header=7, nrows=20)
print(f"Columns: {df38.columns.tolist()}")
print(f"\nFirst 10 rows:")
print(df38.iloc[:10, :6])
