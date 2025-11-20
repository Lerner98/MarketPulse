"""
FastAPI application for MarketPulse Analytics API.

Provides REST endpoints for e-commerce transaction analytics with
security-first approach, rate limiting, and comprehensive error handling.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
# Removed unused typing imports

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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
)
from models.database import DatabaseManager

# =============================================================================
# Configuration & Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database manager instance
db_manager = DatabaseManager()


# =============================================================================
# Lifespan Context Manager
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for database connections and cleanup.
    """
    # Startup
    logger.info("Starting MarketPulse API...")

    # Test database connection
    if not db_manager.test_connection():
        logger.error("Failed to connect to database on startup!")
        raise RuntimeError("Database connection failed")

    logger.info("Database connection established")

    yield

    # Shutdown
    logger.info("Shutting down MarketPulse API...")
    db_manager.close()
    logger.info("Database connections closed")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="MarketPulse API",
    description=(
        "E-commerce analytics platform providing "
        "REST endpoints for business intelligence"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# =============================================================================
# CORS Middleware
# =============================================================================

# Allowed origins (configure based on environment)
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
]

# Add production origins from environment if available
if prod_origin := os.getenv("FRONTEND_URL"):
    allowed_origins.append(prod_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=86400,  # 24 hours
)


# =============================================================================
# Dependency Injection
# =============================================================================


