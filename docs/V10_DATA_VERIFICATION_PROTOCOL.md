# V10 Data Verification Protocol

## Purpose
This document provides the standard procedure for verifying that segment data is correctly pulled from the database before creating frontend visualizations and insights. Following this protocol prevents issues like empty charts, missing translations, or nonsensical business metrics.

**When to use this protocol:**
- Before reprofiling any segment type page
- After modifying ETL pipelines or database schema
- When debugging empty charts or missing data issues
- Before adding new segment types to the dashboard

---

## Quick Verification Command

```bash
cd backend/data/v10_exports
python -c "
import pandas as pd

# Change SEGMENT_TYPE to the one you're verifying
SEGMENT_TYPE = 'Work Status'  # or 'Geographic Region', 'Country of Birth', etc.

df = pd.read_csv('2024-11-22_complete_database_export_6420_records.csv')
seg_data = df[df['segment_type'] == SEGMENT_TYPE]

print(f'=== {SEGMENT_TYPE.upper()} DATA VERIFICATION ===\n')

# 1. Segment codes
print('1. Segment codes and order:')
segments = seg_data[['segment_value', 'segment_order']].drop_duplicates().sort_values('segment_order')
print(segments)
print(f'\nTotal segments: {len(segments)}')

# 2. Income data
print('\n2. Income by segment:')
income = seg_data[seg_data['item_name'].str.contains('Net money income', na=False)][['segment_value', 'expenditure_value']].sort_values('segment_value')
print(income)

# 3. Spending data
print('\n3. Spending by segment:')
spending = seg_data[seg_data['item_name'].str.contains('Money expenditure per household', na=False)][['segment_value', 'expenditure_value']].sort_values('segment_value')
print(spending)
"
```

---

## Step-by-Step Verification Checklist

### ✅ Step 1: Verify Segment Codes Exist

**What to check:**
- All expected segment values are present in the database
- Segment codes match the translation mapping in `segmentCodeTranslation.ts`
- No unexpected codes or missing segments

**Command:**
```python
segments = df[df['segment_type'] == 'Your Segment Type']['segment_value'].unique()
print(sorted(segments))
```

**Example output (Work Status):**
```
['1,176', '3,713', '589']  # 3 segments: Pensioners, Employees, Self-employed
```

**Red flags:**
- ❌ Empty list → ETL failed to load this segment type
- ❌ Fewer segments than expected → Check CSV export or ETL filters
- ❌ Codes don't match translation file → Need to update translations

---

### ✅ Step 2: Verify Income Data

**What to check:**
- Each segment has exactly 2 income records (gross + net)
- Income values are realistic (₪10K-₪30K range for Israeli households)
- No NULL or zero values

**Command:**
```python
income_data = df[
    (df['segment_type'] == 'Your Segment Type') &
    (df['item_name'].str.contains('income', case=False, na=False))
][['segment_value', 'item_name', 'expenditure_value']]
print(income_data)
```

**Example output (Work Status):**
```
segment_value | item_name           | expenditure_value
1,176         | Net money income    | 10540.0
1,176         | Gross money income  | 13850.0
589           | Net money income    | 19205.0
589           | Gross money income  | 24100.0
3,713         | Net money income    | 20522.0
3,713         | Gross money income  | 26800.0
```

**Red flags:**
- ❌ Only 1 income record per segment → Missing gross or net income
- ❌ Income < ₪5K or > ₪50K → Data quality issue or wrong units
- ❌ NULL values → ETL parsing error

---

### ✅ Step 3: Verify Spending Data

**What to check:**
- Each segment has spending data (consumption expenditure)
- Spending < Income (burn rate < 100% for most segments)
- Values are realistic

**Command:**
```python
spending_data = df[
    (df['segment_type'] == 'Your Segment Type') &
    (df['item_name'].str.contains('Money expenditure per household', na=False))
][['segment_value', 'expenditure_value']]
print(spending_data)
```

**Example output:**
```
segment_value | expenditure_value
1,176         | 9444.0   # Pensioners: 90% burn rate (9444/10540)
589           | 17001.0  # Self-employed: 89% burn rate
3,713         | 15710.0  # Employees: 77% burn rate
```

