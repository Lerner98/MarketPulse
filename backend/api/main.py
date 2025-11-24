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
    description="""
    ## Israeli Household Expenditure Analytics Platform

    MarketPulse provides comprehensive REST APIs for analyzing Israeli CBS (Central Bureau of Statistics)
    Household Expenditure Survey data. Built on a normalized star schema with materialized views for
    high-performance analytics.

    ### Key Features

    - **Multi-Dimensional Analysis**: Slice spending data by 7 demographic dimensions
    - **Strategic Insights**: Pre-calculated business intelligence (inequality, burn rate, retail competition)
    - **High Performance**: < 500ms response times via materialized views and indexed queries
    - **Real CBS Data**: Israeli household expenditure survey 2022 (500+ categories)

    ### API Versions

    **V10 Segmentation API** (`/api/v10/*`) - Flexible multi-dimensional analytics
    - Dynamic segment type discovery
    - Inequality and burn rate analysis across any demographic dimension
    - Raw expenditure data for custom analysis

    **V9 Strategic API** (`/api/strategic/*`) - Curated strategic insights
    - Pre-calculated inequality gap analysis (Q1-Q5)
    - Financial pressure indicators (burn rate by quintile)
    - Retail competition analysis (traditional vs supermarket)

    ### Data Source

    Israeli Central Bureau of Statistics (CBS) - Household Expenditure Survey 2022
    - **Coverage**: 500+ expenditure categories
    - **Demographics**: 7 dimensions (Income, Age, Geography, Work Status, etc.)
    - **Currency**: ₪ (Israeli Shekels)
    - **Frequency**: Monthly spending averages

    ### Getting Started

    1. **Explore available segments**: `GET /api/v10/segments/types`
    2. **Analyze financial pressure**: `GET /api/v10/burn-rate?segment_type=Income%20Quintile`
    3. **Identify luxury goods**: `GET /api/v10/inequality/Income%20Quintile`
    4. **Strategic insights**: `GET /api/strategic/inequality-gap`

    ### Performance

    - Response times: < 200ms (strategic), < 500ms (segmentation)
    - Database: PostgreSQL 15 with materialized views
    - Caching: Frontend should cache segment metadata (rarely changes)

    ### Support

    - **Documentation**: Interactive API docs at `/docs`
    - **Alternative Docs**: ReDoc at `/redoc`
    - **Health Check**: `GET /api/health`
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "MarketPulse Analytics",
        "url": "https://github.com/yourusername/marketpulse",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check and system status endpoints",
        },
        {
            "name": "V10 Segmentation",
            "description": "Flexible multi-dimensional expenditure analysis across demographic segments. "
                          "Supports 7 segment types with dynamic discovery, inequality analysis, and burn rate calculations.",
        },
        {
            "name": "Strategic Insights V9",
            "description": "Pre-calculated strategic business insights including inequality gaps, burn rate analysis, "
                          "and retail competition (traditional vs supermarket). Optimized for executive dashboards.",
        },
        {
            "name": "Info",
            "description": "API information and metadata endpoints",
        },
        {
            "name": "Deprecated",
            "description": "Legacy endpoints maintained for backwards compatibility. Use V10 or Strategic APIs instead.",
        },
    ],
)


# =============================================================================
# CORS Middleware
# =============================================================================

# Allowed origins (configure based on environment)
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server (default)
    "http://localhost:8080",  # Vite dev server (alt port)
    "http://localhost:8081",  # Vite dev server (alt port)
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
# Include ONLY Strategic CBS Routers (REAL DATA ONLY)
# =============================================================================

# REMOVED: cbs_endpoints.router - uses FAKE synthetic transaction data
# ONLY strategic endpoints serve REAL CBS Excel data

# Import and register strategic endpoints (REAL CBS DATA)
try:
    from api.strategic_endpoints import router as strategic_router
    app.include_router(strategic_router)
    logger.info("Strategic CBS endpoints registered successfully (REAL DATA)")
except Exception as e:
    logger.error(f"Failed to import strategic endpoints: {e}")

# Import and register segmentation endpoints (NORMALIZED STAR SCHEMA)
try:
    from api.segmentation_endpoints import router as segmentation_router
    app.include_router(segmentation_router)
    logger.info("Segmentation endpoints registered successfully (NORMALIZED STAR SCHEMA)")
except Exception as e:
    logger.error(f"Failed to import segmentation endpoints: {e}")


# =============================================================================
# Dependency Injection
# =============================================================================


def get_db_session():
    """
    Dependency to get database session.

    Creates a new session for each request and ensures cleanup.
    """
    session = db_manager.SessionLocal()
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
    tags=["Deprecated"],
    summary="[DEPRECATED] Get dashboard overview",
    description="This endpoint is deprecated. Use /api/cbs/insights instead for complete business intelligence.",
    deprecated=True,
)
def get_dashboard():
    """
    DEPRECATED: This endpoint is no longer supported.

    Please use the new CBS endpoints:
    - /api/cbs/insights - Complete business intelligence
    - /api/cbs/quintiles - Income segmentation
    - /api/cbs/categories - Category performance
    - /api/cbs/cities - Geographic analysis
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "This endpoint is deprecated",
            "message": "Please use /api/cbs/insights for complete business intelligence",
            "alternatives": {
                "insights": "/api/cbs/insights",
                "quintiles": "/api/cbs/quintiles",
                "categories": "/api/cbs/categories",
                "cities": "/api/cbs/cities"
            }
        }
    )


@app.get(
    "/api/revenue",
    tags=["Deprecated"],
    summary="[DEPRECATED] Get revenue analytics",
    description="This endpoint is deprecated. Use /api/cbs/categories instead.",
    deprecated=True,
)
def get_revenue():
    """DEPRECATED: Use /api/cbs/categories for category-based revenue analysis."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "This endpoint is deprecated",
            "message": "Please use /api/cbs/categories for revenue by category",
            "alternative": "/api/cbs/categories"
        }
    )


@app.get(
    "/api/customers",
    tags=["Deprecated"],
    summary="[DEPRECATED] Get customer analytics",
    description="This endpoint is deprecated. Use /api/cbs/quintiles instead.",
    deprecated=True,
)
def get_customers():
    """DEPRECATED: Use /api/cbs/quintiles for customer segmentation by income."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "This endpoint is deprecated",
            "message": "Please use /api/cbs/quintiles for customer segmentation",
            "alternative": "/api/cbs/quintiles"
        }
    )


@app.get(
    "/api/products",
    tags=["Deprecated"],
    summary="[DEPRECATED] Get product performance",
    description="This endpoint is deprecated. Use /api/cbs/categories instead.",
    deprecated=True,
)
def get_products():
    """DEPRECATED: Use /api/cbs/categories for product category performance."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "This endpoint is deprecated",
            "message": "Please use /api/cbs/categories for product performance",
            "alternative": "/api/cbs/categories"
        }
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
