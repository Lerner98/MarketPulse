# 📋 CBS FILE SPECIFICATIONS - Complete Reference

**Purpose:** Detailed parsing instructions for each CBS file  
**For:** ETL developers, QA testers, data analysts

---

## 📁 FILE 1: הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx

### Basic Info
- **CBS Table:** 1.1
- **Title:** "MONTHLY INCOME AND CONSUMPTION EXPENDITURE (SPECIFIED COMMODITIES) OF HOUSEHOLDS, BY QUINTILE OF NET INCOME PER STANDARD PERSON"
- **Segment Type:** Income Quintile
- **File Size:** 115 KB
- **Encoding:** Windows-1255 (Hebrew) + UTF-8 (English)

### Structure
```
Row 0-3:  Title and metadata (English + Hebrew)
Row 4:    Year (2022)
Row 5:    Column group headers (Quintiles | חמישונים | סך הכל)
Row 6:    Segment values (5 | 4 | 3 | 2 | 1 | Total) ← START HERE
Row 7+:   Data rows (1,368 rows total)
```

### Segments (6 columns)
| Column | Segment | Description | Avg Income | Population |
|--------|---------|-------------|------------|-----------|
| Col 1 | 5 (Q5) | Richest 20% | ₪33,591 | 584.5K households |
| Col 2 | 4 (Q4) | Upper-middle | ₪21,775 | 583.9K households |
| Col 3 | 3 (Q3) | Middle | ₪16,506 | 584.2K households |
| Col 4 | 2 (Q2) | Lower-middle | ₪11,791 | 584.1K households |
| Col 5 | 1 (Q1) | Poorest 20% | ₪7,510 | 583.9K households |
| Col 6 | Total | All households | ₪18,237 | 2,920.8K households |

### Critical Rows (for Burn Rate)
```
Row ~25: "Net money income per household"
  Q5: 33,591 | Q4: 21,775 | Q3: 16,506 | Q2: 11,791 | Q1: 7,510

Row ~29: "Money expenditure per household"
  Q5: 20,076 | Q4: 15,813 | Q3: 13,681 | Q2: 12,078 | Q1: 10,979

Burn Rate = (Row 29 / Row 25) × 100
  Q1: 146.2% (deficit!)
  Q5: 59.8% (healthy savings)
```

### Parsing Rules
1. **Skip rows 0-5** (metadata)
2. **Header row = 6** (5, 4, 3, 2, 1, Total)
3. **Item column:** First text column (Hebrew + English names)
4. **Skip:** Rows with ± (error margins), () footnotes
5. **Clean values:** Remove commas, ±, parentheses, take abs() of negatives
6. **Flag rows:** `is_income_metric` = contains "Net money income per household"
7. **Flag rows:** `is_consumption_metric` = contains "Money expenditure per household"

### ETL Configuration
```python
{
    'segment_type': 'Income Quintile',
    'table_number': '1.1',
    'header_row': 6,
    'segment_pattern': r'^[1-5]$|^Total$',
    'income_row_keyword': 'Net money income per household',
    'consumption_row_keyword': 'Money expenditure per household',
}
```

### Expected Output
- **Segments:** 6 (Q1-Q5 + Total)
- **Categories:** 528 expenditure items
- **Records:** 528 × 6 = 3,168 (before filtering)
- **After filtering:** ~2,640 clean records

---

## 📁 FILE 2: Income_Decile.xlsx

### Basic Info
- **CBS Table:** 2
- **Title:** "MONTHLY INCOME AND CONSUMPTION EXPENDITURE OF HOUSEHOLDS, BY DECILE OF NET MONEY INCOME PER STANDARD PERSON"
- **Segment Type:** Income Decile (Net)
- **File Size:** 46 KB

### Structure
```
Row 0-3:  Title and metadata
Row 4:    Column group headers (Deciles | עשירונים | סך הכל)
Row 5:    Segment values (10 | 9 | 8 | ... | 1 | Total) ← START HERE
Row 6+:   Data rows
```

