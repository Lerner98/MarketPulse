"""
Unit tests for Pydantic models.

Tests validation rules, field constraints, and model serialization.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from api.models import (
    HealthResponse,
    DashboardResponse,
    TopProductItem,
    RecentTrendItem,
    RevenueResponse,
    RevenueDayItem,
    CustomersResponse,
    CustomerItem,
    PaginationInfo,
    ProductsResponse,
    ProductItem,
    ErrorResponse,
    ErrorDetail,
)


# =============================================================================
# Health Check Model Tests
# =============================================================================


class TestHealthResponse:
    """Test HealthResponse model validation."""

    def test_valid_health_response(self):
        """Test creating valid health response."""
        data = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": "connected",
            "version": "1.0.0",
        }
        response = HealthResponse(**data)

        assert response.status == "healthy"
        assert response.database == "connected"
        assert response.version == "1.0.0"

    def test_health_response_default_version(self):
        """Test default version value."""
        data = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": "connected",
        }
        response = HealthResponse(**data)

        assert response.version == "1.0.0"

    def test_health_response_serialization(self):
        """Test JSON serialization."""
        data = {
            "status": "healthy",
            "timestamp": datetime(2025, 11, 20, 12, 0, 0),
            "database": "connected",
        }
        response = HealthResponse(**data)
        json_data = response.model_dump()

        assert json_data["status"] == "healthy"
        assert json_data["database"] == "connected"


# =============================================================================
# Dashboard Model Tests
# =============================================================================


class TestTopProductItem:
    """Test TopProductItem model validation."""

    def test_valid_top_product(self):
        """Test creating valid product item."""
        data = {"product": "מחשב נייד", "revenue": Decimal("1234.56")}
        item = TopProductItem(**data)

        assert item.product == "מחשב נייד"
        assert item.revenue == Decimal("1234.56")

    def test_negative_revenue_rejected(self):
        """Test that negative revenue is rejected."""
        data = {"product": "Test", "revenue": Decimal("-100.00")}

        with pytest.raises(ValidationError) as exc_info:
            TopProductItem(**data)

        assert "greater than or equal to 0" in str(exc_info.value).lower()


class TestRecentTrendItem:
    """Test RecentTrendItem model validation."""

    def test_valid_trend_item(self):
        """Test creating valid trend item."""
        data = {
            "date": date(2025, 11, 20),
            "revenue": Decimal("5000.00"),
            "transaction_count": 50,
        }
        item = RecentTrendItem(**data)

        assert item.transaction_date == date(2025, 11, 20)
        assert item.revenue == Decimal("5000.00")
        assert item.transaction_count == 50

    def test_negative_transaction_count_rejected(self):
        """Test that negative transaction count is rejected."""
        data = {
            "date": date(2025, 11, 20),
            "revenue": Decimal("5000.00"),
            "transaction_count": -5,
        }

        with pytest.raises(ValidationError) as exc_info:
            RecentTrendItem(**data)

        assert "greater than or equal to 0" in str(exc_info.value).lower()


class TestDashboardResponse:
    """Test DashboardResponse model validation."""

    def test_valid_dashboard_response(self, sample_dashboard_response):
        """Test creating valid dashboard response."""
        response = DashboardResponse(**sample_dashboard_response)

        assert response.total_revenue == Decimal("15234567.89")
        assert response.total_transactions == 10000
        assert len(response.top_products) == 2
        assert len(response.recent_trend) == 1

    def test_dashboard_top_products_limit(self, sample_dashboard_response):
        """Test that top_products respects max length of 5."""
        # Add more than 5 products
        sample_dashboard_response["top_products"] = [
            {"product": f"Product {i}", "revenue": Decimal(f"{i}00.00")}
            for i in range(6)
        ]

        with pytest.raises(ValidationError) as exc_info:
            DashboardResponse(**sample_dashboard_response)

        assert "at most 5 items" in str(exc_info.value).lower()

    def test_dashboard_recent_trend_limit(self, sample_dashboard_response):
        """Test that recent_trend respects max length of 7."""
        # Add more than 7 days
        sample_dashboard_response["recent_trend"] = [
            {
                "date": date(2025, 11, i),
                "revenue": Decimal("1000.00"),
                "transaction_count": 10,
            }
            for i in range(1, 9)
        ]

        with pytest.raises(ValidationError) as exc_info:
            DashboardResponse(**sample_dashboard_response)

        assert "at most 7 items" in str(exc_info.value).lower()


# =============================================================================
# Revenue Model Tests
# =============================================================================


class TestRevenueDayItem:
    """Test RevenueDayItem model validation."""

    def test_valid_revenue_day_item(self):
        """Test creating valid revenue day item."""
        data = {
            "transaction_date": date(2025, 11, 20),
            "total_revenue": Decimal("10000.00"),
            "transaction_count": 100,
            "avg_transaction_value": Decimal("100.00"),
            "unique_customers": 75,
        }
        item = RevenueDayItem(**data)

        assert item.transaction_date == date(2025, 11, 20)
        assert item.total_revenue == Decimal("10000.00")

    def test_revenue_day_item_alias_support(self):
        """Test that 'date' alias works for transaction_date."""
        data = {
            "date": date(2025, 11, 20),
            "total_revenue": Decimal("10000.00"),
            "transaction_count": 100,
            "avg_transaction_value": Decimal("100.00"),
            "unique_customers": 75,
        }
        item = RevenueDayItem(**data)

        assert item.transaction_date == date(2025, 11, 20)


class TestRevenueResponse:
    """Test RevenueResponse model validation."""

    def test_valid_revenue_response(self, sample_revenue_data):
        """Test creating valid revenue response."""
        data = {
            "data": sample_revenue_data,
            "total_revenue": Decimal("233691.34"),
            "total_transactions": 166,
            "avg_daily_revenue": Decimal("116845.67"),
        }
        response = RevenueResponse(**data)

        assert len(response.data) == 2
        assert response.total_revenue == Decimal("233691.34")
        assert response.total_transactions == 166


# =============================================================================
# Customer Model Tests
# =============================================================================


class TestCustomerItem:
    """Test CustomerItem model validation."""

    def test_valid_customer_item(self):
        """Test creating valid customer item."""
        data = {
            "customer_name": "אבי כהן",
            "transaction_count": 15,
            "total_spent": Decimal("12345.67"),
            "avg_transaction": Decimal("823.04"),
            "first_purchase": date(2024, 6, 15),
            "last_purchase": date(2025, 11, 18),
        }
        item = CustomerItem(**data)

        assert item.customer_name == "אבי כהן"
        assert item.transaction_count == 15

    def test_customer_name_max_length(self):
        """Test customer name length validation."""
        data = {
            "customer_name": "A" * 256,  # Exceeds 255 character limit
            "transaction_count": 1,
            "total_spent": Decimal("100.00"),
            "avg_transaction": Decimal("100.00"),
            "first_purchase": date(2024, 1, 1),
            "last_purchase": date(2024, 1, 1),
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerItem(**data)

        assert "at most 255 characters" in str(exc_info.value).lower()


class TestPaginationInfo:
    """Test PaginationInfo model validation."""

    def test_valid_pagination(self):
        """Test creating valid pagination info."""
        data = {"limit": 10, "offset": 0, "total": 100}
        pagination = PaginationInfo(**data)

        assert pagination.limit == 10
        assert pagination.offset == 0
        assert pagination.total == 100

    def test_limit_min_constraint(self):
        """Test limit must be at least 1."""
        data = {"limit": 0, "offset": 0, "total": 100}

        with pytest.raises(ValidationError) as exc_info:
            PaginationInfo(**data)

        assert "greater than or equal to 1" in str(exc_info.value).lower()

    def test_limit_max_constraint(self):
        """Test limit must not exceed 100."""
        data = {"limit": 101, "offset": 0, "total": 100}

        with pytest.raises(ValidationError) as exc_info:
            PaginationInfo(**data)

        assert "less than or equal to 100" in str(exc_info.value).lower()

    def test_offset_non_negative(self):
        """Test offset must be non-negative."""
        data = {"limit": 10, "offset": -1, "total": 100}

        with pytest.raises(ValidationError) as exc_info:
            PaginationInfo(**data)

        assert "greater than or equal to 0" in str(exc_info.value).lower()


class TestCustomersResponse:
    """Test CustomersResponse model validation."""

    def test_valid_customers_response(self, sample_customer_data):
        """Test creating valid customers response."""
        data = {
            "customers": sample_customer_data,
            "pagination": {"limit": 10, "offset": 0, "total": 5432},
        }
        response = CustomersResponse(**data)

        assert len(response.customers) == 2
        assert response.pagination.total == 5432


# =============================================================================
# Product Model Tests
# =============================================================================


class TestProductItem:
    """Test ProductItem model validation."""

    def test_valid_product_item(self):
        """Test creating valid product item."""
        data = {
            "product": "מחשב נייד",
            "total_transactions": 100,
            "total_revenue": Decimal("50000.00"),
            "avg_price": Decimal("500.00"),
            "unique_customers": 80,
        }
        item = ProductItem(**data)

        assert item.product == "מחשב נייד"
        assert item.total_transactions == 100


class TestProductsResponse:
    """Test ProductsResponse model validation."""

    def test_valid_products_response(self, sample_product_data):
        """Test creating valid products response."""
        data = {"products": sample_product_data}
        response = ProductsResponse(**data)

        assert len(response.products) == 2
        assert response.products[0].product == "מחשב נייד"


# =============================================================================
# Error Model Tests
# =============================================================================


class TestErrorDetail:
    """Test ErrorDetail model validation."""

    def test_valid_error_detail(self):
        """Test creating valid error detail."""
        data = {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input",
            "details": {"field": "email", "error": "Invalid format"},
        }
        error = ErrorDetail(**data)

        assert error.code == "VALIDATION_ERROR"
        assert error.message == "Invalid input"
        assert error.details == {"field": "email", "error": "Invalid format"}

    def test_error_detail_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated if not provided."""
        data = {"code": "INTERNAL_ERROR", "message": "Something went wrong"}
        error = ErrorDetail(**data)

        assert error.timestamp is not None
        assert isinstance(error.timestamp, datetime)


class TestErrorResponse:
    """Test ErrorResponse model validation."""

    def test_valid_error_response(self):
        """Test creating valid error response."""
        data = {"error": {"code": "NOT_FOUND", "message": "Resource not found"}}
        response = ErrorResponse(**data)

        assert response.error.code == "NOT_FOUND"
        assert response.error.message == "Resource not found"
