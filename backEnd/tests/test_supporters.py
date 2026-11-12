import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.football import Match
from app.models.insight import Insight
from app.models.predictions import Prediction
from app.models.profile import Profile
from app.models.terrace import Post, PostReaction


@pytest.mark.asyncio
async def test_supporter_nonexistent_returns_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/supporters/NonExistentSupporterXYZ")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_supporter_public_profile_from_real_db_records(session_factory):
    now = datetime.datetime.now(datetime.timezone.utc)
    async with session_factory() as session:
        session.add(
            Profile(
                id="usr_seed_alex",
                username="GoonerAlex",
                display_name="Gooner Alex",
                avatar_url="https://example.com/alex.png",
                favorite_club_id="arsenal",
                bio="Emirates tactical analyst",
            )
        )
        session.add(
            Insight(
                id="ins_alex_1",
                user_id="usr_seed_alex",
                author_name="GoonerAlex",
                author_club_id="arsenal",
                title="Emirates Win Rate",
                metric="win_rate",
                team_ids="arsenal",
                venue="home",
                snapshot='{"metric":"win_rate","formula":"(wins/n)*100","venue_filter":"home","series":[]}',
            )
        )
        post = Post(
            id="post_alex_1",
            author_id="usr_seed_alex",
            author_name="GoonerAlex",
            author_club_id="arsenal",
            club_id="arsenal",
            content="High press notes #Tactics",
        )
        session.add(post)
        session.add(
            PostReaction(
                id="rxn_alex_1",
                post_id="post_alex_1",
                user_id="usr_other_fan",
                reaction_type="cheer",
            )
        )
        session.add(
            Match(
                id="m_sup_1",
                competition_id="PL",
                competition_name="Premier League",
                season_id="2026-2027-PL",
                home_team_id="arsenal",
                home_team_name="Arsenal FC",
                away_team_id="chelsea",
                away_team_name="Chelsea FC",
                matchday=1,
                utc_date=now - datetime.timedelta(days=1),
                status="FINISHED",
                home_score=2,
                away_score=0,
                winner="HOME_TEAM",
            )
        )
        session.add(
            Prediction(
                id="pred_alex_1",
                user_id="usr_seed_alex",
                user_name="GoonerAlex",
                user_club_id="arsenal",
                match_id="m_sup_1",
                predicted_home_score=2,
                predicted_away_score=0,
            )
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/supporters/gooneralex")
        assert res.status_code == 200
        profile = res.json()
        assert profile["user_id"] == "usr_seed_alex"
        assert profile["username"] == "GoonerAlex"
        assert profile["display_name"] == "Gooner Alex"
        assert profile["avatar_url"] == "https://example.com/alex.png"
        assert profile["favorite_club_id"] == "arsenal"
        assert profile["bio"] == "Emirates tactical analyst"
        assert profile["stats"]["prediction_points"] == 3
        assert profile["stats"]["prediction_rank"] == 1
        assert profile["stats"]["total_predictions"] == 1
        assert profile["stats"]["exact_scores"] == 1
        assert profile["stats"]["insights_published"] == 1
        assert profile["stats"]["posts_count"] == 1
        assert profile["stats"]["cheers_received"] == 1
        assert len(profile["featured_insights"]) == 1
        assert len(profile["recent_posts"]) == 1


@pytest.mark.asyncio
async def test_supporter_profile_with_zero_predictions_has_rank_0(session_factory):
    async with session_factory() as session:
        session.add(
            Profile(
                id="usr_new_fan",
                username="NewGooner",
                display_name="New Gooner",
                favorite_club_id="arsenal",
            )
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/supporters/NewGooner")
        assert res.status_code == 200
        stats = res.json()["stats"]
        assert stats["prediction_points"] == 0
        assert stats["prediction_rank"] == 0
        assert stats["total_predictions"] == 0
