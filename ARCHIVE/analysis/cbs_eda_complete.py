"""
Phase 4: Complete Exploratory Data Analysis & Business Intelligence
CBS Household Expenditure Analysis

This script performs comprehensive EDA on cleaned CBS data and generates:
- Statistical analysis
- Professional visualizations
- Business insights
- Strategic recommendations
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import json

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

# Setup paths
project_root = Path(__file__).parent.parent.parent
data_dir = project_root / 'data' / 'processed'
analysis_dir = project_root / 'docs' / 'analysis'
analysis_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("CBS HOUSEHOLD EXPENDITURE ANALYSIS")
print("Phase 4: Exploratory Data Analysis & Business Intelligence")
print("Data Source: Israeli Central Bureau of Statistics")
print("="*70)
print()

# Load cleaned data
print("Loading cleaned transaction data...")
df = pd.read_csv(data_dir / 'transactions_cleaned.csv')
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
print(f"[+] Loaded {len(df):,} transactions")
print()

# ============================================================================
# SECTION 1: Dataset Overview
# ============================================================================

print("="*70)
print("SECTION 1: DATASET OVERVIEW")
print("="*70)
print()

print(f"📊 BASIC STATISTICS")
print(f"Total Transactions: {len(df):,}")
print(f"Date Range: {df['transaction_date'].min().date()} to {df['transaction_date'].max().date()}")
print(f"Unique Products: {df['product'].nunique()}")
print(f"Unique Categories: {df['category'].nunique()}")
print(f"Cities Covered: {df['customer_city'].nunique()}")
print(f"Total Volume: ILS {df['amount'].sum():,.2f}")
print(f"Average Transaction: ILS {df['amount'].mean():.2f}")
print(f"Median Transaction: ILS {df['amount'].median():.2f}")
print()

print(f"📋 DATA STRUCTURE")
print(df.dtypes)
print()

print(f"📊 SAMPLE TRANSACTIONS (First 5):")
print(df.head(5).to_string())
print()

# ============================================================================
# SECTION 2: Income Quintile Analysis
# ============================================================================

print("="*70)
print("SECTION 2: INCOME QUINTILE ANALYSIS")
print("Business Question: How do spending patterns differ across income groups?")
print("="*70)
print()

# Calculate spending by quintile
quintile_spending = df.groupby('income_quintile').agg({
    'amount': ['sum', 'mean', 'median', 'count'],
    'transaction_id': 'nunique'
}).round(2)

quintile_spending.columns = ['Total_Spending', 'Avg_Transaction', 'Median_Transaction', 'Transaction_Count', 'Unique_Transactions']

print("📊 SPENDING PATTERNS BY INCOME QUINTILE:")
print(quintile_spending)
print()

# Generate visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. Total spending by quintile
quintile_totals = df.groupby('income_quintile')['amount'].sum()
axes[0, 0].bar(quintile_totals.index, quintile_totals.values, color='steelblue', edgecolor='black')
axes[0, 0].set_title('Total Spending by Income Quintile', fontsize=14, weight='bold')
axes[0, 0].set_xlabel('Income Quintile (1=Lowest, 5=Highest)')
axes[0, 0].set_ylabel('Total Spending (ILS)')
axes[0, 0].set_xticks([1, 2, 3, 4, 5])
for i, v in enumerate(quintile_totals.values, 1):
    axes[0, 0].text(i, v, f'ILS {v:,.0f}', ha='center', va='bottom')

# 2. Average transaction size by quintile
quintile_avg = df.groupby('income_quintile')['amount'].mean()
axes[0, 1].bar(quintile_avg.index, quintile_avg.values, color='coral', edgecolor='black')
axes[0, 1].set_title('Average Transaction Size by Quintile', fontsize=14, weight='bold')
axes[0, 1].set_xlabel('Income Quintile')
axes[0, 1].set_ylabel('Average Amount (ILS)')
axes[0, 1].set_xticks([1, 2, 3, 4, 5])
for i, v in enumerate(quintile_avg.values, 1):
    axes[0, 1].text(i, v, f'ILS {v:.0f}', ha='center', va='bottom')

# 3. Transaction count by quintile
quintile_count = df.groupby('income_quintile').size()
axes[1, 0].bar(quintile_count.index, quintile_count.values, color='lightgreen', edgecolor='black')
axes[1, 0].set_title('Transaction Frequency by Quintile', fontsize=14, weight='bold')
axes[1, 0].set_xlabel('Income Quintile')
axes[1, 0].set_ylabel('Number of Transactions')
axes[1, 0].set_xticks([1, 2, 3, 4, 5])
for i, v in enumerate(quintile_count.values, 1):
    axes[1, 0].text(i, v, f'{v:,}', ha='center', va='bottom')

# 4. Spending distribution (box plot)
df.boxplot(column='amount', by='income_quintile', ax=axes[1, 1])
axes[1, 1].set_title('Spending Distribution by Quintile', fontsize=14, weight='bold')
axes[1, 1].set_xlabel('Income Quintile')
axes[1, 1].set_ylabel('Transaction Amount (ILS)')
plt.sca(axes[1, 1])
plt.xticks([1, 2, 3, 4, 5])

plt.tight_layout()
plt.savefig(analysis_dir / '01_quintile_analysis.png', dpi=300, bbox_inches='tight')
print("[OK] Saved visualization: docs/analysis/01_quintile_analysis.png")
print()

# Business insights
q5_avg = df[df['income_quintile']==5]['amount'].mean()
q1_avg = df[df['income_quintile']==1]['amount'].mean()
ratio = q5_avg / q1_avg

print("💡 BUSINESS INSIGHTS:")
print(f"   • High-income households (Q5) spend {ratio:.2f}x more per transaction than low-income (Q1)")
print(f"   • Average Q5 transaction: ILS {q5_avg:.2f}")
print(f"   • Average Q1 transaction: ILS {q1_avg:.2f}")
print()
print("📈 RECOMMENDATIONS FOR BUSINESSES:")
print("   • Premium products → Target Q4-Q5 (higher spending power)")
print("   • Value/budget products → Target Q1-Q2 (price-sensitive)")
print("   • Mid-range products → Target Q3 (balanced market)")
print()

# ============================================================================
# SECTION 3: Category Performance Analysis
# ============================================================================

print("="*70)
print("SECTION 3: CATEGORY PERFORMANCE ANALYSIS")
print("Business Question: Which product categories drive the most revenue?")
print("="*70)
print()

# Calculate category metrics
category_metrics = df.groupby('category').agg({
    'amount': ['sum', 'mean', 'count'],
    'transaction_id': 'nunique'
}).round(2)

category_metrics.columns = ['Total_Revenue', 'Avg_Transaction', 'Transaction_Count', 'Unique_Transactions']
category_metrics = category_metrics.sort_values('Total_Revenue', ascending=False)

print("📊 TOP 10 CATEGORIES BY REVENUE:")
print(category_metrics.head(10).to_string())
print()

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Top 10 categories by revenue
top_10_revenue = category_metrics.head(10)['Total_Revenue']
y_pos = np.arange(len(top_10_revenue))
axes[0, 0].barh(y_pos, top_10_revenue.values, color='steelblue', edgecolor='black')
axes[0, 0].set_yticks(y_pos)
axes[0, 0].set_yticklabels(top_10_revenue.index)
axes[0, 0].set_title('Top 10 Categories by Revenue', fontsize=14, weight='bold')
axes[0, 0].set_xlabel('Total Revenue (ILS)')
axes[0, 0].invert_yaxis()

# 2. Revenue distribution (pie chart for top 5)
top_5_revenue = category_metrics.head(5)['Total_Revenue']
other_revenue = category_metrics.iloc[5:]['Total_Revenue'].sum()
pie_labels = list(top_5_revenue.index) + ['Others']
pie_data = list(top_5_revenue.values) + [other_revenue]
axes[0, 1].pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90)
axes[0, 1].set_title('Revenue Share: Top 5 vs. Others', fontsize=14, weight='bold')

# 3. Average transaction size by category (top 10)
top_10_avg = category_metrics.head(10)['Avg_Transaction']
y_pos = np.arange(len(top_10_avg))
axes[1, 0].barh(y_pos, top_10_avg.values, color='coral', edgecolor='black')
axes[1, 0].set_yticks(y_pos)
axes[1, 0].set_yticklabels(top_10_avg.index)
axes[1, 0].set_title('Top 10 Categories by Avg Transaction Size', fontsize=14, weight='bold')
axes[1, 0].set_xlabel('Average Amount (ILS)')
axes[1, 0].invert_yaxis()

# 4. Transaction frequency by category (top 10)
top_10_count = category_metrics.head(10)['Transaction_Count']
y_pos = np.arange(len(top_10_count))
axes[1, 1].barh(y_pos, top_10_count.values, color='lightgreen', edgecolor='black')
axes[1, 1].set_yticks(y_pos)
axes[1, 1].set_yticklabels(top_10_count.index)
axes[1, 1].set_title('Top 10 Categories by Transaction Frequency', fontsize=14, weight='bold')
axes[1, 1].set_xlabel('Number of Transactions')
axes[1, 1].invert_yaxis()

plt.tight_layout()
plt.savefig(analysis_dir / '02_category_performance.png', dpi=300, bbox_inches='tight')
print("[OK] Saved visualization: docs/analysis/02_category_performance.png")
print()

# Business insights
top_category = category_metrics.index[0]
top_revenue = category_metrics.iloc[0]['Total_Revenue']
top_pct = (top_revenue / df['amount'].sum()) * 100

print("💡 BUSINESS INSIGHTS:")
print(f"   • Largest category: {top_category} (ILS {top_revenue:,.2f}, {top_pct:.1f}% of total)")
top3_pct = ((category_metrics.head(3)['Total_Revenue'].sum() / df['amount'].sum()) * 100)
print(f"   • Top 3 categories account for {top3_pct:.1f}% of spending")
print()

# Continue in next message due to length...
