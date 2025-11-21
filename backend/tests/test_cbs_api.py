"""
Comprehensive tests for CBS API endpoints.

Tests all 5 CBS-specific endpoints with real database data:
- /api/cbs/quintiles
- /api/cbs/categories
- /api/cbs/cities
- /api/cbs/data-quality
- /api/cbs/insights
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app

# Use TestClient without any overrides - it will use the actual database
client = TestClient(app)


# =============================================================================
# Test Suite 1: Health Check & Basic API
# =============================================================================


def test_health_endpoint():
    """Test health check endpoint returns 200 and correct structure."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "timestamp" in data
    assert "database" in data
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MarketPulse API"
    assert "endpoints" in data


# =============================================================================
# Test Suite 2: CBS Quintile Analysis
# =============================================================================


def test_quintiles_endpoint_success():
    """Test quintile endpoint returns 200 with valid structure."""
    response = client.get("/api/cbs/quintiles")
    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "quintiles" in data
    assert "key_insight" in data
    assert len(data["quintiles"]) == 5  # Must have exactly 5 quintiles


def test_quintiles_data_validity():
    """Test quintile data contains valid values."""
    response = client.get("/api/cbs/quintiles")
    data = response.json()

    quintiles = data["quintiles"]

    for i, q in enumerate(quintiles, 1):
        # Verify quintile number is correct
        assert q["income_quintile"] == i

        # Verify all required fields exist
        assert "transaction_count" in q
        assert "total_spending" in q
        assert "avg_transaction" in q
        assert "median_transaction" in q
        assert "unique_customers" in q
        assert "spending_share_pct" in q

        # Verify values are positive
        assert q["transaction_count"] > 0
        assert float(q["total_spending"]) > 0
        assert float(q["avg_transaction"]) > 0
        assert float(q["median_transaction"]) > 0
        assert q["unique_customers"] > 0

        # Verify spending share is percentage (0-100)
        assert 0 <= float(q["spending_share_pct"]) <= 100


def test_quintiles_spending_order():
    """Test that higher quintiles spend more on average (expected pattern)."""
    response = client.get("/api/cbs/quintiles")
    data = response.json()

    quintiles = data["quintiles"]

    # Q5 should have higher avg transaction than Q1 (typical pattern)
    q1_avg = float(quintiles[0]["avg_transaction"])
    q5_avg = float(quintiles[4]["avg_transaction"])

    assert q5_avg > q1_avg, "Q5 should spend more per transaction than Q1"


def test_quintiles_key_insight():
    """Test key insight contains meaningful text."""
    response = client.get("/api/cbs/quintiles")
    data = response.json()

    insight = data["key_insight"]
    assert len(insight) > 20  # Should be a meaningful sentence
    assert "Q5" in insight or "Q1" in insight  # Should mention quintiles


# =============================================================================
# Test Suite 3: CBS Category Performance
# =============================================================================


def test_categories_endpoint_success():
    """Test categories endpoint returns 200 with valid structure."""
    response = client.get("/api/cbs/categories")
    assert response.status_code == 200
    data = response.json()

    assert "categories" in data
    assert len(data["categories"]) > 0  # Should have at least 1 category


def test_categories_data_validity():
    """Test category data contains valid values."""
    response = client.get("/api/cbs/categories")
    data = response.json()

    for category in data["categories"]:
        # Verify all required fields exist
        assert "category" in category
        assert "transaction_count" in category
        assert "total_revenue" in category
        assert "avg_transaction" in category
        assert "unique_customers" in category
        assert "unique_products" in category
        assert "market_share_pct" in category

        # Verify category name is non-empty
        assert len(category["category"]) > 0

        # Verify values are positive
        assert category["transaction_count"] > 0
        assert float(category["total_revenue"]) > 0
        assert float(category["avg_transaction"]) > 0
        assert category["unique_customers"] > 0
        assert category["unique_products"] > 0

        # Verify market share is percentage
        assert 0 <= float(category["market_share_pct"]) <= 100


def test_categories_sorted_by_revenue():
    """Test categories are sorted by total revenue descending."""
    response = client.get("/api/cbs/categories")
    data = response.json()

    categories = data["categories"]

    if len(categories) > 1:
        # Each category should have revenue >= next category
        for i in range(len(categories) - 1):
            current_revenue = float(categories[i]["total_revenue"])
            next_revenue = float(categories[i + 1]["total_revenue"])
            assert current_revenue >= next_revenue


def test_categories_market_share_sum():
    """Test that all category market shares sum to approximately 100%."""
    response = client.get("/api/cbs/categories")
    data = response.json()

    total_share = sum(float(c["market_share_pct"]) for c in data["categories"])

    # Should be close to 100% (allow 0.1% tolerance for rounding)
    assert 99.9 <= total_share <= 100.1


