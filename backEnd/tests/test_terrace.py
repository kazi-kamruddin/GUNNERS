import pytest
import datetime
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.insight import Insight
from app.models.terrace import Post, PostComment, PostReaction

@pytest.fixture(autouse=True)
async def seed_terrace_data(session_factory):
    # Seed an insight for testing insight posts
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
            snapshot='{"metric":"win_rate","formula":"(wins / matches_played) * 100","venue_filter":"all","series":[{"team_id":"arsenal","team_name":"Arsenal FC","matches_played":5,"wins":4,"draws":0,"losses":1,"goals_for":10,"goals_against":3,"goal_difference":7,"metric_value":80.0,"unit":"%"}]}'
        )
        session.add(ins)
        await session.commit()

    yield

@pytest.mark.asyncio
async def test_create_and_list_posts():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create plain post
        res1 = await ac.post("/api/v1/terrace/posts", json={
            "content": "Excited for the upcoming derby this weekend!",
            "author_name": "GoonerAlex",
            "author_club_id": "arsenal",
            "club_id": "arsenal"
        })
        assert res1.status_code == 201
        p1 = res1.json()
        assert p1["content"] == "Excited for the upcoming derby this weekend!"
        assert p1["insight"] is None

        # Create insight post
        res2 = await ac.post("/api/v1/terrace/posts", json={
            "content": "Look at our incredible home win rate this season. Numbers don't lie.",
            "author_name": "GoonerAlex",
            "author_club_id": "arsenal",
            "club_id": "arsenal",
            "insight_id": "ins_test_123"
        })
        assert res2.status_code == 201
        p2 = res2.json()
        assert p2["insight_id"] == "ins_test_123"
        assert p2["insight"] is not None
        assert p2["insight"]["metric"] == "win_rate"

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

@pytest.mark.asyncio
async def test_post_reactions_toggle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create post first
        create_res = await ac.post("/api/v1/terrace/posts", json={
            "content": "Forza Milan!",
            "author_name": "Rossonero",
            "author_club_id": "milan",
            "club_id": "milan"
        })
        post_id = create_res.json()["id"]

        # Add reaction
        rxn1 = await ac.post(f"/api/v1/terrace/posts/{post_id}/react", json={
            "user_id": "user_fan_1",
            "reaction_type": "cheer"
        })
        assert rxn1.status_code == 200
        assert rxn1.json()["action"] == "added"
        assert rxn1.json()["total_reactions"] == 1

        # Check list shows 1 reaction and user_reacted true
        list_res = await ac.get(f"/api/v1/terrace/posts?current_user_id=user_fan_1")
        assert list_res.status_code == 200
        post_item = list_res.json()[0]
        assert post_item["reactions_count"] == 1
        assert post_item["user_reacted"] is True

        # Toggle again -> removes reaction
        rxn2 = await ac.post(f"/api/v1/terrace/posts/{post_id}/react", json={
            "user_id": "user_fan_1",
            "reaction_type": "cheer"
        })
        assert rxn2.status_code == 200
        assert rxn2.json()["action"] == "removed"
        assert rxn2.json()["total_reactions"] == 0

@pytest.mark.asyncio
async def test_post_comments():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post("/api/v1/terrace/posts", json={
            "content": "Tactical debate on our defensive midfield setup.",
            "author_name": "Analyst10",
            "author_club_id": "barcelona"
        })
        post_id = create_res.json()["id"]

        # Add comment
        cmt_res = await ac.post(f"/api/v1/terrace/posts/{post_id}/comments", json={
            "content": "Agreed, we need more double-pivot coverage away from home.",
            "author_name": "CuleFan",
            "author_club_id": "barcelona"
        })
        assert cmt_res.status_code == 201
        cmt = cmt_res.json()
        assert cmt["content"] == "Agreed, we need more double-pivot coverage away from home."

        # Fetch comments
        comments_list = await ac.get(f"/api/v1/terrace/posts/{post_id}/comments")
        assert comments_list.status_code == 200
        assert len(comments_list.json()) == 1
