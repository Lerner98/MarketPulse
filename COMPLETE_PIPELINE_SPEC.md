# MarketPulse: Professional Data Engineering Pipeline
## Complete Specification for Israeli Tech Recruiters

---

## 🎯 PROJECT PURPOSE

**NOT A TOY DASHBOARD. THIS IS A PROFESSIONAL DATA ENGINEERING SHOWCASE.**

**What Recruiters Want to See:**
1. ✅ Complex data extraction from messy government sources
2. ✅ Professional ETL pipeline with quality monitoring
3. ✅ Real data cleaning challenges solved
4. ✅ Statistical analysis producing business insights
5. ✅ Production-ready code architecture

**What We're Demonstrating:**
- "I can take REAL messy Israeli government data (CBS household expenditure surveys)"
- "I can build a complete ETL pipeline that cleans and transforms it"
- "I can generate meaningful analytics about Israeli consumer behavior"
- "I can present it professionally with Hebrew RTL support"

---

## 📊 DATA SOURCE: Israeli CBS Household Expenditure Surveys

### **What We Have:**

**Primary Data Files:**
```
1. הוצאות_לתצרוכת_למשק_בית_מוצרים_מפורטים.xlsx
   - Detailed product-level expenditure
   - 500+ product categories
   - Hebrew product names
   - Complex multi-row headers
   
2. הרכב_הוצאה_לתצרוכת__לפי_קבוצות_משניות__שנים_נבחרות.xlsx
   - Multi-year consumption trends
   - Category breakdowns
   - Seasonal patterns
   
3. ta01_01.xlsx - Income & expenditure by quintile
   - Q1 (poorest 20%): ₪9,751/month average
   - Q2: ₪17,630/month
   - Q3: ₪24,629/month
   - Q4: ₪26,884/month
   - Q5 (richest 20%): ₪20,546/month
   
4. ta10.xlsx - Geographic breakdown
   - Tel Aviv district
   - Jerusalem district
   - Haifa district
   - Beer Sheva district
   - Other regions
   
5. ta11.xlsx, ta12.xlsx - Demographic dimensions
   - Family size
   - Country of origin
   - Employment status
   
6. unified_businesses.csv
   - 3,056 real Israeli businesses
   - Hebrew names
   - Geographic coordinates
   - Business categories
```

### **Data Characteristics (WHY THIS IS HARD):**
```
❌ Multi-row headers (3-7 rows before actual data)
❌ Bilingual columns (Hebrew + English mixed)
❌ Merged cells in Excel
❌ Error margins embedded (±X.X values)
❌ Mixed data types in same column
❌ Footnotes in data cells
❌ Inconsistent Hebrew encoding
❌ Statistical aggregates mixed with raw data
❌ Non-standard Excel structure
```

**This is REAL messy government data. Perfect for showcasing skills.**

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA ENGINEERING PIPELINE                │
└─────────────────────────────────────────────────────────────┘

Phase 1: EXTRACTION (Complex Excel Parsing)
├── Read CBS Excel files (handle multi-headers)
├── Parse bilingual columns
├── Extract Hebrew product names
├── Handle merged cells
└── Document: 500+ categories from government data
    ↓
Phase 2: TRANSFORMATION (CBS Stats → Individual Transactions)
├── Map categories to products
│   ├── מזון (Food) → specific food items
│   ├── דיור (Housing) → furniture, appliances
│   ├── תחבורה (Transport) → vehicle parts
│   └── etc.
├── Apply spending patterns by income quintile
│   ├── Q1 spends more on essentials (60% food)
│   ├── Q5 spends more on discretionary (30% electronics)
│   └── Realistic distributions
├── Apply geographic distributions
│   ├── Tel Aviv: 30% (higher income)
│   ├── Jerusalem: 15%
│   ├── Haifa: 12%
│   ├── Beer Sheva: 8%
│   └── Other: 35%
├── Generate 10,000 individual transactions
│   ├── Customer: Hebrew name from business registry
│   ├── Product: Hebrew name from CBS categories
│   ├── Amount: From CBS spending averages (±variance)
│   ├── Date: 2024 with Israeli seasonality
│   │   ├── Rosh Hashanah spike (September)
│   │   ├── Passover spike (April)
│   │   └── Summer dip (July-August)
│   └── City: From geographic distribution
└── Inject data quality issues (CRITICAL FOR SHOWCASE)
    ├── 5% missing values (random NULLs)
    ├── 3% duplicate records
    ├── 2% outliers (10x normal amounts)
    ├── Mixed date formats
    └── Hebrew encoding issues
    ↓
Phase 3: LOADING (Database with Quality Metrics)
├── Create PostgreSQL tables
├── Load transactions
├── Track data quality metrics
└── Create indexes
    ↓
