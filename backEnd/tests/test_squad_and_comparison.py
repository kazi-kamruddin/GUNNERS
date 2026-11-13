import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.football import Club
from app.models.squad import Player


@pytest.mark.asyncio
async def test_list_squad_fallback_when_db_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/squad")
        assert res.status_code == 200
        players = res.json()
        assert len(players) > 0
        assert any(p["club_id"] == "arsenal" for p in players)

        res_ars = await ac.get("/api/v1/squad?club_id=arsenal")
        assert res_ars.status_code == 200
        assert all(p["club_id"] == "arsenal" for p in res_ars.json())

        res_pos = await ac.get("/api/v1/squad?club_id=arsenal&position=Attacker")
        assert res_pos.status_code == 200
        for p in res_pos.json():
            assert p["position"].lower() == "attacker"


@pytest.mark.asyncio
async def test_player_comparison_and_get_fallback():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/squad/compare?player1_id=ply_saka&player2_id=ply_gyokeres")
        assert res.status_code == 200
        data = res.json()
        assert data["player1"]["player"]["name"] == "Bukayo Saka"
        assert data["player2"]["player"]["name"] == "Viktor Gyökeres"
        assert "comparison_summary" in data
        assert data["player1"]["discipline_score"] > 0
        assert data["player2"]["discipline_score"] > 0

        single = await ac.get("/api/v1/squad/ply_saka")
        assert single.status_code == 200
        assert single.json()["name"] == "Bukayo Saka"

        res_404 = await ac.get("/api/v1/squad/ply_non_existent")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_squad_db_first_overrides_default_players(session_factory):
    async with session_factory() as session:
        session.add(
            Club(
                id="arsenal",
                slug="arsenal",
                name="Arsenal FC",
                short_name="Arsenal",
                primary_color="#EF0107",
                secondary_color="#FFFFFF",
                accent_color="#9C824A",
                league="Premier League",
                country="England",
            )
        )
        session.add_all(
            [
                Player(
                    id="ply_saka",
                    club_id="arsenal",
                    name="Bukayo Saka (DB)",
                    short_name="B. Saka",
                    position="Attacker",
                    jersey_number=7,
                    nationality="England",
                    appearances=30,
                    goals=15,
                    assists=12,
                    minutes_played=2600,
                    portrait_url="https://example.com/saka_portrait.png",
                    bio="Hale End graduate",
                ),
                Player(
                    id="ply_custom_new",
                    club_id="arsenal",
                    name="Myles Lewis-Skelly",
                    short_name="M. Lewis-Skelly",
                    position="Defender",
                    jersey_number=49,
                    nationality="England",
                    appearances=18,
                    goals=1,
                    assists=3,
                    minutes_played=1200,
                    height="178 cm",
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # DB-first list returns the 2 DB rows, not 23 DEFAULT_PLAYERS
        list_res = await ac.get("/api/v1/squad?club_id=arsenal")
        assert list_res.status_code == 200
        listed = list_res.json()
        assert len(listed) == 2

        # DB-first single player lookup reads updated DB fields & new parity columns
        get_res = await ac.get("/api/v1/squad/ply_saka")
        assert get_res.status_code == 200
        saka = get_res.json()
        assert saka["name"] == "Bukayo Saka (DB)"
        assert saka["goals"] == 15
        assert saka["portrait_url"] == "https://example.com/saka_portrait.png"
        assert saka["bio"] == "Hale End graduate"

        # DB-first compare works for DB-only player and uses DB stats for ply_saka
        cmp_res = await ac.get(
            "/api/v1/squad/compare?player1_id=ply_saka&player2_id=ply_custom_new"
        )
        assert cmp_res.status_code == 200
        cmp_data = cmp_res.json()
        assert cmp_data["player1"]["player"]["name"] == "Bukayo Saka (DB)"
        assert cmp_data["player2"]["player"]["name"] == "Myles Lewis-Skelly"
        assert cmp_data["player2"]["player"]["height"] == "178 cm"

        # When DB is populated, players not in DB return 404 (not DEFAULT_PLAYERS fallback)
        missing_in_db = await ac.get("/api/v1/squad/ply_martinelli")
        assert missing_in_db.status_code == 404
