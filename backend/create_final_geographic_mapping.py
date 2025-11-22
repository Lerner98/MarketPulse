"""
Create FINAL VERIFIED Geographic Region mapping
Extracts Hebrew names from Row 4 and English names from Row 8
Maps to household counts from Row 10
"""
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

CBS_DIR = r"C:\Users\guyle\Desktop\Base\Projects\MarketPulse\CBS Household Expenditure Data Strategy"
FILE_NAME = "WorkStatus-IncomeSource.xlsx"
FILE_PATH = os.path.join(CBS_DIR, FILE_NAME)

# Read with header=4 to get Hebrew names
df_hebrew = pd.read_excel(FILE_PATH, header=4)
hebrew_columns = df_hebrew.columns.tolist()[1:-2]  # Skip first and last 2 columns

# Read with header=8 to get English names
df_english = pd.read_excel(FILE_PATH, header=8)
english_columns = df_english.columns.tolist()[1:-2]  # Skip first and last 2 columns

# Read with header=10 to get household counts (what ETL uses as codes)
df_counts = pd.read_excel(FILE_PATH, header=10)
code_columns = df_counts.columns.tolist()[1:-2]  # Skip first and last 2 columns

print(f"Hebrew columns: {len(hebrew_columns)}")
print(f"English columns: {len(english_columns)}")
print(f"Code columns: {len(code_columns)}")
print()

# Manual correction mapping (CBS has fragmented headers)
MANUAL_HEBREW_NAMES = [
    'יהודה והשומרון',    # Judea & Samaria (cols 1-2 merged)
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

MANUAL_ENGLISH_NAMES = [
    'Judea & Samaria',
    "Be'er Sheva",
    'Ashqelon',
    'Holon',
    'Ramat Gan',
    'Tel Aviv',
    'Rehovot',
    'Ramla',
    'Petah Tiqwa',
    'Sharon',
    'Hadera',
    'Haifa',
    'Akko',
    "Yizre'el",
    'Zefat, Kinneret & Golan',
    'Jerusalem'
]

# Create mapping
print("=== VERIFIED MAPPING ===")
mapping_data = []
for i, (code, hebrew, english) in enumerate(zip(code_columns, MANUAL_HEBREW_NAMES, MANUAL_ENGLISH_NAMES)):
    mapping_data.append({
        'segment_code': str(code),
        'hebrew_name': hebrew,
        'english_name': english,
        'households_in_sample': code,
        'position': i+1
    })
    print(f"{code:>4} → {hebrew:20} | {english}")

# Save to CSV
df_mapping = pd.DataFrame(mapping_data)
output_file = 'FINAL_VERIFIED_geographic_mapping.csv'
df_mapping.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n✅ Saved to: {output_file}")

print("\n=== TYPESCRIPT CODE (Hebrew) ===")
print("const GEOGRAPHIC_REGION_MAP: Record<string, string> = {")
for item in mapping_data:
    code = item['segment_code']
    hebrew = item['hebrew_name']
    print(f"  '{code}': '{hebrew}',  // {item['english_name']}")
print("};")
