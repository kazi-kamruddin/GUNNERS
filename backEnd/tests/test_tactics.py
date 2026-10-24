import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_formation_presets():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/tactics/formations/presets")
        assert res.status_code == 200
        presets = res.json()
        assert len(presets) >= 6
        preset_ids = [p["id"] for p in presets]
        assert "4-3-3" in preset_ids
        assert "4-2-3-1" in preset_ids
        assert "3-4-2-1" in preset_ids

        # Verify 11 players on each preset
        for p in presets:
            assert len(p["players"]) == 11
            for player in p["players"]:
                assert "x" in player and "y" in player
                assert 0.0 <= player["x"] <= 100.0
                assert 0.0 <= player["y"] <= 100.0

@pytest.mark.asyncio
async def test_create_and_get_tactical_board():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create a new board
        payload = {
            "title": "Arsenal Double Inverted Fullbacks",
            "formation": "4-3-3",
            "author_name": "TacticsGooner",
            "author_club_id": "arsenal",
            "lineup": [
                {"id": f"p{i}", "name": f"Player {i}", "number": i, "role": "CM", "x": float(i * 8), "y": 50.0}
                for i in range(1, 12)
            ],
            "annotations": [
                {"id": "a1", "type": "run", "from_x": 20.0, "from_y": 14.0, "to_x": 45.0, "to_y": 35.0, "label": "Invert to pivot"}
            ],
            "tactical_notes": "Zinchenko and White invert alongside Rice forming a 3-2-4-1 in possession."
        }
        res = await ac.post("/api/v1/tactics", json=payload)
        assert res.status_code == 200
        board = res.json()
        assert board["title"] == "Arsenal Double Inverted Fullbacks"
        assert len(board["lineup"]) == 11
        assert len(board["annotations"]) == 1
        board_id = board["id"]

        # Get board by id
        get_res = await ac.get(f"/api/v1/tactics/{board_id}")
        assert get_res.status_code == 200
        fetched = get_res.json()
        assert fetched["id"] == board_id
        assert fetched["author_name"] == "TacticsGooner"

        # List boards filtered by club
        list_res = await ac.get("/api/v1/tactics?club_id=arsenal")
        assert list_res.status_code == 200
        boards = list_res.json()
        assert len(boards) >= 1
        assert any(b["id"] == board_id for b in boards)

@pytest.mark.asyncio
async def test_attach_tactical_board_to_terrace_post():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First create a tactical board
        board_res = await ac.post("/api/v1/tactics", json={
            "title": "Derby Day Counter Setup",
            "formation": "4-2-3-1",
            "author_name": "MikelMasterclass",
            "author_club_id": "arsenal",
            "lineup": [
                {"id": f"p{i}", "name": f"Player {i}", "number": i, "role": "FWD", "x": 50.0, "y": 50.0}
                for i in range(1, 12)
            ],
            "annotations": []
        })
        assert board_res.status_code == 200
        board = board_res.json()
        board_id = board["id"]

        # Post to Terrace attaching tactical board
        post_res = await ac.post("/api/v1/terrace/posts", json={
            "content": "Check out this tactical blueprint for defending against quick transitions.",
            "author_name": "MikelMasterclass",
            "author_club_id": "arsenal",
            "club_id": "arsenal",
            "tactical_board_id": board_id
        })
        assert post_res.status_code == 201
        post = post_res.json()
        assert post["tactical_board_id"] == board_id
        assert post["tactical_board"] is not None
        assert post["tactical_board"]["title"] == "Derby Day Counter Setup"
