"""
FIXED Geographic Region Extraction
Properly reads multi-row headers from CBS Excel file instead of using numeric column names
"""
import pandas as pd
import openpyxl
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

CBS_DIR = Path(r"C:\Users\guyle\Desktop\Base\Projects\MarketPulse\CBS Household Expenditure Data Strategy")
FILE_NAME = "WorkStatus-IncomeSource.xlsx"
FILE_PATH = CBS_DIR / FILE_NAME

print(f"Processing: {FILE_NAME}\n")

# ============================================================================
# CORRECT APPROACH: Read multi-row header using openpyxl
# ============================================================================

wb = openpyxl.load_workbook(FILE_PATH)
ws = wb.active

# Extract Hebrew region names from Row 5 (0-indexed row 4)
# CBS structure: Row 5 has Hebrew names like "באר שבע", "אשקלון", etc.
hebrew_names = []
for col_idx in range(2, 18):  # Columns B to Q (regions start at column B)
    cell = ws.cell(row=5, column=col_idx)
    value = cell.value
    if value and isinstance(value, str) and value.strip():
        hebrew_names.append(value.strip())

print(f"Extracted {len(hebrew_names)} Hebrew region names from Row 5:")
for i, name in enumerate(hebrew_names, 1):
    print(f"  {i}. {name}")

# ============================================================================
# Now read data with correct approach
# ============================================================================

# Read with header=10 to get the DATA structure
df = pd.read_excel(FILE_PATH, header=10)

print(f"\n📊 Data shape: {df.shape}")
print(f"Columns from header=10: {df.columns.tolist()[:5]}")

# Get the item column (first column)
item_col = df.columns[0]

# Get region columns (numeric codes: 281, 471, etc.)
region_code_cols = [col for col in df.columns[1:-2] if isinstance(col, int)]

print(f"\n🔢 Region code columns (household counts): {region_code_cols}")
print(f"Number of codes: {len(region_code_cols)}")
print(f"Number of names: {len(hebrew_names)}")

# ============================================================================
# FIX: Create mapping from codes to Hebrew names
# ============================================================================

# Build complete Hebrew names (some are split across rows)
COMPLETE_HEBREW_NAMES = [
    'יהודה והשומרון',    # Judea & Samaria
    'באר שבע',           # Be'er Sheva
    'אשקלון',            # Ashqelon
    'חולון',             # Holon
    'רמת גן',            # Ramat Gan
    'תל אביב',           # Tel Aviv
    'רחובות',            # Rehovot
    'רמלה',              # Ramla
    'פתח תקווה',         # Petah Tiqwa
    'השרון',             # Sharon
    'חדרה',              # Hadera
    'חיפה',              # Haifa
    'עכו',               # Akko
    'יזרעאל',            # Yizre'el
    'צפת, כנרת וגולן',   # Zefat, Kinneret & Golan
    'ירושלים'            # Jerusalem
]

# Create code → name mapping
code_to_name = {
    str(code): name
    for code, name in zip(region_code_cols, COMPLETE_HEBREW_NAMES)
}

print("\n✅ CODE → HEBREW NAME MAPPING:")
for code, name in code_to_name.items():
    print(f"  {code:>4} → {name}")

# ============================================================================
# Extract data with CORRECT segment values (Hebrew names, not codes)
# ============================================================================

# Melt dataframe
df_long = df.melt(
    id_vars=[item_col],
    value_vars=region_code_cols,
    var_name='segment_code',
    value_name='expenditure_value'
)

# CRITICAL FIX: Replace numeric codes with Hebrew names
df_long['segment_value'] = df_long['segment_code'].astype(str).map(code_to_name)

# Rename columns
df_long = df_long.rename(columns={item_col: 'item_name'})

# Add segment type
df_long['segment_type'] = 'Geographic Region'

# Drop rows with no expenditure value
df_long = df_long.dropna(subset=['expenditure_value'])

print(f"\n📊 Extracted {len(df_long)} records")
print("\nSample data:")
print(df_long[['segment_type', 'segment_value', 'item_name', 'expenditure_value']].head(10))

print("\n✅ VERIFICATION: Unique segment values (should be Hebrew names):")
print(df_long['segment_value'].unique())

# Save for inspection
output_file = CBS_DIR.parent / 'backend' / 'geographic_FIXED_extract.csv'
df_long.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n💾 Saved to: {output_file}")
