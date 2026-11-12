import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.models.football import Club, Competition, Match, Season
from app.models.notifications import Notification
from app.models.predictions import Prediction
from app.models.profile import Profile
from app.models.terrace import PostComment, PostReaction
from tests.helpers import auth_headers


@pytest.mark.asyncio
async def test_terrace_delete_ownership_and_auto_notifications(session_factory):
    author_headers = auth_headers("usr_t_author", display_name="AuthorGooner")
    cheerer_headers = auth_headers("usr_t_cheerer", display_name="CheererGooner")
    commenter_headers = auth_headers("usr_t_commenter", display_name="ReplyGooner")
    intruder_headers = auth_headers("usr_t_intruder", display_name="Intruder")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        post_res = await ac.post(
            "/api/v1/terrace/posts",
            json={"content": "Bukayo Saka inside-right isolation #Tactics"},
            headers=author_headers,
        )
        assert post_res.status_code == 201
        post_id = post_res.json()["id"]

        # 1. Cheer by another user emits cheer notification; toggle off emits none
        cheer_add = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/cheer", headers=cheerer_headers
        )
        assert cheer_add.status_code == 200
        assert cheer_add.json()["action"] == "added"

        cheer_rem = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/cheer", headers=cheerer_headers
        )
        assert cheer_rem.status_code == 200
        assert cheer_rem.json()["action"] == "removed"

        # Self-cheer must NOT emit notification
        self_cheer = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/cheer", headers=author_headers
        )
        assert self_cheer.status_code == 200

        # 2. Comment by another user emits reply notification; self-comment does not
        cmt_res = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/comments",
            json={"content": "White's overlap unlocks the lane."},
            headers=commenter_headers,
        )
        assert cmt_res.status_code == 201
        cmt_id = cmt_res.json()["id"]

        self_cmt = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/comments",
            json={"content": "Adding tactical note to my own post."},
            headers=author_headers,
        )
        assert self_cmt.status_code == 201

        author_notifs = (
            await ac.get("/api/v1/notifications", headers=author_headers)
        ).json()
        assert len(author_notifs) == 2
        by_type = {n["type"]: n for n in author_notifs}
        assert set(by_type.keys()) == {"cheer", "reply"}
        assert by_type["cheer"]["link"] == f"/terrace#post-{post_id}"
        assert by_type["reply"]["link"] == f"/terrace#post-{post_id}"

        # 3. Comment delete ownership: 403 non-owner, 404 missing, 200 owner
        assert (
            await ac.delete(
                f"/api/v1/terrace/posts/{post_id}/comments/{cmt_id}",
                headers=intruder_headers,
            )
        ).status_code == 403
        assert (
            await ac.delete(
                f"/api/v1/terrace/posts/{post_id}/comments/{cmt_id}",
                headers=author_headers,
            )
        ).status_code == 403
        assert (
            await ac.delete(
                f"/api/v1/terrace/posts/{post_id}/comments/cmt_missing",
                headers=commenter_headers,
            )
        ).status_code == 404
        del_cmt = await ac.delete(
            f"/api/v1/terrace/posts/{post_id}/comments/{cmt_id}",
            headers=commenter_headers,
        )
        assert del_cmt.status_code == 200
        assert del_cmt.json() == {"status": "deleted", "id": cmt_id}

        # 4. Post delete ownership: 403 non-owner, 404 missing, 200 owner + child cleanup
        assert (
            await ac.delete(
                f"/api/v1/terrace/posts/{post_id}", headers=intruder_headers
            )
        ).status_code == 403
        assert (
            await ac.delete(
                "/api/v1/terrace/posts/post_missing_999", headers=author_headers
            )
        ).status_code == 404
        del_post = await ac.delete(
            f"/api/v1/terrace/posts/{post_id}", headers=author_headers
        )
        assert del_post.status_code == 200
        assert del_post.json() == {"status": "deleted", "id": post_id}

    async with session_factory() as session:
        rem_comments = (
            await session.execute(
                select(PostComment).where(PostComment.post_id == post_id)
            )
        ).scalars().all()
        rem_reactions = (
            await session.execute(
                select(PostReaction).where(PostReaction.post_id == post_id)
            )
        ).scalars().all()
        assert rem_comments == []
        assert rem_reactions == []