### Segments (11 columns)
| Column | Segment | Upper Limit | Description |
|--------|---------|------------|-------------|
| Col 1 | 10 (D10) | ₪13,160+ | Top 10% |
| Col 2 | 9 (D9) | ₪10,143 | 81-90th percentile |
| Col 3 | 8 (D8) | ₪8,565 | 71-80th percentile |
| Col 4 | 7 (D7) | ₪7,294 | 61-70th percentile |
| Col 5 | 6 (D6) | ₪6,289 | 51-60th percentile |
| Col 6 | 5 (D5) | ₪5,257 | 41-50th percentile |
| Col 7 | 4 (D4) | ₪4,339 | 31-40th percentile |
| Col 8 | 3 (D3) | - | 21-30th percentile |
| Col 9 | 2 (D2) | - | 11-20th percentile |
| Col 10 | 1 (D1) | - | Bottom 10% |
| Col 11 | Total | - | All households |

### Key Differences from File 1
- **10 groups instead of 5** (more granular)
- **Same 528 categories**
- **Income limits shown** (upper bound per decile)
- **Arab household %** included (ethnic breakdown)

### ETL Configuration
```python
{
    'segment_type': 'Income Decile (Net)',
    'table_number': '2',
    'header_row': 5,
    'segment_pattern': r'^[1-9]$|^10$|^Total$',
    'income_row_keyword': 'Net money income per household',
    'consumption_row_keyword': 'Money expenditure per household',
}
```

### Expected Output
- **Segments:** 11 (D1-D10 + Total)
- **Categories:** 528
- **Records:** 528 × 11 = 5,808 (before filtering)
- **After filtering:** ~5,280 clean records

---

## 📁 FILE 3: Education.xlsx

### Basic Info
- **CBS Table:** 13
- **Title:** "MONTHLY INCOME AND CONSUMPTION EXPENDITURE PER JEWISH HOUSEHOLD, BY LEVEL OF RELIGIOSITY"
- **Segment Type:** Religiosity Level
- **File Size:** 35 KB
- **Scope:** Jewish households only (excludes Arab households)

### Structure
```
Row 0-2:  Title
Row 3:    Hebrew segment names
Row 4:    English segment names
Row 5:    Sample sizes ← START HERE
Row 6+:   Data rows
```

### Segments (6 columns)
| Column | Hebrew | English | Sample Size | Avg Household Size |
|--------|--------|---------|-------------|-------------------|
| Col 1 | מעורב/אחר/לא ידוע | Mixed/Other/Unknown | 127 | 3.12 |
| Col 2 | חרדי | Ultra-Orthodox | 593 | 5.15 (largest families!) |
| Col 3 | דתי | Religious | 645 | 3.54 |
| Col 4 | מסורתי | Traditional | 1,139 | 2.90 |
| Col 5 | חילוני | Secular | 2,080 | 2.55 (smallest families) |
| Col 6 | סך הכל | Total | 4,584 | 3.01 |

### Business Insights
- **Ultra-Orthodox:**
  - 5.15 people per household (2x secular)
  - Lower income but larger households
  - High spending on education (religious schools)
  - Different food consumption (kosher requirements)

- **Secular:**
  - 2.55 people per household (couples/singles)
  - Higher income, more discretionary spending
  - More on entertainment, travel, dining out

### ETL Configuration
```python
{
    'segment_type': 'Religiosity Level',
    'table_number': '13',
    'header_row': 5,
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
}
```

### Expected Output
- **Segments:** 6 (5 religiosity levels + Total)
- **Categories:** 528
- **Records:** ~2,640 clean records

---

## 📁 FILE 4: Household_Size.xlsx

### Basic Info
- **CBS Table:** 11
- **Title:** "MONTHLY INCOME AND CONSUMPTION EXPENDITURE PER HOUSEHOLD, BY COUNTRY OF BIRTH AND PERIOD OF IMMIGRATION OF HEAD OF HOUSEHOLD"
- **Segment Type:** Country of Birth & Immigration
- **File Size:** 39 KB

