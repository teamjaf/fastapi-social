from fastapi import APIRouter, status
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    message: str


@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running and healthy",
    response_description="Returns the current health status of the API"
)
async def health_check():
    """
    **Health Check Endpoint**
    
    This endpoint checks if the API is running and healthy.
    
    **Returns:**
    - `status`: Current health status (always "healthy" if endpoint is reachable)
    - `timestamp`: Current UTC timestamp in ISO format
    - `message`: Descriptive message about the API status
    
    **Use Cases:**
    - Monitoring and alerting systems
    - Load balancer health checks
    - Basic connectivity testing
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Social Media API is running"
    }


@router.get(
    "/ready",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Check if the API is ready to serve requests",
    response_description="Returns the readiness status of the API"
)
async def readiness_check():
    """
    **Readiness Check Endpoint**
    
    This endpoint checks if the API is ready to serve requests.
    This is more comprehensive than the health check and may include
    database connectivity and other service dependencies.
    
    **Returns:**
    - `status`: Current readiness status (always "ready" if endpoint is reachable)
    - `timestamp`: Current UTC timestamp in ISO format
    - `message`: Descriptive message about the API readiness
    
    **Use Cases:**
    - Kubernetes readiness probes
    - Service mesh health checks
    - Pre-deployment verification
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "API is ready to serve requests"
    }
