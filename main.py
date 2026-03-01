"""
Main FastAPI Application Entry Point
=====================================

This is the core entry point for the Rizwan Universal AI backend server.
It initializes the FastAPI application, configures middleware, sets up CORS,
and includes all API routers for different features.

Author: Manus AI
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

# Import routers
from routes import auth, users, files, ai, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    
    Startup: Initialize database connections, load models
    Shutdown: Close connections, cleanup resources
    """
    # Startup
    logger.info("🚀 Starting Rizwan Universal AI Backend Server")
    logger.info("📦 Loading AI models and initializing database connections")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down server - closing connections")


# Create FastAPI application instance
app = FastAPI(
    title="Rizwan Universal AI API",
    description="A comprehensive AI-powered backend API with authentication, file handling, and AI capabilities",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS (Cross-Origin Resource Sharing)
# This allows your frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]  # Add your domain in production
)


# Include all API routers
# Each router handles a specific feature/domain
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint - returns API information.
    
    Returns:
        dict: API metadata and status
    """
    return {
        "message": "Welcome to Rizwan Universal AI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",  # Swagger UI documentation
        "redoc": "/redoc"  # ReDoc documentation
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: The HTTP request
        exc: The exception that was raised
        
    Returns:
        JSONResponse: Error response with status code 500
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    # Use: python main.py
    # Or: uvicorn main:app --reload
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