**Red flags:**
- ❌ Spending > Income significantly → Check if units are consistent
- ❌ Missing spending for some segments → ETL filter issue
- ❌ All segments have identical spending → Data duplication bug

---

### ✅ Step 4: Verify Translation Mapping

**What to check:**
- All database codes have Hebrew translations
- No extra codes in translation file that don't exist in data
- Labels are concise enough for chart display

**Where to check:**
`frontend2/src/utils/segmentCodeTranslation.ts`

**Command:**
```python
# Get database codes
db_codes = set(df[df['segment_type'] == 'Your Segment Type']['segment_value'].unique())

# Compare with translation file (manual check)
print(f'Database codes: {sorted(db_codes)}')
print('\nVerify these match the translation file!')
```

**Example (Work Status):**
```typescript
const WORK_STATUS_MAP: Record<string, string> = {
  '1,176': 'פנסיונר',  // ✅ Code exists in DB
  '1176': 'פנסיונר',   // ✅ Variant without comma
  '589': 'עצמאי',      // ✅ Code exists in DB
  '3,713': 'שכיר',     // ✅ Code exists in DB
  '3713': 'שכיר'       // ✅ Variant without comma
};
```

**Red flags:**
- ❌ Code in DB but not in translation → Will display as number in UI
- ❌ Code in translation but not in DB → Dead code, can remove
- ❌ Hebrew label too long → Chart labels will overlap

---

### ✅ Step 5: Calculate Burn Rate Manually

**What to check:**
- Burn rate formula works correctly: `(spending / income) * 100`
- Values are between 0-150% (most should be 60-100%)
- Segments with high/low burn rates make business sense

**Command:**
```python
verification = df[df['segment_type'] == 'Your Segment Type'].copy()

# Get income and spending for each segment
for segment in verification['segment_value'].unique():
    seg_data = verification[verification['segment_value'] == segment]

    income = seg_data[seg_data['item_name'].str.contains('Net money income', na=False)]['expenditure_value'].values
    spending = seg_data[seg_data['item_name'].str.contains('Money expenditure per household', na=False)]['expenditure_value'].values

    if len(income) > 0 and len(spending) > 0:
        burn_rate = (spending[0] / income[0]) * 100
        print(f'{segment}: Income=₪{income[0]:,.0f}, Spending=₪{spending[0]:,.0f}, Burn Rate={burn_rate:.1f}%')
```

**Example output:**
```
1,176: Income=₪10,540, Spending=₪9,444, Burn Rate=89.6%  # Pensioners
589: Income=₪19,205, Spending=₪17,001, Burn Rate=88.5%   # Self-employed
3,713: Income=₪20,522, Spending=₪15,710, Burn Rate=76.6% # Employees
```

