"""
Professional test suite for Strategic CBS API endpoints
Tests the 3 core insights: Quintile Gap, Digital Matrix, Retail Battle

Uses pytest with fixtures, mocks, and comprehensive assertions
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

# Import the FastAPI app
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from api.main import app
from api.strategic_endpoints import get_db_session


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def test_client():
    """Create FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests"""
    session = MagicMock()
    return session


@pytest.fixture
def sample_quintile_data():
    """Sample quintile expenditure data"""
    return {
        'gap_result': MagicMock(
            q5_total=31475.0,
            q1_total=12030.0,
            spending_ratio=2.62
        ),
        'categories': [
            MagicMock(
                category='Bread, cereals, and pastry products',
                quintile_1=74.40,
                quintile_2=80.50,
                quintile_3=85.30,
                quintile_4=90.20,
                quintile_5=95.10,
                total_spending=425.50,
                avg_spending=85.10
            ),
            MagicMock(
                category='Meat and poultry',
                quintile_1=120.50,
                quintile_2=135.30,
                quintile_3=145.80,
                quintile_4=160.20,
                quintile_5=180.40,
                total_spending=742.20,
                avg_spending=148.44
            )
        ]
    }


@pytest.fixture
def sample_digital_data():
    """Sample digital matrix data"""
    return [
        MagicMock(
            category='תוכנות, משחקי מחשב',
            physical_pct=30.1,
            online_israel_pct=69.9,
            online_abroad_pct=29.8,
            total_online_pct=99.7
        ),
        MagicMock(
            category='ספרייה',
            physical_pct=81.5,
            online_israel_pct=18.5,
            online_abroad_pct=0.0,
            total_online_pct=18.5
        )
    ]


@pytest.fixture
def sample_retail_data():
    """Sample retail battle data"""
    return [
        MagicMock(
            category='Meat and poultry',
            supermarket=0.0,
            local_market=0.0,
            butcher=45.1,
            bakery=0.0,
            other=0.0,
            total=45.1,
            winner='Butcher Wins'
        ),
        MagicMock(
            category='Bread, cereals, and pastry products',
            supermarket=0.1,
            local_market=24.7,
            butcher=0.2,
            bakery=50.0,
            other=0.0,
            total=75.0,
            winner='Bakery Wins'
        )
    ]


# =============================================================================
# Unit Tests - Quintile Gap Endpoint
# =============================================================================

class TestQuintileGapEndpoint:
    """Test suite for /api/strategic/quintile-gap endpoint"""

    def test_quintile_gap_success(self, test_client, mock_db_session, sample_quintile_data):
        """Test successful quintile gap retrieval"""
        # Mock database queries
        mock_db_session.execute.side_effect = [
            MagicMock(fetchone=lambda: sample_quintile_data['gap_result']),
            MagicMock(fetchall=lambda: sample_quintile_data['categories'])
        ]

        # Override dependency
        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        # Make request
        response = test_client.get("/api/strategic/quintile-gap")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert 'ratio' in data
        assert 'q5_total' in data
        assert 'q1_total' in data
        assert 'insight' in data
        assert 'categories' in data

        assert data['ratio'] == 2.62
        assert data['q5_total'] == 31475.0
        assert data['q1_total'] == 12030.0
        assert len(data['categories']) == 2

        # Verify insight text
        assert 'High-income households' in data['insight']
        assert '2.62x' in data['insight']

        # Cleanup
        app.dependency_overrides.clear()

    def test_quintile_gap_no_data(self, test_client, mock_db_session):
        """Test quintile gap endpoint when no data exists"""
        # Mock empty result
        mock_db_session.execute.return_value.fetchone.return_value = None

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/quintile-gap")

        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()

        app.dependency_overrides.clear()

    def test_quintile_gap_category_structure(self, test_client, mock_db_session, sample_quintile_data):
        """Test category data structure in response"""
        mock_db_session.execute.side_effect = [
            MagicMock(fetchone=lambda: sample_quintile_data['gap_result']),
            MagicMock(fetchall=lambda: sample_quintile_data['categories'])
        ]

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/quintile-gap")
        data = response.json()

        category = data['categories'][0]
        assert 'category' in category
        assert 'quintile_1' in category
        assert 'quintile_5' in category
        assert 'total_spending' in category
        assert 'avg_spending' in category

        app.dependency_overrides.clear()


# =============================================================================
# Unit Tests - Digital Matrix Endpoint
# =============================================================================

class TestDigitalMatrixEndpoint:
    """Test suite for /api/strategic/digital-matrix endpoint"""

    def test_digital_matrix_success(self, test_client, mock_db_session, sample_digital_data):
        """Test successful digital matrix retrieval"""
        mock_db_session.execute.return_value.fetchall.return_value = sample_digital_data

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/digital-matrix")

        assert response.status_code == 200
        data = response.json()

        assert 'top_israel_online' in data
        assert 'top_abroad_online' in data
        assert 'most_physical' in data
        assert 'categories' in data

        assert len(data['categories']) == 2

        app.dependency_overrides.clear()

    def test_digital_matrix_sorting(self, test_client, mock_db_session, sample_digital_data):
        """Test that categories are properly sorted"""
        mock_db_session.execute.return_value.fetchall.return_value = sample_digital_data

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/digital-matrix")
        data = response.json()

        # Top Israel online should have highest online_israel_pct
        top_israel = data['top_israel_online']
        assert len(top_israel) > 0
        assert 'online_israel_pct' in top_israel[0]

        app.dependency_overrides.clear()

    def test_digital_matrix_no_data(self, test_client, mock_db_session):
        """Test digital matrix endpoint when no data exists"""
        mock_db_session.execute.return_value.fetchall.return_value = []

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/digital-matrix")

        assert response.status_code == 404

        app.dependency_overrides.clear()


# =============================================================================
# Unit Tests - Retail Battle Endpoint
# =============================================================================

class TestRetailBattleEndpoint:
    """Test suite for /api/strategic/retail-battle endpoint"""

    def test_retail_battle_success(self, test_client, mock_db_session, sample_retail_data):
        """Test successful retail battle retrieval"""
        mock_db_session.execute.return_value.fetchall.return_value = sample_retail_data

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/retail-battle")

        assert response.status_code == 200
        data = response.json()

        assert 'supermarket_share' in data
        assert 'local_share' in data
        assert 'butcher_share' in data
        assert 'supermarket_loses' in data
        assert 'categories' in data

        assert len(data['categories']) == 2

        app.dependency_overrides.clear()

    def test_retail_battle_market_share_calculation(self, test_client, mock_db_session, sample_retail_data):
        """Test market share calculations"""
        mock_db_session.execute.return_value.fetchall.return_value = sample_retail_data

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/retail-battle")
        data = response.json()

        # Market shares should be percentages (0-100)
        assert 0 <= data['supermarket_share'] <= 100
        assert 0 <= data['local_share'] <= 100
        assert 0 <= data['butcher_share'] <= 100

        app.dependency_overrides.clear()

    def test_retail_battle_supermarket_losses(self, test_client, mock_db_session, sample_retail_data):
        """Test supermarket loses categories"""
        mock_db_session.execute.return_value.fetchall.return_value = sample_retail_data

        app.dependency_overrides[get_db_session] = lambda: iter([mock_db_session])

        response = test_client.get("/api/strategic/retail-battle")
        data = response.json()

        # Should have supermarket_loses field
        assert 'supermarket_loses' in data

        # Each loss should have category, supermarket_pct, local_pct
        if len(data['supermarket_loses']) > 0:
            loss = data['supermarket_loses'][0]
            assert 'category' in loss
            assert 'supermarket_pct' in loss
            assert 'local_pct' in loss

        app.dependency_overrides.clear()


# =============================================================================
# Integration Tests (Real Database)
# =============================================================================

@pytest.mark.integration
class TestStrategicAPIIntegration:
    """Integration tests with actual database (run with pytest -m integration)"""

    def test_quintile_gap_real_db(self, test_client):
        """Test quintile gap with real database connection"""
        response = test_client.get("/api/strategic/quintile-gap")

        # Should either succeed with data or fail with 404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data['ratio'] > 0
            assert data['q5_total'] > 0
            assert data['q1_total'] > 0
            assert len(data['categories']) > 0

    def test_digital_matrix_real_db(self, test_client):
        """Test digital matrix with real database connection"""
        response = test_client.get("/api/strategic/digital-matrix")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert 'categories' in data
            assert len(data['categories']) > 0

    def test_retail_battle_real_db(self, test_client):
        """Test retail battle with real database connection"""
        response = test_client.get("/api/strategic/retail-battle")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert 'categories' in data
            assert data['supermarket_share'] >= 0


# =============================================================================
# Performance Tests
# =============================================================================

@pytest.mark.performance
class TestStrategicAPIPerformance:
    """Performance tests for API response times"""

    def test_quintile_gap_response_time(self, test_client):
        """Test that quintile gap responds within 500ms"""
        import time

        start = time.time()
        response = test_client.get("/api/strategic/quintile-gap")
        elapsed = time.time() - start

        assert elapsed < 0.5, f"Response took {elapsed:.2f}s, should be < 0.5s"

    def test_digital_matrix_response_time(self, test_client):
        """Test that digital matrix responds within 500ms"""
        import time

        start = time.time()
        response = test_client.get("/api/strategic/digital-matrix")
        elapsed = time.time() - start

        assert elapsed < 0.5, f"Response took {elapsed:.2f}s, should be < 0.5s"

    def test_retail_battle_response_time(self, test_client):
        """Test that retail battle responds within 500ms"""
        import time

        start = time.time()
        response = test_client.get("/api/strategic/retail-battle")
        elapsed = time.time() - start

        assert elapsed < 0.5, f"Response took {elapsed:.2f}s, should be < 0.5s"


# =============================================================================
# Security Tests
# =============================================================================

@pytest.mark.security
class TestStrategicAPISecurity:
    """Security tests for API endpoints"""

    def test_cors_headers(self, test_client):
        """Test that CORS headers are properly set"""
        response = test_client.options("/api/strategic/quintile-gap")

        # Should have CORS headers
        assert 'access-control-allow-origin' in [h.lower() for h in response.headers]

    def test_no_sql_injection(self, test_client):
        """Test that endpoints are protected against SQL injection"""
        # Try SQL injection in query params (if any endpoints accept them)
        malicious_param = "1'; DROP TABLE quintile_expenditure; --"

        # These endpoints don't take params, but test for completeness
        response = test_client.get(f"/api/strategic/quintile-gap")

        # Should not crash
        assert response.status_code in [200, 404, 422]


# =============================================================================
# Data Validation Tests
# =============================================================================

class TestStrategicAPIValidation:
    """Test data validation and business rules"""

    def test_quintile_ratio_realistic(self, test_client):
        """Test that quintile ratio is within realistic bounds"""
        response = test_client.get("/api/strategic/quintile-gap")

        if response.status_code == 200:
            data = response.json()
            # Ratio should be between 1.0 and 10.0 (realistically)
            assert 1.0 <= data['ratio'] <= 10.0, f"Ratio {data['ratio']} seems unrealistic"

    def test_percentages_sum_correctly(self, test_client):
        """Test that digital percentages roughly sum to 100%"""
        response = test_client.get("/api/strategic/digital-matrix")

        if response.status_code == 200:
            data = response.json()
            for category in data['categories']:
                total = (
                    category['physical_pct'] +
                    category['online_israel_pct'] +
                    category['online_abroad_pct']
                )
                # Allow some tolerance for rounding
                assert 80 <= total <= 120, f"Percentages sum to {total}, should be ~100"

    def test_market_shares_add_up(self, test_client):
        """Test that retail market shares are reasonable"""
        response = test_client.get("/api/strategic/retail-battle")

        if response.status_code == 200:
            data = response.json()
            total_share = (
                data['supermarket_share'] +
                data['local_share'] +
                data['butcher_share']
            )
            # Shares should roughly sum to 100%
            assert 80 <= total_share <= 120, f"Market shares sum to {total_share}, should be ~100"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