@pytest.mark.asyncio
async def test_messaging_unread_profiles_read_cursor_and_notifications(session_factory):
    async with session_factory() as session:
        session.add_all(
            [
                Profile(
                    id="usr_msg_1",
                    username="alice_afc",
                    display_name="Alice AFC",
                    avatar_url="https://example.com/alice.png",
                    favorite_club_id="arsenal",
                ),
                Profile(
                    id="usr_msg_2",
                    username="bob_afc",
                    display_name="Bob AFC",
                    avatar_url="https://example.com/bob.png",
                    favorite_club_id="arsenal",
                ),
            ]
        )
        await session.commit()

    u1_headers = auth_headers("usr_msg_1", display_name="Alice AFC")
    u2_headers = auth_headers("usr_msg_2", display_name="Bob AFC")
    intruder_headers = auth_headers("usr_msg_intruder", display_name="Intruder")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Start conversation with initial message
        create_res = await ac.post(
            "/api/v1/messages/conversations",
            json={
                "recipient_id": "usr_msg_2",
                "initial_message": "Thoughts on Rice at 6 vs 8?",
            },
            headers=u1_headers,
        )
        assert create_res.status_code == 201
        c1 = create_res.json()
        conv_id = c1["id"]
        assert c1["unread_count"] == 0
        assert c1["other_member_profile"]["username"] == "bob_afc"
        assert c1["other_member_profile"]["avatar_url"] == "https://example.com/bob.png"

        # 2. Recipient sees unread_count == 1, Alice's profile, and a direct_message notification
        u2_convs = (
            await ac.get("/api/v1/messages/conversations", headers=u2_headers)
        ).json()
        assert len(u2_convs) == 1
        assert u2_convs[0]["unread_count"] == 1
        assert u2_convs[0]["other_member_profile"]["username"] == "alice_afc"

        u2_notifs = (await ac.get("/api/v1/notifications", headers=u2_headers)).json()
        assert len(u2_notifs) == 1
        assert u2_notifs[0]["type"] == "direct_message"
        assert u2_notifs[0]["link"] == f"/messages?c={conv_id}"

        # 3. Sender sends a follow-up -> unread_count becomes 2 and second notification created
        send_res = await ac.post(
            f"/api/v1/messages/conversations/{conv_id}/messages",
            json={"content": "With Zubimendi behind him, Rice thrives at 8."},
            headers=u1_headers,
        )
        assert send_res.status_code == 201

        u2_convs_2 = (
            await ac.get("/api/v1/messages/conversations", headers=u2_headers)
        ).json()
        assert u2_convs_2[0]["unread_count"] == 2
        assert len((await ac.get("/api/v1/notifications", headers=u2_headers)).json()) == 2

        # 4. Non-member / unauthenticated / missing read cursor checks
        assert (
            await ac.post(f"/api/v1/messages/conversations/{conv_id}/read")
        ).status_code == 401
        assert (
            await ac.post(
                f"/api/v1/messages/conversations/{conv_id}/read",
                headers=intruder_headers,
            )
        ).status_code == 403
        assert (
            await ac.post(
                "/api/v1/messages/conversations/conv_missing/read",
                headers=u2_headers,
            )
        ).status_code == 404

        # 5. Recipient marks conversation read -> resets unread_count to 0
        read_res = await ac.post(
            f"/api/v1/messages/conversations/{conv_id}/read", headers=u2_headers
        )
        assert read_res.status_code == 200
        assert read_res.json() == {"status": "ok", "unread_count": 0}

        u2_convs_after = (
            await ac.get("/api/v1/messages/conversations", headers=u2_headers)
        ).json()
        assert u2_convs_after[0]["unread_count"] == 0


