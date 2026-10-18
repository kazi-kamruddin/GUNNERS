from fastapi import APIRouter
from app.schemas.clubs import HealthResponse
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Cheap and reliable health check endpoint for Render and uptime monitoring."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
