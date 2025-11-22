"""
Phase 3.2: Build Data Quality Detection and Cleaning Pipeline

This script demonstrates professional data quality management:
1. Detect quality issues (missing, duplicates, outliers)
2. Apply cleaning strategies
3. Generate before/after quality metrics
4. Produce comprehensive quality report

This showcases enterprise-level data engineering capabilities.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Tuple

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataQualityAnalyzer:
    """Analyze and detect data quality issues"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.issues = {
            'missing_values': {},
            'duplicates': [],
            'outliers': [],
            'data_type_errors': []
        }
        logger.info(f"Initialized analyzer with {len(df)} rows")

    def detect_missing_values(self) -> Dict:
        """Detect missing values across all columns"""
        missing_stats = {}

        for col in self.df.columns:
            null_count = self.df[col].isnull().sum()
            if null_count > 0:
                missing_stats[col] = {
                    'count': int(null_count),
                    'percentage': float(null_count / len(self.df) * 100),
                    'rows': self.df[self.df[col].isnull()].index.tolist()[:10]  # First 10
                }

        self.issues['missing_values'] = missing_stats
        total_missing = sum(s['count'] for s in missing_stats.values())
        logger.info(f"[!] Found {total_missing} missing values across {len(missing_stats)} columns")
        return missing_stats

    def detect_duplicates(self, subset: List[str] = None) -> List:
        """
        Detect duplicate records

        Args:
            subset: Columns to check for duplicates (None = all columns)
        """
        # For transaction data, duplicates are same transaction_id
        if 'transaction_id' in self.df.columns:
            duplicates = self.df[self.df.duplicated(subset=['transaction_id'], keep=False)]
        else:
            duplicates = self.df[self.df.duplicated(keep=False)]

        duplicate_indices = duplicates.index.tolist()
        self.issues['duplicates'] = duplicate_indices

        logger.info(f"[!] Found {len(duplicate_indices)} duplicate rows")
        return duplicate_indices

    def detect_outliers_iqr(self, column: str, multiplier: float = 1.5) -> List:
        """
        Detect outliers using IQR (Interquartile Range) method

        Args:
            column: Numeric column to check
            multiplier: IQR multiplier (1.5 = standard, 3.0 = extreme)

        Returns:
            List of outlier indices
        """
        if column not in self.df.columns:
            return []

        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        outliers = self.df[
            (self.df[column] < lower_bound) |
            (self.df[column] > upper_bound)
        ]

        outlier_indices = outliers.index.tolist()
        logger.info(f"[!] Found {len(outlier_indices)} outliers in '{column}' (IQR method)")

        return outlier_indices

    def detect_all_outliers(self) -> List:
        """Detect outliers in all numeric columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        all_outlier_indices = set()
        outlier_details = []

        for col in numeric_cols:
            outliers = self.detect_outliers_iqr(col, multiplier=1.5)
            all_outlier_indices.update(outliers)

            if outliers:
                outlier_details.append({
                    'column': col,
                    'count': len(outliers),
                    'indices': outliers[:10],  # First 10
                    'values': self.df.loc[outliers[:10], col].tolist()
                })

        self.issues['outliers'] = outlier_details
        logger.info(f"[!] Total unique outlier rows: {len(all_outlier_indices)}")

        return list(all_outlier_indices)

    def calculate_quality_score(self) -> float:
        """
        Calculate overall data quality score (0-100)

        Score components:
        - Completeness: % of non-null values (40%)
        - Uniqueness: % of non-duplicate rows (30%)
        - Validity: % of rows without outliers (30%)
        """
        # Completeness
        total_cells = len(self.df) * len(self.df.columns)
        non_null_cells = self.df.count().sum()
        completeness = (non_null_cells / total_cells) * 100

        # Uniqueness (based on transaction_id)
        if 'transaction_id' in self.df.columns:
            unique_transactions = self.df['transaction_id'].nunique()
            uniqueness = (unique_transactions / len(self.df)) * 100
        else:
            uniqueness = 100

        # Validity (rows without outliers)
        outlier_count = len(set([idx for detail in self.issues['outliers'] for idx in detail['indices']]))
        validity = ((len(self.df) - outlier_count) / len(self.df)) * 100

        # Weighted score
        quality_score = (
            completeness * 0.40 +
            uniqueness * 0.30 +
            validity * 0.30
        )

        logger.info(f"Quality Score: {quality_score:.2f}/100")
        logger.info(f"  - Completeness: {completeness:.2f}% (weight: 40%)")
        logger.info(f"  - Uniqueness: {uniqueness:.2f}% (weight: 30%)")
        logger.info(f"  - Validity: {validity:.2f}% (weight: 30%)")

        return quality_score


class DataQualityCleaner:
    """Clean and fix data quality issues"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.cleaning_actions = []
        logger.info(f"Initialized cleaner with {len(df)} rows")

    def handle_missing_values(self, strategy: str = 'smart'):
        """
        Handle missing values with smart strategies

        Strategies:
        - 'smart': Context-aware imputation
        - 'drop': Drop rows with missing values
        - 'fill': Fill with defaults
        """
        initial_rows = len(self.df)

        if strategy == 'smart':
            # Smart strategy: different approach per column type
            for col in self.df.columns:
                null_count = self.df[col].isnull().sum()
                if null_count == 0:
                    continue

                # Categorical columns: fill with mode or 'Unknown'
                if self.df[col].dtype == 'object':
                    if null_count < len(self.df) * 0.5:  # If < 50% missing
                        mode_value = self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else 'Unknown'
                        self.df[col].fillna(mode_value, inplace=True)
                        self.cleaning_actions.append(f"Filled {null_count} missing '{col}' with mode: {mode_value}")
                    else:
                        self.df[col].fillna('Unknown', inplace=True)
                        self.cleaning_actions.append(f"Filled {null_count} missing '{col}' with 'Unknown'")

                # Numeric columns: fill with median
                elif self.df[col].dtype in [np.float64, np.int64]:
                    median_value = self.df[col].median()
                    self.df[col].fillna(median_value, inplace=True)
                    self.cleaning_actions.append(f"Filled {null_count} missing '{col}' with median: {median_value:.2f}")

        elif strategy == 'drop':
            self.df.dropna(inplace=True)
            dropped = initial_rows - len(self.df)
            self.cleaning_actions.append(f"Dropped {dropped} rows with missing values")

        logger.info(f"[+] Handled missing values using '{strategy}' strategy")

    def remove_duplicates(self, subset: List[str] = None, keep: str = 'first'):
        """
        Remove duplicate records

        Args:
            subset: Columns to check for duplicates
            keep: Which duplicate to keep ('first', 'last', False)
        """
        initial_rows = len(self.df)

        if 'transaction_id' in self.df.columns:
            # For transactions, remove duplicates based on transaction_id
            self.df.drop_duplicates(subset=['transaction_id'], keep=keep, inplace=True)
        else:
            self.df.drop_duplicates(keep=keep, inplace=True)

        removed = initial_rows - len(self.df)
        self.cleaning_actions.append(f"Removed {removed} duplicate records")
        logger.info(f"[+] Removed {removed} duplicates")

    def handle_outliers(self, method: str = 'cap', columns: List[str] = None):
        """
        Handle outliers

        Methods:
        - 'cap': Cap outliers at IQR boundaries (Winsorization)
        - 'remove': Remove outlier rows
        - 'flag': Flag but keep outliers
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()

        for col in columns:
            if col not in self.df.columns:
                continue

            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_count = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()

            if outlier_count == 0:
                continue

            if method == 'cap':
                # Winsorization: cap at boundaries
                self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
                self.cleaning_actions.append(f"Capped {outlier_count} outliers in '{col}' at IQR boundaries")

            elif method == 'remove':
                initial_rows = len(self.df)
                self.df = self.df[
                    (self.df[col] >= lower_bound) &
                    (self.df[col] <= upper_bound)
                ]
                removed = initial_rows - len(self.df)
                self.cleaning_actions.append(f"Removed {removed} rows with outliers in '{col}'")

            elif method == 'flag':
                self.df[f'{col}_is_outlier'] = (
                    (self.df[col] < lower_bound) |
                    (self.df[col] > upper_bound)
                )
                self.cleaning_actions.append(f"Flagged {outlier_count} outliers in '{col}'")

        logger.info(f"[+] Handled outliers using '{method}' method")

    def get_cleaned_data(self) -> pd.DataFrame:
        """Return cleaned DataFrame"""
        return self.df

    def get_cleaning_report(self) -> List[str]:
        """Return list of all cleaning actions performed"""
        return self.cleaning_actions


def generate_quality_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    analyzer_before: DataQualityAnalyzer,
    analyzer_after: DataQualityAnalyzer,
    cleaning_actions: List[str],
    output_path: Path
):
    """Generate comprehensive data quality report"""

    report = f"""# Data Quality Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report documents the data quality assessment and cleaning pipeline for CBS transaction data.

