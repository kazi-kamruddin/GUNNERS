from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    clubs,
    matches,
    insights,
    terrace,
    messaging,
    squad,
    predictions,
    notifications,
    supporters,
    historical
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(clubs.router, prefix="/clubs", tags=["Clubs"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches & Analytics"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(terrace.router, prefix="/terrace", tags=["The Terrace"])
api_router.include_router(messaging.router, prefix="/messages", tags=["Direct Messaging"])
api_router.include_router(squad.router, prefix="/squad", tags=["Squad & Player Comparisons"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Matchday Predictions & Leaderboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["In-App Notifications"])
api_router.include_router(supporters.router, prefix="/supporters", tags=["Supporter Public Profiles"])
api_router.include_router(historical.router, prefix="/analytics/historical", tags=["StatsBomb Historical Tactical Analytics"])


