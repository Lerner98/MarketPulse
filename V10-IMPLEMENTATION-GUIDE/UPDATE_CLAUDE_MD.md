# 📝 CLAUDE.md UPDATE INSTRUCTIONS

**CRITICAL:** Claude Code must update its project knowledge file BEFORE starting implementation!

---

## 🎯 WHAT TO UPDATE

The `.claude/CLAUDE.md` file needs to reflect:

1. ✅ **ACTUAL FILES YOU HAVE** (not theoretical ta2-ta13)
2. ✅ **V10 ARCHITECTURE** (normalized star schema)
3. ✅ **CORRECTED FILE MAPPING** (Income_Decile.xlsx, not ta2.xlsx)
4. ✅ **CURRENT PROJECT STATE** (what works, what doesn't)

---

## 📋 SECTION-BY-SECTION UPDATES

### Section 1: Project Overview

**OLD (WRONG):**
```markdown
## Data Sources
- CBS Table 1.1 (Income Quintile) - ✅ Working
- CBS Table ta2-ta13 (Other segments) - ⏳ Pending
```

**NEW (CORRECT):**
```markdown
## Data Sources
Currently have 8 CBS Excel files in /mnt/user-data/uploads:

1. ✅ הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx (Income Quintile)
2. ❌ Income_Decile.xlsx (Income Decile Net) - NOT LOADED YET
3. ❌ Education.xlsx (Religiosity Level - Table 13) - NOT LOADED YET
4. ❌ Household_Size.xlsx (Country of Birth - Table 11) - NOT LOADED YET
5. ❌ Household_Size2.xlsx (Income Decile Gross - Table 3) - NOT LOADED YET
6. ❌ WorkStatus-IncomeSource.xlsx (Geographic Region - Table 10) - NOT LOADED YET
7. ❌ WorkStatus-IncomeSource2.xlsx (Work Status - Table 12) - NOT LOADED YET
8. ⏸️ הוצאה_למזון_ללא_ארוחות_מחוץ_לבית_לפי_סוג_חנות.xlsx (Table 38 - Separate pipeline)

**CRITICAL ISSUE:** ETL pipeline looking for wrong file names (ta2.xlsx instead of Income_Decile.xlsx)
**SOLUTION:** Use /mnt/user-data/outputs/load_segmentation_corrected.py
```

### Section 2: Database Schema

**ADD THIS SECTION:**
```markdown
## Database Architecture: V10 Normalized Star Schema

### Current State
- ✅ V9 schema exists (household_profiles, household_expenditures, retail_competition)
- ⏳ V10 schema ready to apply (dim_segment, fact_segment_expenditure)

### V10 Tables
1. **dim_segment** - Dimension table (The "WHO")
   - Stores ALL segment types (Income, Age, Education, etc.)
   - 52 rows expected after full load
   - Columns: segment_key, segment_type, segment_value, segment_order

2. **fact_segment_expenditure** - Fact table (The "WHAT" + "HOW MUCH")
   - Stores spending data for all segments
   - 27,456 rows expected after full load (7 files × 528 categories × segments)
   - Columns: item_name, segment_key, expenditure_value, is_income_metric, is_consumption_metric

3. **Materialized Views**
   - vw_segment_burn_rate - Calculates spending/income ratio
   - vw_segment_inequality - Calculates rich/poor spending gaps

### Migration Strategy
- Phase 1: Apply V10 schema (parallel to V9)
- Phase 2: Load V9 data into V10 structure
- Phase 3: Load additional segments (ta2-ta13 equivalents)
- Phase 4: Create backward-compatible views
- Phase 5: Deprecate V9 endpoints
```

### Section 3: ETL Pipeline

**OLD (WRONG):**
```markdown
## ETL Pipeline
- File: backend/etl/load_segmentation.py
- Processes: ta2.xlsx, ta5.xlsx, ta12.xlsx, ta13.xlsx
```

**NEW (CORRECT):**
```markdown
## ETL Pipeline Status

### Current Pipeline (BROKEN)
- File: backend/etl/load_segmentation.py
- Problem: Looks for ta2.xlsx, ta5.xlsx, etc. (FILES DON'T EXIST!)
- Result: Only loads 1/8 files (Income Quintile)
- Current records: 2,651

### Fixed Pipeline (TO BE APPLIED)
- File: /mnt/user-data/outputs/load_segmentation_corrected.py
- Solution: Maps to actual file names (Income_Decile.xlsx, Education.xlsx, etc.)
- Expected records: 27,456 (10.4x increase!)

### File Mapping (CRITICAL - USE THIS!)
```python
SEGMENTATION_FILES = {
    # Actual file names in /mnt/user-data/uploads/
    'הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx': ('Income Quintile', 1),
    'Income_Decile.xlsx': ('Income Decile (Net)', 2),
    'Education.xlsx': ('Religiosity Level', 13),  # CBS Table 13
    'Household_Size.xlsx': ('Country of Birth', 11),  # CBS Table 11
    'Household_Size2.xlsx': ('Income Decile (Gross)', 3),  # CBS Table 3
    'WorkStatus-IncomeSource.xlsx': ('Geographic Region', 10),  # CBS Table 10
    'WorkStatus-IncomeSource2.xlsx': ('Work Status', 12),  # CBS Table 12
}
```

### Next Steps
1. ⏳ Replace backend/etl/load_segmentation.py with corrected version
2. ⏳ Run ETL pipeline
3. ⏳ Verify 27,456 records loaded
4. ⏳ Create V10 API endpoints
5. ⏳ Update frontend selector
```

### Section 4: Known Issues

**ADD THIS SECTION:**
```markdown
## Known Issues & Solutions

### Issue 1: File Name Mismatch
**Problem:** ETL expects ta2.xlsx, ta5.xlsx, etc.  
**Reality:** Files are named Income_Decile.xlsx, Education.xlsx, etc.  
**Impact:** Only 1/8 files loads (9.6% of data)  
**Solution:** Use /mnt/user-data/outputs/load_segmentation_corrected.py

### Issue 2: Hebrew Encoding
**Problem:** CBS files use Windows-1255 encoding  
**Solution:** Already handled in corrected ETL (auto-detection + conversion)

### Issue 3: Complex Headers
**Problem:** Each file has different header row positions (5, 6, 8, 10, 11)  
**Solution:** Corrected ETL has dynamic header detection per file

### Issue 4: CBS Statistical Notation
**Problem:** Values contain ±, .., (), negatives  
**Solution:** clean_cbs_value() function handles all cases

### Issue 5: Burn Rate Calculation
**Problem:** If you SUM all 528 categories, you get WRONG burn rate  
**Solution:** Use is_income_metric and is_consumption_metric flags (only 2 aggregate rows)
```

### Section 5: Testing Requirements

**ADD THIS SECTION:**
```markdown
## Testing Framework

### Validation Script
File: /mnt/user-data/outputs/test_etl_validation.py

Run after EVERY step:
```bash
python /mnt/user-data/outputs/test_etl_validation.py
```

### Critical Test Cases
1. **File Existence:** All 8 files in /mnt/user-data/uploads/
2. **Schema Validation:** dim_segment + fact_segment_expenditure exist
3. **Data Volume:** 27,456 records loaded
4. **CBS Test Cases:** 
   - Q1 income = ₪7,510 (±100)
   - Q5 consumption = ₪20,076 (±100)
   - Alcoholic beverages: Special shop 30.4%, Supermarket 51.1%
5. **Burn Rate Calculation:**
   - Q1 = 146.2% (±2)
   - Q5 = 59.8% (±2)

### Test Failure Protocol
❌ **IF ANY TEST FAILS:**
1. STOP immediately
2. Check error messages
3. Fix root cause
4. Re-run validation
5. Only proceed when ✅ ALL PASSED
```

### Section 6: Implementation Checklist

**ADD THIS SECTION:**
```markdown
## Implementation Order (FOLLOW EXACTLY)

### Phase 0: Preparation (30 min)
- [ ] Read all documentation in /mnt/user-data/outputs/
- [ ] Verify all 8 CBS files exist
- [ ] Backup current database

### Phase 1: Database Schema (15 min)
- [ ] Apply V10 schema: `python backend/apply_schema_v10.py`
- [ ] Verify tables created
- [ ] Run validation: TEST 2.2 must pass

### Phase 2: ETL Pipeline (45 min)
- [ ] Replace load_segmentation.py with corrected version
- [ ] Test with 1 file first (Income Quintile)
- [ ] Verify CBS test case: Q1 income = ₪7,510
- [ ] Load all 8 files
- [ ] Verify 27,456 records

### Phase 3: Data Validation (30 min)
- [ ] Run full test suite
- [ ] ALL tests must show ✅
- [ ] Manual spot checks

### Phase 4: API Endpoints (30 min)
- [ ] Create segmentation_endpoints_v10.py
- [ ] Test with curl
- [ ] Verify in browser /docs

### Phase 5: Frontend Updates (60 min)
- [ ] Create SegmentSelector component
- [ ] Create apiV10.ts client
- [ ] Update dashboard
- [ ] Test switching segments

**TOTAL TIME:** 3-4 hours  
**CRITICAL:** Don't skip validation steps!
```

---

## 🚨 CRITICAL REMINDERS TO ADD

Add these to the top of CLAUDE.md:

```markdown
# ⚠️ CRITICAL PROJECT STATE (November 22, 2024)

## CURRENT PROBLEM
The ETL pipeline only loads 1 out of 8 CBS files due to **file name mismatch**.

**Expected:** ta2.xlsx, ta5.xlsx, ta12.xlsx, etc.  
**Reality:** Income_Decile.xlsx, Education.xlsx, WorkStatus-IncomeSource.xlsx, etc.

## IMMEDIATE ACTION REQUIRED
1. DO NOT modify existing files without reading /mnt/user-data/outputs/ documentation first
2. USE /mnt/user-data/outputs/load_segmentation_corrected.py (NOT backend/etl/load_segmentation.py)
3. RUN /mnt/user-data/outputs/test_etl_validation.py after EVERY step
4. FOLLOW /mnt/user-data/outputs/IMPLEMENTATION_CHECKLIST.md exactly

## EXPECTED FINAL STATE
- Database: 27,456 records (currently 2,651)
- Segment types: 7 (currently 1)
- API endpoints: Dynamic segmentation (currently static)
- Frontend: 7-option selector (currently none)

## REFERENCE DOCUMENTS
All in /mnt/user-data/outputs/:
1. EXECUTIVE_SUMMARY.md - Overview
2. QUICK_START_GUIDE.md - Implementation steps
3. CBS_DATA_MAPPING_COMPLETE.md - Architecture
4. FILE_SPECIFICATIONS.md - Technical details
5. IMPLEMENTATION_CHECKLIST.md - Step-by-step
6. test_etl_validation.py - Validation framework
```

---

## ✅ VERIFICATION CHECKLIST

After updating CLAUDE.md, verify it includes:

- [ ] Correct file names (Income_Decile.xlsx, NOT ta2.xlsx)
- [ ] V10 architecture explanation
- [ ] Current problem statement (file name mismatch)
- [ ] Solution path (/mnt/user-data/outputs/ files)
- [ ] Testing requirements (validation script)
- [ ] Implementation checklist reference
- [ ] Critical reminders at top
- [ ] Expected final state (27,456 records)

---

**NEXT STEP AFTER UPDATING CLAUDE.md:**
Run `/mnt/user-data/outputs/test_etl_validation.py` to establish baseline