### Quality Improvement

| Metric | Before Cleaning | After Cleaning | Improvement |
|--------|-----------------|----------------|-------------|
| **Total Rows** | {len(df_before):,} | {len(df_after):,} | {len(df_after) - len(df_before):+,} |
| **Quality Score** | {analyzer_before.calculate_quality_score():.2f}/100 | {analyzer_after.calculate_quality_score():.2f}/100 | {analyzer_after.calculate_quality_score() - analyzer_before.calculate_quality_score():+.2f} |
| **Missing Values** | {sum(s['count'] for s in analyzer_before.issues['missing_values'].values()):,} | {sum(s['count'] for s in analyzer_after.issues['missing_values'].values()):,} | {sum(s['count'] for s in analyzer_after.issues['missing_values'].values()) - sum(s['count'] for s in analyzer_before.issues['missing_values'].values()):+,} |
| **Duplicates** | {len(analyzer_before.issues['duplicates']):,} | {len(analyzer_after.issues['duplicates']):,} | {len(analyzer_after.issues['duplicates']) - len(analyzer_before.issues['duplicates']):+,} |
| **Completeness** | {(df_before.count().sum() / (len(df_before) * len(df_before.columns)) * 100):.2f}% | {(df_after.count().sum() / (len(df_after) * len(df_after.columns)) * 100):.2f}% | {((df_after.count().sum() / (len(df_after) * len(df_after.columns))) - (df_before.count().sum() / (len(df_before) * len(df_before.columns)))) * 100:+.2f}% |

