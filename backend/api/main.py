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

# Import and register strategic V9 endpoints (REAL CBS DATA - V9 PRODUCTION)
try:
    from api.strategic_endpoints_v9 import router as strategic_router
    app.include_router(strategic_router)
    logger.info("Strategic CBS V9 endpoints registered successfully (REAL DATA - V9 PRODUCTION)")
except Exception as e:
    logger.error(f"Failed to import strategic V9 endpoints: {e}")

# Import and register V10 segmentation endpoints (NORMALIZED STAR SCHEMA - V10)
try:
    from api.segmentation_endpoints_v10 import router as v10_router
    app.include_router(v10_router)
    logger.info("V10 segmentation endpoints registered successfully (NORMALIZED STAR SCHEMA)")
except Exception as e:
    logger.error(f"Failed to import V10 segmentation endpoints: {e}")


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