### Structure
```
Row 0-9:   Complex multi-row headers
Row 10:    Sub-headers (Country/Period breakdown)
Row 11:    Sample sizes ← START HERE
Row 12+:   Data rows
```

### Segments (6 columns)
| Column | Description | Sample | Avg Household Size |
|--------|-------------|--------|-------------------|
| Col 1 | Other (non-USSR) | 325 | 3.26 |
| Col 2 | USSR (all periods) | 649 | 2.54 |
| Col 3 | USSR (2000+) | 371 | 2.98 |
| Col 4 | USSR (up to 1999) | 603 | 2.65 |
| Col 5 | Israel-born + non-USSR immigrants | 3,777 | 2.78 |
| Col 6 | Total | varies | 3.05 |

### Business Insights
- **USSR 1990s wave:** Established, higher income, integrated
- **USSR 2000s wave:** Newer, lower income, still integrating
- **Israel-born:** Diverse group, baseline for comparison
- **Spending patterns:** Immigrants spend more on tech/electronics (familiar from home country)

### ETL Configuration
```python
{
    'segment_type': 'Country of Birth',
    'table_number': '11',
    'header_row': 11,
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
}
```

### Expected Output
- **Segments:** 6
- **Categories:** 528
- **Records:** ~2,640 clean records

---

## 📁 FILE 5: Household_Size2.xlsx

### Basic Info
- **CBS Table:** 3
- **Title:** "MONTHLY INCOME AND CONSUMPTION EXPENDITURE OF HOUSEHOLDS, BY DECILE OF GROSS MONEY INCOME PER HOUSEHOLD"
- **Segment Type:** Income Decile (Gross)
- **File Size:** 46 KB

### Structure
```
Row 0-3:  Title
Row 4:    Column group headers
Row 5:    Segment values (10 | 9 | ... | 1 | Total) ← START HERE
Row 6+:   Data rows
```

### Segments (11 columns)
| Column | Segment | Upper Limit | Avg Household Size |
|--------|---------|------------|-------------------|
| Col 1 | 10 (D10) | ₪44,578+ | 3.95 (larger families) |
| Col 2 | 9 (D9) | ₪32,581 | 3.87 |
| Col 3 | 8 (D8) | ₪25,420 | 3.69 |
| ... | ... | ... | ... |
| Col 10 | 1 (D1) | Below ₪7,800 | Varies |
| Col 11 | Total | - | 3.17 |

### Key Difference from File 2
- **File 2:** Net income **per standard person** (normalized for household size)
- **File 5:** Gross income **per household** (raw total)

**Example:**
- Family of 4 earning ₪30,000:
  - File 2: ₪7,500 per standard person → D5-D6
  - File 5: ₪30,000 per household → D8-D9

### Business Value
- **File 2** = fairness (income adjusted for household size)
- **File 5** = purchasing power (actual household total income)
- **Combined:** Full picture of both equity and absolute spending capacity

### ETL Configuration
```python
{
    'segment_type': 'Income Decile (Gross)',
    'table_number': '3',
    'header_row': 5,
    'segment_pattern': r'^[1-9]$|^10$|^Total$',
    'income_row_keyword': 'Gross money income per household',  # DIFFERENT!
    'consumption_row_keyword': 'Money expenditure per household',
}
```

### Expected Output
- **Segments:** 11 (D1-D10 + Total)
- **Categories:** 528
- **Records:** ~5,280 clean records

---

## 📁 FILE 6: WorkStatus-IncomeSource.xlsx

### Basic Info
- **CBS Table:** 10
- **Title:** "MONTHLY INCOME AND CONSUMPTION EXPENDITURE PER HOUSEHOLD, BY SUB-DISTRICT"
- **Segment Type:** Geographic Region (נפה)
- **File Size:** 61 KB

### Structure
```
Row 0-9:   Complex multi-row headers (Hebrew + English region names)
Row 10:    Sample sizes ← START HERE
Row 11+:   Data rows
```

