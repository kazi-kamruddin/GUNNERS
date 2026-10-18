import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_list_squad():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/squad")
        assert res.status_code == 200
        players = res.json()
        assert len(players) > 0
        assert any(p["club_id"] == "arsenal" for p in players)

        # Filter by club
        res_ars = await ac.get("/api/v1/squad?club_id=arsenal")
        assert res_ars.status_code == 200
        ars_players = res_ars.json()
        assert all(p["club_id"] == "arsenal" for p in ars_players)

        # Filter by position
        res_pos = await ac.get("/api/v1/squad?club_id=arsenal&position=Attacker")
        assert res_pos.status_code == 200
        for p in res_pos.json():
            assert p["position"].lower() == "attacker"

@pytest.mark.asyncio
async def test_player_comparison():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/squad/compare?player1_id=ply_saka&player2_id=ply_vinicius")
        assert res.status_code == 200
        data = res.json()
        assert data["player1"]["player"]["name"] == "Bukayo Saka"
        assert data["player2"]["player"]["name"] == "Vinícius Júnior"
        assert "comparison_summary" in data
        assert data["player1"]["discipline_score"] > 0
        assert data["player2"]["discipline_score"] > 0

@pytest.mark.asyncio
async def test_get_single_player():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/squad/ply_yamal")
        assert res.status_code == 200
        player = res.json()
        assert player["name"] == "Lamine Yamal"
        assert player["club_id"] == "barcelona"

        # 404 for unknown
        res_404 = await ac.get("/api/v1/squad/ply_non_existent")
        assert res_404.status_code == 404
