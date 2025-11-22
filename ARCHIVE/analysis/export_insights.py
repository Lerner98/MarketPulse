"""
Export Business Insights to JSON for API Consumption

This script generates structured JSON containing all business insights
discovered during EDA analysis. The JSON can be consumed by:
- API endpoints
- Frontend dashboards
- Business intelligence tools
"""

import sys
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def generate_insights():
    """Generate comprehensive business insights from cleaned data"""

    print("="*70)
    print("EXPORTING BUSINESS INSIGHTS TO JSON")
    print("="*70)
    print()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data' / 'processed'

    # Load cleaned data
    print("Loading cleaned transaction data...")
    df = pd.read_csv(data_dir / 'transactions_cleaned.csv')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    print(f"[+] Loaded {len(df):,} transactions")
    print()

    # Generate insights
    print("Generating business insights...")

    insights = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'data_source': 'Israeli Central Bureau of Statistics',
            'analysis_period': '2024',
            'version': '1.0'
        },

        'data_summary': {
            'total_transactions': int(len(df)),
            'total_volume': float(df['amount'].sum()),
            'average_transaction': float(df['amount'].mean()),
            'median_transaction': float(df['amount'].median()),
            'date_range': {
                'start': df['transaction_date'].min().isoformat(),
                'end': df['transaction_date'].max().isoformat()
            },
            'unique_products': int(df['product'].nunique()),
            'unique_categories': int(df['category'].nunique()),
            'unique_cities': int(df['customer_city'].nunique())
        },

        'income_quintile_analysis': {
            'quintile_1': {
                'total_spending': float(df[df['income_quintile']==1]['amount'].sum()),
                'avg_transaction': float(df[df['income_quintile']==1]['amount'].mean()),
                'transaction_count': int(len(df[df['income_quintile']==1])),
                'percentage_of_total': float((df[df['income_quintile']==1]['amount'].sum() / df['amount'].sum()) * 100)
            },
            'quintile_2': {
                'total_spending': float(df[df['income_quintile']==2]['amount'].sum()),
                'avg_transaction': float(df[df['income_quintile']==2]['amount'].mean()),
                'transaction_count': int(len(df[df['income_quintile']==2])),
                'percentage_of_total': float((df[df['income_quintile']==2]['amount'].sum() / df['amount'].sum()) * 100)
            },
            'quintile_3': {
                'total_spending': float(df[df['income_quintile']==3]['amount'].sum()),
                'avg_transaction': float(df[df['income_quintile']==3]['amount'].mean()),
                'transaction_count': int(len(df[df['income_quintile']==3])),
                'percentage_of_total': float((df[df['income_quintile']==3]['amount'].sum() / df['amount'].sum()) * 100)
            },
            'quintile_4': {
                'total_spending': float(df[df['income_quintile']==4]['amount'].sum()),
                'avg_transaction': float(df[df['income_quintile']==4]['amount'].mean()),
                'transaction_count': int(len(df[df['income_quintile']==4])),
                'percentage_of_total': float((df[df['income_quintile']==4]['amount'].sum() / df['amount'].sum()) * 100)
            },
            'quintile_5': {
                'total_spending': float(df[df['income_quintile']==5]['amount'].sum()),
                'avg_transaction': float(df[df['income_quintile']==5]['amount'].mean()),
                'transaction_count': int(len(df[df['income_quintile']==5])),
                'percentage_of_total': float((df[df['income_quintile']==5]['amount'].sum() / df['amount'].sum()) * 100)
            },
            'key_insight': f"High-income households (Q5) spend {df[df['income_quintile']==5]['amount'].mean() / df[df['income_quintile']==1]['amount'].mean():.2f}x more per transaction than low-income (Q1)"
        },

        'top_categories': {
            category: float(revenue)
            for category, revenue in df.groupby('category')['amount'].sum().sort_values(ascending=False).head(10).items()
        },

        'top_products': {
            product: float(revenue)
            for product, revenue in df.groupby('product')['amount'].sum().sort_values(ascending=False).head(20).items()
        },

        'top_cities': {
            city: {
                'total_spending': float(df[df['customer_city']==city]['amount'].sum()),
                'avg_transaction': float(df[df['customer_city']==city]['amount'].mean()),
                'transaction_count': int(len(df[df['customer_city']==city])),
                'market_share_pct': float((df[df['customer_city']==city]['amount'].sum() / df['amount'].sum()) * 100)
            }
            for city in df['customer_city'].value_counts().head(10).index
        },

        'monthly_trend': {
            int(month): float(spending)
            for month, spending in df.groupby(df['transaction_date'].dt.month)['amount'].sum().items()
        },

        'seasonal_insights': {
            'peak_month': int(df.groupby(df['transaction_date'].dt.month)['amount'].sum().idxmax()),
            'low_month': int(df.groupby(df['transaction_date'].dt.month)['amount'].sum().idxmin()),
            'peak_spending': float(df.groupby(df['transaction_date'].dt.month)['amount'].sum().max()),
            'low_spending': float(df.groupby(df['transaction_date'].dt.month)['amount'].sum().min()),
            'seasonal_variation_pct': float(((df.groupby(df['transaction_date'].dt.month)['amount'].sum().max() / df.groupby(df['transaction_date'].dt.month)['amount'].sum().min()) - 1) * 100)
        },

        'pareto_analysis': {
            'products_for_80pct_revenue': int((df.groupby('product')['amount'].sum().sort_values(ascending=False).cumsum() / df['amount'].sum() <= 0.8).sum()),
            'total_products': int(df['product'].nunique()),
            'concentration_ratio': float((df.groupby('product')['amount'].sum().sort_values(ascending=False).cumsum() / df['amount'].sum() <= 0.8).sum() / df['product'].nunique() * 100)
        },

        'business_recommendations': [
            "Focus on Tel Aviv (32.4%), Jerusalem (15.1%), and Haifa (11.5%) for 60%+ of market coverage",
            "Develop tiered product strategy: value products for Q1-Q2, premium for Q4-Q5",
            "Plan inventory around Jewish holiday calendar - peak in October (Rosh Hashanah), low in July-August",
            "Top 33% of products generate 80% of revenue - optimize inventory investment accordingly",
            "High-income households (Q4-Q5) account for 48.9% of total spending despite being 40% of population",
            "Food & Beverages category (17.2% of market) - consider subscription models and home delivery",
            "Education & Culture has highest average transaction (ILS 454) - premium positioning opportunity",
            "Mobile-first approach critical - optimize for Israeli mobile shopping behavior",
            "Kosher certification is table-stakes in Jerusalem market (15.1% market share)",
            "Summer months (July-August) show 89% drop from peak - adjust operations accordingly"
        ],

        'key_metrics': {
            'market_concentration': {
                'top_city_share': float((df.groupby('customer_city')['amount'].sum().max() / df['amount'].sum()) * 100),
                'top_3_cities_share': float((df.groupby('customer_city')['amount'].sum().nlargest(3).sum() / df['amount'].sum()) * 100),
                'top_category_share': float((df.groupby('category')['amount'].sum().max() / df['amount'].sum()) * 100),
                'top_3_categories_share': float((df.groupby('category')['amount'].sum().nlargest(3).sum() / df['amount'].sum()) * 100)
            },
            'income_disparity': {
                'q5_to_q1_ratio': float(df[df['income_quintile']==5]['amount'].mean() / df[df['income_quintile']==1]['amount'].mean()),
                'high_income_share': float(((df[df['income_quintile']>=4]['amount'].sum()) / df['amount'].sum()) * 100),
                'low_income_share': float(((df[df['income_quintile']<=2]['amount'].sum()) / df['amount'].sum()) * 100)
            }
        }
    }

    # Save to JSON
    output_file = data_dir / 'business_insights.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(insights, f, ensure_ascii=False, indent=2)

    print(f"[+] Exported business insights to: {output_file}")
    print()

    # Print summary
    print("="*70)
    print("INSIGHTS SUMMARY")
    print("="*70)
    print()
    print(f"Total Volume: ILS {insights['data_summary']['total_volume']:,.2f}")
    print(f"Average Transaction: ILS {insights['data_summary']['average_transaction']:.2f}")
    print(f"Unique Products: {insights['data_summary']['unique_products']}")
    print(f"Unique Categories: {insights['data_summary']['unique_categories']}")
    print()
    print("Top 3 Cities:")
    for i, (city, data) in enumerate(list(insights['top_cities'].items())[:3], 1):
        print(f"  {i}. {city}: ILS {data['total_spending']:,.2f} ({data['market_share_pct']:.1f}%)")
    print()
    print("Top 3 Categories:")
    for i, (category, revenue) in enumerate(list(insights['top_categories'].items())[:3], 1):
        pct = (revenue / insights['data_summary']['total_volume']) * 100
        print(f"  {i}. {category}: ILS {revenue:,.2f} ({pct:.1f}%)")
    print()
    print("Income Quintile Distribution:")
    for q in [1, 2, 3, 4, 5]:
        data = insights['income_quintile_analysis'][f'quintile_{q}']
        print(f"  Q{q}: ILS {data['total_spending']:,.2f} ({data['percentage_of_total']:.1f}%) - Avg: ILS {data['avg_transaction']:.2f}")
    print()
    print("="*70)
    print("EXPORT COMPLETE")
    print("="*70)

    return insights

if __name__ == "__main__":
    insights = generate_insights()
