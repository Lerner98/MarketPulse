"""
CORRECTED ETL CONFIGURATION - MarketPulse V10
Load ALL 8 CBS files with proper mapping

This replaces the broken load_segmentation.py that was looking for non-existent ta2-ta13 files.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# ============================================================================
# FILE CONFIGURATION - CORRECTED FOR ACTUAL FILES
# ============================================================================

SEGMENTATION_FILES = {
    # File 1: Income Quintile (Main file) ✅
    'הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx': {
        'segment_type': 'Income Quintile',
        'table_number': '1.1',
        'header_row': 6,  # Row with "5 4 3 2 1 Total"
        'segment_pattern': r'^[1-5]$|^Total$',  # Matches: 5, 4, 3, 2, 1, Total
        'income_row_keyword': 'Net money income per household',
        'consumption_row_keyword': 'Money expenditure per household',
    },
    
    # File 2: Income Decile (Net) ❌ NOT LOADED YET
    'Income_Decile.xlsx': {
        'segment_type': 'Income Decile (Net)',
        'table_number': '2',
        'header_row': 5,  # Row with "10 9 8 7 6 5 4 3 2 1 Total"
        'segment_pattern': r'^[1-9]$|^10$|^Total$',
        'income_row_keyword': 'Net money income per household',
        'consumption_row_keyword': 'Money expenditure per household',
    },
    
    # File 3: Religiosity Level ❌ NOT LOADED YET
    'Education.xlsx': {
        'segment_type': 'Religiosity Level',
        'table_number': '13',
        'header_row': 5,
        # Columns: Mixed/Other | Ultra-Orthodox | Religious | Traditional | Secular | Total
        'segment_mapping': {
            0: 'Mixed/Other',
            1: 'Ultra-Orthodox',
            2: 'Religious', 
            3: 'Traditional',
            4: 'Secular',
            5: 'Total'
        },
        'income_row_keyword': 'Net money income per household',
        'consumption_row_keyword': 'Money expenditure per household',
    },
    
    # File 4: Country of Birth ❌ NOT LOADED YET
    'Household_Size.xlsx': {
        'segment_type': 'Country of Birth',
        'table_number': '11',
        'header_row': 11,  # Complex header structure
        'segment_mapping': {
            0: 'Other (non-USSR)',
            1: 'USSR (all)',
            2: 'USSR (2000+)',
            3: 'USSR (up to 1999)',
            4: 'Israel-born',
            5: 'Total'
        },
        'income_row_keyword': 'Net money income per household',
        'consumption_row_keyword': 'Money expenditure per household',
    },
    
    # File 5: Gross Income Decile ❌ NOT LOADED YET
    'Household_Size2.xlsx': {
        'segment_type': 'Income Decile (Gross)',
        'table_number': '3',
        'header_row': 5,
        'segment_pattern': r'^[1-9]$|^10$|^Total$',
        'income_row_keyword': 'Gross money income per household',  # DIFFERENT!
        'consumption_row_keyword': 'Money expenditure per household',
    },
    
    # File 6: Geographic Region ❌ NOT LOADED YET
    'WorkStatus-IncomeSource.xlsx': {
        'segment_type': 'Geographic Region',
        'table_number': '10',
        'header_row': 10,
        'segment_mapping': {
            # Will need to be extracted from complex multi-row header
            0: 'Judea & Samaria',
            1: 'Be\'er Sheva',
            2: 'Ashqelon',
            3: 'Holon',
            4: 'Ramat Gan',
            5: 'Tel Aviv',
            6: 'Rehovot',
            7: 'Ramla',
            8: 'Petah Tikva',
            9: 'Sharon',
            10: 'Hadera',
            11: 'Haifa',
            12: 'Zefat/Kinneret/Golan',
            13: 'Jerusalem',
            14: 'Total'
        },
        'income_row_keyword': 'Net money income per household',
        'consumption_row_keyword': 'Money expenditure per household',
    },
    
    # File 7: Work Status ❌ NOT LOADED YET
    'WorkStatus-IncomeSource2.xlsx': {
        'segment_type': 'Work Status',
        'table_number': '12',
        'header_row': 8,
        'segment_mapping': {
            0: 'Not Working',
            1: 'Self-Employed',
            2: 'Employee',
            3: 'Total'
        },
        'income_row_keyword': 'Net money income per household',
        'consumption_row_keyword': 'Money expenditure per household',
    },
}

# ============================================================================
# CBS VALUE CLEANING FUNCTIONS
# ============================================================================

def clean_cbs_value(value):
    """
    Clean CBS statistical notation:
    - "5.8±0.3" → 5.8
    - ".." → None (suppressed data)
    - "(42.3)" → 42.3 (low reliability, but keep value)
    - Negative values → abs()
    """
    if pd.isna(value):
        return None
    
    value_str = str(value).strip()
    
    # Suppressed data
    if value_str == "..":
        return None
    
    # Remove error margins: "5.8±0.3" → "5.8"
    if "±" in value_str:
        value_str = value_str.split("±")[0].strip()
    
    # Remove parentheses (low reliability flag)
    value_str = value_str.replace("(", "").replace(")", "")
    
    # Remove commas
    value_str = value_str.replace(",", "")
    
    # Convert to float
    try:
        num = float(value_str)
        # CBS sometimes has negative values due to rounding - take absolute
        return abs(num) if num < 0 else num
    except ValueError:
        return None


def is_skip_row(item_name):
    """
    Determine if row should be skipped:
    - Error margins (contains ±)
    - Footnotes (starts with number in parentheses)
    - Metadata (contains TABLE, PUBLICATION, etc.)
    """
    if pd.isna(item_name):
        return True
    
    item_str = str(item_name).strip()
    
    # Skip if empty
    if not item_str:
        return True
    
    # Skip error margin rows
    if "±" in item_str:
        return True
    
    # Skip footnotes like "(1)" at start
    if item_str.startswith("(") and item_str[1].isdigit():
        return True
    
    # Skip metadata rows
    skip_keywords = ['TABLE', 'PUBLICATION', 'NIS', 'unless otherwise', 
                     'Quintiles', 'Deciles', 'עשירונים', 'חמישונים']
    if any(kw in item_str for kw in skip_keywords):
        return True
    
    return False


# ============================================================================
# MAIN ETL FUNCTION
# ============================================================================

def process_segmentation_file(file_path, config):
    """
    Universal CBS file processor.
    Handles different header structures and segment types.
    """
    segment_type = config['segment_type']
    header_row = config['header_row']
    
    print(f"\n{'='*80}")
    print(f"Processing: {file_path.name}")
    print(f"Segment Type: {segment_type}")
    print(f"Table: {config['table_number']}")
    print(f"{'='*80}")
    
    # Step 1: Read Excel with correct header row
    df = pd.read_excel(file_path, header=header_row)
    
    print(f"✅ Loaded {len(df)} rows")
    print(f"Columns: {df.columns.tolist()[:10]}")  # Show first 10 columns
    
    # Step 2: Identify segment columns
    segment_cols = []
    
    if 'segment_pattern' in config:
        # Pattern-based (Income Quintile/Decile)
        import re
        pattern = re.compile(config['segment_pattern'])
        segment_cols = [col for col in df.columns if pattern.match(str(col))]
    
    elif 'segment_mapping' in config:
        # Index-based (Religiosity, Work Status, etc.)
        segment_mapping = config['segment_mapping']
        segment_cols = [df.columns[idx] for idx in segment_mapping.keys() if idx < len(df.columns)]
    
    print(f"✅ Found {len(segment_cols)} segment columns: {segment_cols}")
    
    # Step 3: Extract item names (first column that's not a number)
    item_col = None
    for col in df.columns:
        if not str(col).isdigit() and 'Total' not in str(col):
            # Check if this column contains text (not numbers)
            sample_vals = df[col].dropna().head(10)
            if any(isinstance(v, str) for v in sample_vals):
                item_col = col
                break
    
    if item_col is None:
        # Fallback: use first column
        item_col = df.columns[0]
    
    print(f"✅ Item column: {item_col}")
    
    # Step 4: Clean and filter data
    df_clean = df.copy()
    
    # Remove skip rows
    df_clean = df_clean[~df_clean[item_col].apply(is_skip_row)]
    
    print(f"✅ After filtering: {len(df_clean)} rows")
    
    # Step 5: Melt to long format
    id_vars = [item_col]
    value_vars = segment_cols
    
    df_long = df_clean.melt(
        id_vars=id_vars,
        value_vars=value_vars,
        var_name='segment_value',
        value_name='expenditure_value'
    )
    
    # Rename item column
    df_long = df_long.rename(columns={item_col: 'item_name'})
    
    # Clean expenditure values
    df_long['expenditure_value'] = df_long['expenditure_value'].apply(clean_cbs_value)
    
    # Drop rows with no value
    df_long = df_long.dropna(subset=['expenditure_value'])
    
    print(f"✅ Long format: {len(df_long)} records")
    
    # Step 6: Flag income/consumption rows for burn rate
    income_keyword = config.get('income_row_keyword', 'Net money income per household')
    consumption_keyword = config.get('consumption_row_keyword', 'Money expenditure per household')
    
    df_long['is_income_metric'] = df_long['item_name'].str.contains(
        income_keyword, case=False, na=False
    )
    
    df_long['is_consumption_metric'] = df_long['item_name'].str.contains(
        consumption_keyword, case=False, na=False
    )
    
    income_count = df_long['is_income_metric'].sum()
    consumption_count = df_long['is_consumption_metric'].sum()
    
    print(f"✅ Flagged {income_count} income rows")
    print(f"✅ Flagged {consumption_count} consumption rows")
    
    # Step 7: Add segment type column
    df_long['segment_type'] = segment_type
    df_long['file_source'] = file_path.name
    
    return df_long


# ============================================================================
# DATABASE LOADING
# ============================================================================

def load_to_database(df_long, segment_type, file_source):
    """
    Load processed data into PostgreSQL star schema.
    """
    print(f"\n{'='*80}")
    print(f"Loading to Database: {segment_type}")
    print(f"{'='*80}")
    
    # Step 1: Get unique segments
    unique_segments = df_long['segment_value'].unique()
    
    print(f"Segments to insert: {unique_segments}")
    
    # Step 2: Insert segments into dim_segment
    with engine.begin() as conn:
        for idx, seg_value in enumerate(unique_segments):
            # Check if segment already exists
            result = conn.execute(text("""
                SELECT segment_key FROM dim_segment
                WHERE segment_type = :seg_type AND segment_value = :seg_val
            """), {"seg_type": segment_type, "seg_val": str(seg_value)})
            
            existing = result.fetchone()
            
            if not existing:
                # Determine segment order (for sorting)
                if str(seg_value).isdigit():
                    segment_order = int(seg_value)
                elif seg_value == 'Total':
                    segment_order = 999  # Always last
                else:
                    segment_order = idx + 1
                
                # Insert new segment
                conn.execute(text("""
                    INSERT INTO dim_segment (segment_type, segment_value, segment_order, file_source)
                    VALUES (:seg_type, :seg_val, :seg_order, :file_src)
                """), {
                    "seg_type": segment_type,
                    "seg_val": str(seg_value),
                    "seg_order": segment_order,
                    "file_src": file_source
                })
                
                print(f"  ✅ Inserted segment: {seg_value}")
            else:
                print(f"  ⏭️  Segment exists: {seg_value}")
    
    # Step 3: Insert expenditures
    with engine.begin() as conn:
        for _, row in df_long.iterrows():
            # Get segment_key
            result = conn.execute(text("""
                SELECT segment_key FROM dim_segment
                WHERE segment_type = :seg_type AND segment_value = :seg_val
            """), {"seg_type": segment_type, "seg_val": str(row['segment_value'])})
            
            segment_key = result.fetchone()[0]
            
            # Insert expenditure
            conn.execute(text("""
                INSERT INTO fact_segment_expenditure 
                (item_name, segment_key, expenditure_value, is_income_metric, is_consumption_metric, metric_type)
                VALUES (:item, :seg_key, :value, :is_income, :is_consumption, 'Monthly Spend')
            """), {
                "item": row['item_name'],
                "seg_key": segment_key,
                "value": float(row['expenditure_value']),
                "is_income": bool(row['is_income_metric']),
                "is_consumption": bool(row['is_consumption_metric'])
            })
        
        print(f"✅ Inserted {len(df_long)} expenditure records")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Process ALL CBS files and load to database.
    """
    print("\n" + "="*80)
    print("CBS DATA ETL - COMPLETE PIPELINE")
    print("="*80)
    
    # Base directory (adjust based on where files are)
    data_dir = Path(__file__).parent.parent.parent / 'CBS Household Expenditure Data Strategy'
    
    # Track results
    total_records = 0
    loaded_files = []
    failed_files = []
    
    # Process each file
    for filename, config in SEGMENTATION_FILES.items():
        file_path = data_dir / filename
        
        if not file_path.exists():
            print(f"\n❌ FILE NOT FOUND: {filename}")
            failed_files.append(filename)
            continue
        
        try:
            # Process file
            df_long = process_segmentation_file(file_path, config)
            
            # Load to database
            load_to_database(df_long, config['segment_type'], filename)
            
            total_records += len(df_long)
            loaded_files.append(filename)
            
            print(f"✅ SUCCESS: {filename} ({len(df_long)} records)")
        
        except Exception as e:
            print(f"\n❌ ERROR processing {filename}: {e}")
            failed_files.append(filename)
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Loaded: {len(loaded_files)} files")
    print(f"❌ Failed: {len(failed_files)} files")
    print(f"📊 Total records: {total_records:,}")
    
    if loaded_files:
        print(f"\nLoaded files:")
        for f in loaded_files:
            print(f"  - {f}")
    
    if failed_files:
        print(f"\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")
    
    # Verify database
    print(f"\n{'='*80}")
    print("DATABASE VERIFICATION")
    print(f"{'='*80}")
    
    with engine.connect() as conn:
        # Count segments
        result = conn.execute(text("SELECT COUNT(*) FROM dim_segment"))
        segment_count = result.scalar()
        
        # Count expenditures
        result = conn.execute(text("SELECT COUNT(*) FROM fact_segment_expenditure"))
        expenditure_count = result.scalar()
        
        # Count by segment type
        result = conn.execute(text("""
            SELECT s.segment_type, COUNT(*) as records
            FROM fact_segment_expenditure f
            JOIN dim_segment s ON f.segment_key = s.segment_key
            GROUP BY s.segment_type
            ORDER BY records DESC
        """))
        
        print(f"\n📊 Database Statistics:")
        print(f"  Segments: {segment_count}")
        print(f"  Expenditures: {expenditure_count:,}")
        
        print(f"\n📊 Records by Segment Type:")
        for row in result:
            print(f"  {row[0]}: {row[1]:,}")


if __name__ == '__main__':
    main()