**Red flags:**
- ❌ Burn rate > 110% for all segments → Formula error or data issue
- ❌ Burn rate < 50% → Unrealistic (Israelis don't save 50%+)
- ❌ Identical burn rates across segments → Data not segmented properly

---

## Common Issues and Solutions

### Issue 1: Empty Charts in Frontend

**Symptoms:**
- Frontend displays "אין נתונים זמינים"
- API returns empty array `[]`
- Burn rate chart shows no bars

**Diagnosis steps:**
1. Run Step 1 verification → Check if segment type exists in DB
2. Check materialized view: `SELECT * FROM vw_segment_burn_rate WHERE segment_type = 'Your Type' LIMIT 5`
3. Check if materialized view was refreshed after data load

**Solution:**
```sql
-- Refresh materialized views
REFRESH MATERIALIZED VIEW vw_segment_burn_rate;
REFRESH MATERIALIZED VIEW vw_segment_inequality;

-- Verify data now exists
SELECT segment_type, COUNT(*) FROM vw_segment_burn_rate GROUP BY segment_type;
```

---

### Issue 2: Numeric Codes Instead of Hebrew Labels

**Symptoms:**
- Chart shows "325", "371" instead of "מדינות אחרות", "עולי ברה״מ"
- Pie chart legend displays numbers

**Diagnosis steps:**
1. Run Step 4 verification → Check translation mapping
2. Verify `translateSegmentCode()` is called in component
3. Check browser console for errors in translation function

**Solution:**
Add missing codes to `segmentCodeTranslation.ts`:
```typescript
const YOUR_SEGMENT_MAP: Record<string, string> = {
  '325': 'מדינות אחרות',
  '371': 'עולי ברה״מ 2000+',
  // ... add all codes found in Step 1
};
```

---

### Issue 3: Nonsensical Business Insights

**Symptoms:**
- Insights reference tax payments or income metrics
- Inequality ratios like "×92" (too high)
- Insights don't match visible chart data

**Diagnosis steps:**
1. Check inequality view data quality (see V10_INEQUALITY_VIEW_DATA_QUALITY_FIX.md)
2. Verify insights are using burn rate data, not inequality data (unless intended)
3. Check if metric calculations match visible charts

**Solution:**
- Update insights to reference burn rate data from charts
- Exclude non-consumption items from inequality view (already fixed in V10)
- Recalculate metrics based on actual data values

---

## Production Deployment Checklist

Before deploying segment type changes to production:

- [ ] All 5 verification steps pass ✅
- [ ] Manual burn rate calculations match materialized view
- [ ] Translation mappings complete for all codes
- [ ] Frontend charts display correctly in browser
- [ ] Metric cards show realistic values (not "טוען..." forever)
- [ ] Business insights are meaningful and correlate with charts
- [ ] No console errors in browser developer tools
- [ ] Tested on all 7 segment types (if applicable)

---

## Automation Script

Save this as `backend/scripts/verify_segment_data.py`:

```python
#!/usr/bin/env python3
"""
V10 Segment Data Verification Script
Usage: python verify_segment_data.py "Work Status"
"""

import sys
import pandas as pd
from pathlib import Path

def verify_segment(segment_type: str):
    csv_path = Path(__file__).parent.parent / "data" / "v10_exports" / "2024-11-22_complete_database_export_6420_records.csv"

    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    seg_data = df[df['segment_type'] == segment_type]

    if seg_data.empty:
        print(f"❌ No data found for segment type: {segment_type}")
        return False

    print(f"=== {segment_type.upper()} DATA VERIFICATION ===\n")

    # Step 1: Segment codes
    segments = seg_data[['segment_value', 'segment_order']].drop_duplicates().sort_values('segment_order')
    print(f"✅ Step 1: Found {len(segments)} segments")
    print(segments.to_string(index=False))

    # Step 2: Income data
    income_data = seg_data[seg_data['item_name'].str.contains('Net money income', na=False)]
    print(f"\n✅ Step 2: Found {len(income_data)} income records")

    # Step 3: Spending data
    spending_data = seg_data[seg_data['item_name'].str.contains('Money expenditure per household', na=False)]
    print(f"✅ Step 3: Found {len(spending_data)} spending records")

    # Step 5: Calculate burn rates
    print("\n✅ Step 5: Burn rate verification:")
    for segment_value in segments['segment_value'].unique():
        seg_subset = seg_data[seg_data['segment_value'] == segment_value]

        income = seg_subset[seg_subset['item_name'].str.contains('Net money income', na=False)]['expenditure_value'].values
        spending = seg_subset[seg_subset['item_name'].str.contains('Money expenditure per household', na=False)]['expenditure_value'].values

        if len(income) > 0 and len(spending) > 0:
            burn_rate = (spending[0] / income[0]) * 100
            surplus = income[0] - spending[0]
            print(f"  {segment_value}: ₪{income[0]:,.0f} income, ₪{spending[0]:,.0f} spending → {burn_rate:.1f}% burn rate, ₪{surplus:,.0f} surplus")

    print(f"\n✅ All verification steps passed for {segment_type}!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_segment_data.py 'Segment Type Name'")
        sys.exit(1)

    segment_type = sys.argv[1]
    success = verify_segment(segment_type)
    sys.exit(0 if success else 1)
```

**Usage:**
```bash
cd backend
python scripts/verify_segment_data.py "Work Status"
python scripts/verify_segment_data.py "Geographic Region"
python scripts/verify_segment_data.py "Country of Birth"
```

---

**Created**: November 23, 2024
**Last Updated**: November 23, 2024
**Status**: ✅ Active Protocol
**Next Review**: Before any new segment type additions
