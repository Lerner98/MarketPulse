# MarketPulse Data Dictionary

## CBS Categories (cbs_categories_FIXED.csv)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| category_hebrew | string | Hebrew CBS category name | "לחם, דגנים ומוצרי בצק" |
| category_english | string | English translation | "Bread, cereals, and pastry" |
| quintile_1 | float | Q1 avg monthly spending (ILS) | 383.4 |
| quintile_2 | float | Q2 avg monthly spending (ILS) | 389.3 |
| quintile_3 | float | Q3 avg monthly spending (ILS) | 368.7 |
| quintile_4 | float | Q4 avg monthly spending (ILS) | 372.0 |
| quintile_5 | float | Q5 avg monthly spending (ILS) | 343.6 |
| avg_spending | float | Overall avg spending (ILS) | 371.4 |
| category | string | Unified category field | "לחם, דגנים ומוצרי בצק" |

**Note:** Quintile 1 = Lowest income, Quintile 5 = Highest income

---

## Transactions (transactions_cleaned.csv)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| transaction_id | integer | Unique transaction ID | 10000 |
| customer_name | string | Hebrew customer name | "רבקה בוחבוט" |
| product | string | Hebrew product name | "ירקות טריים" |
| category | string | CBS category | "מזון ומשקאות" |
| amount | float | Transaction amount (ILS) | 254.46 |
| currency | string | Currency code | "ILS" |
| transaction_date | date | Date (YYYY-MM-DD) | "2024-11-10" |
| status | string | Transaction status | "completed" |
| customer_city | string | Hebrew city name | "תל אביב" |
| income_quintile | integer | Income group (1-5) | 4 |

**Statuses:** completed, pending, cancelled
**Cities:** Tel Aviv, Jerusalem, Haifa, Beer Sheva, etc.

---

## Business Insights (business_insights.json)

**Structure:**
```json
{
  "metadata": { /* generation info */ },
  "data_summary": { /* 10K transactions */ },
  "income_quintile_analysis": { /* Q1-Q5 */ },
  "top_categories": { /* category: revenue */ },
  "top_products": { /* product: revenue */ },
  "top_cities": { /* city: metrics */ },
  "monthly_trend": { /* month: spending */ },
  "seasonal_insights": { /* peak/low */ },
  "pareto_analysis": { /* 80/20 rule */ },
  "business_recommendations": [ /* list */ ],
  "key_metrics": { /* concentration, disparity */ }
}
```

**Encoding:** UTF-8 with Hebrew characters
