import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.helpers import auth_headers


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

        for p in presets:
            assert len(p["players"]) == 11
            for player in p["players"]:
                assert "x" in player and "y" in player
                assert 0.0 <= player["x"] <= 100.0
                assert 0.0 <= player["y"] <= 100.0


@pytest.mark.asyncio
async def test_create_get_list_and_delete_tactical_board():
    owner_headers = auth_headers("usr_tactician", display_name="TacticsGooner")
    other_headers = auth_headers("usr_visitor", display_name="Visitor")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Cold-start empty DB falls back to DEMO_BOARDS on read
        cold_res = await ac.get("/api/v1/tactics?club_id=arsenal")
        assert cold_res.status_code == 200
        assert len(cold_res.json()) == 3

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
            "tactical_notes": "Zinchenko and White invert alongside Rice forming a 3-2-4-1 in possession.",
            "is_public": True,
        }
        res = await ac.post("/api/v1/tactics", json=payload, headers=owner_headers)
        assert res.status_code == 200
        board = res.json()
        assert board["user_id"] == "usr_tactician"
        assert board["title"] == "Arsenal Double Inverted Fullbacks"
        assert len(board["lineup"]) == 11
        assert len(board["annotations"]) == 1
        board_id = board["id"]

        # Create a private board as well
        priv_res = await ac.post(
            "/api/v1/tactics",
            json={**payload, "title": "Private Set Piece", "is_public": False},
            headers=owner_headers,
        )
        assert priv_res.status_code == 200
        priv_id = priv_res.json()["id"]

        # Public listing omits private board for other users, includes it for owner
        other_list = await ac.get("/api/v1/tactics?club_id=arsenal", headers=other_headers)
        assert other_list.status_code == 200
        other_ids = [b["id"] for b in other_list.json()]
        assert board_id in other_ids
        assert priv_id not in other_ids

        owner_list = await ac.get("/api/v1/tactics?club_id=arsenal", headers=owner_headers)
        assert owner_list.status_code == 200
        owner_ids = [b["id"] for b in owner_list.json()]
        assert board_id in owner_ids
        assert priv_id in owner_ids

        # Get board by id
        get_res = await ac.get(f"/api/v1/tactics/{board_id}")
        assert get_res.status_code == 200
        assert get_res.json()["author_name"] == "TacticsGooner"

        # Delete owned board
        del_res = await ac.delete(f"/api/v1/tactics/{board_id}", headers=owner_headers)
        assert del_res.status_code == 200
        assert (await ac.get(f"/api/v1/tactics/{board_id}")).status_code == 404


@pytest.mark.asyncio
async def test_attach_tactical_board_to_terrace_post():
    headers = auth_headers("usr_mikel", display_name="MikelMasterclass")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        board_res = await ac.post(
            "/api/v1/tactics",
            json={
                "title": "Derby Day Counter Setup",
                "formation": "4-2-3-1",
                "author_name": "MikelMasterclass",
                "author_club_id": "arsenal",
                "lineup": [
                    {"id": f"p{i}", "name": f"Player {i}", "number": i, "role": "FWD", "x": 50.0, "y": 50.0}
                    for i in range(1, 12)
                ],
                "annotations": [],
            },
            headers=headers,
        )
        assert board_res.status_code == 200
        board_id = board_res.json()["id"]

        post_res = await ac.post(
            "/api/v1/terrace/posts",
            json={
                "content": "Check out this tactical blueprint for defending against quick transitions.",
                "author_name": "MikelMasterclass",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
                "tactical_board_id": board_id,
            },
            headers=headers,
        )
        assert post_res.status_code == 201
        post = post_res.json()
        assert post["tactical_board_id"] == board_id
        assert post["tactical_board"] is not None
        assert post["tactical_board"]["title"] == "Derby Day Counter Setup"