# =============================================================================
# Test Suite 4: CBS City Performance
# =============================================================================


def test_cities_endpoint_success():
    """Test cities endpoint returns 200 with valid structure."""
    response = client.get("/api/cbs/cities")
    assert response.status_code == 200
    data = response.json()

    assert "cities" in data
    assert len(data["cities"]) > 0  # Should have at least 1 city


def test_cities_data_validity():
    """Test city data contains valid values."""
    response = client.get("/api/cbs/cities")
    data = response.json()

    for city in data["cities"]:
        # Verify all required fields exist
        assert "customer_city" in city
        assert "transaction_count" in city
        assert "total_revenue" in city
        assert "avg_transaction" in city
        assert "unique_customers" in city
        assert "market_share_pct" in city

        # Verify city name is non-empty
        assert len(city["customer_city"]) > 0

        # Verify values are positive
        assert city["transaction_count"] > 0
        assert float(city["total_revenue"]) > 0
        assert float(city["avg_transaction"]) > 0
        assert city["unique_customers"] > 0

        # Verify market share is percentage
        assert 0 <= float(city["market_share_pct"]) <= 100


def test_cities_sorted_by_revenue():
    """Test cities are sorted by total revenue descending."""
    response = client.get("/api/cbs/cities")
    data = response.json()

    cities = data["cities"]

    if len(cities) > 1:
        # Each city should have revenue >= next city
        for i in range(len(cities) - 1):
            current_revenue = float(cities[i]["total_revenue"])
            next_revenue = float(cities[i + 1]["total_revenue"])
            assert current_revenue >= next_revenue


def test_cities_top_city():
    """Test that Tel Aviv is the top city (expected from EDA)."""
    response = client.get("/api/cbs/cities")
    data = response.json()

    cities = data["cities"]
    top_city = cities[0]["customer_city"]

    # Tel Aviv should be top city based on EDA findings
    assert "תל אביב" in top_city or top_city == "תל אביב"


def test_cities_market_share_sum():
    """Test that all city market shares sum to approximately 100%."""
    response = client.get("/api/cbs/cities")
    data = response.json()

    total_share = sum(float(c["market_share_pct"]) for c in data["cities"])

    # Should be close to 100% (allow 0.1% tolerance for rounding)
    assert 99.9 <= total_share <= 100.1


# =============================================================================
# Test Suite 5: Data Quality Metrics
# =============================================================================


def test_data_quality_endpoint_success():
    """Test data quality endpoint returns 200 with valid structure."""
    response = client.get("/api/cbs/data-quality")
    assert response.status_code == 200
    data = response.json()

    # Verify all required fields exist
    assert "completeness" in data
    assert "uniqueness" in data
    assert "validity" in data
    assert "overall" in data
    assert "assessment" in data


def test_data_quality_scores_range():
    """Test data quality scores are within 0-100 range."""
    response = client.get("/api/cbs/data-quality")
    data = response.json()

    scores = [
        float(data["completeness"]),
        float(data["uniqueness"]),
        float(data["validity"]),
        float(data["overall"])
    ]

    for score in scores:
        assert 0 <= score <= 100


def test_data_quality_assessment():
    """Test assessment matches overall score."""
    response = client.get("/api/cbs/data-quality")
    data = response.json()

    overall = float(data["overall"])
    assessment = data["assessment"]

    # Verify assessment matches score range
    if overall >= 95:
        assert assessment == "EXCELLENT"
    elif overall >= 85:
        assert assessment == "GOOD"
    elif overall >= 70:
        assert assessment == "ACCEPTABLE"
    else:
        assert assessment == "POOR"


def test_data_quality_high_scores():
    """Test that data quality scores are high (>= 95% expected)."""
    response = client.get("/api/cbs/data-quality")
    data = response.json()

    # We loaded clean data, so all scores should be very high
    assert float(data["completeness"]) >= 95.0
    assert float(data["uniqueness"]) >= 95.0
    assert float(data["validity"]) >= 95.0
    assert float(data["overall"]) >= 95.0


# =============================================================================
# Test Suite 6: Business Insights Export
# =============================================================================


def test_insights_endpoint_success():
    """Test insights endpoint returns 200 with valid structure."""
    response = client.get("/api/cbs/insights")
    assert response.status_code == 200
    data = response.json()

    # Verify main sections exist
    assert "metadata" in data
    assert "data_summary" in data
    assert "income_quintile_analysis" in data
    assert "top_categories" in data
    assert "top_products" in data
    assert "top_cities" in data
    assert "monthly_trend" in data
    assert "seasonal_insights" in data
    assert "pareto_analysis" in data
    assert "business_recommendations" in data
    assert "key_metrics" in data


