import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.api.v1.endpoints.squad import DEFAULT_PLAYERS, DEPARTED_PLAYER_IDS
from app.main import app
from app.models.football import Club, Competition, Match, Season
from app.models.profile import Profile
from app.providers.football_data import FootballDataProvider
from app.services.ingestion import FootballIngestionService
from app.services.news_aggregator import NewsAggregatorService


@pytest.mark.asyncio
async def test_match_detail_endpoint_and_404(session_factory):
    now = datetime.datetime.now(datetime.timezone.utc)
    async with session_factory() as session:
        session.add_all(
            [
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
                ),
                Club(
                    id="chelsea",
                    slug="chelsea",
                    name="Chelsea FC",
                    short_name="Chelsea",
                    primary_color="#034694",
                    secondary_color="#FFFFFF",
                    accent_color="#DBA111",
                    league="Premier League",
                    country="England",
                ),
                Competition(id="PL", code="PL", name="Premier League", country="England"),
                Season(id="2026-2027-PL", competition_id="PL", start_year=2026, end_year=2027, is_current=True),
                Match(
                    id="m_detail_1",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Home Team",
                    away_team_id="chelsea",
                    away_team_name="Away Team",
                    matchday=5,
                    utc_date=now - datetime.timedelta(days=3),
                    status="FINISHED",
                    venue="Emirates Stadium",
                    home_score=3,
                    away_score=1,
                    winner="HOME_TEAM",
                    goalscorers=[
                        {"minute": 18, "player": "Bukayo Saka", "team": "Arsenal FC", "assist": "Martin Ødegaard", "type": "REGULAR"}
                    ],
                    lineups={
                        "home": {"formation": "4-3-3", "xi": ["David Raya", "Bukayo Saka"]},
                        "away": {"formation": "4-2-3-1", "xi": ["Robert Sanchez"]},
                    },
                    highlights=[
                        {"label": "Extended Highlights", "url": "https://www.arsenal.com/news", "source": "Arsenal.com"}
                    ],
                ),
                Match(
                    id="m_detail_nulls",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    matchday=6,
                    utc_date=now + datetime.timedelta(days=4),
                    status="SCHEDULED",
                    goalscorers=None,
                    lineups=None,
                    highlights=None,
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/matches/m_detail_1")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "m_detail_1"
        assert data["home_team_name"] == "Arsenal FC"
        assert data["away_team_name"] == "Chelsea FC"
        assert len(data["goalscorers"]) == 1
        assert data["goalscorers"][0]["player"] == "Bukayo Saka"
        assert data["lineups"]["home"]["formation"] == "4-3-3"
        assert len(data["highlights"]) == 1

        nulls_res = await ac.get("/api/v1/matches/m_detail_nulls")
        assert nulls_res.status_code == 200
        nulls_data = nulls_res.json()
        assert nulls_data["goalscorers"] == []
        assert nulls_data["lineups"] == {}
        assert nulls_data["highlights"] == []

        missing_res = await ac.get("/api/v1/matches/nonexistent_match_999")
        assert missing_res.status_code == 404

        # Ensure static routes remain reachable above /{match_id}
        assert (await ac.get("/api/v1/matches/seasons")).status_code == 200
        assert (await ac.get("/api/v1/matches/summary?club_id=arsenal")).status_code == 200
        assert (await ac.get("/api/v1/matches/sync-status")).status_code == 200


@pytest.mark.asyncio
async def test_arsenal_only_foundation_invariant_and_mock_sync(session_factory):
    assert FootballDataProvider.FOUNDATION_IDS == {57: "arsenal"}

    async with session_factory() as session:
        # Pre-seed an opponent wrongly flagged as foundation to confirm sync repairs it
        session.add(
            Club(
                id="real-madrid",
                slug="real-madrid",
                name="Real Madrid CF",
                short_name="Real Madrid",
                primary_color="#00529F",
                secondary_color="#FFFFFF",
                accent_color="#EEB028",
                league="La Liga",
                country="Spain",
                is_foundation=True,
                is_active=True,
            )
        )
        await session.commit()

        result = await FootballIngestionService.run_sync(db=session, force_mock=True)
        assert result["status"] == "SUCCESS"
        assert result["matches_synced"] >= 40

        clubs = {c.id: c for c in (await session.execute(select(Club))).scalars().all()}
        assert clubs["arsenal"].is_foundation is True
        for opp in ("real-madrid", "barcelona", "milan"):
            assert clubs[opp].is_foundation is False

        matches = (await session.execute(select(Match))).scalars().all()
        assert len(matches) >= 40
        assert all(m.home_team_id == "arsenal" or m.away_team_id == "arsenal" for m in matches)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        featured = await ac.get("/api/v1/matches/fd-ars-1")
        assert featured.status_code == 200
        detail = featured.json()
        assert len(detail["goalscorers"]) > 0
        assert "home" in detail["lineups"] and "away" in detail["lineups"]
        assert len(detail["highlights"]) > 0


@pytest.mark.asyncio
async def test_news_wire_pagination_and_filters(monkeypatch):
    monkeypatch.setattr(NewsAggregatorService, "_fetch_source_sync", classmethod(lambda cls, src: []))
    monkeypatch.setattr(NewsAggregatorService, "_cache", None)
    monkeypatch.setattr(NewsAggregatorService, "_cache_time", None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        page1 = await ac.get("/api/v1/news?limit=5&offset=0")
        assert page1.status_code == 200
        d1 = page1.json()
        assert d1["total"] >= 14
        assert len(d1["articles"]) == 5
        assert d1["has_more"] is True

        page_last = await ac.get(f"/api/v1/news?limit=5&offset={d1['total'] - 2}")
        assert page_last.status_code == 200
        d_last = page_last.json()
        assert len(d_last["articles"]) == 2
        assert d_last["total"] == d1["total"]
        assert d_last["has_more"] is False

        # Exact boundary: full batch in one page -> has_more is False
        full_page = await ac.get(f"/api/v1/news?limit={d1['total']}&offset=0")
        assert full_page.status_code == 200
        assert full_page.json()["has_more"] is False

        # Category filter
        cat_res = await ac.get("/api/v1/news?category=reddit&limit=10&offset=0")
        assert cat_res.status_code == 200
        cat_data = cat_res.json()
        assert 0 < cat_data["total"] < d1["total"]
        assert all(a["source_category"] == "reddit" for a in cat_data["articles"])

        # Tag filter
        tag_res = await ac.get("/api/v1/news?tag=UCL&limit=10&offset=0")
        assert tag_res.status_code == 200
        tag_data = tag_res.json()
        assert tag_data["total"] > 0
        assert all(any("ucl" in t.lower() for t in a["tags"]) for a in tag_data["articles"])

        # Search filter
        search_res = await ac.get("/api/v1/news?search=Gyökeres")
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["total"] >= 1
        assert search_data["has_more"] is False


@pytest.mark.asyncio
async def test_official_squad_refreshed_roster_and_detail():
    player_ids = {p["id"] for p in DEFAULT_PLAYERS}
    assert "ply_saka" in player_ids
    assert "ply_odegaard" in player_ids
    for departed_id in DEPARTED_PLAYER_IDS:
        assert departed_id not in player_ids

    for expected_new in (
        "ply_kepa",
        "ply_mosquera",
        "ply_hincapie",
        "ply_lewis_skelly",
        "ply_eze",
        "ply_konsa",
        "ply_zubimendi",
        "ply_gyokeres",
        "ply_madueke",
    ):
        assert expected_new in player_ids

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/squad?club_id=arsenal")
        assert res.status_code == 200
        squad = res.json()
        assert len(squad) == len(DEFAULT_PLAYERS)

        returned_ids = {p["id"] for p in squad}
        assert "ply_saka" in returned_ids
        assert "ply_odegaard" in returned_ids
        for departed_id in DEPARTED_PLAYER_IDS:
            assert departed_id not in returned_ids

        for player in squad:
            assert player["bio"]
            if player["id"] != "ply_hashi":
                assert player["portrait_url"]
                assert player["action_url"]
            assert player["date_of_birth"]
            assert player["height"]
            assert player["joined_date"]

        saka_res = await ac.get("/api/v1/squad/ply_saka")
        assert saka_res.status_code == 200
        saka = saka_res.json()
        assert saka["name"] == "Bukayo Saka"
        assert saka["bio"]
        assert saka["portrait_url"]
        assert saka["action_url"]
        assert saka["goal_contributions"] == saka["goals"] + saka["assists"]

        assert (await ac.get("/api/v1/squad/ply_neto")).status_code == 404


@pytest.mark.asyncio
async def test_supporter_search_directory_filtering_and_schema(session_factory):
    async with session_factory() as session:
        session.add_all(
            [
                Profile(
                    id="usr_dir_1",
                    username="GoonerAlex",
                    display_name="Alex Highbury",
                    avatar_url="https://example.com/alex.png",
                    favorite_club_id="arsenal",
                    bio="Pressing structure analyst",
                ),
                Profile(
                    id="usr_dir_2",
                    username="ClockEndTactician",
                    display_name="Clock End Tactician",
                    avatar_url="https://example.com/clock.png",
                    favorite_club_id="arsenal",
                    bio="Double-pivot notes",
                ),
                Profile(
                    id="usr_dir_3",
                    username="NorthBankFan",
                    display_name="North Bank Regular",
                    favorite_club_id="arsenal",
                ),
                Profile(
                    id="usr_dir_no_username",
                    username=None,
                    display_name="Incomplete Profile",
                    favorite_club_id="arsenal",
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        all_res = await ac.get("/api/v1/supporters")
        assert all_res.status_code == 200
        items = all_res.json()
        assert len(items) == 3
        assert [i["username"] for i in items] == [
            "ClockEndTactician",
            "GoonerAlex",
            "NorthBankFan",
        ]
        first = items[0]
        assert set(first.keys()) >= {
            "user_id",
            "username",
            "display_name",
            "avatar_url",
            "favorite_club_id",
            "bio",
        }

        # Case-insensitive filter by display_name or username
        q_res = await ac.get("/api/v1/supporters?q=highbury")
        assert q_res.status_code == 200
        q_items = q_res.json()
        assert len(q_items) == 1
        assert q_items[0]["username"] == "GoonerAlex"

        # Limit parameter
        lim_res = await ac.get("/api/v1/supporters?limit=2")
        assert lim_res.status_code == 200
        assert len(lim_res.json()) == 2

        # No match
        empty_res = await ac.get("/api/v1/supporters?q=DoesNotExistXYZ")
        assert empty_res.status_code == 200
        assert empty_res.json() == []
