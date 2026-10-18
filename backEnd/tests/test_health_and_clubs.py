import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

@pytest.mark.asyncio
async def test_clubs_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/clubs")
    assert response.status_code == 200
    clubs = response.json()
    assert len(clubs) == 4
    slugs = [c["slug"] for c in clubs]
    assert "arsenal" in slugs
    assert "real-madrid" in slugs
    assert "barcelona" in slugs
    assert "milan" in slugs