Phase 4: DATA QUALITY LAYER (THE SHOWCASE)
├── Detection:
│   ├── Missing value report
│   ├── Duplicate detection
│   ├── Outlier analysis
│   └── Format inconsistencies
├── Cleaning:
│   ├── Imputation strategies
│   ├── Deduplication logic
│   ├── Outlier handling
│   └── Standardization
└── Reporting:
    ├── Before/after statistics
    ├── Quality score (0-100)
    └── Cleaning actions log
    ↓
Phase 5: ANALYTICS ENGINE (Business Intelligence)
├── Revenue analysis
│   ├── Growth trends
│   ├── Anomaly detection
│   └── Forecasting
├── Customer segmentation
│   ├── Income quintile behavior
│   ├── Geographic patterns
│   └── RFM analysis
├── Product performance
│   ├── Category analysis
│   ├── Cross-sell opportunities
│   └── Trend detection
└── Statistical insights
    ├── Correlation discovery
    ├── Seasonal patterns
    └── Actionable recommendations
    ↓
Phase 6: API & FRONTEND (Professional Presentation)
├── FastAPI backend
│   ├── /api/dashboard - Metrics
│   ├── /api/revenue - Time series
│   ├── /api/customers - Segmented
│   ├── /api/products - Analyzed
│   └── /api/data-quality - Quality report
└── React frontend (Hebrew RTL)
    ├── Dashboard with insights
    ├── Data quality report
    ├── Interactive charts
    └── Professional design
