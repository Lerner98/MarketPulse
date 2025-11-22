# 🎯 INSTRUCTIONS FOR CLAUDE CODE

**READ THIS ENTIRE FILE BEFORE STARTING ANY WORK!**

---

## 📋 YOUR MISSION

Transform the MarketPulse data pipeline from loading **1/8 CBS files (2,651 records)** to loading **ALL 8 files (27,456 records)** with **100% data integrity verified**.

---

## 🚨 CRITICAL CONTEXT

### The Problem
Your current ETL pipeline (`backend/etl/load_segmentation.py`) is looking for files that DON'T EXIST:
- ❌ Looking for: `ta2.xlsx`, `ta5.xlsx`, `ta12.xlsx`, etc.
- ✅ Actually have: `Income_Decile.xlsx`, `Education.xlsx`, `WorkStatus-IncomeSource.xlsx`, etc.

**Result:** Only 1 out of 8 files loads successfully.

### The Solution
I've created complete documentation and corrected code in `/mnt/user-data/outputs/`:

1. **EXECUTIVE_SUMMARY.md** - Project overview and problem statement
2. **QUICK_START_GUIDE.md** - 20-minute implementation guide
3. **CBS_DATA_MAPPING_COMPLETE.md** - Complete architecture documentation
4. **FILE_SPECIFICATIONS.md** - Technical details for each CBS file
5. **VISUAL_ARCHITECTURE.md** - Data flow diagrams
6. **IMPLEMENTATION_CHECKLIST.md** - Step-by-step checklist ⭐ START HERE
7. **load_segmentation_corrected.py** - Fixed ETL script
8. **test_etl_validation.py** - Comprehensive validation framework ⭐ RUN AFTER EACH STEP

---

## 📖 MANDATORY READING ORDER

**BEFORE WRITING ANY CODE, READ THESE IN ORDER:**

1. **FIRST:** `/mnt/user-data/outputs/EXECUTIVE_SUMMARY.md` (10 minutes)
   - Understand the complete picture
   - See before/after comparison
   - Understand the file name mismatch issue

2. **SECOND:** `/mnt/user-data/outputs/IMPLEMENTATION_CHECKLIST.md` (5 minutes)
   - This is your step-by-step guide
   - Every checkbox MUST be verified before moving forward
   - DO NOT SKIP ANY STEPS

3. **THIRD:** `/mnt/user-data/outputs/UPDATE_CLAUDE_MD.md` (5 minutes)
   - Update `.claude/CLAUDE.md` with current project state
   - This ensures you remember the correct file names

4. **OPTIONAL BUT RECOMMENDED:**
   - `/mnt/user-data/outputs/CBS_DATA_MAPPING_COMPLETE.md` - If you need architecture details
   - `/mnt/user-data/outputs/FILE_SPECIFICATIONS.md` - If you need file-specific details

---

## ⚡ QUICK START (After Reading)

### Step 1: Update Your Knowledge Base
```bash
# Update .claude/CLAUDE.md with current project state
# Follow instructions in /mnt/user-data/outputs/UPDATE_CLAUDE_MD.md
```

**VERIFY:** `.claude/CLAUDE.md` now says "Income_Decile.xlsx" (NOT "ta2.xlsx")

### Step 2: Run Baseline Validation
```bash
python /mnt/user-data/outputs/test_etl_validation.py
```

**EXPECTED RESULT:**
- ✅ File Existence: 8/8 files found
- ❌ Data Volume: Only 2,651 records (not 27,456)
- ❌ Segment Types: Only 1 type (not 7)

This establishes your baseline.

### Step 3: Follow the Checklist
Open `/mnt/user-data/outputs/IMPLEMENTATION_CHECKLIST.md` and follow it **EXACTLY**.

**CRITICAL RULE:** ✅ = Must verify before proceeding to next step

---

## 🔍 VALIDATION FRAMEWORK

### Run After EVERY Step
```bash
python /mnt/user-data/outputs/test_etl_validation.py
```

### Test Coverage
This script validates:
1. **File Existence** - All 8 CBS files present
2. **Database Schema** - V10 tables exist
3. **Data Volume** - 27,456 records loaded
4. **Burn Rate Flags** - Income/consumption metrics flagged correctly
5. **CBS Test Cases** - Values match CBS Excel screenshots:
   - Q1 income = ₪7,510
   - Q5 consumption = ₪20,076
   - Alcoholic beverages percentages
6. **Burn Rate Calculation** - Q1=146%, Q5=60%

