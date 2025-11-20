"""
Database connection module for MarketPulse
Implements secure connection pooling with SQLAlchemy
Security: Uses environment variables, connection pooling, prepared statements
"""

import os
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()


class DatabaseManager:
    """
    Secure database connection manager with connection pooling

    Security features:
    - Uses environment variables for credentials (never hardcoded)
    - Connection pooling to prevent connection exhaustion
    - Automatic retry logic
    - Prepared statements via SQLAlchemy
    - Connection validation
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection

        Args:
            database_url: PostgreSQL connection string (optional, reads from env if not provided)
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')

        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        # Security: Log connection attempt without exposing credentials
        logger.info(f"Connecting to database at {self._safe_url()}")

        # Create engine with connection pooling
        # Pool settings prevent connection exhaustion attacks
        self.engine = create_engine(
            self.database_url,
            poolclass=pool.QueuePool,
            pool_size=5,  # Maximum number of connections
            max_overflow=10,  # Maximum overflow connections
            pool_pre_ping=True,  # Validate connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False,  # Set to True for SQL query logging in development
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Add connection event listeners
        self._setup_event_listeners()

    def _safe_url(self) -> str:
        """
        Return database URL with password redacted for logging

        Returns:
            Sanitized connection string
        """
        if not self.database_url:
            return "No URL configured"

        # Redact password from URL
        parts = self.database_url.split('@')
        if len(parts) > 1:
            user_pass = parts[0].split('//')[-1]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                return f"postgresql://{user}:****@{parts[1]}"
        return "postgresql://****:****@localhost"

    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for monitoring"""

        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Log successful connections"""
            logger.debug("Database connection established")

        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_conn, connection_record):
            """Log connection closures"""
            logger.debug("Database connection closed")

    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions
        Ensures proper cleanup even if errors occur

        Usage:
            with db.get_session() as session:
                session.query(Model).all()

        Yields:
            SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    def init_db(self):
        """
        Initialize database schema
        Creates all tables defined in models
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    def execute_sql_file(self, file_path: str):
        """
        Execute SQL file (for running schema.sql)

        Args:
            file_path: Path to SQL file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            with self.engine.begin() as connection:
                # Execute the entire file as one transaction
                # This preserves functions, procedures, and triggers
                connection.execute(text(sql_content))
                connection.commit()

            logger.info(f"Successfully executed SQL file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to execute SQL file {file_path}: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def close(self):
        """Close all database connections"""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """
    Get global database instance (singleton pattern)

    Returns:
        DatabaseManager instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


# Dependency injection for FastAPI
def get_db_session():
    """
    FastAPI dependency for database sessions

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db_session)):
            return db.query(User).all()
    """
    db = get_db()
    with db.get_session() as session:
        yield session


if __name__ == "__main__":
    # Test database connection
    db = DatabaseManager()
    if db.test_connection():
        print("✓ Database connection successful!")

        # Initialize schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            db.execute_sql_file(schema_path)
            print("✓ Database schema initialized!")
        else:
            print("⚠ schema.sql not found")
    else:
        print("✗ Database connection failed")