```

---

## 📋 DETAILED IMPLEMENTATION PLAN

### **PHASE 1: DATA EXTRACTION (2-3 hours)**

#### **1.1 CBS Excel Parser**

**File:** `etl/extract_cbs.py`

```python
"""
Professional CBS Excel Extractor
Handles complex government data structure
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class CBSExcelParser:
    """
    Parse Israeli CBS household expenditure Excel files
    with complex multi-header structure
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.categories = {}
        self.quintiles = {}
        self.geographic = {}
        
    def detect_header_row(self, filepath: Path) -> int:
        """
        Intelligently detect where actual data starts
        CBS files have 3-7 header rows before data
        """
        df = pd.read_excel(filepath, nrows=10)
        
        # Look for first row with all non-null values
        for idx, row in df.iterrows():
            if row.notna().sum() > len(row) * 0.7:  # 70% non-null
                return idx
        
        return 0  # Fallback
    
    def extract_product_categories(self) -> pd.DataFrame:
        """
        Extract detailed product categories from CBS file
        Returns: DataFrame with Hebrew category names and spending amounts
        """
        filepath = self.data_dir / "הוצאות_לתצרוכת_למשק_בית_מוצרים_מפורטים.xlsx"
        
        # Detect header row
        skip_rows = self.detect_header_row(filepath)
        logger.info(f"Detected header at row {skip_rows}")
        
        # Read with proper header
        df = pd.read_excel(
            filepath,
            skiprows=skip_rows,
            engine='openpyxl'
        )
        
        # Extract bilingual columns (Hebrew + English)
        hebrew_cols = [col for col in df.columns if self._is_hebrew(col)]
        english_cols = [col for col in df.columns if not self._is_hebrew(col)]
        
        # Clean column names
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # Remove error margins (±X.X values)
        df = self._remove_error_margins(df)
        
        # Extract categories and average spending
        categories = []
        for _, row in df.iterrows():
            if pd.notna(row.get('category')) and pd.notna(row.get('amount')):
                categories.append({
                    'category_hebrew': row['category'],
                    'category_english': row.get('category_en', ''),
                    'avg_monthly_spending': float(row['amount']),
                    'households_surveyed': int(row.get('households', 0))
                })
        
        logger.info(f"Extracted {len(categories)} product categories")
        return pd.DataFrame(categories)
    
    def extract_income_quintiles(self) -> pd.DataFrame:
        """
        Extract spending patterns by income quintile
        Returns: DataFrame with Q1-Q5 spending distributions
        """
        filepath = self.data_dir / "ta01_01.xlsx"
        skip_rows = self.detect_header_row(filepath)
        
        df = pd.read_excel(filepath, skiprows=skip_rows)
        
        # Extract quintile data (columns for Q1-Q5)
        quintiles = []
        for q in range(1, 6):
            col_name = f'quintile_{q}'
            if col_name in df.columns:
                avg_income = df[df['metric'] == 'average_income'][col_name].values[0]
                avg_spending = df[df['metric'] == 'total_expenditure'][col_name].values[0]
                
                # Category breakdowns
                food_pct = df[df['metric'] == 'food_beverages'][col_name].values[0]
                housing_pct = df[df['metric'] == 'housing'][col_name].values[0]
                transport_pct = df[df['metric'] == 'transport'][col_name].values[0]
                
                quintiles.append({
                    'quintile': q,
                    'avg_income': avg_income,
                    'avg_spending': avg_spending,
                    'food_pct': food_pct,
                    'housing_pct': housing_pct,
                    'transport_pct': transport_pct
                })
        
        logger.info(f"Extracted {len(quintiles)} income quintiles")
        return pd.DataFrame(quintiles)
    
    def extract_geographic_distribution(self) -> pd.DataFrame:
        """
        Extract geographic spending patterns
        Returns: DataFrame with district-level data
        """
        filepath = self.data_dir / "ta10.xlsx"
        skip_rows = self.detect_header_row(filepath)
        
        df = pd.read_excel(filepath, skiprows=skip_rows)
        
        # Extract districts
        districts = []
        for _, row in df.iterrows():
            if pd.notna(row.get('district')):
                districts.append({
                    'district_hebrew': row['district'],
                    'avg_spending': row['total_expenditure'],
                    'population_pct': row['population_percentage']
                })
        
        logger.info(f"Extracted {len(districts)} geographic districts")
        return pd.DataFrame(districts)
    
    def extract_business_registry(self) -> pd.DataFrame:
        """
        Extract real Israeli businesses for product name mapping
        Returns: DataFrame with business names and categories
        """
        filepath = self.data_dir / "unified_businesses.csv"
        
        df = pd.read_csv(filepath, encoding='utf-8')
        
        # Clean and categorize businesses
        businesses = df[[
            'business_name',
            'business_kind',
            'full_address',
            'location_lat',
            'location_lng'
        ]].copy()
        
        # Map business types to CBS categories
        businesses['cbs_category'] = businesses['business_kind'].apply(
            self._map_business_to_category
        )
        
        logger.info(f"Extracted {len(businesses)} businesses")
        return businesses
    
    def _is_hebrew(self, text: str) -> bool:
        """Check if text contains Hebrew characters"""
        return bool(re.search('[\u0590-\u05FF]', str(text)))
    
    def _clean_column_name(self, col: str) -> str:
        """Clean column names (remove special chars, normalize)"""
        # Implementation
        pass
    
    def _remove_error_margins(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove ±X.X error margin values from data"""
        # Implementation
        pass
    
    def _map_business_to_category(self, business_kind: str) -> str:
        """Map business type to CBS expenditure category"""
        mapping = {
            'מזון': ['מחסן אחסנה בקירור', 'מפעל לייצור מזון'],
            'דיור': ['נגריה', 'שיש מכירה'],
            'אלקטרוניקה': ['מכשירי חשמל'],
            # ... full mapping
        }
        # Implementation
        pass

# Usage
parser = CBSExcelParser(Path('data/raw/cbs_household_survey'))
categories = parser.extract_product_categories()
quintiles = parser.extract_income_quintiles()
geographic = parser.extract_geographic_distribution()
businesses = parser.extract_business_registry()
```

#### **1.2 Data Extraction Report**

**Generate:** `docs/01_EXTRACTION_REPORT.md`

```markdown
# Data Extraction Report

## Source: Israeli Central Bureau of Statistics
## Survey: Household Income and Expenditure 2022

### Files Processed:
1. ✅ הוצאות_לתצרוכת_למשק_בית_מוצרים_מפורטים.xlsx
   - Header detected at row: 5
   - Categories extracted: 523
   - Data quality: Complex structure handled

2. ✅ ta01_01.xlsx (Income Quintiles)
   - Quintiles extracted: 5
   - Spending patterns captured
   
3. ✅ ta10.xlsx (Geographic)
   - Districts extracted: 15
   - Population distribution captured

4. ✅ unified_businesses.csv
   - Businesses extracted: 3,056
   - Categories mapped: 8 major groups

### Extraction Challenges Overcome:
- Multi-row headers (3-7 rows)
- Bilingual column detection
- Merged cell parsing
- Error margin removal
- Encoding normalization

### Extracted Data Summary:
- Product categories: 523
- Income quintiles: 5 (Q1: ₪9,751 → Q5: ₪20,546)
- Geographic regions: 15 districts
- Business names: 3,056 real Israeli businesses
```

---

### **PHASE 2: TRANSFORMATION (3-4 hours)**

#### **2.1 Transaction Generator**

**File:** `etl/transform_transactions.py`

```python
"""
Transform CBS statistical aggregates into individual transactions
Applies realistic spending patterns and generates 10,000 transactions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TransactionGenerator:
    """
    Generate realistic individual transactions from CBS aggregate data
    """
    
    def __init__(
        self,
        categories: pd.DataFrame,
        quintiles: pd.DataFrame,
        geographic: pd.DataFrame,
        businesses: pd.DataFrame
    ):
        self.categories = categories
        self.quintiles = quintiles
        self.geographic = geographic
        self.businesses = businesses
        
        # Israeli holiday dates for seasonality
        self.holidays = {
            'rosh_hashanah': datetime(2024, 9, 16),
            'yom_kippur': datetime(2024, 9, 25),
            'sukkot': datetime(2024, 9, 30),
            'passover': datetime(2024, 4, 22),
            'shavuot': datetime(2024, 6, 12),
        }
    
    def generate(self, n_transactions: int = 10000) -> pd.DataFrame:
        """
        Generate n individual transactions based on CBS patterns
        """
        logger.info(f"Generating {n_transactions} transactions...")
        
        transactions = []
        for i in range(n_transactions):
            # 1. Select income quintile (weighted by population)
            quintile = self._select_quintile()
            
            # 2. Select category based on quintile spending patterns
            category = self._select_category(quintile)
            
            # 3. Select specific product from category
            product = self._select_product(category)
            
            # 4. Calculate amount (CBS average ± realistic variance)
            amount = self._calculate_amount(category, quintile)
            
            # 5. Generate date with Israeli seasonality
            date = self._generate_date()
            
            # 6. Select customer city from geographic distribution
            city = self._select_city()
            
            # 7. Generate Hebrew customer name
            customer_name = self._generate_customer_name()
            
            # 8. Set status (92% completed, 5% pending, 3% cancelled)
            status = random.choices(
                ['completed', 'pending', 'cancelled'],
                weights=[92, 5, 3]
            )[0]
            
            transactions.append({
                'transaction_id': 10000 + i,
                'customer_name': customer_name,
                'product': product,
                'category': category,
                'amount': amount,
                'currency': 'ILS',
                'transaction_date': date,
                'status': status,
                'customer_city': city,
                'income_quintile': quintile
            })
        
        df = pd.DataFrame(transactions)
        logger.info(f"Generated {len(df)} transactions")
        
        return df
    
    def _select_quintile(self) -> int:
        """Select income quintile (weighted by population %)"""
        return random.choices(
            [1, 2, 3, 4, 5],
            weights=[20, 20, 20, 20, 20]  # Equal distribution
        )[0]
    
    def _select_category(self, quintile: int) -> str:
        """
        Select category based on quintile spending patterns
        Q1: More food/essentials
        Q5: More electronics/discretionary
        """
        quintile_data = self.quintiles[self.quintiles['quintile'] == quintile].iloc[0]
        
        # Weight categories by quintile preferences
        if quintile <= 2:  # Low income
            weights = {
                'מזון ומשקאות': 35,
                'דיור': 25,
                'תחבורה': 15,
                'הלבשה': 10,
                'בריאות': 8,
                'תרבות': 5,
                'אחר': 2
            }
        else:  # High income
            weights = {
                'מזון ומשקאות': 20,
                'דיור': 30,
                'תחבורה': 20,
                'הלבשה': 10,
                'בריאות': 5,
                'תרבות': 10,
                'אחר': 5
            }
        
        return random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
    
    def _select_product(self, category: str) -> str:
        """
        Select specific product from category
        Uses real business names from unified_businesses.csv
        """
        # Map category to business types
        category_businesses = self.businesses[
            self.businesses['cbs_category'] == category
        ]
        
        if len(category_businesses) > 0:
            # Use real business name as product
            business = category_businesses.sample(1).iloc[0]
            return business['business_name']
        else:
            # Fallback to CBS category name
            category_products = self.categories[
                self.categories['category_hebrew'].str.contains(category, na=False)
            ]
            if len(category_products) > 0:
                return category_products.sample(1).iloc[0]['category_hebrew']
            else:
                return category
    
    def _calculate_amount(self, category: str, quintile: int) -> float:
        """
        Calculate transaction amount based on CBS averages
        Apply quintile multiplier and random variance
        """
        # Get CBS average for category
        cat_data = self.categories[
            self.categories['category_hebrew'].str.contains(category, na=False)
        ]
        
        if len(cat_data) > 0:
            base_amount = cat_data.iloc[0]['avg_monthly_spending']
        else:
            base_amount = 1000  # Fallback
        
        # Quintile multiplier (Q1: 0.6x, Q5: 1.8x)
        quintile_multipliers = {1: 0.6, 2: 0.8, 3: 1.0, 4: 1.3, 5: 1.8}
        amount = base_amount * quintile_multipliers[quintile]
        
        # Add realistic variance (±30%)
        variance = random.uniform(0.7, 1.3)
        amount *= variance
        
        # Round to nearest 10
        return round(amount / 10) * 10
    
    def _generate_date(self) -> datetime:
        """
        Generate date in 2024 with Israeli seasonality
        Higher volume around holidays
        """
        # Random date in 2024
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        days = (end - start).days
        random_date = start + timedelta(days=random.randint(0, days))
        
        # Check if near holiday (boost probability)
        for holiday_name, holiday_date in self.holidays.items():
            days_to_holiday = abs((random_date - holiday_date).days)
            if days_to_holiday <= 7:  # Week before/after
                # 2x probability of transaction near holidays
                if random.random() < 0.5:
                    return random_date
        
        return random_date
    
    def _select_city(self) -> str:
        """
        Select customer city from geographic distribution
        """
        cities = {
            'תל אביב': 30,
            'ירושלים': 15,
            'חיפה': 12,
            'באר שבע': 8,
            'רחובות': 5,
            'פתח תקווה': 5,
            'ראשון לציון': 5,
            'נתניה': 5,
            'חולון': 5,
            'בני ברק': 5,
            'אחר': 5
        }
        
        return random.choices(
            list(cities.keys()),
            weights=list(cities.values())
        )[0]
    
    def _generate_customer_name(self) -> str:
        """
        Generate realistic Hebrew customer name
        """
        first_names = [
            'דוד', 'שרה', 'משה', 'רחל', 'יוסף', 'מרים',
            'אברהם', 'לאה', 'יעקב', 'שושנה', 'יצחק', 'רבקה'
        ]
        last_names = [
            'כהן', 'לוי', 'מזרחי', 'פרץ', 'ביטון', 'אברהם',
            'דוד', 'ישראל', 'חיים', 'גולן', 'אשכנזי', 'ספרדי'
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"

# Usage
generator = TransactionGenerator(categories, quintiles, geographic, businesses)
transactions = generator.generate(n_transactions=10000)
```

#### **2.2 Data Quality Issue Injection**

**File:** `etl/inject_quality_issues.py`

```python
"""
Inject realistic data quality issues to showcase cleaning pipeline
"""

import pandas as pd
import numpy as np
import random
from typing import List

class DataQualityInjector:
    """
    Deliberately inject data quality issues to demonstrate cleaning
    """
    
    def inject_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all quality issues"""
        df = self.inject_missing_values(df, rate=0.05)
        df = self.inject_duplicates(df, rate=0.03)
        df = self.inject_outliers(df, rate=0.02)
        df = self.inject_format_issues(df)
        df = self.inject_encoding_issues(df)
        
        return df
    
    def inject_missing_values(self, df: pd.DataFrame, rate: float) -> pd.DataFrame:
        """Randomly set 5% of values to NULL"""
        df_copy = df.copy()
        
        columns_to_affect = ['customer_name', 'product', 'amount', 'customer_city']
        
        for col in columns_to_affect:
            n_nulls = int(len(df) * rate)
            null_indices = random.sample(range(len(df)), n_nulls)
            df_copy.loc[null_indices, col] = None
        
        return df_copy
    
    def inject_duplicates(self, df: pd.DataFrame, rate: float) -> pd.DataFrame:
        """Add 3% exact duplicate rows"""
        n_duplicates = int(len(df) * rate)
        duplicate_indices = random.sample(range(len(df)), n_duplicates)
        duplicates = df.iloc[duplicate_indices].copy()
        
        return pd.concat([df, duplicates], ignore_index=True)
    
    def inject_outliers(self, df: pd.DataFrame, rate: float) -> pd.DataFrame:
        """Set 2% of amounts to 10x normal (data entry errors)"""
        df_copy = df.copy()
        
        n_outliers = int(len(df) * rate)
        outlier_indices = random.sample(range(len(df)), n_outliers)
        
        df_copy.loc[outlier_indices, 'amount'] *= 10
        
        return df_copy
    
    def inject_format_issues(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mix date formats, inconsistent formatting"""
        df_copy = df.copy()
        
        # Convert some dates to different formats
        for idx in random.sample(range(len(df)), int(len(df) * 0.1)):
            date = df_copy.loc[idx, 'transaction_date']
            # Mix ISO, DD/MM/YYYY, MM-DD-YYYY
            formats = [
                date.strftime('%Y-%m-%d'),
                date.strftime('%d/%m/%Y'),
                date.strftime('%m-%d-%Y'),
                date.strftime('%Y-%m-%d %H:%M:%S')  # With timestamp
            ]
            df_copy.loc[idx, 'transaction_date'] = random.choice(formats)
        
        return df_copy
    
    def inject_encoding_issues(self, df: pd.DataFrame) -> pd.DataFrame:
        """Introduce Hebrew encoding problems (mojibake)"""
        df_copy = df.copy()
        
        for idx in random.sample(range(len(df)), int(len(df) * 0.02)):
            # Simulate encoding issue
            text = df_copy.loc[idx, 'product']
            if isinstance(text, str) and any('\u0590' <= c <= '\u05FF' for c in text):
                # Replace with mojibake-like pattern
                df_copy.loc[idx, 'product'] = text.encode('utf-8').decode('windows-1255', errors='ignore')
        
        return df_copy

# Usage
injector = DataQualityInjector()
dirty_transactions = injector.inject_all(clean_transactions)
```

---

### **PHASE 3: DATA QUALITY PIPELINE (2-3 hours)**

#### **3.1 Quality Detector**

**File:** `etl/data_quality.py`

```python
"""
Professional data quality detection and reporting
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class DataQualityAnalyzer:
    """
    Detect and report data quality issues
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.report = {}
    
    def analyze(self) -> Dict:
        """Run all quality checks"""
        self.report = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': self._detect_missing(),
            'duplicates': self._detect_duplicates(),
            'outliers': self._detect_outliers(),
            'format_issues': self._detect_format_issues(),
            'encoding_issues': self._detect_encoding(),
            'quality_score': 0.0
        }
        
        # Calculate overall quality score (0-100)
        self.report['quality_score'] = self._calculate_quality_score()
        
        return self.report
    
    def _detect_missing(self) -> Dict:
        """Detect missing values"""
        missing = {}
        for col in self.df.columns:
            null_count = self.df[col].isna().sum()
            if null_count > 0:
                missing[col] = {
                    'count': int(null_count),
                    'percentage': float(null_count / len(self.df) * 100)
                }
        
        return missing
    
    def _detect_duplicates(self) -> Dict:
        """Detect duplicate rows"""
        duplicates = self.df[self.df.duplicated(keep=False)]
        
        return {
            'count': len(duplicates),
            'percentage': float(len(duplicates) / len(self.df) * 100),
            'duplicate_groups': int(len(duplicates) / 2) if len(duplicates) > 0 else 0
        }
    
    def _detect_outliers(self) -> Dict:
        """Detect statistical outliers in numeric columns"""
        outliers = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                outliers[col] = {
                    'count': int(outlier_count),
                    'percentage': float(outlier_count / len(self.df) * 100),
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'expected_range': f"{lower_bound:.2f} - {upper_bound:.2f}"
                }
        
        return outliers
    
    def _detect_format_issues(self) -> Dict:
        """Detect inconsistent date formats"""
        issues = {}
        
        # Check date column
        if 'transaction_date' in self.df.columns:
            unique_formats = self.df['transaction_date'].astype(str).apply(
                lambda x: self._infer_date_format(x)
            ).value_counts()
            
            if len(unique_formats) > 1:
                issues['transaction_date'] = {
                    'format_variations': dict(unique_formats),
                    'inconsistent': True
                }
        
        return issues
    
    def _detect_encoding(self) -> Dict:
        """Detect Hebrew encoding issues"""
        issues = {}
        
        text_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            problematic = self.df[col].apply(
                lambda x: isinstance(x, str) and '�' in x or '×' in str(x)
            ).sum()
            
            if problematic > 0:
                issues[col] = {
                    'count': int(problematic),
                    'percentage': float(problematic / len(self.df) * 100)
                }
        
        return issues
    
    def _calculate_quality_score(self) -> float:
        """
        Calculate overall quality score (0-100)
        Higher is better
        """
        penalties = 0
        
        # Missing values penalty
        if self.report['missing_values']:
            total_missing = sum(v['count'] for v in self.report['missing_values'].values())
            missing_rate = total_missing / (len(self.df) * len(self.df.columns))
            penalties += missing_rate * 30  # Max 30 points
        
        # Duplicates penalty
        dup_rate = self.report['duplicates']['percentage'] / 100
        penalties += dup_rate * 20  # Max 20 points
        
        # Outliers penalty
        if self.report['outliers']:
            total_outliers = sum(v['count'] for v in self.report['outliers'].values())
            outlier_rate = total_outliers / len(self.df)
            penalties += outlier_rate * 20  # Max 20 points
        
        # Format issues penalty
        if self.report['format_issues']:
            penalties += 15
        
        # Encoding issues penalty
        if self.report['encoding_issues']:
            penalties += 15
        
        score = max(0, 100 - penalties)
        return round(score, 2)
    
    def _infer_date_format(self, date_str: str) -> str:
        """Infer date format from string"""
        if '-' in date_str and ':' in date_str:
            return 'ISO_TIMESTAMP'
        elif '-' in date_str:
            return 'ISO_DATE'
        elif '/' in date_str:
            return 'DD/MM/YYYY'
        else:
            return 'UNKNOWN'
    
    def generate_report(self) -> str:
        """Generate markdown report"""
        report = f"""# Data Quality Report

## Overview
- Total Records: {self.report['total_rows']:,}
- Total Columns: {self.report['total_columns']}
- **Quality Score: {self.report['quality_score']}/100**

## Issues Detected

### Missing Values
{self._format_missing_report()}

### Duplicates
{self._format_duplicates_report()}

### Outliers
{self._format_outliers_report()}

### Format Issues
{self._format_format_report()}

### Encoding Issues
{self._format_encoding_report()}

## Recommendations
{self._generate_recommendations()}
"""
        return report
    
    def _format_missing_report(self) -> str:
        if not self.report['missing_values']:
            return "✅ No missing values detected"
        
        lines = []
        for col, data in self.report['missing_values'].items():
            lines.append(f"- **{col}**: {data['count']} ({data['percentage']:.2f}%)")
        return '\n'.join(lines)
    
    # Similar methods for other report sections...

# Usage
analyzer = DataQualityAnalyzer(dirty_transactions)
quality_report = analyzer.analyze()
print(analyzer.generate_report())
```

#### **3.2 Data Cleaner**

**File:** `etl/data_cleaner.py`

```python
"""
Professional data cleaning with documented strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Clean data quality issues with documented strategies
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.cleaning_log = []
    
    def clean_all(self) -> pd.DataFrame:
        """Execute all cleaning steps"""
        self.df = self.handle_missing_values()
        self.df = self.remove_duplicates()
        self.df = self.handle_outliers()
        self.df = self.standardize_formats()
        self.df = self.fix_encoding()
        
        return self.df
    
    def handle_missing_values(self) -> pd.DataFrame:
        """
        Imputation strategy:
        - Numeric: Median by category
        - Text: Mode by category
        - Critical fields: Drop row
        """
        df = self.df.copy()
        
        # customer_name: If missing, drop (critical field)
        before_count = len(df)
        df = df.dropna(subset=['customer_name'])
        dropped = before_count - len(df)
        if dropped > 0:
            self.cleaning_log.append(f"Dropped {dropped} rows with missing customer_name")
        
        # amount: Impute with median by category
        for category in df['category'].unique():
            mask = (df['category'] == category) & (df['amount'].isna())
            if mask.any():
                median_amount = df[df['category'] == category]['amount'].median()
                df.loc[mask, 'amount'] = median_amount
                count = mask.sum()
                self.cleaning_log.append(
                    f"Imputed {count} missing amounts in {category} with median ₪{median_amount:.2f}"
                )
        
        # product: Impute with mode by category
        for category in df['category'].unique():
            mask = (df['category'] == category) & (df['product'].isna())
            if mask.any():
                mode_product = df[df['category'] == category]['product'].mode()[0]
                df.loc[mask, 'product'] = mode_product
                count = mask.sum()
                self.cleaning_log.append(
                    f"Imputed {count} missing products in {category} with mode '{mode_product}'"
                )
        
        # city: Impute with most common
        if df['customer_city'].isna().any():
            mode_city = df['customer_city'].mode()[0]
            count = df['customer_city'].isna().sum()
            df.loc[df['customer_city'].isna(), 'customer_city'] = mode_city
            self.cleaning_log.append(f"Imputed {count} missing cities with mode '{mode_city}'")
        
        return df
    
    def remove_duplicates(self) -> pd.DataFrame:
        """
        Remove exact duplicates, keep first occurrence
        """
        df = self.df.copy()
        
        before_count = len(df)
        df = df.drop_duplicates(keep='first')
        removed = before_count - len(df)
        
        if removed > 0:
            self.cleaning_log.append(f"Removed {removed} duplicate rows")
        
        return df
    
    def handle_outliers(self) -> pd.DataFrame:
        """
        Outlier strategy:
        - Values >10x median: Cap at 3*IQR
        - Document capping
        """
        df = self.df.copy()
        
        # Handle amount outliers
        Q1 = df['amount'].quantile(0.25)
        Q3 = df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        outlier_mask = (df['amount'] < lower_bound) | (df['amount'] > upper_bound)
        outlier_count = outlier_mask.sum()
        
        if outlier_count > 0:
            df.loc[df['amount'] > upper_bound, 'amount'] = upper_bound
            df.loc[df['amount'] < lower_bound, 'amount'] = lower_bound
            self.cleaning_log.append(
                f"Capped {outlier_count} outlier amounts to range ₪{lower_bound:.2f}-₪{upper_bound:.2f}"
            )
        
        return df
    
    def standardize_formats(self) -> pd.DataFrame:
        """
        Standardize date formats to ISO 8601
        """
        df = self.df.copy()
        
        # Convert all dates to ISO format
        df['transaction_date'] = pd.to_datetime(
            df['transaction_date'],
            errors='coerce',
            infer_datetime_format=True
        )
        
        # Drop rows with unparseable dates
        before_count = len(df)
        df = df.dropna(subset=['transaction_date'])
        invalid = before_count - len(df)
        
        if invalid > 0:
            self.cleaning_log.append(f"Removed {invalid} rows with invalid dates")
        
        return df
    
    def fix_encoding(self) -> pd.DataFrame:
        """
        Fix Hebrew encoding issues
        """
        df = self.df.copy()
        
        text_cols = ['product', 'customer_name', 'customer_city']
        
        for col in text_cols:
            # Try to fix mojibake
            fixed_count = 0
            for idx in df.index:
                text = df.loc[idx, col]
                if isinstance(text, str) and ('�' in text or not self._is_valid_hebrew(text)):
                    # Attempt to fix by re-encoding
                    try:
                        fixed = text.encode('windows-1255').decode('utf-8')
                        if self._is_valid_hebrew(fixed):
                            df.loc[idx, col] = fixed
                            fixed_count += 1
                    except:
                        pass
            
            if fixed_count > 0:
                self.cleaning_log.append(f"Fixed {fixed_count} encoding issues in {col}")
        
        return df
    
    def _is_valid_hebrew(self, text: str) -> bool:
        """Check if text contains valid Hebrew characters"""
        if not isinstance(text, str):
            return False
        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
        return hebrew_chars > 0
    
    def get_cleaning_summary(self) -> str:
        """Generate cleaning summary"""
        summary = "# Data Cleaning Summary\n\n"
        summary += "## Actions Taken:\n"
        for i, action in enumerate(self.cleaning_log, 1):
            summary += f"{i}. {action}\n"
        return summary

# Usage
cleaner = DataCleaner(dirty_transactions)
clean_transactions = cleaner.clean_all()
print(cleaner.get_cleaning_summary())
```

---

### **PHASE 4: ANALYTICS ENGINE (2 hours)**

**NOTE:** analytics.ts already exists and is excellent. Just need backend equivalent.

**File:** `backend/analytics/insights.py`

```python
"""
Generate business insights from clean data
Matches frontend analytics.ts functionality
"""

# [Implementation matches the analytics.ts we verified earlier]
# This generates the same insights but on the backend
```

---

### **PHASE 5: API & DATABASE (2 hours)**

#### **5.1 Database Schema**

```sql
-- PostgreSQL schema
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    product VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'ILS',
    transaction_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    income_quintile INTEGER CHECK (income_quintile BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE data_quality_log (
    id SERIAL PRIMARY KEY,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_rows INTEGER,
    quality_score NUMERIC(5,2),
    missing_values_count INTEGER,
    duplicates_count INTEGER,
    outliers_count INTEGER,
    report JSON
);

CREATE INDEX idx_transaction_date ON transactions(transaction_date);
CREATE INDEX idx_customer_city ON transactions(customer_city);
CREATE INDEX idx_category ON transactions(category);
CREATE INDEX idx_income_quintile ON transactions(income_quintile);
```

#### **5.2 FastAPI Endpoints**

```python
# Add new endpoint
@app.get("/api/data-quality")
async def get_data_quality_report(db: Session = Depends(get_db)):
    """
    Return comprehensive data quality report
    """
    latest_report = db.query(DataQualityLog).order_by(
        DataQualityLog.check_date.desc()
    ).first()
    
    return {
        "quality_score": latest_report.quality_score,
        "total_rows": latest_report.total_rows,
        "issues": latest_report.report,
        "last_checked": latest_report.check_date
    }
```

---

### **PHASE 6: DOCUMENTATION (1 hour)**

**Generate comprehensive documentation:**

```
docs/
├── 01_EXTRACTION_REPORT.md      # CBS data extraction
├── 02_TRANSFORMATION_SPEC.md    # How we generated transactions
├── 03_DATA_QUALITY_REPORT.md    # Before/after cleaning
├── 04_ANALYTICS_METHODOLOGY.md  # Statistical methods
├── 05_API_DOCUMENTATION.md      # Endpoint specs
└── README.md                    # Project overview
```

---

## 📊 FINAL DELIVERABLES

### **What Recruiters Will See:**

1. **Professional README** - "I analyzed CBS household expenditure data"
2. **Data Quality Dashboard** - Before/after cleaning metrics
3. **Analytics Platform** - Hebrew RTL with actionable insights
4. **Complete Pipeline** - Extraction → Cleaning → Analytics → API
5. **Documentation** - Every step explained

### **Key Differentiators:**

| Typical Portfolio | MarketPulse |
|-------------------|-------------|
| Kaggle CSV | ✅ CBS government Excel (messy) |
| Clean data | ✅ Data quality pipeline |
| Basic charts | ✅ Statistical insights |
| English only | ✅ Hebrew/RTL native |
| 100 lines | ✅ 5,000+ lines professional code |

---

## ⏰ TIME ESTIMATE

- Phase 1 (Extraction): 2-3 hours
- Phase 2 (Transformation): 3-4 hours  
- Phase 3 (Quality Pipeline): 2-3 hours
- Phase 4 (Analytics): 2 hours (backend version)
- Phase 5 (API/DB): 2 hours
- Phase 6 (Documentation): 1 hour

**Total: 12-15 hours for complete professional pipeline**

---

## 🎯 SUCCESS CRITERIA

**This project succeeds when:**

1. ✅ Extracts 10,000+ realistic transactions from CBS data
2. ✅ Documents quality issues and cleaning steps
3. ✅ Generates statistical insights (not just displays data)
4. ✅ Professional Hebrew RTL frontend
5. ✅ Complete API with quality endpoints
6. ✅ Comprehensive documentation
7. ✅ Shows senior-level engineering

**Interview talking point:**
"I built a complete data engineering pipeline using Israeli CBS household expenditure surveys. I extracted 523 product categories from complex Excel files, transformed statistical aggregates into 10,000 individual transactions, implemented a professional data quality pipeline, and generated actionable insights about Israeli consumer behavior. The frontend is Hebrew RTL with statistical analysis, not just charts."

---

## NEXT STEPS

**START HERE:**
1. Extract CBS data (Phase 1)
2. Generate transactions (Phase 2)
3. Build quality pipeline (Phase 3)
4. Everything else follows

This is professional data engineering work. Not a toy project.
