import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.football import Club, Competition, Match, Season
from app.models.predictions import Prediction
from tests.helpers import auth_headers


@pytest.mark.asyncio
async def test_honest_empty_predictions_and_leaderboard():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        up_res = await ac.get("/api/v1/predictions/upcoming")
        assert up_res.status_code == 200
        assert up_res.json() == []

        lb_res = await ac.get("/api/v1/predictions/leaderboard")
        assert lb_res.status_code == 200
        assert lb_res.json() == []


@pytest.mark.asyncio
async def test_upcoming_and_submit_prediction_with_kickoff_lock_and_counts(session_factory):
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
                Competition(id="PL", code="PL", name="Premier League", country="England"),
                Season(id="2026-2027-PL", competition_id="PL", start_year=2026, end_year=2027, is_current=True),
                Match(
                    id="match_future_1",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="tottenham",
                    away_team_name="Tottenham Hotspur",
                    matchday=12,
                    utc_date=now + datetime.timedelta(days=2),
                    status="SCHEDULED",
                ),
                Match(
                    id="match_locked_past",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    matchday=11,
                    utc_date=now - datetime.timedelta(hours=1),
                    status="SCHEDULED",
                ),
            ]
        )
        await session.commit()

    headers = auth_headers("usr_fan_10", display_name="GoonerSam")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        up_res = await ac.get("/api/v1/predictions/upcoming", headers=headers)
        assert up_res.status_code == 200
        matches = up_res.json()
        assert len(matches) == 1

        by_id = {m["match"]["id"]: m for m in matches}
        assert by_id["match_future_1"]["can_predict"] is True
        assert by_id["match_future_1"]["total_predictions_count"] == 0
        assert "match_locked_past" not in by_id

        # Submit score prediction (spoofed user_id in JSON is ignored)
        pred_res = await ac.post(
            "/api/v1/predictions",
            json={
                "user_id": "forged_other_user",
                "user_name": "GoonerSam",
                "user_club_id": "arsenal",
                "match_id": "match_future_1",
                "predicted_home_score": 3,
                "predicted_away_score": 1,
            },
            headers=headers,
        )
        assert pred_res.status_code == 201
        pred = pred_res.json()
        assert pred["user_id"] == "usr_fan_10"
        assert pred["predicted_home_score"] == 3
        assert pred["predicted_away_score"] == 1

        # Fetch again: prediction attached and real SQL count == 1 (never hardcoded 12)
        up_res2 = await ac.get("/api/v1/predictions/upcoming", headers=headers)
        assert up_res2.status_code == 200
        found = next(m for m in up_res2.json() if m["match"]["id"] == "match_future_1")
        assert found["user_prediction"] is not None
        assert found["user_prediction"]["predicted_home_score"] == 3
        assert found["total_predictions_count"] == 1

        # Upsert existing prediction
        upd_res = await ac.post(
            "/api/v1/predictions",
            json={
                "match_id": "match_future_1",
                "predicted_home_score": 2,
                "predicted_away_score": 0,
            },
            headers=headers,
        )
        assert upd_res.status_code == 201
        assert upd_res.json()["predicted_home_score"] == 2
        assert upd_res.json()["predicted_away_score"] == 0


@pytest.mark.asyncio
async def test_predictions_leaderboard_real_grading(session_factory):
    now = datetime.datetime.now(datetime.timezone.utc)
    async with session_factory() as session:
        session.add_all(
            [
                Competition(id="PL", code="PL", name="Premier League", country="England"),
                Season(id="2026-2027-PL", competition_id="PL", start_year=2026, end_year=2027, is_current=True),
                Match(
                    id="m_fin_1",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    matchday=1,
                    utc_date=now - datetime.timedelta(days=5),
                    status="FINISHED",
                    home_score=2,
                    away_score=1,
                    winner="HOME_TEAM",
                ),
                Match(
                    id="m_fin_2",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="liverpool",
                    away_team_name="Liverpool FC",
                    matchday=2,
                    utc_date=now - datetime.timedelta(days=2),
                    status="FINISHED",
                    home_score=3,
                    away_score=1,
                    winner="HOME_TEAM",
                ),
                # User 1: exact on m_fin_1 (3 pts) + outcome on m_fin_2 (1 pt) = 4 pts, 100% accuracy
                Prediction(
                    id="p_1a",
                    user_id="usr_alex",
                    user_name="GoonerAlex",
                    user_club_id="arsenal",
                    match_id="m_fin_1",
                    predicted_home_score=2,
                    predicted_away_score=1,
                ),
                Prediction(
                    id="p_1b",
                    user_id="usr_alex",
                    user_name="GoonerAlex",
                    user_club_id="arsenal",
                    match_id="m_fin_2",
                    predicted_home_score=1,
                    predicted_away_score=0,
                ),
                # User 2: outcome on m_fin_1 (1 pt) + miss on m_fin_2 (0 pts) = 1 pt, 50% accuracy
                Prediction(
                    id="p_2a",
                    user_id="usr_clock",
                    user_name="ClockEndTactician",
                    user_club_id="arsenal",
                    match_id="m_fin_1",
                    predicted_home_score=3,
                    predicted_away_score=0,
                ),
                Prediction(
                    id="p_2b",
                    user_id="usr_clock",
                    user_name="ClockEndTactician",
                    user_club_id="arsenal",
                    match_id="m_fin_2",
                    predicted_home_score=0,
                    predicted_away_score=2,
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/predictions/leaderboard?club_id=arsenal")
        assert res.status_code == 200
        entries = res.json()
        assert len(entries) == 2

        first, second = entries[0], entries[1]
        assert first["rank"] == 1
        assert first["user_name"] == "GoonerAlex"
        assert first["total_points"] == 4
        assert first["exact_scores"] == 1
        assert first["correct_outcomes"] == 2
        assert first["accuracy_rate"] == 100.0

        assert second["rank"] == 2
        assert second["user_name"] == "ClockEndTactician"
        assert second["total_points"] == 1
        assert second["exact_scores"] == 0
        assert second["correct_outcomes"] == 1
        assert second["accuracy_rate"] == 50.0
