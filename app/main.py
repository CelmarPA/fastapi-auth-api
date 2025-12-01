# main.py

"""
Main application entry point for the FastAPI service.

This module initializes the FastAPI application, configures middleware
(CORS and rate limiting), sets up the database, and includes all API routers.

The application exposes a root endpoint ("/") used primarily for health checks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from typing import Any

from app.core.config import settings
from app.core.rate_limit import limiter
from app.database import engine, Base
from app.routers import auth, admin_users, products


# Initialize FastAPI instance
app: Any = FastAPI(
    title="Auth API",
    description="Authentication and product management service.",
    version="1.0.0"
)

# Attach the rate limiter instance to the FastAPI application state
# SlowAPI uses this internally to enforce request throttling
app.state.limiter = limiter

# ----------------------------------------------------------------------
# CORS Middleware
# ----------------------------------------------------------------------
# Enables cross-origin requests. Required when the frontend runs on a
# different domain or port than this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],     # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],     # allow all headers
)

# ----------------------------------------------------------------------
# Rate Limit Middleware (SlowAPI)
# ----------------------------------------------------------------------
# This middleware monitors incoming requests and enforces rate limits
# configured inside `app.core.rate_limit`.
app.add_middleware(SlowAPIMiddleware)

# ----------------------------------------------------------------------
# Database Initialization
# ----------------------------------------------------------------------
# Creates database tables defined in SQLAlchemy models if they do not exist.
Base.metadata.create_all(bind=engine)

# ----------------------------------------------------------------------
# Routers
# ----------------------------------------------------------------------
# These modules contain the application's endpoints grouped by domain logic.
app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(products.router)

# ----------------------------------------------------------------------
# Root Route
# ----------------------------------------------------------------------
@app.get("/")
def root():
    """
    Root endpoint used for health checking.

    :return: dict[str, str]: A simple JSON message confirming that the API is running.
    """

    return {"message": "Auth API is running"}