### Segments (15 columns)
| Column | Region (English) | Region (Hebrew) | Sample | Avg Household Size |
|--------|-----------------|----------------|--------|-------------------|
| Col 1 | Judea & Samaria | אזור יהודה והשומרון | 281 | 4.35 |
| Col 2 | Be'er Sheva | באר שבע | 471 | 3.61 |
| Col 3 | Ashqelon | אשקלון | 405 | 3.08 |
| Col 4 | Holon | חולון | 117 | 2.98 |
| Col 5 | Ramat Gan | רמת גן | 132 | 2.69 |
| Col 6 | Tel Aviv | תל אביב | 218 | 2.42 (smallest!) |
| Col 7 | Rehovot | רחובות | 362 | 2.95 |
| Col 8 | Ramla | רמלה | - | - |
| Col 9 | Petah Tikva | פתח תקווה | - | - |
| Col 10 | Sharon | שרון | - | - |
| Col 11 | Hadera | חדרה | - | - |
| Col 12 | Haifa | חיפה | - | - |
| Col 13 | Zefat/Kinneret/Golan | צפת/כנרת/גולן | - | - |
| Col 14 | Jerusalem | ירושלים | - | - |
| Col 15 | Total | סך הכל | - | 3.17 |

### Business Insights
- **Tel Aviv:** Small households (2.42), high income, luxury spending
- **Judea & Samaria:** Large households (4.35), religious families
- **Be'er Sheva:** Periphery, lower income, budget-conscious
- **Geographic gaps:** Tel Aviv vs periphery = different retail strategies

### ETL Configuration
```python
{
    'segment_type': 'Geographic Region',
    'table_number': '10',
    'header_row': 10,
    'segment_mapping': {
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
}
```

### Expected Output
- **Segments:** 15 (14 regions + Total)
- **Categories:** 528
- **Records:** ~7,920 (before filtering) → ~7,392 clean

---

## 📁 FILE 7: WorkStatus-IncomeSource2.xlsx

### Basic Info
- **CBS Table:** 12
- **Title:** "MONTHLY INCOME AND CONSUMPTION EXPENDITURE PER HOUSEHOLD, BY SOURCES OF INCOME AND STATUS AT WORK OF HEAD OF HOUSEHOLD"
- **Segment Type:** Work Status
- **File Size:** 31 KB

### Structure
```
Row 0-6:  Title
Row 7:    Hebrew segment names (לא עובד | עצמאי | שכיר)
Row 8:    English segment names (Not working | Self-employed | Employee) ← START HERE
Row 9+:   Data rows
```

### Segments (4 columns)
| Column | Status (Hebrew) | Status (English) | Sample | Avg Household Size |
|--------|----------------|------------------|--------|-------------------|
| Col 1 | לא עובד | Not Working | 1,176 | 1.87 (singles/elderly) |
| Col 2 | עצמאי | Self-Employed | 589 | 3.19 |
| Col 3 | שכיר | Employee | 3,713 | 3.58 (largest group) |
| Col 4 | סך הכל | Total | 5,478 | 3.17 |

### Business Insights
- **Employee (67% of households):**
  - Stable income, predictable spending
  - Largest segment → mass market strategies
  
- **Self-Employed (11% of households):**
  - Irregular income, cash flow challenges
  - Higher risk tolerance
  - Different credit needs

- **Not Working (21% of households):**
  - Retirees + unemployed
  - Small households (1.87 avg)
  - Budget-conscious, low burn rate

### ETL Configuration
```python
{
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
}
```

### Expected Output
- **Segments:** 4 (3 work statuses + Total)
- **Categories:** 528
- **Records:** ~1,584 clean records

---

## 📁 FILE 8: הוצאה_למזון_ללא_ארוחות_מחוץ_לבית_לפי_סוג_חנות.xlsx

