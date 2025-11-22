# 📊 Ultimate ETL Best Practices Guide: Robust Data Extraction from Complex CSV/Excel Sources

## Executive Summary
This document consolidates industry-leading best practices for building resilient ETL pipelines that handle complex, non-standard tabular data commonly found in government, legacy, and enterprise systems. Based on extensive research from Stack Overflow, GitHub repositories, and production implementations, this guide provides actionable patterns for Python-based data extraction.

---

## 🎯 Core Architecture Principles

### 1. The Separation of Concerns Pattern

**Never mix data extraction with metadata extraction**

```python
# ❌ BAD: Single-pass extraction mixing headers and data
df = pd.read_csv('complex_file.csv', header=10)  # Assumes row 10 has everything

# ✅ GOOD: Separate metadata and data extraction
import openpyxl
import pandas as pd

def extract_metadata(file_path):
    """Extract header information from complex multi-row headers"""
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active
    
    # Read first N rows containing headers
    headers = []
    for row in ws.iter_rows(min_row=1, max_row=8, values_only=True):
        headers.append(row)
    
    return process_multirow_headers(headers)

def extract_data(file_path, skip_rows=10):
    """Extract actual data rows"""
    return pd.read_csv(file_path, skiprows=skip_rows, header=None)
```

### 2. The Single Source of Truth Pattern

**Critical Rule**: Never rely on raw data files for human-readable names of coded values.

```python
# Create a centralized mapping table
DIMENSION_MAPPINGS = {
    'geographic': {
        '471': 'באר שבע',
        '143': 'תל אביב',
        '061': 'ירושלים',
        # ... complete mapping
    },
    'sector': {
        'A': 'Agriculture',
        'B': 'Manufacturing',
        'C': 'Services'
    }
}

class MappingRepository:
    """Centralized repository for all code-to-name mappings"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
        self._load_mappings()
    
    def _load_mappings(self):
        """Load mappings from database dim_code_map table"""
        query = """
        SELECT mapping_type, code, name, name_hebrew, is_active
        FROM dim_code_map
        WHERE is_active = true
        """
        self.mappings = pd.read_sql(query, self.conn)
    
    def get_name(self, mapping_type, code):
        """Lookup human-readable name for a code"""
        result = self.mappings[
            (self.mappings['mapping_type'] == mapping_type) &
            (self.mappings['code'] == str(code))
        ]
        if not result.empty:
            return result.iloc[0]['name_hebrew']
        return f"UNKNOWN_{code}"  # Defensive fallback
```

---

## 🔧 Technical Implementation Patterns

### Pattern 1: Multi-Row Header Extraction

**Problem**: Government/enterprise Excel files often have headers spanning rows 1-8 with merged cells.

**Solution**: Use openpyxl for metadata, pandas for data:

```python
import pandas as pd
import openpyxl
from typing import List, Dict, Tuple

class ComplexExcelReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.workbook = openpyxl.load_workbook(file_path, data_only=True)
        
    def read_multirow_headers(self, header_rows: List[int]) -> pd.MultiIndex:
        """
        Extract multi-row headers handling merged cells
        Example: header_rows=[0,1,2,3] for rows 1-4
        """
        ws = self.workbook.active
        headers = []
        
        for row_idx in header_rows:
            row_values = []
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_idx + 1, column=col)
                
                # Handle merged cells
                if cell.value is None:
                    # Check if this cell is part of a merged range
                    for merged_range in ws.merged_cells.ranges:
                        if cell.coordinate in merged_range:
                            # Get the value from the top-left cell of the range
                            min_col, min_row = merged_range.min_col, merged_range.min_row
                            value = ws.cell(row=min_row, column=min_col).value
                            row_values.append(value)
                            break
                    else:
                        # Forward fill from previous column if not merged
                        row_values.append(row_values[-1] if row_values else None)
                else:
                    row_values.append(cell.value)
            
            headers.append(row_values)
        
        # Create MultiIndex from headers
        return pd.MultiIndex.from_arrays(headers)
    
    def read_data_with_complex_headers(self, 
                                      header_rows: List[int], 
                                      data_start_row: int) -> pd.DataFrame:
        """
        Complete extraction with proper header handling
        """
        # Get multi-level headers
        columns = self.read_multirow_headers(header_rows)
        
        # Read data starting from specified row
        df = pd.read_excel(
            self.file_path, 
            skiprows=data_start_row - 1, 
            header=None
        )
        
        # Apply the multi-level column index
        df.columns = columns
        
        return df

# Usage
reader = ComplexExcelReader('government_data.xlsx')
df = reader.read_data_with_complex_headers(
    header_rows=[3, 4, 5, 6],  # Rows 4-7 contain headers
    data_start_row=11           # Data starts at row 11
)
```

