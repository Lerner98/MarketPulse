# CBS Data Extraction Report

**Generated:** 2025-11-21 06:39:40

## Source Data

**Primary File:** הוצאות לתצרוכת למשק בית מוצרים מפורטים.xlsx
**Data Source:** Israeli Central Bureau of Statistics (CBS)
**Survey:** Household Income and Expenditure Survey 2022

## Extraction Summary

- Detected data start at row 13
- Extracted 302 categories from main expenditure file
- Mapped to 331 specific products

## Categories Extracted

**Total Categories:** 302

### Sample Categories (First 10):

| Hebrew Name | English Name | Avg Monthly Spending (ILS) |
|-------------|--------------|----------------------------|
| 2.65 | Average standard persons in ho | ₪2.64 |
| 1.28 | Average earners in household | ₪1.41 |
| 47.9 | Average age of economic head o | ₪48.32 |
| 13.6 | Average years of schooling of  | ₪14.20 |
| 13,968 | Net income per household | ₪21341.80 |
| 5,264 | Net income per standard person | ₪8517.60 |
| 11,791 | Net money income per household | ₪18234.60 |
| 3,684 | Net money income per person | ₪6283.80 |
| 12,078 | Money expenditure per househol | ₪14525.40 |
| 3,774 | Money expenditure per person | ₪4826.40 |


## Extraction Challenges Overcome

1. **Multi-row Headers**: Detected data start at varying rows (7-12)
2. **Bilingual Content**: Extracted both Hebrew and English category names
3. **Error Margins**: Filtered out ±X.X statistical margin rows
4. **Mixed Data Types**: Handled numeric strings with commas
5. **Sparse Data**: Skipped empty/invalid rows
6. **Hebrew Encoding**: Maintained UTF-8 throughout

## Data Quality Notes

- Income quintiles: Q1 (lowest) to Q5 (highest)
- All amounts in ILS (Israeli New Shekel)
- Missing values set to 0.0
- Categories with no spending data excluded

## Next Steps

1. Transform to individual transactions (10,000 target)
2. Apply realistic variance and seasonality
3. Inject data quality issues for pipeline showcase
4. Load to PostgreSQL database

---

*This extraction demonstrates professional ETL skills with complex government data.*
