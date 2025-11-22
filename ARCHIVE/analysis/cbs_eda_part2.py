"""
Phase 4 EDA - Part 2: Geographic, Temporal, and Product Analysis
Continuation of cbs_eda_complete.py
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sns.set_style("whitegrid")

project_root = Path(__file__).parent.parent.parent
data_dir = project_root / 'data' / 'processed'
analysis_dir = project_root / 'docs' / 'analysis'

# Load data
df = pd.read_csv(data_dir / 'transactions_cleaned.csv')
df['transaction_date'] = pd.to_datetime(df['transaction_date'])

# ============================================================================
# SECTION 4: Geographic Analysis
# ============================================================================

print("="*70)
print("SECTION 4: GEOGRAPHIC MARKET ANALYSIS")
print("Business Question: Which Israeli cities represent the largest market opportunities?")
print("="*70)
print()

# Calculate city metrics
city_metrics = df.groupby('customer_city').agg({
    'amount': ['sum', 'mean', 'count'],
    'transaction_id': 'nunique'
}).round(2)

city_metrics.columns = ['Total_Spending', 'Avg_Transaction', 'Transaction_Count', 'Unique_Transactions']
city_metrics = city_metrics.sort_values('Total_Spending', ascending=False)

print("📊 TOP CITIES BY SPENDING:")
print(city_metrics.head(10).to_string())
print()

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Top 10 cities by total spending
top_10_cities = city_metrics.head(10)['Total_Spending']
y_pos = np.arange(len(top_10_cities))
axes[0, 0].barh(y_pos, top_10_cities.values, color='steelblue', edgecolor='black')
axes[0, 0].set_yticks(y_pos)
axes[0, 0].set_yticklabels(top_10_cities.index)
axes[0, 0].set_title('Top 10 Cities by Total Spending', fontsize=14, weight='bold')
axes[0, 0].set_xlabel('Total Spending (ILS)')
axes[0, 0].invert_yaxis()

# 2. Market share by city (pie chart)
top_5_cities = city_metrics.head(5)['Total_Spending']
other_cities = city_metrics.iloc[5:]['Total_Spending'].sum()
pie_labels = list(top_5_cities.index) + ['Other Cities']
pie_data = list(top_5_cities.values) + [other_cities]
axes[0, 1].pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90)
axes[0, 1].set_title('Market Share by City', fontsize=14, weight='bold')

# 3. Average transaction size by city
top_10_avg_city = city_metrics.head(10)['Avg_Transaction']
y_pos = np.arange(len(top_10_avg_city))
axes[1, 0].barh(y_pos, top_10_avg_city.values, color='coral', edgecolor='black')
axes[1, 0].set_yticks(y_pos)
axes[1, 0].set_yticklabels(top_10_avg_city.index)
axes[1, 0].set_title('Top 10 Cities by Avg Transaction Size', fontsize=14, weight='bold')
axes[1, 0].set_xlabel('Average Amount (ILS)')
axes[1, 0].invert_yaxis()

# 4. Transaction frequency by city
top_10_count_city = city_metrics.head(10)['Transaction_Count']
y_pos = np.arange(len(top_10_count_city))
axes[1, 1].barh(y_pos, top_10_count_city.values, color='lightgreen', edgecolor='black')
axes[1, 1].set_yticks(y_pos)
axes[1, 1].set_yticklabels(top_10_count_city.index)
axes[1, 1].set_title('Top 10 Cities by Transaction Frequency', fontsize=14, weight='bold')
axes[1, 1].set_xlabel('Number of Transactions')
axes[1, 1].invert_yaxis()

plt.tight_layout()
plt.savefig(analysis_dir / '03_geographic_analysis.png', dpi=300, bbox_inches='tight')
print("[OK] Saved visualization: docs/analysis/03_geographic_analysis.png")
print()

# Business insights
top_city = city_metrics.index[0]
top_city_revenue = city_metrics.iloc[0]['Total_Spending']
top_city_pct = (top_city_revenue / df['amount'].sum()) * 100

print("💡 BUSINESS INSIGHTS:")
print(f"   • Largest market: {top_city} (ILS {top_city_revenue:,.2f}, {top_city_pct:.1f}% of total)")
top3_cities_pct = ((city_metrics.head(3)['Total_Spending'].sum() / df['amount'].sum()) * 100)
print(f"   • Top 3 cities represent {top3_cities_pct:.1f}% of market")
print()
print("📈 RECOMMENDATIONS FOR BUSINESSES:")
print("   • Priority markets: תל אביב, ירושלים, חיפה (highest volume)")
print("   • Secondary markets: באר שבע, פתח תקווה (growth potential)")
print("   • Consider urban vs. suburban spending patterns")
print()

# ============================================================================
# SECTION 5: Temporal Analysis
# ============================================================================

print("="*70)
print("SECTION 5: TEMPORAL & SEASONAL PATTERNS")
print("Business Question: Are there seasonal patterns in Israeli consumer spending?")
print("="*70)
print()

# Extract time features
df['month'] = df['transaction_date'].dt.month
df['day_of_week'] = df['transaction_date'].dt.day_name()

# Monthly analysis
monthly_spending = df.groupby('month').agg({
    'amount': ['sum', 'mean', 'count']
}).round(2)

print("📊 MONTHLY SPENDING PATTERNS:")
print(monthly_spending)
print()

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Monthly spending trend
monthly_totals = df.groupby('month')['amount'].sum()
axes[0, 0].plot(monthly_totals.index, monthly_totals.values, marker='o', linewidth=2, markersize=8, color='steelblue')
axes[0, 0].set_title('Monthly Spending Trend (2024)', fontsize=14, weight='bold')
axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Total Spending (ILS)')
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].set_xticks(range(1, 13))
axes[0, 0].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

# 2. Day of week patterns
dow_spending = df.groupby('day_of_week')['amount'].sum()
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_spending = dow_spending.reindex(dow_order)
axes[0, 1].bar(range(len(dow_spending)), dow_spending.values, color='steelblue', edgecolor='black')
axes[0, 1].set_title('Spending by Day of Week', fontsize=14, weight='bold')
axes[0, 1].set_xlabel('Day')
axes[0, 1].set_ylabel('Total Spending (ILS)')
axes[0, 1].set_xticks(range(len(dow_spending)))
axes[0, 1].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=45)

# 3. Transaction volume over time (weekly aggregation for cleaner viz)
df['week'] = df['transaction_date'].dt.isocalendar().week
weekly_count = df.groupby('week').size()
axes[1, 0].plot(weekly_count.index, weekly_count.values, alpha=0.7, color='coral')
axes[1, 0].set_title('Weekly Transaction Volume', fontsize=14, weight='bold')
axes[1, 0].set_xlabel('Week of Year')
axes[1, 0].set_ylabel('Number of Transactions')
axes[1, 0].grid(True, alpha=0.3)

# 4. Heatmap of spending by month and quintile
pivot_month_quintile = df.pivot_table(
    values='amount',
    index='month',
    columns='income_quintile',
    aggfunc='sum'
)
sns.heatmap(pivot_month_quintile, annot=True, fmt='.0f', cmap='YlOrRd', ax=axes[1, 1], cbar_kws={'label': 'Total Spending (ILS)'})
axes[1, 1].set_title('Spending Heatmap: Month vs. Quintile', fontsize=14, weight='bold')
axes[1, 1].set_xlabel('Income Quintile')
axes[1, 1].set_ylabel('Month')

plt.tight_layout()
plt.savefig(analysis_dir / '04_temporal_analysis.png', dpi=300, bbox_inches='tight')
print("[OK] Saved visualization: docs/analysis/04_temporal_analysis.png")
print()

# Business insights
peak_month = monthly_totals.idxmax()
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
peak_month_name = month_names[peak_month - 1]
low_month = monthly_totals.idxmin()
low_month_name = month_names[low_month - 1]

print("💡 BUSINESS INSIGHTS:")
print(f"   • Peak spending month: {peak_month_name} (ILS {monthly_totals[peak_month]:,.2f})")
print(f"   • Lowest spending month: {low_month_name} (ILS {monthly_totals[low_month]:,.2f})")
variation = ((monthly_totals.max() / monthly_totals.min() - 1) * 100)
print(f"   • Variation: {variation:.1f}% between peak and low")
print()
print("📈 RECOMMENDATIONS FOR BUSINESSES:")
print("   • Holiday seasons (Rosh Hashanah, Passover) → Plan inventory 2-3 months ahead")
print("   • Summer months → Adjust for vacation spending patterns")
print("   • Consider Jewish holiday calendar for promotional campaigns")
print()

# ============================================================================
# SECTION 6: Product-Level Analysis
# ============================================================================

print("="*70)
print("SECTION 6: PRODUCT-LEVEL PERFORMANCE")
print("Business Question: Which specific products are best-sellers?")
print("="*70)
print()

# Calculate product metrics
product_metrics = df.groupby('product').agg({
    'amount': ['sum', 'mean', 'count'],
    'income_quintile': 'mean'
}).round(2)

product_metrics.columns = ['Total_Revenue', 'Avg_Price', 'Sales_Count', 'Avg_Quintile']
product_metrics = product_metrics.sort_values('Total_Revenue', ascending=False)

print("📊 TOP 20 PRODUCTS BY REVENUE:")
print(product_metrics.head(20).to_string())
print()

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Top 15 products by revenue
top_15_products = product_metrics.head(15)['Total_Revenue']
y_pos = np.arange(len(top_15_products))
axes[0, 0].barh(y_pos, top_15_products.values, color='steelblue', edgecolor='black')
axes[0, 0].set_yticks(y_pos)
axes[0, 0].set_yticklabels(top_15_products.index, fontsize=9)
axes[0, 0].set_title('Top 15 Products by Revenue', fontsize=14, weight='bold')
axes[0, 0].set_xlabel('Total Revenue (ILS)')
axes[0, 0].invert_yaxis()

# 2. Price vs. sales volume scatter
top_100 = product_metrics.head(100)
axes[0, 1].scatter(top_100['Sales_Count'], top_100['Avg_Price'], alpha=0.6, color='coral', edgecolors='black')
axes[0, 1].set_title('Price vs. Sales Volume (Top 100 Products)', fontsize=14, weight='bold')
axes[0, 1].set_xlabel('Sales Count')
axes[0, 1].set_ylabel('Average Price (ILS)')
axes[0, 1].grid(True, alpha=0.3)

# 3. Products by target quintile
quintile_distribution = product_metrics.head(20)['Avg_Quintile']
y_pos = np.arange(len(quintile_distribution))
axes[1, 0].barh(y_pos, quintile_distribution.values, color='coral', edgecolor='black')
axes[1, 0].set_yticks(y_pos)
axes[1, 0].set_yticklabels(quintile_distribution.index, fontsize=9)
axes[1, 0].set_title('Top 20 Products by Avg Income Quintile', fontsize=14, weight='bold')
axes[1, 0].set_xlabel('Average Income Quintile')
axes[1, 0].invert_yaxis()
axes[1, 0].axvline(x=3, color='red', linestyle='--', alpha=0.5, label='Middle Income (Q3)')
axes[1, 0].legend()

# 4. Revenue contribution (Pareto chart)
cumulative_revenue = product_metrics['Total_Revenue'].cumsum()
cumulative_pct = (cumulative_revenue / cumulative_revenue.iloc[-1]) * 100
axes[1, 1].plot(range(1, min(51, len(cumulative_pct)+1)), cumulative_pct[:50], marker='o', color='steelblue')
axes[1, 1].axhline(y=80, color='red', linestyle='--', alpha=0.5, label='80% Revenue')
axes[1, 1].set_title('Pareto Chart: Revenue Concentration', fontsize=14, weight='bold')
axes[1, 1].set_xlabel('Number of Products (Ranked)')
axes[1, 1].set_ylabel('Cumulative Revenue %')
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].legend()

plt.tight_layout()
plt.savefig(analysis_dir / '05_product_performance.png', dpi=300, bbox_inches='tight')
print("[OK] Saved visualization: docs/analysis/05_product_performance.png")
print()

# Business insights
top_product = product_metrics.index[0]
top_product_revenue = product_metrics.iloc[0]['Total_Revenue']

# Calculate 80/20 rule
products_for_80pct = (cumulative_pct <= 80).sum()
pct_products_for_80pct = (products_for_80pct / len(product_metrics)) * 100

print("💡 BUSINESS INSIGHTS:")
print(f"   • Best-selling product: {top_product} (ILS {top_product_revenue:,.2f})")
print(f"   • 80/20 Rule: {products_for_80pct} products ({pct_products_for_80pct:.1f}%) generate 80% of revenue")
print()
print("📈 RECOMMENDATIONS FOR BUSINESSES:")
print(f"   • Focus inventory investment on top {products_for_80pct} SKUs")
print("   • High-volume products → Competitive pricing, supply chain efficiency")
print("   • Low-volume, high-margin products → Premium positioning")
print("   • Cross-sell complementary products within categories")
print()

print("="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print()
print("Generated 5 professional visualizations:")
print("  1. docs/analysis/01_quintile_analysis.png")
print("  2. docs/analysis/02_category_performance.png")
print("  3. docs/analysis/03_geographic_analysis.png")
print("  4. docs/analysis/04_temporal_analysis.png")
print("  5. docs/analysis/05_product_performance.png")
print()
