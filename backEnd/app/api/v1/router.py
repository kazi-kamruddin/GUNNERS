from fastapi import APIRouter
from app.api.v1.endpoints import health, clubs, matches, insights

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(clubs.router, prefix="/clubs", tags=["Clubs"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches & Analytics"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
