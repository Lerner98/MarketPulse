"""
Pytest configuration and fixtures for CBS API tests.
"""
import sys
import pytest
from pathlib import Path
from sqlalchemy import text

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import DatabaseManager


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Session-level fixture to ensure database schema is ready before any tests run.
    """
    db = DatabaseManager()

    with db.engine.begin() as conn:
        # Refresh all materialized views
        views = ['mv_quintile_analysis', 'mv_category_performance', 'mv_city_performance', 'mv_daily_revenue']

        for view in views:
            try:
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                print(f"✓ Refreshed {view}")
            except Exception as e:
                print(f"⚠ Could not refresh {view}: {e}")

    yield db
