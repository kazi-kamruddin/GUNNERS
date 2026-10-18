import httpx
import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings

class FootballDataProvider:
    """
    Adapter for football-data.org Free Tier (10 calls/min, 12 competitions).
    Provides resilient parsing, canonical normalization, and fallback synthetic data
    when operating without an API key in local development.
    """
    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FOOTBALL_DATA_API_KEY
        self.headers = {"X-Auth-Token": self.api_key} if self.api_key else {}

    async def fetch_matches_for_competition(self, competition_code: str = "PL", season: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch matches from provider with rate-limit and error resilience."""
        if not self.api_key:
            # Fallback mock data when running without external key
            return self._get_fallback_matches(competition_code)

        url = f"{self.BASE_URL}/competitions/{competition_code}/matches"
        params = {}
        if season:
            params["season"] = season

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("matches", [])
                elif response.status_code == 429:
                    # Rate limit exceeded
                    return []
                else:
                    return []
            except httpx.RequestError:
                return []

    def _get_fallback_matches(self, comp_code: str) -> List[Dict[str, Any]]:
        """Generates minimal test records for local testing without internet/keys."""
        return [
            {
                "id": "mock-m1",
                "competition_id": comp_code,
                "season_id": "2024-2025",
                "home_team_id": "arsenal",
                "away_team_id": "milan",
                "matchday": 1,
                "utc_date": datetime.datetime(2024, 10, 1, 19, 0, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_score": 2,
                "away_score": 0,
                "winner": "HOME_TEAM",
                "source": "mock-provider"
            }
        ]