### Basic Info
- **CBS Table:** 38
- **Title:** "FOOD EXPENDITURE (EXCLUDING DINING OUT) BY TYPE OF STORE"
- **Segment Type:** Retail Competition
- **File Size:** 29 KB
- **Data Type:** Percentages (not NIS amounts!)

### Structure
```
Row 0-7:  Title and headers
Row 8:    Store type names ← START HERE
Row 9+:   Data rows (alternating: values + error margins)
```

### Segments (8 store types × 13 food categories)
**Store Types (columns):**
1. **אחר (Other):** 0.3% - miscellaneous
2. **חנות מיוחדת (Special Shop):** 2.3% - wine, specialty
3. **אטליז (Butcher):** 8.8% - fresh meat
4. **חנות ירקות ופירות (Veg/Fruit Shop):** 5.9% - fresh produce
5. **רשת מזון מקוונת (Online Supermarket):** 3.4% - digital
6. **רשתות מזון (Supermarket Chain):** 53.4% - THE DOMINANT PLAYER
7. **שוק (Market):** 15.6% - outdoor traditional
8. **מכולת (Grocery):** 10.3% - corner stores

**Food Categories (rows):**
1. Bread & Cereals
2. Meat & Poultry
3. Fish
4. Dairy & Eggs
5. Oils & Fats
6. Fresh Vegetables
7. Fresh Fruits
8. Sugar & Sweets
9. Other Food
10. Coffee, Tea, Cocoa
11. Mineral Water, Soft Drinks, Juices
12. Alcoholic Beverages
13. Food Products (general)

### Critical Insight: Fresh vs Packaged Battle

**Supermarket Chain Dominance:**
- Bread: 53.4%
- Packaged goods: 60%+

**Traditional Store Wins:**
- Butcher (Meat): 45.1%
- Market (Fresh Veg): 27.9%
- Market (Fresh Fruit): 36.7%

**Test Case (Alcoholic Beverages):**
```
Special Shop: 30.4%  ← Wine expertise
Supermarket: 51.1%   ← Convenience
Grocery: 11.4%       ← Local access
Market: 0%           ← Not sold there
Total: ~100%
```

### ETL Configuration
```python
# DIFFERENT PIPELINE - This is percentage data, not expenditure amounts!
{
    'table_number': '38',
    'header_row': 8,
    'store_columns': {
        1: 'Other',
        2: 'Special Shop',
        3: 'Butcher',
        4: 'Veg/Fruit Shop',
        5: 'Online Supermarket',
        6: 'Supermarket Chain',
        7: 'Market',
        8: 'Grocery'
    },
    'data_pattern': 'alternating',  # Row N = data, Row N+1 = error margin
}
```

### Expected Output
- **Categories:** 13 food types
- **Store Types:** 8
- **Records:** 13 × 8 = 104 percentage values
- **Validation:** Each category row should sum to ~100%

---

## 🔍 SUMMARY TABLE

| File | Segment Type | Segments | Categories | Records | Business Value |
|------|--------------|----------|-----------|---------|---------------|
| 1 | Income Quintile | 5 | 528 | 2,640 | ✅ Wealth inequality, burn rate |
| 2 | Income Decile (Net) | 10 | 528 | 5,280 | Granular income analysis |
| 3 | Religiosity | 5 | 528 | 2,640 | Cultural spending patterns |
| 4 | Country of Birth | 5 | 528 | 2,640 | Immigrant vs native behavior |
| 5 | Income Decile (Gross) | 10 | 528 | 5,280 | Raw household purchasing power |
| 6 | Geographic | 14 | 528 | 7,392 | Regional marketing strategies |
| 7 | Work Status | 3 | 528 | 1,584 | Employment-based segmentation |
| 8 | Retail | 8 stores × 13 foods | - | 104 | Fresh vs packaged competition |
| **TOTAL** | **7 types** | **52** | **528** | **27,560** | **Complete demographic view** |

---

*Last Updated: November 22, 2024*  
*Purpose: Technical reference for ETL development*  
*Status: Production-ready specifications*