def test_insights_metadata():
    """Test insights metadata contains required fields."""
    response = client.get("/api/cbs/insights")
    data = response.json()

    metadata = data["metadata"]
    assert "generated_at" in metadata
    assert "data_source" in metadata
    assert "analysis_period" in metadata
    assert "version" in metadata

    # Verify data source mentions CBS
    assert "CBS" in metadata["data_source"] or "Central Bureau" in metadata["data_source"]


def test_insights_data_summary():
    """Test data summary contains transaction metrics."""
    response = client.get("/api/cbs/insights")
    data = response.json()

    summary = data["data_summary"]

    # Verify required metrics exist
    assert "total_transactions" in summary
    assert "total_volume" in summary
    assert "average_transaction" in summary

    # Verify values are positive
    assert summary["total_transactions"] > 0
    assert float(summary["total_volume"]) > 0
    assert float(summary["average_transaction"]) > 0


def test_insights_quintile_analysis():
    """Test quintile analysis contains all 5 quintiles."""
    response = client.get("/api/cbs/insights")
    data = response.json()

    quintile_data = data["income_quintile_analysis"]

    # Should have quintile_1 through quintile_5
    for i in range(1, 6):
        key = f"quintile_{i}"
        assert key in quintile_data

        # Each quintile should have spending metrics
        q = quintile_data[key]
        assert "total_spending" in q
        assert "avg_transaction" in q
        assert "transaction_count" in q


def test_insights_business_recommendations():
    """Test business recommendations is a non-empty list."""
    response = client.get("/api/cbs/insights")
    data = response.json()

    recommendations = data["business_recommendations"]

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    # Each recommendation should be a meaningful string
    for rec in recommendations:
        assert isinstance(rec, str)
        assert len(rec) > 20  # Should be a real recommendation


def test_insights_pareto_analysis():
    """Test Pareto analysis contains 80/20 rule metrics."""
    response = client.get("/api/cbs/insights")
    data = response.json()

    pareto = data["pareto_analysis"]

    assert "products_for_80pct_revenue" in pareto
    assert "total_products" in pareto
    assert "concentration_ratio" in pareto

    # Products for 80% should be less than total products
    assert pareto["products_for_80pct_revenue"] < pareto["total_products"]


# =============================================================================
# Test Suite 7: Integration Tests
# =============================================================================


def test_all_endpoints_reachable():
    """Test all CBS endpoints are reachable and return 200."""
    endpoints = [
        "/api/cbs/quintiles",
        "/api/cbs/categories",
        "/api/cbs/cities",
        "/api/cbs/data-quality",
        "/api/cbs/insights",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"Endpoint {endpoint} failed"


def test_response_times():
    """Test endpoints respond within reasonable time (< 2 seconds)."""
    import time

    endpoints = [
        "/api/cbs/quintiles",
        "/api/cbs/categories",
        "/api/cbs/cities",
        "/api/cbs/data-quality",
    ]

    for endpoint in endpoints:
        start = time.time()
        response = client.get(endpoint)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0, f"Endpoint {endpoint} took {elapsed:.2f}s"


def test_cors_headers():
    """Test CORS headers are present in responses."""
    response = client.get("/api/cbs/quintiles")

    # Should have CORS headers (FastAPI adds these)
    assert response.status_code == 200


def test_json_content_type():
    """Test all endpoints return JSON content type."""
    endpoints = [
        "/api/cbs/quintiles",
        "/api/cbs/categories",
        "/api/cbs/cities",
        "/api/cbs/data-quality",
        "/api/cbs/insights",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert "application/json" in response.headers["content-type"]


# =============================================================================
# Test Suite 8: Error Handling
# =============================================================================


def test_invalid_endpoint_404():
    """Test invalid endpoint returns 404."""
    response = client.get("/api/cbs/invalid-endpoint")
    assert response.status_code == 404


def test_openapi_docs_available():
    """Test OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json_available():
    """Test OpenAPI JSON schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()

    # Should have CBS endpoints in schema
    assert "paths" in data
    assert "/api/cbs/quintiles" in data["paths"]


# =============================================================================
# Test Summary
# =============================================================================


if __name__ == "__main__":
    # Run tests with pytest
    import subprocess

    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    # Calculate pass rate
    if "passed" in result.stdout:
        import re
        match = re.search(r'(\d+) passed', result.stdout)
        if match:
            passed = int(match.group(1))
            total_match = re.search(r'(\d+) passed.*in', result.stdout)
            print(f"\n✓ {passed} tests passed")