## Issues Detected (Before Cleaning)

### Missing Values

"""

    # Missing values detail
    if analyzer_before.issues['missing_values']:
        report += "| Column | Missing Count | Percentage |\n"
        report += "|--------|---------------|------------|\n"
        for col, stats in analyzer_before.issues['missing_values'].items():
            report += f"| {col} | {stats['count']:,} | {stats['percentage']:.2f}% |\n"
    else:
        report += "No missing values detected.\n"

    report += f"""

### Duplicates

**Total duplicate rows:** {len(analyzer_before.issues['duplicates']):,}

Duplicates were identified based on `transaction_id` field.

### Outliers

"""

    # Outliers detail
    if analyzer_before.issues['outliers']:
        report += "| Column | Outlier Count | Method |\n"
        report += "|--------|---------------|--------|\n"
        for detail in analyzer_before.issues['outliers']:
            report += f"| {detail['column']} | {detail['count']:,} | IQR (1.5x) |\n"
    else:
        report += "No outliers detected.\n"

    report += f"""

## Cleaning Actions Performed

"""

    for i, action in enumerate(cleaning_actions, 1):
        report += f"{i}. {action}\n"

    report += f"""

## Quality Metrics (After Cleaning)

### Completeness by Column

| Column | Non-Null Count | Completeness |
|--------|----------------|--------------|
"""

    for col in df_after.columns:
        non_null = df_after[col].count()
        completeness = (non_null / len(df_after)) * 100
        report += f"| {col} | {non_null:,} | {completeness:.2f}% |\n"

    report += f"""

### Data Distribution

**Total transactions:** {len(df_after):,}
**Date range:** {df_after['transaction_date'].min()} to {df_after['transaction_date'].max()}
**Total revenue:** ILS {df_after['amount'].sum():,.2f}
**Average transaction value:** ILS {df_after['amount'].mean():.2f}

## Validation

### Before Cleaning
- Rows: {len(df_before):,}
- Missing values: {sum(s['count'] for s in analyzer_before.issues['missing_values'].values()):,}
- Duplicates: {len(analyzer_before.issues['duplicates']):,}
- Quality score: {analyzer_before.calculate_quality_score():.2f}/100

### After Cleaning
- Rows: {len(df_after):,}
- Missing values: {sum(s['count'] for s in analyzer_after.issues['missing_values'].values()):,}
- Duplicates: {len(analyzer_after.issues['duplicates']):,}
- Quality score: {analyzer_after.calculate_quality_score():.2f}/100

## Methodology

### Missing Value Handling
- **Categorical fields**: Filled with mode (most common value) or 'Unknown'
- **Numeric fields**: Filled with median value
- **Rationale**: Preserves data distribution while maintaining row count

