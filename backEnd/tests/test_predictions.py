import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_upcoming_and_submit_prediction():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch upcoming matches for prediction
        up_res = await ac.get("/api/v1/predictions/upcoming?user_id=usr_fan_10")
        assert up_res.status_code == 200
        matches = up_res.json()
        assert len(matches) > 0
        match_id = matches[0]["match"]["id"]

        # 2. Submit score prediction
        pred_res = await ac.post("/api/v1/predictions", json={
            "user_id": "usr_fan_10",
            "user_name": "GoonerSam",
            "user_club_id": "arsenal",
            "match_id": match_id,
            "predicted_home_score": 3,
            "predicted_away_score": 1
        })
        assert pred_res.status_code == 201
        pred = pred_res.json()
        assert pred["predicted_home_score"] == 3
        assert pred["predicted_away_score"] == 1

        # 3. Fetch again, prediction should be attached
        up_res2 = await ac.get("/api/v1/predictions/upcoming?user_id=usr_fan_10")
        assert up_res2.status_code == 200
        found = next(m for m in up_res2.json() if m["match"]["id"] == match_id)
        assert found["user_prediction"] is not None
        assert found["user_prediction"]["predicted_home_score"] == 3

@pytest.mark.asyncio
async def test_predictions_leaderboard():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/predictions/leaderboard")
        assert res.status_code == 200
        entries = res.json()
        assert len(entries) > 0
        assert entries[0]["rank"] == 1
        assert "total_points" in entries[0]

        # Club filter
        res_club = await ac.get("/api/v1/predictions/leaderboard?club_id=arsenal")
        assert res_club.status_code == 200
        assert len(res_club.json()) > 0
