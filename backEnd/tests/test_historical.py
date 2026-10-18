import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_historical_matches_and_detail():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. List matches
        list_res = await ac.get("/api/v1/analytics/historical/matches")
        assert list_res.status_code == 200
        matches = list_res.json()
        assert len(matches) >= 2
        match_id = matches[0]["id"]
        assert "StatsBomb" in matches[0]["data_provider"]

        # 2. Get match detail with shots and passes
        det_res = await ac.get(f"/api/v1/analytics/historical/matches/{match_id}")
        assert det_res.status_code == 200
        detail = det_res.json()
        assert len(detail["shots"]) > 0
        assert len(detail["pass_nodes"]) > 0
        assert len(detail["pass_links"]) > 0
        assert detail["total_xg_home"] > 0

        # 3. 404 for invalid match id
        res_404 = await ac.get("/api/v1/analytics/historical/matches/hist_unknown_xyz")
        assert res_404.status_code == 404
