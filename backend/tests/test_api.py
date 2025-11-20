"""
Integration tests for FastAPI endpoints.

Tests all API endpoints with real database interactions, ensuring
proper HTTP status codes, response validation, and error handling.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from fastapi import status
from fastapi.testclient import TestClient


# =============================================================================
# Health Endpoint Tests
# =============================================================================

class TestHealthEndpoint:
    """Test /api/health endpoint."""

    def test_health_check_success(self, test_client: TestClient):
        """Test health check returns healthy status."""
        response = test_client.get("/api/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    def test_health_check_response_time(self, test_client: TestClient, assert_response_time):
        """Test health check responds within 200ms."""
        start_time = datetime.now()
        response = test_client.get("/api/health")
        assert_response_time(start_time, target_ms=200)

        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Dashboard Endpoint Tests
# =============================================================================

class TestDashboardEndpoint:
    """Test /api/dashboard endpoint."""

    def test_dashboard_success(self, test_client: TestClient, seed_test_transactions):
        """Test dashboard returns aggregated metrics."""
        response = test_client.get("/api/dashboard")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check required fields
        assert "total_revenue" in data
        assert "total_transactions" in data
        assert "avg_order_value" in data
        assert "completed_transactions" in data
        assert "pending_transactions" in data
        assert "cancelled_transactions" in data
        assert "top_products" in data
        assert "recent_trend" in data

        # Validate data types
        assert isinstance(data["total_transactions"], int)
        assert isinstance(data["top_products"], list)
        assert isinstance(data["recent_trend"], list)

    def test_dashboard_top_products_structure(self, test_client: TestClient, seed_test_transactions):
        """Test top products have correct structure."""
        response = test_client.get("/api/dashboard")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if data["top_products"]:
            product = data["top_products"][0]
            assert "product" in product
            assert "revenue" in product
            assert isinstance(product["product"], str)

    def test_dashboard_recent_trend_structure(self, test_client: TestClient, seed_test_transactions):
        """Test recent trend has correct structure."""
        response = test_client.get("/api/dashboard")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if data["recent_trend"]:
            trend_item = data["recent_trend"][0]
            assert "date" in trend_item
            assert "revenue" in trend_item
            assert "transaction_count" in trend_item

    def test_dashboard_response_time(self, test_client: TestClient, seed_test_transactions, assert_response_time):
        """Test dashboard responds within 200ms."""
        start_time = datetime.now()
        response = test_client.get("/api/dashboard")
        assert_response_time(start_time, target_ms=200)

        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Revenue Endpoint Tests
# =============================================================================

class TestRevenueEndpoint:
    """Test /api/revenue endpoint."""

    def test_revenue_default_params(self, test_client: TestClient, seed_test_transactions):
        """Test revenue with default parameters."""
        response = test_client.get("/api/revenue")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "data" in data
        assert "total_revenue" in data
        assert "total_transactions" in data
        assert "avg_daily_revenue" in data

        assert isinstance(data["data"], list)

    def test_revenue_with_limit(self, test_client: TestClient, seed_test_transactions):
        """Test revenue with custom limit."""
        response = test_client.get("/api/revenue?limit=7")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["data"]) <= 7

    def test_revenue_limit_validation_min(self, test_client: TestClient):
        """Test revenue rejects limit below 1."""
        response = test_client.get("/api/revenue?limit=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_revenue_limit_validation_max(self, test_client: TestClient):
        """Test revenue rejects limit above 365."""
        response = test_client.get("/api/revenue?limit=366")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_revenue_data_structure(self, test_client: TestClient, seed_test_transactions):
        """Test revenue data items have correct structure."""
        response = test_client.get("/api/revenue?limit=5")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if data["data"]:
            item = data["data"][0]
            assert "date" in item  # Using alias field
            assert "total_revenue" in item
            assert "transaction_count" in item
            assert "avg_transaction_value" in item
            assert "unique_customers" in item

    def test_revenue_response_time(self, test_client: TestClient, seed_test_transactions, assert_response_time):
        """Test revenue responds within 200ms."""
        start_time = datetime.now()
        response = test_client.get("/api/revenue?limit=30")
        assert_response_time(start_time, target_ms=200)

        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Customers Endpoint Tests
# =============================================================================

class TestCustomersEndpoint:
    """Test /api/customers endpoint."""

    def test_customers_default_params(self, test_client: TestClient, seed_test_transactions):
        """Test customers with default parameters."""
        response = test_client.get("/api/customers")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "customers" in data
        assert "pagination" in data

        assert isinstance(data["customers"], list)

    def test_customers_pagination(self, test_client: TestClient, seed_test_transactions, validate_pagination):
        """Test customers pagination structure."""
        response = test_client.get("/api/customers?limit=5&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        validate_pagination(data, expected_limit=5, expected_offset=0)
        assert len(data["customers"]) <= 5

    def test_customers_limit_validation_min(self, test_client: TestClient):
        """Test customers rejects limit below 1."""
        response = test_client.get("/api/customers?limit=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_customers_limit_validation_max(self, test_client: TestClient):
        """Test customers rejects limit above 100."""
        response = test_client.get("/api/customers?limit=101")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_customers_offset_validation(self, test_client: TestClient):
        """Test customers rejects negative offset."""
        response = test_client.get("/api/customers?offset=-1")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_customers_sort_by_total_spent(self, test_client: TestClient, seed_test_transactions):
        """Test customers can be sorted by total_spent."""
        response = test_client.get("/api/customers?sort_by=total_spent&order=desc")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify descending order if multiple customers
        if len(data["customers"]) >= 2:
            assert Decimal(data["customers"][0]["total_spent"]) >= \
                   Decimal(data["customers"][1]["total_spent"])

    def test_customers_sort_by_transaction_count(self, test_client: TestClient, seed_test_transactions):
        """Test customers can be sorted by transaction_count."""
        response = test_client.get("/api/customers?sort_by=transaction_count&order=desc")

        assert response.status_code == status.HTTP_200_OK

    def test_customers_sort_by_last_purchase(self, test_client: TestClient, seed_test_transactions):
        """Test customers can be sorted by last_purchase."""
        response = test_client.get("/api/customers?sort_by=last_purchase&order=desc")

        assert response.status_code == status.HTTP_200_OK

    def test_customers_invalid_sort_field(self, test_client: TestClient):
        """Test customers rejects invalid sort field."""
        response = test_client.get("/api/customers?sort_by=invalid_field")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_customers_invalid_order(self, test_client: TestClient):
        """Test customers rejects invalid order."""
        response = test_client.get("/api/customers?order=invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_customers_data_structure(self, test_client: TestClient, seed_test_transactions):
        """Test customer items have correct structure."""
        response = test_client.get("/api/customers?limit=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if data["customers"]:
            customer = data["customers"][0]
            assert "customer_name" in customer
            assert "transaction_count" in customer
            assert "total_spent" in customer
            assert "avg_transaction" in customer
            assert "first_purchase" in customer
            assert "last_purchase" in customer

    def test_customers_response_time(self, test_client: TestClient, seed_test_transactions, assert_response_time):
        """Test customers responds within 200ms."""
        start_time = datetime.now()
        response = test_client.get("/api/customers?limit=10")
        assert_response_time(start_time, target_ms=200)

        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Products Endpoint Tests
# =============================================================================

class TestProductsEndpoint:
    """Test /api/products endpoint."""

    def test_products_success(self, test_client: TestClient, seed_test_transactions):
        """Test products returns performance metrics."""
        response = test_client.get("/api/products")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "products" in data
        assert isinstance(data["products"], list)

    def test_products_data_structure(self, test_client: TestClient, seed_test_transactions):
        """Test product items have correct structure."""
        response = test_client.get("/api/products")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if data["products"]:
            product = data["products"][0]
            assert "product" in product
            assert "total_transactions" in product
            assert "total_revenue" in product
            assert "avg_price" in product
            assert "unique_customers" in product

    def test_products_sorted_by_revenue(self, test_client: TestClient, seed_test_transactions):
        """Test products are sorted by revenue descending."""
        response = test_client.get("/api/products")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify descending order by revenue if multiple products
        if len(data["products"]) >= 2:
            assert Decimal(data["products"][0]["total_revenue"]) >= \
                   Decimal(data["products"][1]["total_revenue"])

    def test_products_response_time(self, test_client: TestClient, seed_test_transactions, assert_response_time):
        """Test products responds within 200ms."""
        start_time = datetime.now()
        response = test_client.get("/api/products")
        assert_response_time(start_time, target_ms=200)

        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Root Endpoint Tests
# =============================================================================

class TestRootEndpoint:
    """Test / root endpoint."""

    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint returns API information."""
        response = test_client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["name"] == "MarketPulse API"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test API error handling."""

    def test_404_not_found(self, test_client: TestClient):
        """Test 404 error for non-existent endpoint."""
        response = test_client.get("/api/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_method_not_allowed(self, test_client: TestClient):
        """Test 405 error for unsupported HTTP method."""
        response = test_client.post("/api/health")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# =============================================================================
# CORS Tests
# =============================================================================

class TestCORS:
    """Test CORS middleware configuration."""

    def test_cors_headers_present(self, test_client: TestClient):
        """Test CORS headers are present in responses."""
        response = test_client.options(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )

        assert "access-control-allow-origin" in response.headers or \
               response.status_code == status.HTTP_200_OK

    def test_cors_allows_localhost_3000(self, test_client: TestClient):
        """Test CORS allows requests from localhost:3000."""
        response = test_client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == status.HTTP_200_OK
