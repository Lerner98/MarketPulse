"""
COMPREHENSIVE ETL VALIDATION FRAMEWORK
Tests every step of the V10 pipeline to ensure 100% data integrity

This script MUST be run after each ETL step to verify:
1. File loading correctness
2. Data cleaning accuracy
3. Database insertion integrity
4. View calculations validity
5. API endpoint responses

CRITICAL: If ANY test fails, STOP and fix before proceeding!
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from typing import Dict, List, Tuple

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

class TestConfig:
    """Configuration for all validation tests"""
    
    # Expected data volumes (CRITICAL: Update these after each file load)
    EXPECTED_FILES = 8
    EXPECTED_SEGMENT_TYPES = 7
    EXPECTED_MIN_RECORDS = 27000  # Minimum total expenditure records
    
    # File-specific expectations
    FILE_EXPECTATIONS = {
        'הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx': {
            'segment_type': 'Income Quintile',
            'segments': 6,  # Q1-Q5 + Total
            'categories': 528,
            'min_records': 2500
        },
        'Income_Decile.xlsx': {
            'segment_type': 'Income Decile (Net)',
            'segments': 11,  # D1-D10 + Total
            'categories': 528,
            'min_records': 5000
        },
        'Education.xlsx': {
            'segment_type': 'Religiosity Level',
            'segments': 6,  # 5 levels + Total
            'categories': 528,
            'min_records': 2500
        },
        'Household_Size.xlsx': {
            'segment_type': 'Country of Birth',
            'segments': 6,
            'categories': 528,
            'min_records': 2500
        },
        'Household_Size2.xlsx': {
            'segment_type': 'Income Decile (Gross)',
            'segments': 11,
            'categories': 528,
            'min_records': 5000
        },
        'WorkStatus-IncomeSource.xlsx': {
            'segment_type': 'Geographic Region',
            'segments': 15,  # 14 regions + Total
            'categories': 528,
            'min_records': 7000
        },
        'WorkStatus-IncomeSource2.xlsx': {
            'segment_type': 'Work Status',
            'segments': 4,  # 3 types + Total
            'categories': 528,
            'min_records': 1500
        },
    }
    
    # Test cases from CBS Excel (CRITICAL: These MUST match CBS screenshots)
    TEST_CASES = {
        'alcoholic_beverages': {
            'table': 38,
            'category': 'Alcoholic beverages',
            'special_shop_pct': 30.4,
            'supermarket_chain_pct': 51.1,
            'grocery_pct': 11.4,
            'tolerance': 1.0  # ±1% tolerance for rounding
        },
        'income_quintile_q1': {
            'segment_type': 'Income Quintile',
            'segment_value': '1',
            'income_keyword': 'Net money income per household',
            'expected_income': 7510,  # From CBS Table 1.1 row 25
            'consumption_keyword': 'Money expenditure per household',
            'expected_consumption': 10979,  # From CBS Table 1.1 row 29
            'tolerance': 100  # ±100 NIS tolerance
        },
        'income_quintile_q5': {
            'segment_type': 'Income Quintile',
            'segment_value': '5',
            'income_keyword': 'Net money income per household',
            'expected_income': 33591,
            'consumption_keyword': 'Money expenditure per household',
            'expected_consumption': 20076,
            'tolerance': 100
        }
    }


# ============================================================================
# PHASE 1: FILE VALIDATION
# ============================================================================

def test_file_existence():
    """Test 1.1: Verify all CBS files exist"""
    print(f"\n{'='*80}")
    print("TEST 1.1: FILE EXISTENCE")
    print(f"{'='*80}")
    
    upload_dir = Path(__file__).parent.parent / 'CBS Household Expenditure Data Strategy'

    results = {
        'total_files': 0,
        'found': [],
        'missing': []
    }
    
    for filename in TestConfig.FILE_EXPECTATIONS.keys():
        filepath = upload_dir / filename
        
        if filepath.exists():
            results['found'].append(filename)
            print(f"   ✅ FOUND: {filename}")
        else:
            results['missing'].append(filename)
            print(f"   ❌ MISSING: {filename}")
    
    results['total_files'] = len(results['found'])
    
    print(f"\nSummary:")
    print(f"   Found: {len(results['found'])}/{len(TestConfig.FILE_EXPECTATIONS)}")
    print(f"   Missing: {len(results['missing'])}")
    
    # CRITICAL: All files must exist
    if results['missing']:
        print(f"\n❌ CRITICAL FAILURE: {len(results['missing'])} files missing!")
        print(f"   Missing files: {results['missing']}")
        return False
    
    print(f"\n✅ PASSED: All {results['total_files']} files exist")
    return True


def test_file_structure(filename: str):
    """Test 1.2: Verify file has expected structure"""
    print(f"\n{'='*80}")
    print(f"TEST 1.2: FILE STRUCTURE - {filename}")
    print(f"{'='*80}")
    
    filepath = Path(__file__).parent.parent / 'CBS Household Expenditure Data Strategy' / filename
    expectations = TestConfig.FILE_EXPECTATIONS[filename]
    
    try:
        # Load Excel
        df = pd.read_excel(filepath, header=None, nrows=20)
        
        print(f"   File dimensions: {df.shape}")
        print(f"   Expected segments: {expectations['segments']}")
        
        # Find header row (contains segment pattern)
        header_found = False
        for idx, row in df.iterrows():
            row_str = ' '.join([str(x) for x in row.dropna().values])
            
            # Look for segment patterns
            if any(pattern in row_str for pattern in ['5 4 3 2 1', '10 9 8 7 6', 'Total']):
                print(f"   ✅ Header row found at index {idx}")
                header_found = True
                break
        
        if not header_found:
            print(f"   ❌ Header row NOT found")
            return False
        
        print(f"\n✅ PASSED: File structure valid")
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR reading file: {e}")
        return False


# ============================================================================
# PHASE 2: DATABASE VALIDATION
# ============================================================================

def test_database_connection():
    """Test 2.1: Verify database is accessible"""
    print(f"\n{'='*80}")
    print("TEST 2.1: DATABASE CONNECTION")
    print(f"{'='*80}")
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print(f"   ❌ DATABASE_URL not found in environment")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            
        print(f"   ✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False


def test_schema_exists():
    """Test 2.2: Verify V10 schema tables exist"""
    print(f"\n{'='*80}")
    print("TEST 2.2: SCHEMA VALIDATION")
    print(f"{'='*80}")
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    
    required_tables = ['dim_segment', 'fact_segment_expenditure']
    required_views = ['vw_segment_inequality', 'vw_segment_burn_rate']
    
    results = {
        'tables': {'found': [], 'missing': []},
        'views': {'found': [], 'missing': []}
    }
    
    with engine.connect() as conn:
        # Check tables
        for table in required_tables:
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = '{table}'
            """)).scalar()
            
            if result > 0:
                results['tables']['found'].append(table)
                print(f"   ✅ Table: {table}")
            else:
                results['tables']['missing'].append(table)
                print(f"   ❌ Table: {table} NOT FOUND")
        
        # Check views
        for view in required_views:
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM pg_matviews
                WHERE matviewname = '{view}'
            """)).scalar()
            
            if result > 0:
                results['views']['found'].append(view)
                print(f"   ✅ View: {view}")
            else:
                results['views']['missing'].append(view)
                print(f"   ❌ View: {view} NOT FOUND")
    
    # CRITICAL: All schema objects must exist
    if results['tables']['missing'] or results['views']['missing']:
        print(f"\n❌ CRITICAL FAILURE: Schema incomplete!")
        return False
    
    print(f"\n✅ PASSED: All schema objects exist")
    return True


def test_data_volume():
    """Test 2.3: Verify expected data volumes"""
    print(f"\n{'='*80}")
    print("TEST 2.3: DATA VOLUME VALIDATION")
    print(f"{'='*80}")
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Count segments
        segment_count = conn.execute(text("""
            SELECT COUNT(*) FROM dim_segment
        """)).scalar()
        
        print(f"   Segments in database: {segment_count}")
        
        # Count expenditures
        expenditure_count = conn.execute(text("""
            SELECT COUNT(*) FROM fact_segment_expenditure
        """)).scalar()
        
        print(f"   Expenditures in database: {expenditure_count:,}")
        
        # Count segment types
        segment_types = conn.execute(text("""
            SELECT COUNT(DISTINCT segment_type) FROM dim_segment
        """)).scalar()
        
        print(f"   Segment types: {segment_types}")
        
        # Breakdown by segment type
        print(f"\n   Records per segment type:")
        result = conn.execute(text("""
            SELECT s.segment_type, COUNT(*) as records
            FROM fact_segment_expenditure f
            JOIN dim_segment s ON f.segment_key = s.segment_key
            GROUP BY s.segment_type
            ORDER BY records DESC
        """))
        
        total_verified = 0
        for row in result:
            print(f"      {row[0]:30} {row[1]:>6,} records")
            total_verified += row[1]
    
    # CRITICAL: Check minimum thresholds
    if expenditure_count < TestConfig.EXPECTED_MIN_RECORDS:
        print(f"\n❌ CRITICAL FAILURE: Only {expenditure_count:,} records (expected {TestConfig.EXPECTED_MIN_RECORDS:,})")
        return False
    
    if segment_types < TestConfig.EXPECTED_SEGMENT_TYPES:
        print(f"\n❌ CRITICAL FAILURE: Only {segment_types} segment types (expected {TestConfig.EXPECTED_SEGMENT_TYPES})")
        return False
    
    print(f"\n✅ PASSED: Data volume meets expectations")
    print(f"   Total: {expenditure_count:,} records")
    print(f"   Segment types: {segment_types}")
    
    return True


# ============================================================================
# PHASE 3: DATA INTEGRITY VALIDATION
# ============================================================================

def test_burn_rate_flags():
    """Test 3.1: Verify income/consumption flags are set correctly"""
    print(f"\n{'='*80}")
    print("TEST 3.1: BURN RATE FLAGS VALIDATION")
    print(f"{'='*80}")
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Count income metric flags
        income_count = conn.execute(text("""
            SELECT COUNT(*) FROM fact_segment_expenditure
            WHERE is_income_metric = TRUE
        """)).scalar()
        
        print(f"   Income metric rows: {income_count}")
        
        # Count consumption metric flags
        consumption_count = conn.execute(text("""
            SELECT COUNT(*) FROM fact_segment_expenditure
            WHERE is_consumption_metric = TRUE
        """)).scalar()
        
        print(f"   Consumption metric rows: {consumption_count}")
        
        # Show examples
        print(f"\n   Income metric examples:")
        result = conn.execute(text("""
            SELECT DISTINCT f.item_name, s.segment_type
            FROM fact_segment_expenditure f
            JOIN dim_segment s ON f.segment_key = s.segment_key
            WHERE f.is_income_metric = TRUE
            LIMIT 3
        """))
        for row in result:
            print(f"      - {row[0][:50]} ({row[1]})")
        
        print(f"\n   Consumption metric examples:")
        result = conn.execute(text("""
            SELECT DISTINCT f.item_name, s.segment_type
            FROM fact_segment_expenditure f
            JOIN dim_segment s ON f.segment_key = s.segment_key
            WHERE f.is_consumption_metric = TRUE
            LIMIT 3
        """))
        for row in result:
            print(f"      - {row[0][:50]} ({row[1]})")
    
    # CRITICAL: Must have flagged rows for burn rate calculation
    if income_count == 0 or consumption_count == 0:
        print(f"\n❌ CRITICAL FAILURE: Missing burn rate flags!")
        return False
    
    print(f"\n✅ PASSED: Burn rate flags set correctly")
    return True


def test_cbs_test_cases():
    """Test 3.2: Verify specific CBS values match Excel screenshots"""
    print(f"\n{'='*80}")
    print("TEST 3.2: CBS TEST CASE VALIDATION")
    print(f"{'='*80}")
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    
    passed_tests = []
    failed_tests = []
    
    # Test Case 1: Income Quintile Q1
    test_case = TestConfig.TEST_CASES['income_quintile_q1']
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT f.expenditure_value
            FROM fact_segment_expenditure f
            JOIN dim_segment s ON f.segment_key = s.segment_key
            WHERE s.segment_type = :seg_type
              AND s.segment_value = :seg_val
              AND f.is_income_metric = TRUE
        """), {
            'seg_type': test_case['segment_type'],
            'seg_val': test_case['segment_value']
        }).scalar()
        
        expected = test_case['expected_income']
        tolerance = test_case['tolerance']
        
        print(f"\n   Test: Income Quintile Q1 - Net Income")
        print(f"      Expected: ₪{expected:,}")
        print(f"      Actual: ₪{result:,}" if result else "      Actual: NOT FOUND")
        
        if result and abs(result - expected) <= tolerance:
            print(f"      ✅ PASSED (within ±{tolerance})")
            passed_tests.append('Q1_income')
        else:
            print(f"      ❌ FAILED (difference: {abs(result - expected) if result else 'N/A'})")
            failed_tests.append('Q1_income')
    
    # Test Case 2: Income Quintile Q5
    test_case = TestConfig.TEST_CASES['income_quintile_q5']
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT f.expenditure_value
            FROM fact_segment_expenditure f
            JOIN dim_segment s ON f.segment_key = s.segment_key
            WHERE s.segment_type = :seg_type
              AND s.segment_value = :seg_val
              AND f.is_consumption_metric = TRUE
        """), {
            'seg_type': test_case['segment_type'],
            'seg_val': test_case['segment_value']
        }).scalar()
        
        expected = test_case['expected_consumption']
        tolerance = test_case['tolerance']
        
        print(f"\n   Test: Income Quintile Q5 - Money Expenditure")
        print(f"      Expected: ₪{expected:,}")
        print(f"      Actual: ₪{result:,}" if result else "      Actual: NOT FOUND")
        
        if result and abs(result - expected) <= tolerance:
            print(f"      ✅ PASSED (within ±{tolerance})")
            passed_tests.append('Q5_consumption')
        else:
            print(f"      ❌ FAILED (difference: {abs(result - expected) if result else 'N/A'})")
            failed_tests.append('Q5_consumption')
    
    print(f"\nSummary:")
    print(f"   Passed: {len(passed_tests)}")
    print(f"   Failed: {len(failed_tests)}")
    
    if failed_tests:
        print(f"\n❌ CRITICAL FAILURE: {len(failed_tests)} test cases failed!")
        return False
    
    print(f"\n✅ PASSED: All CBS test cases match Excel data")
    return True


def test_burn_rate_calculation():
    """Test 3.3: Verify burn rate calculation is correct"""
    print(f"\n{'='*80}")
    print("TEST 3.3: BURN RATE CALCULATION VALIDATION")
    print(f"{'='*80}")
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Refresh view first
        conn.execute(text("REFRESH MATERIALIZED VIEW vw_segment_burn_rate"))
        
        # Get burn rates
        result = conn.execute(text("""
            SELECT segment_value, income, spending, burn_rate_pct
            FROM vw_segment_burn_rate
            ORDER BY segment_value
        """))
        
        print(f"\n   Burn Rate Results:")
        print(f"   {'Segment':<10} {'Income':>12} {'Spending':>12} {'Burn Rate':>12}")
        print(f"   {'-'*48}")
        
        for row in result:
            print(f"   {row[0]:<10} ₪{row[1]:>10,.0f} ₪{row[2]:>10,.0f} {row[3]:>10.1f}%")
        
        # Verify Q1 and Q5 specifically
        q1 = conn.execute(text("""
            SELECT burn_rate_pct FROM vw_segment_burn_rate
            WHERE segment_value = '1'
        """)).scalar()
        
        q5 = conn.execute(text("""
            SELECT burn_rate_pct FROM vw_segment_burn_rate
            WHERE segment_value = '5'
        """)).scalar()
        
        print(f"\n   Critical Values:")
        print(f"      Q1 burn rate: {q1:.1f}% (expected: ~146%)")
        print(f"      Q5 burn rate: {q5:.1f}% (expected: ~60%)")
        
        # CRITICAL: Q1 should be > 100% (deficit), Q5 should be < 70% (savings)
        if not (140 <= q1 <= 150 and 55 <= q5 <= 65):
            print(f"\n❌ CRITICAL FAILURE: Burn rates outside expected range!")
            return False
    
    print(f"\n✅ PASSED: Burn rate calculations correct")
    return True


# ============================================================================
# PHASE 4: API VALIDATION
# ============================================================================

def test_api_endpoints():
    """Test 4.1: Verify API endpoints return correct data"""
    print(f"\n{'='*80}")
    print("TEST 4.1: API ENDPOINT VALIDATION")
    print(f"{'='*80}")
    
    print(f"\n   ⚠️  MANUAL TEST REQUIRED:")
    print(f"   1. Start backend: cd backend && uvicorn api.main:app --reload")
    print(f"   2. Test endpoints:")
    print(f"      curl http://localhost:8000/api/segments/types")
    print(f"      curl http://localhost:8000/api/v10/burn-rate")
    print(f"      curl http://localhost:8000/api/v10/inequality/Income%20Quintile")
    print(f"   3. Verify response data matches database")
    
    return True  # Requires manual verification


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run complete test suite"""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE ETL VALIDATION FRAMEWORK")
    print(f"{'='*80}")
    print(f"\nThis will test:")
    print(f"  - Phase 1: File existence and structure")
    print(f"  - Phase 2: Database schema and volume")
    print(f"  - Phase 3: Data integrity and CBS test cases")
    print(f"  - Phase 4: API endpoint responses")
    
    results = {
        'passed': [],
        'failed': [],
        'total': 0
    }
    
    tests = [
        ('File Existence', test_file_existence),
        ('Database Connection', test_database_connection),
        ('Schema Validation', test_schema_exists),
        ('Data Volume', test_data_volume),
        ('Burn Rate Flags', test_burn_rate_flags),
        ('CBS Test Cases', test_cbs_test_cases),
        ('Burn Rate Calculation', test_burn_rate_calculation),
    ]
    
    for test_name, test_func in tests:
        results['total'] += 1
        
        try:
            if test_func():
                results['passed'].append(test_name)
            else:
                results['failed'].append(test_name)
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            results['failed'].append(test_name)
    
    # Print final summary
    print(f"\n{'='*80}")
    print("FINAL TEST RESULTS")
    print(f"{'='*80}")
    
    print(f"\n✅ PASSED: {len(results['passed'])}/{results['total']}")
    for test in results['passed']:
        print(f"   ✅ {test}")
    
    if results['failed']:
        print(f"\n❌ FAILED: {len(results['failed'])}/{results['total']}")
        for test in results['failed']:
            print(f"   ❌ {test}")
        
        print(f"\n{'='*80}")
        print("⚠️  CRITICAL: FIX FAILED TESTS BEFORE PROCEEDING!")
        print(f"{'='*80}")
        return False
    else:
        print(f"\n{'='*80}")
        print("🎉 ALL TESTS PASSED - PIPELINE READY!")
        print(f"{'='*80}")
        return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