### Failure Protocol
**IF ANY TEST FAILS:**
1. ❌ **STOP IMMEDIATELY**
2. 🔍 Read error message carefully
3. 🔧 Fix root cause (don't skip it!)
4. ✅ Re-run validation
5. ➡️ Only proceed when ALL tests pass

---

## 📁 FILE LOCATIONS REFERENCE

### Input Files (CBS Data)
```
/mnt/user-data/uploads/
├── הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx (Income Quintile)
├── Income_Decile.xlsx (Income Decile Net)
├── Education.xlsx (Religiosity - Table 13)
├── Household_Size.xlsx (Country of Birth - Table 11)
├── Household_Size2.xlsx (Income Decile Gross - Table 3)
├── WorkStatus-IncomeSource.xlsx (Geographic - Table 10)
├── WorkStatus-IncomeSource2.xlsx (Work Status - Table 12)
└── הוצאה_למזון_ללא_ארוחות_מחוץ_לבית_לפי_סוג_חנות.xlsx (Table 38 - Separate)
```

### Documentation (Your Guides)
```
/mnt/user-data/outputs/
├── EXECUTIVE_SUMMARY.md ⭐ Start here
├── IMPLEMENTATION_CHECKLIST.md ⭐ Follow this
├── test_etl_validation.py ⭐ Run after each step
├── load_segmentation_corrected.py ⭐ Use this ETL
├── QUICK_START_GUIDE.md
├── CBS_DATA_MAPPING_COMPLETE.md
├── FILE_SPECIFICATIONS.md
├── VISUAL_ARCHITECTURE.md
└── UPDATE_CLAUDE_MD.md
```

### Backend Files (To Be Modified)
```
backend/
├── models/
│   ├── schema_v10_normalized.sql (Already exists - ready to apply)
│   └── database.py (Already exists - don't modify)
├── etl/
│   ├── load_segmentation.py ⚠️ REPLACE with corrected version
│   └── extract_table_38.py (Already exists - don't modify)
├── api/
│   ├── main.py (Already exists - may need minor updates)
│   ├── strategic_endpoints_v9.py (Already exists - keep)
│   └── segmentation_endpoints_v10.py ⚠️ CREATE THIS
└── apply_schema_v10.py (Already exists - ready to run)
```

---

## ⚠️ CRITICAL DO'S AND DON'TS

### ✅ DO:
1. ✅ Read ALL documentation before starting
2. ✅ Update `.claude/CLAUDE.md` first
3. ✅ Run validation after EVERY step
4. ✅ Use `/mnt/user-data/outputs/load_segmentation_corrected.py`
5. ✅ Follow checklist exactly (don't skip steps)
6. ✅ Verify CBS test cases match Excel screenshots
7. ✅ Stop if ANY test fails
8. ✅ Back up database before major changes
9. ✅ Test with 1 file first, then all 8
10. ✅ Ask for clarification if confused

### ❌ DON'T:
1. ❌ Start coding without reading documentation
2. ❌ Modify `backend/etl/load_segmentation.py` (replace it entirely)
3. ❌ Skip validation steps
4. ❌ Continue if tests fail
5. ❌ Assume file names (check actual files)
6. ❌ Hardcode file paths or header rows
7. ❌ Skip the implementation checklist
8. ❌ Load all files at once (test 1 first)
9. ❌ Ignore error messages
10. ❌ Make changes to V9 schema (keep parallel)

---

## 🎯 SUCCESS CRITERIA

You will know you're done when:

- [ ] All 8 CBS files load without errors
- [ ] Database has **27,456** expenditure records (±500 tolerance)
- [ ] Database has **7 segment types** (not just 1)
- [ ] Burn rate: Q1=146.2%, Q5=59.8% (±2% tolerance)
- [ ] CBS test cases match Excel values (±100 NIS tolerance)
- [ ] All validation tests show ✅ (no ❌)
- [ ] API endpoint `/api/segments/types` returns 7 types
- [ ] API endpoint `/api/v10/burn-rate` returns valid percentages
- [ ] Frontend selector shows 7 options
- [ ] Charts update when changing segment selection
- [ ] No console errors in browser or terminal

**IF ALL CHECKED:** 🎉 You've successfully implemented V10!

---

## 📊 EXPECTED TIMELINE

| Phase | Duration | Verification |
|-------|----------|--------------|
| Reading docs | 30 min | Understand problem completely |
| Update CLAUDE.md | 10 min | `.claude/CLAUDE.md` updated |
| Apply schema | 15 min | `test_etl_validation.py` → Schema tests pass |
| ETL pipeline | 45 min | `test_etl_validation.py` → ALL tests pass |
| Data validation | 30 min | Manual spot checks confirm |
| API endpoints | 30 min | curl tests return valid JSON |
| Frontend updates | 60 min | Browser shows 7 segments |
| **TOTAL** | **3-4 hours** | All success criteria met |

---

## 🆘 TROUBLESHOOTING QUICK REF

| Problem | Check This | Solution |
|---------|-----------|----------|
| File not found | `/mnt/user-data/uploads/` | Verify actual file names |
| Header row error | `FILE_SPECIFICATIONS.md` | Check expected header_row per file |
| Wrong data count | `test_etl_validation.py` | Run validation, check which files failed |
| CBS values don't match | Excel screenshots | Verify data cleaning (no negatives, ±) |
| Burn rate wrong | `is_income_metric` flags | Check flags are set correctly |
| API 500 error | Backend logs | Verify database connection, check SQL |
| Frontend blank | Browser console | Check API URL, verify CORS |

---

## 📞 FINAL CHECKLIST BEFORE STARTING

- [ ] I've read `EXECUTIVE_SUMMARY.md` completely
- [ ] I've read `IMPLEMENTATION_CHECKLIST.md` completely
- [ ] I understand the file name mismatch problem
- [ ] I know to use `load_segmentation_corrected.py` (not the old one)
- [ ] I know to run `test_etl_validation.py` after each step
- [ ] I know to STOP if any test fails
- [ ] I have all 8 CBS files in `/mnt/user-data/uploads/`
- [ ] I have PostgreSQL running with DATABASE_URL in `.env`
- [ ] I'm ready to follow the checklist exactly

**IF ALL CHECKED:** Proceed to Phase 0 in `IMPLEMENTATION_CHECKLIST.md`

---

## 🚀 START HERE

1. Open `/mnt/user-data/outputs/IMPLEMENTATION_CHECKLIST.md`
2. Start with "Phase 0: Preparation"
3. Check every box as you complete it
4. Run validation after each phase
5. Proceed to next phase only when ALL tests pass

**Good luck! The documentation has everything you need.** 🎯

---

*If you get stuck, re-read the relevant documentation section.*  
*If still stuck, check the troubleshooting table.*  
*If still stuck, ask for clarification with specific error messages.*
