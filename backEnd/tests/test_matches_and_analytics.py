import pytest
import datetime
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.football import Club, Competition, Season, Match

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed data
    async with TestSessionLocal() as session:
        arsenal = Club(
            id="arsenal",
            slug="arsenal",
            name="Arsenal FC",
            short_name="Arsenal",
            primary_color="#EF0107",
            secondary_color="#FFFFFF",
            accent_color="#9C824A",
            league="Premier League",
            country="England"
        )
        barcelona = Club(
            id="barcelona",
            slug="barcelona",
            name="FC Barcelona",
            short_name="Barcelona",
            primary_color="#A50044",
            secondary_color="#004D98",
            accent_color="#EDBB00",
            league="La Liga",
            country="Spain"
        )
        comp = Competition(id="PL", code="PL", name="Premier League", country="England")
        season = Season(id="2024-2025", competition_id="PL", start_year=2024, end_year=2025, is_current=True)
        
        # Add 3 matches for Arsenal (2 Home wins, 1 Away loss)
        m1 = Match(
            id="m1",
            competition_id="PL",
            season_id="2024-2025",
            home_team_id="arsenal",
            away_team_id="barcelona",
            matchday=1,
            utc_date=datetime.datetime(2024, 9, 1, 15, 0, tzinfo=datetime.timezone.utc),
            status="FINISHED",
            home_score=2,
            away_score=1,
            winner="HOME_TEAM"
        )
        m2 = Match(
            id="m2",
            competition_id="PL",
            season_id="2024-2025",
            home_team_id="arsenal",
            away_team_id="barcelona",
            matchday=2,
            utc_date=datetime.datetime(2024, 9, 15, 15, 0, tzinfo=datetime.timezone.utc),
            status="FINISHED",
            home_score=3,
            away_score=0,
            winner="HOME_TEAM"
        )
        m3 = Match(
            id="m3",
            competition_id="PL",
            season_id="2024-2025",
            home_team_id="barcelona",
            away_team_id="arsenal",
            matchday=3,
            utc_date=datetime.datetime(2024, 9, 29, 15, 0, tzinfo=datetime.timezone.utc),
            status="FINISHED",
            home_score=2,
            away_score=1,
            winner="HOME_TEAM"
        )

        session.add_all([arsenal, barcelona, comp, season, m1, m2, m3])
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_get_matches():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/matches?club_id=arsenal")
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) == 3

@pytest.mark.asyncio
async def test_analytics_win_rate_all_venue():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "metric": "win_rate",
            "team_ids": ["arsenal"],
            "venue": "all"
        }
        response = await ac.post("/api/v1/matches/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "win_rate"
    series = data["series"][0]
    assert series["matches_played"] == 3
    assert series["wins"] == 2
    assert series["losses"] == 1
    # 2/3 * 100 = 66.7%
    assert series["metric_value"] == 66.7

@pytest.mark.asyncio
async def test_analytics_win_rate_home_venue():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "metric": "win_rate",
            "team_ids": ["arsenal"],
            "venue": "home"
        }
        response = await ac.post("/api/v1/matches/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    series = data["series"][0]
    assert series["matches_played"] == 2
    assert series["wins"] == 2
    assert series["losses"] == 0
    # 2/2 * 100 = 100.0%
    assert series["metric_value"] == 100.0