### Duplicate Removal
- **Method**: Remove duplicates based on `transaction_id`
- **Keep**: First occurrence
- **Rationale**: Transaction ID should be unique; duplicates indicate system errors

### Outlier Treatment
- **Method**: IQR-based capping (Winsorization)
- **Threshold**: Q1 - 1.5*IQR to Q3 + 1.5*IQR
- **Rationale**: Preserves data points while limiting extreme values from skewing analysis

## Next Steps

1. Load cleaned data to PostgreSQL database
2. Create data quality monitoring dashboard
3. Implement automated quality checks in production pipeline
4. Setup alerting for quality degradation

---

*This report was generated as part of the MarketPulse data engineering pipeline.*
"""

    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Quality report saved to: {output_path}")


def main():
    """Run data quality pipeline"""
    print("=" * 70)
    print("DATA QUALITY PIPELINE")
    print("Phase 3.2: Detect Issues and Clean Data")
    print("=" * 70)
    print()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / 'data' / 'processed'
    docs_dir = project_root / 'docs' / 'etl'

    dirty_file = processed_dir / 'transactions_dirty.csv'
    clean_file = processed_dir / 'transactions_cleaned.csv'
    report_file = docs_dir / '03_DATA_QUALITY_REPORT.md'

    # Load dirty data
    print(f"Loading dirty data from: {dirty_file.name}")
    df_dirty = pd.read_csv(dirty_file, encoding='utf-8')
    print(f"[+] Loaded {len(df_dirty):,} rows")
    print()

    # BEFORE: Analyze quality issues
    print("Analyzing data quality issues (BEFORE)...")
    analyzer_before = DataQualityAnalyzer(df_dirty)
    analyzer_before.detect_missing_values()
    analyzer_before.detect_duplicates()
    analyzer_before.detect_all_outliers()
    quality_score_before = analyzer_before.calculate_quality_score()
    print()

    # Clean data
    print("Cleaning data...")
    cleaner = DataQualityCleaner(df_dirty)

    print("  1. Handling missing values...")
    cleaner.handle_missing_values(strategy='smart')

    print("  2. Removing duplicates...")
    cleaner.remove_duplicates(keep='first')

    print("  3. Handling outliers...")
    cleaner.handle_outliers(method='cap', columns=['amount', 'quantity'])

    df_clean = cleaner.get_cleaned_data()
    cleaning_actions = cleaner.get_cleaning_report()
    print()

    # AFTER: Analyze cleaned data quality
    print("Analyzing data quality (AFTER)...")
    analyzer_after = DataQualityAnalyzer(df_clean)
    analyzer_after.detect_missing_values()
    analyzer_after.detect_duplicates()
    analyzer_after.detect_all_outliers()
    quality_score_after = analyzer_after.calculate_quality_score()
    print()

    # Save cleaned data
    print(f"Saving cleaned data to: {clean_file.name}")
    df_clean.to_csv(clean_file, index=False, encoding='utf-8-sig')
    print(f"[+] Saved {len(df_clean):,} cleaned rows")
    print()

    # Generate report
    print("Generating quality report...")
    generate_quality_report(
        df_before=df_dirty,
        df_after=df_clean,
        analyzer_before=analyzer_before,
        analyzer_after=analyzer_after,
        cleaning_actions=cleaning_actions,
        output_path=report_file
    )
    print()

    # Summary
    print("=" * 70)
    print("QUALITY IMPROVEMENT SUMMARY")
    print("=" * 70)
    print(f"Rows:            {len(df_dirty):,} -> {len(df_clean):,} ({len(df_clean) - len(df_dirty):+,})")
    print(f"Quality Score:   {quality_score_before:.2f} -> {quality_score_after:.2f} ({quality_score_after - quality_score_before:+.2f})")
    print(f"Missing Values:  {sum(s['count'] for s in analyzer_before.issues['missing_values'].values()):,} -> {sum(s['count'] for s in analyzer_after.issues['missing_values'].values()):,}")
    print(f"Duplicates:      {len(analyzer_before.issues['duplicates']):,} -> {len(analyzer_after.issues['duplicates']):,}")
    print()

    print("=" * 70)
    print("PHASE 3 COMPLETE")
    print("=" * 70)
    print()
    print("Generated:")
    print(f"  - {clean_file.name} ({len(df_clean):,} rows)")
    print(f"  - {report_file.name}")
    print()
    print("Next step: Phase 4 - Load data to PostgreSQL database")
    print()


if __name__ == '__main__':
    main()
