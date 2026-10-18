from fastapi import APIRouter
from app.api.v1.endpoints import health, clubs, matches

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(clubs.router, prefix="/clubs", tags=["Clubs"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches & Analytics"])