### Pattern 2: Defensive Data Validation with Pydantic

**Use Pydantic for schema enforcement and data quality**:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
import pandas as pd

class SegmentData(BaseModel):
    """Schema for segmentation data with validation"""
    
    year: int = Field(..., ge=2020, le=2030)
    month: int = Field(..., ge=1, le=12)
    segment_code: str = Field(..., regex=r'^\d{3}$')  # 3-digit code
    segment_value: Optional[str] = None  # Will be populated from mapping
    amount: float = Field(..., ge=0)
    currency: Literal['ILS', 'USD', 'EUR'] = 'ILS'
    
    @validator('segment_value', always=True)
    def populate_segment_name(cls, v, values):
        """Auto-populate segment name from code"""
        if 'segment_code' in values:
            # In production, this would query the mapping table
            return DIMENSION_MAPPINGS.get(values['segment_code'], v)
        return v
    
    class Config:
        # Ensure all fields are validated
        validate_assignment = True
        use_enum_values = True

class ETLValidator:
    """Validate and separate good/bad records"""
    
    def __init__(self, schema_class: BaseModel):
        self.schema = schema_class
        self.valid_records = []
        self.invalid_records = []
        
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Validate DataFrame rows against schema
        Returns: (valid_df, invalid_df)
        """
        for idx, row in df.iterrows():
            try:
                # Validate row against schema
                validated = self.schema(**row.to_dict())
                self.valid_records.append(validated.dict())
            except Exception as e:
                # Log invalid record with error details
                invalid_record = row.to_dict()
                invalid_record['_error'] = str(e)
                invalid_record['_row_index'] = idx
                self.invalid_records.append(invalid_record)
        
        valid_df = pd.DataFrame(self.valid_records)
        invalid_df = pd.DataFrame(self.invalid_records)
        
        return valid_df, invalid_df

# Usage
validator = ETLValidator(SegmentData)
valid_data, invalid_data = validator.validate_dataframe(raw_df)

# Save invalid records for inspection
if not invalid_data.empty:
    invalid_data.to_csv('data_quality_issues.csv', index=False)
    logger.warning(f"Found {len(invalid_data)} invalid records")
```

### Pattern 3: Robust Error Handling & Logging

```python
import logging
import functools
from typing import Callable, Any
import time

# Configure structured logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    level=logging.INFO
)

class ETLError(Exception):
    """Base exception for ETL operations"""
    pass

class DataExtractionError(ETLError):
    """Raised when data extraction fails"""
    pass

class TransformationError(ETLError):
    """Raised when transformation fails"""
    pass

def etl_error_handler(operation_name: str):
    """Decorator for comprehensive error handling"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            start_time = time.time()
            
            try:
                logger.info(f"Starting {operation_name}")
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"Completed {operation_name} in {elapsed:.2f}s")
                return result
                
            except pd.errors.EmptyDataError as e:
                logger.error(f"Empty data in {operation_name}: {e}")
                raise DataExtractionError(f"No data found during {operation_name}")
                
            except KeyError as e:
                logger.error(f"Missing column in {operation_name}: {e}")
                raise TransformationError(f"Expected column not found: {e}")
                
            except Exception as e:
                logger.error(
                    f"Unexpected error in {operation_name}: {e}",
                    exc_info=True  # Include full traceback
                )
                raise ETLError(f"Failed during {operation_name}: {e}")
        
        return wrapper
    return decorator