def get_db_session() -> Session:
    """
    Dependency to get database session.

    Creates a new session for each request and ensures cleanup.
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


# =============================================================================
# Error Handlers
# =============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with standard error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database error occurred",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


# =============================================================================
# API Endpoints
# =============================================================================


@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Check API and database connectivity status",
)
def health_check(db: Session = Depends(get_db_session)) -> HealthResponse:
    """
    Health check endpoint.

    Returns service status and database connectivity information.
    """
    # Test database connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check database error: {e}")
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        timestamp=datetime.now(timezone.utc),
        database=db_status,
        version="1.0.0",
    )


@app.get(
    "/api/dashboard",
    response_model=DashboardResponse,
    tags=["Analytics"],
    summary="Get dashboard overview",
    description=(
        "Aggregated metrics including revenue, transactions, "
        "top products, and trends"
    ),
)
def get_dashboard(db: Session = Depends(get_db_session)) -> DashboardResponse:
    """
    Dashboard endpoint providing aggregated business metrics.

    Returns:
    - Total revenue and transaction counts
    - Status breakdown (completed/pending/cancelled)
    - Top 5 products by revenue
    - Last 7 days revenue trend
    """
    try:
        # Get overall statistics
        overall_query = text(
            """
            SELECT
                COUNT(*) as total_transactions,
                SUM(CASE WHEN status = 'completed'
                    THEN 1 ELSE 0 END) as completed_transactions,
                SUM(CASE WHEN status = 'pending'
                    THEN 1 ELSE 0 END) as pending_transactions,
                SUM(CASE WHEN status = 'cancelled'
                    THEN 1 ELSE 0 END) as cancelled_transactions,
                SUM(CASE WHEN status = 'completed'
                    THEN amount ELSE 0 END) as total_revenue,
                AVG(CASE WHEN status = 'completed'
                    THEN amount ELSE NULL END) as avg_order_value
            FROM transactions
        """
        )
        overall_result = db.execute(overall_query).fetchone()

        # Get top 5 products by revenue
        top_products_query = text(
            """
            SELECT product, SUM(amount) as revenue
            FROM transactions
            WHERE status = 'completed'
            GROUP BY product
            ORDER BY revenue DESC
            LIMIT 5
        """
        )
        top_products_results = db.execute(top_products_query).fetchall()

        # Get last 7 days trend
        trend_query = text(
            """
            SELECT
                transaction_date as date,
                SUM(amount) as revenue,
                COUNT(*) as transaction_count
            FROM transactions
            WHERE status = 'completed'
              AND transaction_date >= CURRENT_DATE - INTERVAL '6 days'
            GROUP BY transaction_date
            ORDER BY transaction_date DESC
            LIMIT 7
        """
        )
        trend_results = db.execute(trend_query).fetchall()

        # Build response
        return DashboardResponse(
            total_revenue=Decimal(str(overall_result.total_revenue or 0)),
            total_transactions=overall_result.total_transactions or 0,
            avg_order_value=Decimal(str(overall_result.avg_order_value or 0)),
            completed_transactions=overall_result.completed_transactions or 0,
            pending_transactions=overall_result.pending_transactions or 0,
            cancelled_transactions=overall_result.cancelled_transactions or 0,
            top_products=[
                TopProductItem(product=row.product, revenue=Decimal(str(row.revenue)))
                for row in top_products_results
            ],
            recent_trend=[
                RecentTrendItem(
                    transaction_date=row.date,
                    revenue=Decimal(str(row.revenue)),
                    transaction_count=row.transaction_count,
                )
                for row in trend_results
            ],
        )

    except SQLAlchemyError as e:
        logger.error(f"Dashboard query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data",
        )


@app.get(
    "/api/revenue",
    response_model=RevenueResponse,
    tags=["Analytics"],
    summary="Get revenue analytics",
    description="Daily revenue breakdown with aggregations and trends",
)
def get_revenue(
    limit: int = Query(
        default=30, ge=1, le=365, description="Number of days to retrieve"
    ),
    db: Session = Depends(get_db_session),
) -> RevenueResponse:
    """
    Revenue analytics endpoint using v_daily_revenue view.

    Query Parameters:
    - limit: Number of days to retrieve (1-365, default: 30)

    Returns daily revenue with transaction counts and averages.
    """
    try:
        # Query v_daily_revenue view
        revenue_query = text(
            """
            SELECT
                transaction_date,
                total_revenue,
                transaction_count,
                avg_transaction_value,
                unique_customers
            FROM v_daily_revenue
            ORDER BY transaction_date DESC
            LIMIT :limit
        """
        )

        results = db.execute(revenue_query, {"limit": limit}).fetchall()

        # Calculate totals
        total_revenue = sum(Decimal(str(row.total_revenue)) for row in results)
        total_transactions = sum(row.transaction_count for row in results)
        avg_daily_revenue = total_revenue / len(results) if results else Decimal(0)

        return RevenueResponse(
            data=[
                RevenueDayItem(
                    transaction_date=row.transaction_date,
                    total_revenue=Decimal(str(row.total_revenue)),
                    transaction_count=row.transaction_count,
                    avg_transaction_value=Decimal(str(row.avg_transaction_value)),
                    unique_customers=row.unique_customers,
                )
                for row in results
            ],
            total_revenue=total_revenue,
            total_transactions=total_transactions,
            avg_daily_revenue=avg_daily_revenue,
        )

    except SQLAlchemyError as e:
        logger.error(f"Revenue query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue data",
        )


@app.get(
    "/api/customers",
    response_model=CustomersResponse,
    tags=["Analytics"],
    summary="Get customer analytics",
    description="Customer behavior analysis with pagination",
)
def get_customers(
    limit: int = Query(default=10, ge=1, le=100, description="Results per page"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    sort_by: str = Query(
        default="total_spent", pattern="^(total_spent|transaction_count|last_purchase)$"
    ),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db_session),
) -> CustomersResponse:
    """
    Customer analytics endpoint using v_customer_analytics view.

    Query Parameters:
    - limit: Results per page (1-100, default: 10)
    - offset: Pagination offset (default: 0)
    - sort_by: Sort field (total_spent, transaction_count, last_purchase)
    - order: Sort order (asc, desc)

    Returns customer data with spending patterns and transaction history.
    """
    try:
        # Get total count
        count_query = text("SELECT COUNT(*) as total FROM v_customer_analytics")
        total_count = db.execute(count_query).fetchone().total

        # Get paginated results
        customers_query = text(
            f"""
            SELECT
                customer_name,
                transaction_count,
                total_spent,
                avg_transaction,
                first_purchase,
                last_purchase
            FROM v_customer_analytics
            ORDER BY {sort_by} {order.upper()}
            LIMIT :limit OFFSET :offset
        """
        )

        results = db.execute(
            customers_query, {"limit": limit, "offset": offset}
        ).fetchall()

        return CustomersResponse(
            customers=[
                CustomerItem(
                    customer_name=row.customer_name,
                    transaction_count=row.transaction_count,
                    total_spent=Decimal(str(row.total_spent)),
                    avg_transaction=Decimal(str(row.avg_transaction)),
                    first_purchase=row.first_purchase,
                    last_purchase=row.last_purchase,
                )
                for row in results
            ],
            pagination=PaginationInfo(limit=limit, offset=offset, total=total_count),
        )

    except SQLAlchemyError as e:
        logger.error(f"Customers query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer data",
        )


@app.get(
    "/api/products",
    response_model=ProductsResponse,
    tags=["Analytics"],
    summary="Get product performance",
    description="Product sales metrics and performance analysis",
)
def get_products(db: Session = Depends(get_db_session)) -> ProductsResponse:
    """
    Product performance endpoint using v_product_performance view.

    Returns product metrics including:
    - Total transactions and revenue per product
    - Average price
    - Unique customer count
    """
    try:
        # Query v_product_performance view
        products_query = text(
            """
            SELECT
                product,
                total_transactions,
                total_revenue,
                avg_price,
                unique_customers
            FROM v_product_performance
            ORDER BY total_revenue DESC
        """
        )

        results = db.execute(products_query).fetchall()

        return ProductsResponse(
            products=[
                ProductItem(
                    product=row.product,
                    total_transactions=row.total_transactions,
                    total_revenue=Decimal(str(row.total_revenue)),
                    avg_price=Decimal(str(row.avg_price)),
                    unique_customers=row.unique_customers,
                )
                for row in results
            ]
        )

    except SQLAlchemyError as e:
        logger.error(f"Products query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product data",
        )


# =============================================================================
# Root Endpoint
# =============================================================================


@app.get(
    "/",
    tags=["Info"],
    summary="API information",
    description="Get basic API information and available endpoints",
)
def root():
    """Root endpoint providing API information."""
    return {
        "name": "MarketPulse API",
        "version": "1.0.0",
        "description": "E-commerce analytics platform",
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "dashboard": "/api/dashboard",
            "revenue": "/api/revenue",
            "customers": "/api/customers",
            "products": "/api/products",
        },
    }
