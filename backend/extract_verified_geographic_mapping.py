"""
Create VERIFIED Geographic Region mapping from CBS Excel source
Maps household sample counts (used as segment codes) to actual region names
"""
import pandas as pd
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# VERIFIED mapping extracted from WorkStatus-IncomeSource.xlsx Row 8 & Row 10
# The numbers are household sample counts that were incorrectly used as segment codes
VERIFIED_GEOGRAPHIC_MAPPING = {
    '281': 'יהודה והשומרון',  # Judea & Samaria Area
    '471': 'באר שבע',         # Be'er Sheva
    '405': 'אשקלון',          # Ashqelon
    '117': 'חולון',           # Holon
    '132': 'רמת גן',          # Ramat Gan
    '218': 'תל אביב',         # Tel Aviv
    '362': 'רחובות',          # Rehovot
    '260': 'רמלה',            # Ramla
    '230': 'פתח תקווה',       # Petah Tiqwa
    '143': 'השרון',           # Sharon
    '323': 'חדרה',            # Hadera
    '551': 'חיפה',            # Haifa
    '481': 'עכו',             # Akko
    '421': 'יזרעאל',          # Yizre'el
    '200': 'צפת, כנרת וגולן', # Zefat, Kinneret & Golan
    '883': 'ירושלים'          # Jerusalem
}

# Also create English version for reference
ENGLISH_NAMES = {
    '281': 'Judea & Samaria',
    '471': "Be'er Sheva",
    '405': 'Ashqelon',
    '117': 'Holon',
    '132': 'Ramat Gan',
    '218': 'Tel Aviv',
    '362': 'Rehovot',
    '260': 'Ramla',
    '230': 'Petah Tiqwa',
    '143': 'Sharon',
    '323': 'Hadera',
    '551': 'Haifa',
    '481': 'Akko',
    '421': "Yizre'el",
    '200': 'Zefat, Kinneret & Golan',
    '883': 'Jerusalem'
}

# Create DataFrame
df = pd.DataFrame({
    'segment_code': list(VERIFIED_GEOGRAPHIC_MAPPING.keys()),
    'hebrew_name': list(VERIFIED_GEOGRAPHIC_MAPPING.values()),
    'english_name': list(ENGLISH_NAMES.values()),
    'source': ['CBS Table 10 - WorkStatus-IncomeSource.xlsx Row 10 (Household Sample Count)'] * len(VERIFIED_GEOGRAPHIC_MAPPING)
})

# Save to CSV
output_file = 'VERIFIED_geographic_mapping.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("=== VERIFIED GEOGRAPHIC REGION MAPPING ===\n")
print(df.to_string(index=False))
print(f"\n✅ Saved to: {output_file}")

print("\n=== ROOT CAUSE ===")
print("The ETL process mistakenly used 'household sample counts' (from Row 10)")
print("as segment codes instead of the actual region names (from Row 8).")
print("This is why we see '117', '132', '218' instead of 'Holon', 'Ramat Gan', 'Tel Aviv'.")
