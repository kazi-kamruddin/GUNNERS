import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.insight import Insight
from tests.helpers import auth_headers


@pytest.fixture(autouse=True)
async def seed_terrace_data(session_factory):
    async with session_factory() as session:
        ins = Insight(
            id="ins_test_123",
            user_id="usr_1",
            author_name="GoonerAlex",
            author_club_id="arsenal",
            title="Arsenal 80% Win Rate",
            metric="win_rate",
            team_ids="arsenal",
            venue="all",
            snapshot='{"metric":"win_rate","formula":"(wins / matches_played) * 100","venue_filter":"all","series":[{"team_id":"arsenal","team_name":"Arsenal FC","matches_played":5,"wins":4,"draws":0,"losses":1,"goals_for":10,"goals_against":3,"goal_difference":7,"metric_value":80.0,"unit":"%"}]}',
        )
        session.add(ins)
        await session.commit()

    yield


@pytest.mark.asyncio
async def test_create_and_list_posts_with_auth():
    headers = auth_headers("usr_alex", display_name="GoonerAlex")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Unauthenticated tags when DB has 0 posts -> honest empty list
        empty_tags = await ac.get("/api/v1/terrace/tags")
        assert empty_tags.status_code == 200
        assert empty_tags.json() == []

        # Create plain post
        res1 = await ac.post(
            "/api/v1/terrace/posts",
            json={
                "content": "Excited for the upcoming derby this weekend! #NorthLondonDerby",
                "author_name": "GoonerAlex",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
            },
            headers=headers,
        )
        assert res1.status_code == 201
        p1 = res1.json()
        assert p1["author_id"] == "usr_alex"
        assert p1["content"] == "Excited for the upcoming derby this weekend! #NorthLondonDerby"
        assert p1["insight"] is None

        # Create insight post
        res2 = await ac.post(
            "/api/v1/terrace/posts",
            json={
                "content": "Look at our incredible home win rate this season. #NorthLondonDerby #Tactics",
                "author_name": "GoonerAlex",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
                "insight_id": "ins_test_123",
            },
            headers=headers,
        )
        assert res2.status_code == 201
        p2 = res2.json()
        assert p2["author_id"] == "usr_alex"
        assert p2["insight_id"] == "ins_test_123"
        assert p2["insight"] is not None
        assert p2["insight"]["metric"] == "win_rate"

        # Invalid tactical_board_id returns 400
        bad_tb = await ac.post(
            "/api/v1/terrace/posts",
            json={
                "content": "Broken board attachment",
                "tactical_board_id": "tb_missing_999",
            },
            headers=headers,
        )
        assert bad_tb.status_code == 400

        # List all posts
        list_res = await ac.get("/api/v1/terrace/posts")
        assert list_res.status_code == 200
        posts = list_res.json()
        assert len(posts) == 2

        # Filter by club
        club_res = await ac.get("/api/v1/terrace/posts?club_id=arsenal")
        assert club_res.status_code == 200
        assert len(club_res.json()) == 2

        other_res = await ac.get("/api/v1/terrace/posts?club_id=real-madrid")
        assert other_res.status_code == 200
        assert len(other_res.json()) == 0

        # Dynamic tags computed from real DB posts (no hardcoded ElClasico/DerbyDellaMadonnina)
        tags_res = await ac.get("/api/v1/terrace/tags")
        assert tags_res.status_code == 200
        tags = tags_res.json()
        tag_map = {t["tag"]: t["count"] for t in tags}
        assert tag_map["NorthLondonDerby"] == 2
        assert tag_map["Tactics"] == 1
        assert "ElClasico" not in tag_map


@pytest.mark.asyncio
async def test_post_reactions_toggle_uses_jwt_subject():
    author_headers = auth_headers("usr_author", display_name="GoonerAuthor")
    reactor_headers = auth_headers("usr_fan_jwt", display_name="ReactorFan")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post(
            "/api/v1/terrace/posts",
            json={
                "content": "COYG from the North Bank!",
                "author_name": "GoonerAuthor",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
            },
            headers=author_headers,
        )
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]

        # Add reaction (spoofed user_id in body must be ignored; JWT sub wins)
        rxn1 = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/react",
            json={"user_id": "spoofed_user", "reaction_type": "cheer"},
            headers=reactor_headers,
        )
        assert rxn1.status_code == 200
        assert rxn1.json()["action"] == "added"
        assert rxn1.json()["total_reactions"] == 1

        # Authenticated GET /posts shows user_reacted=True for JWT user, False for author
        list_reactor = await ac.get("/api/v1/terrace/posts", headers=reactor_headers)
        assert list_reactor.status_code == 200
        assert list_reactor.json()[0]["reactions_count"] == 1
        assert list_reactor.json()[0]["user_reacted"] is True

        list_author = await ac.get("/api/v1/terrace/posts", headers=author_headers)
        assert list_author.status_code == 200
        assert list_author.json()[0]["user_reacted"] is False

        # Toggle again -> removes reaction
        rxn2 = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/react",
            json={"reaction_type": "cheer"},
            headers=reactor_headers,
        )
        assert rxn2.status_code == 200
        assert rxn2.json()["action"] == "removed"
        assert rxn2.json()["total_reactions"] == 0


@pytest.mark.asyncio
async def test_post_comments_and_delete():
    author_headers = auth_headers("usr_post_owner", display_name="Analyst10")
    commenter_headers = auth_headers("usr_commenter", display_name="NorthBanker")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post(
            "/api/v1/terrace/posts",
            json={
                "content": "Tactical debate on our defensive midfield setup.",
                "author_name": "Analyst10",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
            },
            headers=author_headers,
        )
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]

        # Add comment
        cmt_res = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/comments",
            json={
                "content": "Agreed, we need more double-pivot coverage away from home.",
                "author_name": "NorthBanker",
                "author_club_id": "arsenal",
            },
            headers=commenter_headers,
        )
        assert cmt_res.status_code == 201
        cmt = cmt_res.json()
        assert cmt["author_id"] == "usr_commenter"
        assert cmt["content"] == "Agreed, we need more double-pivot coverage away from home."

        # Fetch comments
        comments_list = await ac.get(f"/api/v1/terrace/posts/{post_id}/comments")
        assert comments_list.status_code == 200
        assert len(comments_list.json()) == 1

        # Delete comment by owner, then post by owner
        del_cmt = await ac.delete(
            f"/api/v1/terrace/posts/{post_id}/comments/{cmt['id']}",
            headers=commenter_headers,
        )
        assert del_cmt.status_code == 200

        del_post = await ac.delete(
            f"/api/v1/terrace/posts/{post_id}",
            headers=author_headers,
        )
        assert del_post.status_code == 200
