import pytest
from httpx import ASGITransport, AsyncClient

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
async def test_clubs_list_arsenal_foundation_and_opponents():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/clubs")
    assert response.status_code == 200
    clubs = response.json()
    assert len(clubs) == 4
    by_slug = {c["slug"]: c for c in clubs}
    assert by_slug["arsenal"]["is_foundation"] is True
    assert by_slug["arsenal"]["is_active"] is True
    for opp in ("real-madrid", "barcelona", "milan"):
        assert opp in by_slug
        assert by_slug[opp]["is_foundation"] is False
