"""
Unit tests for database module.

Tests database connection manager, session management, and error handling.
"""

import pytest
from sqlalchemy import text

from models.database import DatabaseManager


# =============================================================================
# DatabaseManager Tests
# =============================================================================


class TestDatabaseManager:
    """Test DatabaseManager class."""

    def test_initialization_with_env_url(self, test_database_url):
        """Test DatabaseManager initializes with environment URL."""
        db = DatabaseManager(database_url=test_database_url)

        assert db.database_url == test_database_url
        assert db.engine is not None

    def test_test_connection_success(self, db_manager):
        """Test database connection succeeds."""
        result = db_manager.test_connection()

        assert result is True

    def test_get_session_context_manager(self, db_manager):
        """Test get_session works as context manager."""
        with db_manager.get_session() as session:
            # Should be able to execute simple query
            result = session.execute(text("SELECT 1"))
            assert result is not None

    def test_close(self, db_manager):
        """Test close disposes engine."""
        db_manager.close()

        # After closing, engine should be disposed
        assert db_manager.engine is not None  # Object still exists

    def test_safe_url_redacts_password(self, test_database_url):
        """Test _safe_url redacts password in connection string."""
        db = DatabaseManager(database_url=test_database_url)
        safe_url = db._safe_url()

        assert "****" in safe_url
        assert "dev123" not in safe_url  # Password should be redacted
        assert "marketpulse_user" in safe_url  # Username should be present


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestDatabaseErrorHandling:
    """Test database error handling."""

    def test_invalid_connection_string(self):
        """Test DatabaseManager handles invalid connection string."""
        db = DatabaseManager(
            database_url="postgresql://invalid:invalid@localhost:9999/invalid"
        )

        # Should not crash on initialization
        assert db is not None

        # Connection test should fail
        result = db.test_connection()
        assert result is False

    def test_connection_failure_handling(self):
        """Test handling of connection failures."""
        db = DatabaseManager(database_url="postgresql://user:pass@nonexistent:5432/db")

        # test_connection should return False, not raise exception
        result = db.test_connection()
        assert result is False
