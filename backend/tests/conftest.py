"""
Pytest fixtures for testing MarketPulse API.

Provides test database setup, test client, mock data, and utility functions
for comprehensive testing of the API endpoints.
"""

import os
import sys
from datetime import date, datetime
from decimal import Decimal
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import DatabaseManager


# =============================================================================
# Environment Configuration
# =============================================================================

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Test database URL from environment or default."""
    # CI/CD uses DATABASE_URL, local dev uses TEST_DATABASE_URL or fallback to 5433
    return os.getenv(
        'DATABASE_URL',
        os.getenv('TEST_DATABASE_URL', 'postgresql://marketpulse_user:dev123@localhost:5433/marketpulse')
    )


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def db_engine(test_database_url: str):
    """Create test database engine (session-scoped)."""
    engine = create_engine(
        test_database_url,
        pool_pre_ping=True,
        echo=False  # Set to True for SQL query logging
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create a new database session for each test.

    Wraps each test in a transaction that is rolled back after the test completes,
    ensuring test isolation.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def db_manager(test_database_url: str) -> DatabaseManager:
    """Database manager instance for tests."""
    return DatabaseManager(database_url=test_database_url)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_transaction_data() -> dict:
    """Sample transaction record for testing."""
    return {
        "transaction_id": 99999,
        "customer_name": "Test Customer",
        "product": "מחשב נייד",
        "amount": Decimal("1500.50"),
        "currency": "ILS",
        "transaction_date": date(2025, 11, 20),
        "status": "completed"
    }


@pytest.fixture
def sample_dashboard_response() -> dict:
    """Sample dashboard response data."""
    return {
        "total_revenue": Decimal("15234567.89"),
        "total_transactions": 10000,
        "avg_order_value": Decimal("1523.46"),
        "completed_transactions": 3313,
        "pending_transactions": 3388,
        "cancelled_transactions": 3299,
        "top_products": [
            {"product": "מחשב נייד", "revenue": Decimal("5234567.89")},
            {"product": "טלפון סלולרי", "revenue": Decimal("4123456.78")}
        ],
        "recent_trend": [
            {
                "transaction_date": date(2025, 11, 20),
                "revenue": Decimal("123456.78"),
                "transaction_count": 87
            }
        ]
    }


@pytest.fixture
def sample_revenue_data() -> list:
    """Sample revenue analytics data."""
    return [
        {
            "transaction_date": date(2025, 11, 20),
            "total_revenue": Decimal("123456.78"),
            "transaction_count": 87,
            "avg_transaction_value": Decimal("1419.04"),
            "unique_customers": 65
        },
        {
            "transaction_date": date(2025, 11, 19),
            "total_revenue": Decimal("110234.56"),
            "transaction_count": 79,
            "avg_transaction_value": Decimal("1394.87"),
            "unique_customers": 62
        }
    ]


@pytest.fixture
def sample_customer_data() -> list:
    """Sample customer analytics data."""
    return [
        {
            "customer_name": "אבי כהן",
            "transaction_count": 15,
            "total_spent": Decimal("12345.67"),
            "avg_transaction": Decimal("823.04"),
            "first_purchase": date(2024, 6, 15),
            "last_purchase": date(2025, 11, 18)
        },
        {
            "customer_name": "שרה לוי",
            "transaction_count": 12,
            "total_spent": Decimal("9876.54"),
            "avg_transaction": Decimal("823.05"),
            "first_purchase": date(2024, 7, 10),
            "last_purchase": date(2025, 11, 15)
        }
    ]


@pytest.fixture
def sample_product_data() -> list:
    """Sample product performance data."""
    return [
        {
            "product": "מחשב נייד",
            "total_transactions": 2134,
            "total_revenue": Decimal("5234567.89"),
            "avg_price": Decimal("2453.21"),
            "unique_customers": 1876
        },
        {
            "product": "טלפון סלולרי",
            "total_transactions": 1987,
            "total_revenue": Decimal("4123456.78"),
            "avg_price": Decimal("2076.89"),
            "unique_customers": 1654
        }
    ]


# =============================================================================
# Test Client Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_client(db_session) -> Generator[TestClient, None, None]:
    """
    FastAPI test client with database session override.

    Overrides the database dependency to use the test database session.
    """
    from api.main import app, get_db_session

    def override_get_db_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# =============================================================================
# Database Seeding Fixtures
# =============================================================================

@pytest.fixture
def seed_test_transactions(db_session, sample_transaction_data):
    """
    Seed test database with sample transaction data.

    Creates a few test transactions for integration tests.
    """
    # Insert test transactions
    for i in range(5):
        transaction = sample_transaction_data.copy()
        transaction['transaction_id'] = 99990 + i
        transaction['customer_name'] = f"Test Customer {i+1}"

        db_session.execute(
            text("""
                INSERT INTO transactions
                (transaction_id, customer_name, product, amount, currency,
                 transaction_date, status)
                VALUES
                (:transaction_id, :customer_name, :product, :amount, :currency,
                 :transaction_date, :status)
                ON CONFLICT (transaction_id) DO NOTHING
            """),
            transaction
        )

    db_session.commit()

    yield

    # Cleanup: Remove test transactions
    db_session.execute(
        text("DELETE FROM transactions WHERE transaction_id BETWEEN 99990 AND 99999")
    )
    db_session.commit()


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def assert_response_time():
    """
    Fixture to assert API response time is under target.

    Usage:
        assert_response_time(start_time, target_ms=200)
    """
    def _assert(start_time: datetime, target_ms: int = 200):
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        assert duration_ms < target_ms, f"Response time {duration_ms:.2f}ms exceeds target {target_ms}ms"

    return _assert


@pytest.fixture
def validate_pagination():
    """
    Fixture to validate pagination response structure.

    Usage:
        validate_pagination(response_data, expected_limit=10)
    """
    def _validate(data: dict, expected_limit: int = 10, expected_offset: int = 0):
        assert "pagination" in data
        pagination = data["pagination"]
        assert pagination["limit"] == expected_limit
        assert pagination["offset"] == expected_offset
        assert pagination["total"] >= 0
        assert isinstance(pagination["total"], int)

    return _validate


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_db_connection_error(monkeypatch):
    """
    Mock database connection error for testing error handling.

    Usage:
        mock_db_connection_error(DatabaseManager, 'test_connection', False)
    """
    def _mock(cls, method_name: str, return_value=False):
        def mock_method(*args, **kwargs):
            return return_value

        monkeypatch.setattr(f"{cls.__module__}.{cls.__name__}.{method_name}", mock_method)

    return _mock
