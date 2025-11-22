"""
Phase 3.1: Inject Data Quality Issues

This script takes the clean CBS-generated transactions and intentionally
introduces realistic data quality issues:
- Missing values (5%)
- Duplicate records (3%)
- Outliers/anomalies (2%)

This demonstrates professional data quality detection and cleaning capabilities.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import random
import logging

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QualityIssueInjector:
    """Inject realistic data quality issues into clean transaction data"""

    def __init__(self, df_clean: pd.DataFrame):
        """
        Initialize with clean transaction data

        Args:
            df_clean: Clean transaction DataFrame
        """
        self.df_clean = df_clean.copy()
        self.df_dirty = df_clean.copy()
        self.issues_injected = {
            'missing_values': [],
            'duplicates': [],
            'outliers': []
        }
        logger.info(f"Initialized with {len(df_clean)} clean transactions")

    def inject_missing_values(self, target_rate: float = 0.05):
        """
        Inject missing values in realistic patterns

        Missing data typically occurs due to:
        - Form abandonment (missing customer info)
        - Integration errors (missing metadata)
        - Manual entry mistakes

        Args:
            target_rate: Target percentage of rows with missing data (default 5%)
        """
        n_rows = len(self.df_dirty)
        n_missing = int(n_rows * target_rate)

        # Select random rows to inject missing values
        missing_indices = random.sample(range(n_rows), n_missing)

        # Define fields that can have missing values (not transaction_id or transaction_date)
        # CBS household expenditure schema - no emails, phones, or e-commerce fields
        nullable_fields = [
            'customer_name',
            'customer_city',
            'category',
            'currency'
        ]

        for idx in missing_indices:
            # Randomly select 1-3 fields to make null
            n_fields = random.randint(1, 3)
            fields_to_null = random.sample(nullable_fields, n_fields)

            for field in fields_to_null:
                self.df_dirty.at[idx, field] = None
                self.issues_injected['missing_values'].append({
                    'row': idx,
                    'field': field,
                    'original_value': self.df_clean.at[idx, field]
                })

        logger.info(f"[+] Injected {len(self.issues_injected['missing_values'])} missing values across {n_missing} rows")

    def inject_duplicates(self, target_rate: float = 0.03):
        """
        Inject duplicate records

        Duplicates occur due to:
        - System retries
        - Data integration issues
        - User double-clicks

        Args:
            target_rate: Target percentage of duplicate rows (default 3%)
        """
        n_rows = len(self.df_dirty)
        n_duplicates = int(n_rows * target_rate)

        # Select random rows to duplicate
        duplicate_indices = random.sample(range(n_rows), n_duplicates)

        duplicates = []
        for idx in duplicate_indices:
            duplicate_row = self.df_dirty.iloc[idx].copy()

            # Modify transaction_date slightly (within 1 day - typical entry error)
            # CBS data uses transaction_date (YYYY-MM-DD format), not timestamp
            original_date = pd.to_datetime(duplicate_row['transaction_date'])
            duplicate_row['transaction_date'] = (original_date + timedelta(days=random.choice([0, 1]))).strftime('%Y-%m-%d')

            # Keep same transaction_id (realistic duplicate scenario)
            duplicates.append(duplicate_row)

            self.issues_injected['duplicates'].append({
                'original_row': idx,
                'transaction_id': duplicate_row['transaction_id']
            })

        # Append duplicates to DataFrame
        if duplicates:
            self.df_dirty = pd.concat([
                self.df_dirty,
                pd.DataFrame(duplicates)
            ], ignore_index=True)

        logger.info(f"[+] Injected {n_duplicates} duplicate records")

    def inject_outliers(self, target_rate: float = 0.02):
        """
        Inject outliers and anomalies

        Outliers occur due to:
        - Data entry errors (extra zeros)
        - Price glitches
        - Testing data left in production
        - Fraud attempts

        Args:
            target_rate: Target percentage of outlier rows (default 2%)
        """
        n_rows = len(self.df_dirty)
        n_outliers = int(n_rows * target_rate)

        # Select random rows for outliers
        outlier_indices = random.sample(range(len(self.df_dirty)), n_outliers)

        for idx in outlier_indices:
            # CBS data has no quantity field - only amount
            outlier_type = random.choice([
                'price_spike',
                'price_error',
                'negative_amount'
            ])

            original_amount = self.df_dirty.at[idx, 'amount']

            if outlier_type == 'price_spike':
                # 10x-50x normal amount (data entry error)
                self.df_dirty.at[idx, 'amount'] = original_amount * random.uniform(10, 50)

            elif outlier_type == 'price_error':
                # Extra zero added (e.g., 50 -> 500)
                self.df_dirty.at[idx, 'amount'] = original_amount * 10

            elif outlier_type == 'negative_amount':
                # Negative transaction (data entry error, not refund)
                self.df_dirty.at[idx, 'amount'] = -abs(original_amount)

            self.issues_injected['outliers'].append({
                'row': idx,
                'type': outlier_type,
                'original_amount': original_amount,
                'new_amount': self.df_dirty.at[idx, 'amount']
            })

        logger.info(f"[+] Injected {n_outliers} outliers")

    def get_quality_report(self) -> dict:
        """Generate summary report of injected issues"""
        return {
            'original_rows': len(self.df_clean),
            'dirty_rows': len(self.df_dirty),
            'missing_values': {
                'count': len(self.issues_injected['missing_values']),
                'percentage': len(self.issues_injected['missing_values']) / len(self.df_clean) * 100
            },
            'duplicates': {
                'count': len(self.issues_injected['duplicates']),
                'percentage': len(self.issues_injected['duplicates']) / len(self.df_clean) * 100
            },
            'outliers': {
                'count': len(self.issues_injected['outliers']),
                'percentage': len(self.issues_injected['outliers']) / len(self.df_clean) * 100
            },
            'total_issues': (
                len(self.issues_injected['missing_values']) +
                len(self.issues_injected['duplicates']) +
                len(self.issues_injected['outliers'])
            )
        }

    def save_dirty_data(self, output_path: Path):
        """Save dirty data with injected issues"""
        self.df_dirty.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Dirty data saved to: {output_path}")

    def save_issue_log(self, output_path: Path):
        """Save detailed log of all injected issues for validation"""
        import json

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.issues_injected, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Issue log saved to: {output_path}")


def main():
    """Run quality issue injection pipeline"""
    print("=" * 70)
    print("DATA QUALITY ISSUE INJECTION")
    print("Phase 3.1: Inject Realistic Quality Issues")
    print("=" * 70)
    print()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / 'data' / 'processed'

    clean_file = processed_dir / 'transactions_generated.csv'
    dirty_file = processed_dir / 'transactions_dirty.csv'
    issue_log_file = processed_dir / 'quality_issues_log.json'

    # Load clean transactions
    print(f"Loading clean transactions from: {clean_file.name}")
    df_clean = pd.read_csv(clean_file, encoding='utf-8')
    print(f"[+] Loaded {len(df_clean)} clean transactions")
    print()

    # Initialize injector
    print("Initializing quality issue injector...")
    injector = QualityIssueInjector(df_clean)
    print()

    # Inject issues
    print("Injecting quality issues...")
    print()

    print("1. Injecting missing values (5% target)...")
    injector.inject_missing_values(target_rate=0.05)
    print()

    print("2. Injecting duplicate records (3% target)...")
    injector.inject_duplicates(target_rate=0.03)
    print()

    print("3. Injecting outliers and anomalies (2% target)...")
    injector.inject_outliers(target_rate=0.02)
    print()

    # Get quality report
    report = injector.get_quality_report()

    print("=" * 70)
    print("INJECTION SUMMARY")
    print("=" * 70)
    print(f"Original rows:     {report['original_rows']:,}")
    print(f"Rows after dirty:  {report['dirty_rows']:,}")
    print(f"Added rows:        {report['dirty_rows'] - report['original_rows']:,}")
    print()
    print(f"Missing values:    {report['missing_values']['count']:,} ({report['missing_values']['percentage']:.1f}%)")
    print(f"Duplicates:        {report['duplicates']['count']:,} ({report['duplicates']['percentage']:.1f}%)")
    print(f"Outliers:          {report['outliers']['count']:,} ({report['outliers']['percentage']:.1f}%)")
    print(f"Total issues:      {report['total_issues']:,}")
    print()

    # Save outputs
    print("Saving outputs...")
    injector.save_dirty_data(dirty_file)
    injector.save_issue_log(issue_log_file)
    print()

    print("=" * 70)
    print("PHASE 3.1 COMPLETE")
    print("=" * 70)
    print()
    print("Generated:")
    print(f"  - {dirty_file.name} ({len(injector.df_dirty):,} rows)")
    print(f"  - {issue_log_file.name}")
    print()
    print("Next step: Phase 3.2 - Build quality detection and cleaning pipeline")
    print("  Run: python etl/build_quality_pipeline.py")
    print()


if __name__ == '__main__':
    main()
