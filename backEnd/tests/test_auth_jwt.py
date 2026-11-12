import base64
import datetime
import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.security import _decode_supabase_jwt
from app.models.football import Club, Competition, Match, Season
from app.models.notifications import Notification
from app.main import app
from tests.helpers import TEST_JWT_SECRET, auth_headers, make_supabase_jwt


def _b64url(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _make_alg_none_token(sub: str = "usr_attacker") -> str:
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    header = _b64url({"alg": "none", "typ": "JWT"})
    payload = _b64url(
        {
            "sub": sub,
            "aud": "authenticated",
            "exp": now + 3600,
            "email": "attacker@example.com",
        }
    )
    return f"{header}.{payload}."


@pytest.mark.asyncio
async def test_missing_bearer_returns_401_across_protected_endpoints():
    protected_requests = [
        ("POST", "/api/v1/insights", {"title": "Test Insight", "metric": "win_rate", "team_ids": ["arsenal"]}),
        ("DELETE", "/api/v1/insights/ins_1", None),
        ("POST", "/api/v1/terrace/posts", {"content": "COYG"}),
        ("DELETE", "/api/v1/terrace/posts/post_1", None),
        ("POST", "/api/v1/terrace/posts/post_1/react", {"reaction_type": "cheer"}),
        ("POST", "/api/v1/terrace/posts/post_1/comments", {"content": "Nice"}),
        ("DELETE", "/api/v1/terrace/posts/post_1/comments/cmt_1", None),
        ("POST", "/api/v1/tactics", {"title": "4-3-3 Press", "formation": "4-3-3", "lineup": []}),
        ("DELETE", "/api/v1/tactics/tb_1", None),
        ("POST", "/api/v1/predictions", {"match_id": "m_1", "predicted_home_score": 2, "predicted_away_score": 0}),
        ("GET", "/api/v1/messages/conversations", None),
        ("POST", "/api/v1/messages/conversations", {"recipient_id": "usr_2"}),
        ("GET", "/api/v1/messages/conversations/conv_1/messages", None),
        ("POST", "/api/v1/messages/conversations/conv_1/messages", {"content": "Hi"}),
        ("GET", "/api/v1/notifications", None),
        ("GET", "/api/v1/notifications/unread-count", None),
        ("POST", "/api/v1/notifications/notif_1/read", None),
        ("POST", "/api/v1/notifications/read-all", None),
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for method, path, body in protected_requests:
            res = await ac.request(method, path, json=body)
            assert res.status_code == 401, f"{method} {path} returned {res.status_code}, expected 401"


@pytest.mark.asyncio
async def test_jwt_validation_rejects_malformed_alg_none_expired_wrong_secret_and_aud():
    bad_tokens = [
        ("garbage", "not-even-a-jwt"),
        ("alg-none", _make_alg_none_token()),
        ("expired", make_supabase_jwt(exp_delta_seconds=-120)),
        ("wrong-secret", make_supabase_jwt(secret="wrong-secret-key-at-least-32-chars-999")),
        ("wrong-aud", make_supabase_jwt(audience="anon")),
        ("missing-aud", make_supabase_jwt(audience=None)),
        ("missing-exp", make_supabase_jwt(include_exp=False)),
        ("missing-sub", make_supabase_jwt(include_sub=False)),
        ("blank-sub", make_supabase_jwt(user_id="   ")),
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for label, token in bad_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            res = await ac.get("/api/v1/notifications/unread-count", headers=headers)
            assert res.status_code == 401, f"{label} expected 401 on protected route, got {res.status_code}"

            # Optional-auth endpoints must STILL reject invalid Authorization headers
            opt_res = await ac.get("/api/v1/terrace/posts", headers=headers)
            assert opt_res.status_code == 401, f"{label} expected 401 on optional-auth route, got {opt_res.status_code}"

        # Non-Bearer Authorization header format
        bad_scheme = await ac.get(
            "/api/v1/notifications", headers={"Authorization": "Basic dXNlcjpwYXNz"}
        )
        assert bad_scheme.status_code == 401

        empty_bearer = await ac.get("/api/v1/notifications", headers={"Authorization": "Bearer "})
        assert empty_bearer.status_code == 401


@pytest.mark.asyncio
async def test_unset_jwt_secret_fails_closed(monkeypatch):
    valid_looking_token = make_supabase_jwt(user_id="usr_1", secret=TEST_JWT_SECRET)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", "")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/api/v1/notifications/unread-count",
            headers={"Authorization": f"Bearer {valid_looking_token}"},
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_user_metadata_role_admin_escalation_is_ignored():
    escalated_token = make_supabase_jwt(
        user_id="usr_attacker",
        email="attacker@example.com",
        user_metadata={"role": "admin", "is_admin": True},
    )
    decoded = _decode_supabase_jwt(escalated_token)
    assert decoded.id == "usr_attacker"
    assert decoded.role == "supporter"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create a post as usr_owner
        post_res = await ac.post(
            "/api/v1/terrace/posts",
            json={"content": "Owner tactical post"},
            headers=auth_headers("usr_owner", display_name="OwnerGooner"),
        )
        assert post_res.status_code == 201
        post_id = post_res.json()["id"]

        # Attacker with user_metadata.role="admin" must still receive 403
        del_res = await ac.delete(
            f"/api/v1/terrace/posts/{post_id}",
            headers={"Authorization": f"Bearer {escalated_token}"},
        )
        assert del_res.status_code == 403


@pytest.mark.asyncio
async def test_cross_user_403_ownership_on_posts_comments_insights_and_tactics():
    owner_headers = auth_headers("usr_owner", display_name="OwnerFan")
    other_headers = auth_headers("usr_other", display_name="OtherFan")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Insight ownership
        ins_res = await ac.post(
            "/api/v1/insights",
            json={
                "title": "Owner Win Rate",
                "metric": "win_rate",
                "team_ids": ["arsenal"],
                "venue": "all",
            },
            headers=owner_headers,
        )
        assert ins_res.status_code == 201
        insight_id = ins_res.json()["id"]
        assert ins_res.json()["user_id"] == "usr_owner"

        assert (await ac.delete(f"/api/v1/insights/{insight_id}", headers=other_headers)).status_code == 403
        assert (await ac.delete(f"/api/v1/insights/{insight_id}", headers=owner_headers)).status_code == 200
        assert (await ac.delete(f"/api/v1/insights/{insight_id}", headers=owner_headers)).status_code == 404

        # 2. Tactical board ownership & private board access
        tb_res = await ac.post(
            "/api/v1/tactics",
            json={
                "title": "Secret Set Piece",
                "formation": "4-3-3",
                "lineup": [
                    {"id": f"p{i}", "name": f"Player {i}", "number": i, "role": "CM", "x": 50.0, "y": 50.0}
                    for i in range(1, 12)
                ],
                "is_public": False,
            },
            headers=owner_headers,
        )
        assert tb_res.status_code == 200
        board_id = tb_res.json()["id"]
        assert tb_res.json()["user_id"] == "usr_owner"

        assert (await ac.get(f"/api/v1/tactics/{board_id}")).status_code == 403
        assert (await ac.get(f"/api/v1/tactics/{board_id}", headers=other_headers)).status_code == 403
        assert (await ac.get(f"/api/v1/tactics/{board_id}", headers=owner_headers)).status_code == 200

        assert (await ac.delete(f"/api/v1/tactics/{board_id}", headers=other_headers)).status_code == 403
        assert (await ac.delete(f"/api/v1/tactics/{board_id}", headers=owner_headers)).status_code == 200

        # 3. Post & comment ownership
        post_res = await ac.post(
            "/api/v1/terrace/posts",
            json={"content": "Arsenal press breakdown"},
            headers=owner_headers,
        )
        assert post_res.status_code == 201
        post_id = post_res.json()["id"]

        cmt_res = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/comments",
            json={"content": "Great read"},
            headers=other_headers,
        )
        assert cmt_res.status_code == 201
        comment_id = cmt_res.json()["id"]

        # Owner of post cannot delete someone else's comment directly, and non-owner cannot delete post
        assert (
            await ac.delete(
                f"/api/v1/terrace/posts/{post_id}/comments/{comment_id}",
                headers=owner_headers,
            )
        ).status_code == 403
        assert (await ac.delete(f"/api/v1/terrace/posts/{post_id}", headers=other_headers)).status_code == 403

        # Comment author can delete own comment; post author can delete own post
        assert (
            await ac.delete(
                f"/api/v1/terrace/posts/{post_id}/comments/{comment_id}",
                headers=other_headers,
            )
        ).status_code == 200
        assert (await ac.delete(f"/api/v1/terrace/posts/{post_id}", headers=owner_headers)).status_code == 200


@pytest.mark.asyncio
async def test_messaging_non_member_and_cross_user_403():
    user_a = auth_headers("usr_dm_a", display_name="UserA")
    user_c = auth_headers("usr_dm_intruder", display_name="Intruder")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        conv_res = await ac.post(
            "/api/v1/messages/conversations",
            json={"recipient_id": "usr_dm_b", "initial_message": "Private tactics talk"},
            headers=user_a,
        )
        assert conv_res.status_code == 201
        conv_id = conv_res.json()["id"]

        # Intruder cannot read or send messages in A<->B conversation
        assert (
            await ac.get(f"/api/v1/messages/conversations/{conv_id}/messages", headers=user_c)
        ).status_code == 403
        assert (
            await ac.post(
                f"/api/v1/messages/conversations/{conv_id}/messages",
                json={"content": "Sneaking in"},
                headers=user_c,
            )
        ).status_code == 403

        # Cross-user query param mismatch returns 403
        assert (
            await ac.get("/api/v1/messages/conversations?user_id=usr_dm_a", headers=user_c)
        ).status_code == 403


@pytest.mark.asyncio
async def test_notifications_cross_user_403(session_factory):
    async with session_factory() as session:
        session.add(
            Notification(
                id="notif_private_1",
                user_id="usr_notif_owner",
                type="cheer",
                title="New Cheer",
                message="Someone cheered your post",
                link="/terrace",
                is_read=False,
            )
        )
        await session.commit()

    other_headers = auth_headers("usr_notif_other")
    owner_headers = auth_headers("usr_notif_owner")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        assert (
            await ac.get("/api/v1/notifications?user_id=usr_notif_owner", headers=other_headers)
        ).status_code == 403
        assert (
            await ac.get(
                "/api/v1/notifications/unread-count?user_id=usr_notif_owner",
                headers=other_headers,
            )
        ).status_code == 403
        assert (
            await ac.post(
                "/api/v1/notifications/read-all?user_id=usr_notif_owner",
                headers=other_headers,
            )
        ).status_code == 403
        assert (
            await ac.post("/api/v1/notifications/notif_private_1/read", headers=other_headers)
        ).status_code == 403

        # Owner can mark it read
        ok_res = await ac.post("/api/v1/notifications/notif_private_1/read", headers=owner_headers)
        assert ok_res.status_code == 200


@pytest.mark.asyncio
async def test_predictor_kickoff_lock_400_and_404(session_factory):
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
                    id="match_past_scheduled",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    matchday=10,
                    utc_date=now - datetime.timedelta(minutes=15),
                    status="SCHEDULED",
                ),
                Match(
                    id="match_already_finished",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    matchday=9,
                    utc_date=now + datetime.timedelta(days=1),
                    status="FINISHED",
                    home_score=2,
                    away_score=0,
                    winner="HOME_TEAM",
                ),
            ]
        )
        await session.commit()

    headers = auth_headers("usr_pred_1", display_name="Predictor")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        past_res = await ac.post(
            "/api/v1/predictions",
            json={
                "user_id": "forged_other_user",
                "match_id": "match_past_scheduled",
                "predicted_home_score": 2,
                "predicted_away_score": 1,
            },
            headers=headers,
        )
        assert past_res.status_code == 400
        assert "locked" in past_res.json()["detail"].lower()

        fin_res = await ac.post(
            "/api/v1/predictions",
            json={
                "match_id": "match_already_finished",
                "predicted_home_score": 2,
                "predicted_away_score": 0,
            },
            headers=headers,
        )
        assert fin_res.status_code == 400

        missing_res = await ac.post(
            "/api/v1/predictions",
            json={
                "match_id": "match_does_not_exist",
                "predicted_home_score": 1,
                "predicted_away_score": 1,
            },
            headers=headers,
        )
        assert missing_res.status_code == 404