class ResilientETLPipeline:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    @etl_error_handler("data extraction")
    def extract(self, source_path: str) -> pd.DataFrame:
        """Extract with comprehensive error handling"""
        
        # Try multiple encoding options
        encodings = ['utf-8', 'windows-1255', 'iso-8859-8']  # For Hebrew data
        
        for encoding in encodings:
            try:
                if source_path.endswith('.xlsx'):
                    return pd.read_excel(source_path)
                else:
                    return pd.read_csv(source_path, encoding=encoding)
            except UnicodeDecodeError:
                continue
        
        raise DataExtractionError(f"Could not read file with any encoding: {encodings}")
    
    @etl_error_handler("data transformation")
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform with validation at each step"""
        
        # Validate required columns exist
        required_cols = self.config.get('required_columns', [])
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise TransformationError(f"Missing required columns: {missing_cols}")
        
        # Apply transformations with individual error handling
        for transform_step in self.config.get('transformations', []):
            try:
                df = transform_step(df)
                self.logger.info(f"Applied transformation: {transform_step.__name__}")
            except Exception as e:
                self.logger.error(f"Transformation {transform_step.__name__} failed: {e}")
                # Decide whether to fail or continue based on criticality
                if transform_step.critical:
                    raise
        
        return df
```

---

## 🏗️ Production Pipeline Architecture

### Complete ETL Pipeline Template

```python
from dataclasses import dataclass
from pathlib import Path
import yaml
from typing import Dict, List, Optional
import psycopg2
from contextlib import contextmanager

@dataclass
class ETLConfig:
    """Configuration for ETL pipeline"""
    source_path: Path
    db_connection_string: str
    mapping_table: str
    target_table: str
    header_rows: List[int]
    data_start_row: int
    column_mappings: Dict[str, str]
    validation_rules: Dict
    
    @classmethod
    def from_yaml(cls, config_path: str):
        """Load configuration from YAML file"""
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return cls(**config)

class ProductionETLPipeline:
    """Production-ready ETL pipeline with all best practices"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.mapping_repo = None
        self.metrics = {}
        
    @contextmanager
    def db_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(self.config.db_connection_string)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def initialize_mappings(self):
        """Load all mapping tables into memory"""
        with self.db_connection() as conn:
            self.mapping_repo = MappingRepository(conn)
            self.logger.info("Initialized mapping repository")
    
    def extract(self) -> pd.DataFrame:
        """Extract data with proper header handling"""
        reader = ComplexExcelReader(str(self.config.source_path))
        
        # Extract with multi-row header handling
        df = reader.read_data_with_complex_headers(
            header_rows=self.config.header_rows,
            data_start_row=self.config.data_start_row
        )
        
        self.metrics['rows_extracted'] = len(df)
        self.logger.info(f"Extracted {len(df)} rows from {self.config.source_path}")
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply transformations with mapping lookups"""
        
        # 1. Rename columns based on configuration
        if self.config.column_mappings:
            df = df.rename(columns=self.config.column_mappings)
        
        # 2. Apply code-to-name mappings
        for col, mapping_type in [('segment_code', 'geographic'), 
                                  ('sector_code', 'sector')]:
            if col in df.columns:
                df[f'{col}_name'] = df[col].apply(
                    lambda x: self.mapping_repo.get_name(mapping_type, x)
                )
        
        # 3. Data type conversions
        df = self._apply_type_conversions(df)
        
        # 4. Validation
        validator = ETLValidator(SegmentData)
        valid_df, invalid_df = validator.validate_dataframe(df)
        
        self.metrics['rows_valid'] = len(valid_df)
        self.metrics['rows_invalid'] = len(invalid_df)
        
        # Save invalid records for review
        if not invalid_df.empty:
            invalid_path = Path('data_quality') / f"invalid_{datetime.now():%Y%m%d_%H%M%S}.csv"
            invalid_path.parent.mkdir(exist_ok=True)
            invalid_df.to_csv(invalid_path, index=False)
            self.logger.warning(f"Saved {len(invalid_df)} invalid records to {invalid_path}")
        
        return valid_df
    
    def load(self, df: pd.DataFrame):
        """Load data to destination with proper error handling"""
        with self.db_connection() as conn:
            # Create staging table
            staging_table = f"{self.config.target_table}_staging"
            
            # Load to staging first
            df.to_sql(
                staging_table,
                conn,
                if_exists='replace',
                index=False,
                method='multi',  # Bulk insert
                chunksize=1000
            )
            
            # Perform atomic swap
            cursor = conn.cursor()
            cursor.execute(f"""
                BEGIN;
                DROP TABLE IF EXISTS {self.config.target_table}_old;
                ALTER TABLE {self.config.target_table} 
                    RENAME TO {self.config.target_table}_old;
                ALTER TABLE {staging_table} 
                    RENAME TO {self.config.target_table};
                COMMIT;
            """)
            
            self.metrics['rows_loaded'] = len(df)
            self.logger.info(f"Successfully loaded {len(df)} rows to {self.config.target_table}")
    
    def run(self):
        """Execute complete ETL pipeline"""
        start_time = time.time()
        
        try:
            # Initialize
            self.initialize_mappings()
            
            # Extract
            raw_df = self.extract()
            
            # Transform
            clean_df = self.transform(raw_df)
            
            # Load
            if not clean_df.empty:
                self.load(clean_df)
            else:
                self.logger.error("No valid data to load after transformation")
                
            # Report metrics
            elapsed = time.time() - start_time
            self.metrics['duration_seconds'] = elapsed
            self.logger.info(f"Pipeline completed successfully: {self.metrics}")
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise

# Usage
if __name__ == "__main__":
    config = ETLConfig.from_yaml('config/etl_config.yaml')
    pipeline = ProductionETLPipeline(config)
    pipeline.run()
```

---

## 📋 Critical Checklist

### Pre-Extraction Phase
- [ ] Analyze source file structure using openpyxl, not pandas
- [ ] Identify all merged cells and multi-row headers
- [ ] Document all coded values that need mapping
- [ ] Create/update dim_code_map table with all mappings

### Extraction Phase
- [ ] Separate metadata extraction from data extraction
- [ ] Use appropriate library for file type (openpyxl for complex Excel)
- [ ] Handle multiple encodings for international characters
- [ ] Implement retry logic for transient failures

### Transformation Phase
- [ ] Apply mapping lookups from centralized source
- [ ] Validate data types and ranges with Pydantic
- [ ] Separate valid and invalid records
- [ ] Log all transformation steps with metrics

### Loading Phase
- [ ] Use staging tables for atomic operations
- [ ] Implement bulk insert with chunking
- [ ] Create indexes after data load
- [ ] Backup previous version before overwrite

### Post-Load Phase
- [ ] Validate row counts match expectations
- [ ] Run data quality checks
- [ ] Alert on threshold violations
- [ ] Archive source files with timestamp

---

## 🚨 Common Pitfalls to Avoid

1. **Never use `pd.read_csv(header=N)` for complex headers**
   - This assumes a single row contains all information
   - Use openpyxl for metadata extraction instead

2. **Never trust the source file for human-readable names**
   - Always maintain a separate mapping table
   - Implement defensive fallbacks for unknown codes

3. **Never use bare except clauses**
   - Always catch specific exceptions
   - Log full stack traces for debugging

4. **Never load directly to production tables**
   - Always use staging tables
   - Implement atomic swap operations

5. **Never ignore data validation**
   - Use Pydantic or similar for schema enforcement
   - Separate and log invalid records

---

## 📊 Performance Optimization

```python
# For large files (>100MB)
def read_large_csv_in_chunks(file_path: str, chunk_size: int = 10000):
    """Process large CSV files in chunks to avoid memory issues"""
    
    chunks = []
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Process each chunk
        processed_chunk = transform_chunk(chunk)
        chunks.append(processed_chunk)
    
    return pd.concat(chunks, ignore_index=True)

# Use Polars for better performance
import polars as pl

def extract_with_polars(file_path: str) -> pl.DataFrame:
    """Use Polars for 10-20x faster processing"""
    return pl.read_csv(
        file_path,
        has_header=False,
        skip_rows=10,
        encoding='utf8-lossy'  # Handle encoding errors gracefully
    )
```

---

## 🔗 Additional Resources

### Libraries Used
- **pandas**: Data manipulation and analysis
- **openpyxl**: Reading/writing Excel files with complex structures
- **pydantic**: Data validation and schema enforcement  
- **polars**: High-performance DataFrame library
- **psycopg2/sqlalchemy**: Database connectivity

### Testing Strategy
```python
import pytest
from unittest.mock import Mock, patch

def test_mapping_lookup():
    """Test that mapping repository returns correct values"""
    repo = MappingRepository(mock_connection)
    assert repo.get_name('geographic', '471') == 'באר שבע'
    assert repo.get_name('geographic', '999') == 'UNKNOWN_999'

def test_multirow_header_extraction():
    """Test extraction of complex headers"""
    reader = ComplexExcelReader('test_data/complex_headers.xlsx')
    headers = reader.read_multirow_headers([0, 1, 2])
    assert len(headers.levels) == 3
    assert headers.nlevels == 3
```

---

## 📝 Configuration Template (YAML)

```yaml
# etl_config.yaml
source_path: /data/input/cbs_data.xlsx
db_connection_string: postgresql://user:pass@localhost/datawarehouse
mapping_table: dim_code_map
target_table: fact_segments

# Header configuration
header_rows: [3, 4, 5, 6]  # Rows 4-7 contain headers
data_start_row: 11          # Data starts at row 11

# Column mappings
column_mappings:
  'קוד': 'segment_code'
  'שנה': 'year'
  'חודש': 'month'
  'סכום': 'amount'

# Validation rules
validation_rules:
  year:
    min: 2020
    max: 2030
  amount:
    min: 0
    max: 1000000000

# Transformation steps
transformations:
  - name: apply_currency_conversion
    critical: true
  - name: calculate_derived_fields
    critical: false
```

---

## Conclusion

This comprehensive guide provides battle-tested patterns for building robust ETL pipelines that can handle the messiest data sources. By following these practices, you can:

- **Prevent** data corruption from misinterpreted headers
- **Ensure** consistent code-to-name translations
- **Handle** errors gracefully with proper logging
- **Scale** to handle large datasets efficiently
- **Maintain** data quality through validation

Remember: The key to successful ETL is **defensive programming** - assume the source data will be messy, plan for failures, and always maintain a clear separation between data and metadata.

**Last Updated**: November 2024  
**Version**: 1.0.0
