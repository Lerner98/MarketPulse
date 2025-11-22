"""
Create CORRECT Geographic Region mapping
Maps household sample counts (column names when header=10) to region names (from header=8)
"""
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

CBS_DIR = r"C:\Users\guyle\Desktop\Base\Projects\MarketPulse\CBS Household Expenditure Data Strategy"
FILE_NAME = "WorkStatus-IncomeSource.xlsx"
FILE_PATH = os.path.join(CBS_DIR, FILE_NAME)

# Read with header=8 to get region names
df_names = pd.read_excel(FILE_PATH, header=8)
region_columns_names = df_names.columns.tolist()[1:-2]  # Skip first and last 2 columns

# Read with header=10 to get household counts (what ETL uses)
df_counts = pd.read_excel(FILE_PATH, header=10)
region_columns_counts = df_counts.columns.tolist()[1:-2]  # Skip first and last 2 columns

print("=== POSITION MATCHING ===")
print(f"Number of regions (from names): {len(region_columns_names)}")
print(f"Number of regions (from counts): {len(region_columns_counts)}")
print()

# Create mapping
mapping = {}
for i, (code, name) in enumerate(zip(region_columns_counts, region_columns_names)):
    # Normalize name
    name_clean = name.strip()

    # Build full names from fragments
    if name_clean == 'Samaria':
        name_clean = 'Judea & Samaria'
    elif name_clean == 'Sheva':
        name_clean = "Be'er Sheva"
    elif name_clean == ' Gan':
        name_clean = 'Ramat Gan'
    elif name_clean == 'Tiqwa':
        name_clean = 'Petah Tiqwa'
    elif name_clean == '& Golan':
        name_clean = 'Zefat, Kinneret & Golan'
    elif name_clean == "Yizre'el":
        name_clean = "Yizre'el"

    mapping[str(code)] = name_clean
    print(f"Code {code} ({type(code).__name__}) → {name_clean}")

print("\n=== TYPESCRIPT MAPPING ===")
print("const GEOGRAPHIC_REGION_MAP: Record<string, string> = {")
for code, name in mapping.items():
    print(f"  '{code}': '{name}',")
print("};")

# Save to CSV
df_mapping = pd.DataFrame({
    'segment_code': list(mapping.keys()),
    'english_name': list(mapping.values()),
    'source': ['CBS Table 10, Row 8 (English names) matched to Row 10 (column positions)'] * len(mapping)
})

output_file = 'CORRECT_geographic_mapping.csv'
df_mapping.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n✅ Saved to: {output_file}")
