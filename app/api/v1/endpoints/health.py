from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Social Media API is running"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "API is ready to serve requests"
    }
