import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_supporter_public_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/supporters/GoonerAlex")
        assert res.status_code == 200
        profile = res.json()
        assert profile["username"] == "GoonerAlex"
        assert profile["favorite_club_id"] == "arsenal"
        assert "stats" in profile
        assert profile["stats"]["prediction_points"] >= 0
        assert "featured_insights" in profile
        assert "recent_posts" in profile
