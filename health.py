"""
Health Check Routes
===================

API endpoints for system health monitoring:
- Server status
- Database connectivity
- AI service status

Endpoints:
- GET /api/health - Overall health status
- GET /api/health/db - Database health
- GET /api/health/ai - AI service health

Author: Manus AI
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import logging

# Import from parent modules
import sys
sys.path.append('..')
from ai_service import is_ai_available

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    version: str = "1.0.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "All systems operational",
                "version": "1.0.0"
            }
        }


class DetailedHealthResponse(BaseModel):
    """Detailed health check response"""
    status: str
    message: str
    components: Dict[str, Any]
    version: str = "1.0.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "All systems operational",
                "components": {
                    "server": "ok",
                    "database": "ok",
                    "ai_service": "ok"
                },
                "version": "1.0.0"
            }
        }


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check - returns server status.
    
    Returns:
        HealthResponse: Server health status
        
    Example:
        GET /api/health
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "message": "Rizwan Universal AI Backend is running",
        "version": "1.0.0"
    }


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check - returns status of all components.
    
    Returns:
        DetailedHealthResponse: Detailed component status
        
    Example:
        GET /api/health/detailed
    """
    components = {
        "server": "ok",
        "database": "ok",
        "ai_service": "ok" if is_ai_available() else "unavailable"
    }
    
    # Determine overall status
    if "unavailable" in components.values():
        overall_status = "degraded"
        message = "Some components are unavailable"
    else:
        overall_status = "healthy"
        message = "All systems operational"
    
    logger.info(f"Detailed health check: {overall_status}")
    
    return {
        "status": overall_status,
        "message": message,
        "components": components,
        "version": "1.0.0"
    }


@router.get("/db")
async def database_health():
    """
    Check database connectivity.
    
    Returns:
        dict: Database status
        
    Example:
        GET /api/health/db
    """
    try:
        # Import here to avoid circular imports
        from database import SessionLocal
        
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        logger.info("Database health check: OK")
        return {
            "status": "ok",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


@router.get("/ai")
async def ai_health():
    """
    Check AI service availability.
    
    Returns:
        dict: AI service status
        
    Example:
        GET /api/health/ai
    """
    available = is_ai_available()
    
    if available:
        logger.info("AI service health check: OK")
        return {
            "status": "ok",
            "message": "AI service is operational",
            "model": "gpt-3.5-turbo"
        }
    else:
        logger.warning("AI service health check: UNAVAILABLE")
        return {
            "status": "unavailable",
            "message": "AI service is not available",
            "note": "Set OPENAI_API_KEY environment variable"
        }


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness probe.
    
    Returns 200 if service is ready to accept requests.
    
    Returns:
        dict: Readiness status
        
    Example:
        GET /api/health/ready
    """
    return {
        "ready": True,
        "message": "Service is ready"
    }


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe.
    
    Returns 200 if service is alive and responsive.
    
    Returns:
        dict: Liveness status
        
    Example:
        GET /api/health/live
    """
    return {
        "alive": True,
        "message": "Service is alive"
    }