@pytest.mark.asyncio
async def test_predictions_grade_idempotency_notifications_and_history(session_factory):
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
                Season(
                    id="2026-2027-PL",
                    competition_id="PL",
                    start_year=2026,
                    end_year=2027,
                    is_current=True,
                ),
                Match(
                    id="m_grade_fin",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    matchday=10,
                    utc_date=now - datetime.timedelta(days=1),
                    status="FINISHED",
                    home_score=2,
                    away_score=1,
                    winner="HOME_TEAM",
                ),
                Match(
                    id="m_grade_sched",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="tottenham",
                    away_team_name="Tottenham Hotspur",
                    matchday=11,
                    utc_date=now + datetime.timedelta(days=5),
                    status="SCHEDULED",
                ),
                # Exact (3 pts)
                Prediction(
                    id="pr_exact",
                    user_id="usr_p_exact",
                    user_name="ExactFan",
                    user_club_id="arsenal",
                    match_id="m_grade_fin",
                    predicted_home_score=2,
                    predicted_away_score=1,
                    created_at=now - datetime.timedelta(days=2),
                ),
                # Correct outcome (1 pt)
                Prediction(
                    id="pr_outcome",
                    user_id="usr_p_outcome",
                    user_name="OutcomeFan",
                    user_club_id="arsenal",
                    match_id="m_grade_fin",
                    predicted_home_score=3,
                    predicted_away_score=0,
                    created_at=now - datetime.timedelta(days=2),
                ),
                # Miss (0 pts)
                Prediction(
                    id="pr_miss",
                    user_id="usr_p_miss",
                    user_name="MissFan",
                    user_club_id="arsenal",
                    match_id="m_grade_fin",
                    predicted_home_score=0,
                    predicted_away_score=2,
                    created_at=now - datetime.timedelta(days=2),
                ),
                # Pending prediction for usr_p_exact on future match
                Prediction(
                    id="pr_pending",
                    user_id="usr_p_exact",
                    user_name="ExactFan",
                    user_club_id="arsenal",
                    match_id="m_grade_sched",
                    predicted_home_score=2,
                    predicted_away_score=0,
                    created_at=now - datetime.timedelta(hours=1),
                ),
            ]
        )
        await session.commit()

    exact_headers = auth_headers("usr_p_exact", display_name="ExactFan")
    outcome_headers = auth_headers("usr_p_outcome", display_name="OutcomeFan")
    miss_headers = auth_headers("usr_p_miss", display_name="MissFan")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Unauth checks
        assert (await ac.post("/api/v1/predictions/grade/m_grade_fin")).status_code == 401
        assert (await ac.get("/api/v1/predictions/history")).status_code == 401

        # Missing & non-finished checks
        assert (
            await ac.post("/api/v1/predictions/grade/m_missing", headers=exact_headers)
        ).status_code == 404
        assert (
            await ac.post(
                "/api/v1/predictions/grade/m_grade_sched", headers=exact_headers
            )
        ).status_code == 400

        # Grade finished match
        grade_res = await ac.post(
            "/api/v1/predictions/grade/m_grade_fin", headers=exact_headers
        )
        assert grade_res.status_code == 200
        assert grade_res.json() == {"match_id": "m_grade_fin", "graded_count": 3}

        # Idempotent second call -> graded_count == 0, no duplicate notifications
        grade_res_2 = await ac.post(
            "/api/v1/predictions/grade/m_grade_fin", headers=exact_headers
        )
        assert grade_res_2.status_code == 200
        assert grade_res_2.json() == {"match_id": "m_grade_fin", "graded_count": 0}

        # Verify prediction_result notifications emitted exactly once per user
        for hdrs, expected_pts in [
            (exact_headers, "3 pts"),
            (outcome_headers, "1 pt"),
            (miss_headers, "0 pts"),
        ]:
            notifs = (await ac.get("/api/v1/notifications", headers=hdrs)).json()
            assert len(notifs) == 1
            assert notifs[0]["type"] == "prediction_result"
            assert notifs[0]["link"] == "/predictions"
            assert expected_pts in notifs[0]["message"]

        # Verify prediction history ordering & fields
        hist_res = await ac.get("/api/v1/predictions/history", headers=exact_headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) == 2

        # Newest first: scheduled pending match, then graded finished match
        assert history[0]["match_id"] == "m_grade_sched"
        assert history[0]["status"] == "PENDING"
        assert history[0]["points_awarded"] is None
        assert history[0]["home_team"] == "Arsenal FC"
        assert history[0]["away_team"] == "Tottenham Hotspur"

        assert history[1]["match_id"] == "m_grade_fin"
        assert history[1]["status"] == "GRADED"
        assert history[1]["points_awarded"] == 3
        assert history[1]["home_score"] == 2
        assert history[1]["away_score"] == 1
        assert history[1]["competition"] == "Premier League"
