import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.models.football import Club, Competition, Match, Season
from app.models.insight import Insight
from app.models.notifications import Notification
from app.models.predictions import Prediction
from app.services.ingestion import FootballIngestionService
from tests.helpers import auth_headers


@pytest.mark.asyncio
async def test_multi_season_trends_rollup_venue_and_route_precedence(session_factory):
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
                Competition(id="CL", code="CL", name="UEFA Champions League", country="Europe"),
                Season(id="2024-2025-PL", competition_id="PL", start_year=2024, end_year=2025, is_current=False),
                Season(id="2024-2025-CL", competition_id="CL", start_year=2024, end_year=2025, is_current=False),
                Season(id="2026-2027-PL", competition_id="PL", start_year=2026, end_year=2027, is_current=True),
                # 2024-2025 PL home win + clean sheet (2-0)
                Match(
                    id="tr_2425_pl_h",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2024-2025-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    utc_date=datetime.datetime(2024, 10, 1, 15, 0, tzinfo=datetime.timezone.utc),
                    status="FINISHED",
                    home_score=2,
                    away_score=0,
                    winner="HOME_TEAM",
                ),
                # 2024-2025 CL away draw (1-1) -> rolls into 2024-2025 campaign bucket
                Match(
                    id="tr_2425_cl_a",
                    competition_id="CL",
                    competition_name="UEFA Champions League",
                    season_id="2024-2025-CL",
                    home_team_id="real-madrid",
                    home_team_name="Real Madrid CF",
                    away_team_id="arsenal",
                    away_team_name="Arsenal FC",
                    utc_date=datetime.datetime(2025, 3, 1, 20, 0, tzinfo=datetime.timezone.utc),
                    status="FINISHED",
                    home_score=1,
                    away_score=1,
                    winner="DRAW",
                ),
                # 2026-2027 PL away loss (0-2)
                Match(
                    id="tr_2627_pl_a",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="liverpool",
                    home_team_name="Liverpool FC",
                    away_team_id="arsenal",
                    away_team_name="Arsenal FC",
                    utc_date=now - datetime.timedelta(days=5),
                    status="FINISHED",
                    home_score=2,
                    away_score=0,
                    winner="HOME_TEAM",
                ),
                # Scheduled & null-score finished matches must be ignored
                Match(
                    id="tr_2627_sched",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="wolves",
                    away_team_name="Wolverhampton Wanderers FC",
                    utc_date=now + datetime.timedelta(days=5),
                    status="SCHEDULED",
                ),
                Match(
                    id="tr_2627_null",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="everton",
                    away_team_name="Everton FC",
                    utc_date=now - datetime.timedelta(days=2),
                    status="FINISHED",
                    home_score=None,
                    away_score=None,
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Route precedence: /matches/trends must NOT fall through to /{match_id} (404)
        res_all = await ac.get("/api/v1/matches/trends?club_id=arsenal&venue=all")
        assert res_all.status_code == 200
        body = res_all.json()
        assert body["club_id"] == "arsenal"
        assert body["club_name"] == "Arsenal FC"
        assert body["venue_filter"] == "all"

        trends = body["trends"]
        assert len(trends) == 8
        # Strictly chronological 2019/20 -> 2026/27
        start_years = [t["start_year"] for t in trends]
        assert start_years == [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

        by_season = {t["season_id"]: t for t in trends}
        # Zero-division safety for empty season
        empty_season = by_season["2019-2020-PL"]
        assert empty_season["matches_played"] == 0
        assert empty_season["win_rate"] == 0.0
        assert empty_season["points_per_game"] == 0.0
        assert empty_season["goals_per_match"] == 0.0
        assert empty_season["clean_sheet_rate"] == 0.0
        assert empty_season["loss_rate"] == 0.0

        # 2024-2025 combines PL (2-0 W) + CL (1-1 D) => 2 MP, 1 W, 1 D, 0 L, 1 CS, 3 GF, 1 GA
        s24 = by_season["2024-2025-PL"]
        assert s24["matches_played"] == 2
        assert s24["wins"] == 1
        assert s24["draws"] == 1
        assert s24["losses"] == 0
        assert s24["clean_sheets"] == 1
        assert s24["goals_for"] == 3
        assert s24["goals_against"] == 1
        assert s24["goal_difference"] == 2
        assert s24["win_rate"] == 50.0
        assert s24["points_per_game"] == 2.0
        assert s24["goals_per_match"] == 1.5
        assert s24["clean_sheet_rate"] == 50.0
        assert s24["loss_rate"] == 0.0

        # 2026-2027 only counts finished non-null away loss (0-2)
        s26 = by_season["2026-2027-PL"]
        assert s26["matches_played"] == 1
        assert s26["losses"] == 1
        assert s26["loss_rate"] == 100.0

        # Venue filtering: home -> only 2024-2025 PL home win
        res_home = await ac.get("/api/v1/matches/trends?club_id=arsenal&venue=home")
        assert res_home.status_code == 200
        h24 = {t["season_id"]: t for t in res_home.json()["trends"]}["2024-2025-PL"]
        assert h24["matches_played"] == 1
        assert h24["wins"] == 1
        assert h24["win_rate"] == 100.0
        assert h24["clean_sheet_rate"] == 100.0

        # Venue filtering: away -> 2024-2025 CL draw + 2026-2027 PL loss
        res_away = await ac.get("/api/v1/matches/trends?club_id=arsenal&venue=away")
        assert res_away.status_code == 200
        away_map = {t["season_id"]: t for t in res_away.json()["trends"]}
        assert away_map["2024-2025-PL"]["matches_played"] == 1
        assert away_map["2024-2025-PL"]["draws"] == 1
        assert away_map["2024-2025-PL"]["points_per_game"] == 1.0
        assert away_map["2026-2027-PL"]["losses"] == 1

        # Invalid venue rejected cleanly
        bad_venue = await ac.get("/api/v1/matches/trends?club_id=arsenal&venue=neutral")
        assert bad_venue.status_code == 422


@pytest.mark.asyncio
async def test_opponent_h2h_math_ordering_opponents_and_venue(session_factory):
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
                Season(id="2024-2025-PL", competition_id="PL", start_year=2024, end_year=2025, is_current=True),
                # Oldest Arsenal vs Chelsea: Home win 5-0 (clean sheet)
                Match(
                    id="h2h_1",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2024-2025-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    utc_date=datetime.datetime(2024, 4, 23, 19, 0, tzinfo=datetime.timezone.utc),
                    status="FINISHED",
                    home_score=5,
                    away_score=0,
                    winner="HOME_TEAM",
                ),
                # Middle Arsenal vs Chelsea: Away draw 1-1
                Match(
                    id="h2h_2",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2024-2025-PL",
                    home_team_id="chelsea",
                    home_team_name="Chelsea FC",
                    away_team_id="arsenal",
                    away_team_name="Arsenal FC",
                    utc_date=datetime.datetime(2024, 11, 10, 16, 30, tzinfo=datetime.timezone.utc),
                    status="FINISHED",
                    home_score=1,
                    away_score=1,
                    winner="DRAW",
                ),
                # Newest Arsenal vs Chelsea: Away loss 1-2
                Match(
                    id="h2h_3",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2024-2025-PL",
                    home_team_id="chelsea",
                    home_team_name="Chelsea FC",
                    away_team_id="arsenal",
                    away_team_name="Arsenal FC",
                    utc_date=datetime.datetime(2025, 3, 16, 13, 30, tzinfo=datetime.timezone.utc),
                    status="FINISHED",
                    home_score=2,
                    away_score=1,
                    winner="HOME_TEAM",
                ),
                # Another opponent (Tottenham) to verify available_opponents list
                Match(
                    id="h2h_spurs",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2024-2025-PL",
                    home_team_id="tottenham",
                    home_team_name="Tottenham Hotspur FC",
                    away_team_id="arsenal",
                    away_team_name="Arsenal FC",
                    utc_date=datetime.datetime(2024, 9, 15, 13, 0, tzinfo=datetime.timezone.utc),
                    status="FINISHED",
                    home_score=0,
                    away_score=1,
                    winner="AWAY_TEAM",
                ),
                # Scheduled match against Chelsea must be excluded
                Match(
                    id="h2h_sched",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2024-2025-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    utc_date=datetime.datetime(2027, 4, 1, 15, 0, tzinfo=datetime.timezone.utc),
                    status="SCHEDULED",
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/matches/h2h?club_id=arsenal&opponent_id=chelsea&venue=all")
        assert res.status_code == 200
        data = res.json()
        assert data["club_id"] == "arsenal"
        assert data["opponent_id"] == "chelsea"
        assert data["opponent_name"] == "Chelsea FC"
        assert data["matches_played"] == 3
        assert data["wins"] == 1
        assert data["draws"] == 1
        assert data["losses"] == 1
        assert data["clean_sheets"] == 1
        assert data["goals_for"] == 7
        assert data["goals_against"] == 3
        assert data["goal_difference"] == 4
        assert data["win_rate"] == 33.3

        # Newest-first recent_matches ordering
        assert [m["id"] for m in data["recent_matches"]] == ["h2h_3", "h2h_2", "h2h_1"]

        # available_opponents includes Chelsea (3) then Tottenham (1)
        opponents = {o["opponent_id"]: o for o in data["available_opponents"]}
        assert opponents["chelsea"]["matches_played"] == 3
        assert opponents["chelsea"]["opponent_name"] == "Chelsea FC"
        assert opponents["tottenham"]["matches_played"] == 1
        assert opponents["tottenham"]["opponent_name"] == "Tottenham Hotspur FC"

        # Venue filtering: home -> only h2h_1
        res_home = await ac.get("/api/v1/matches/h2h?club_id=arsenal&opponent_id=chelsea&venue=home")
        assert res_home.status_code == 200
        home_data = res_home.json()
        assert home_data["matches_played"] == 1
        assert home_data["wins"] == 1
        assert home_data["win_rate"] == 100.0
        assert [m["id"] for m in home_data["recent_matches"]] == ["h2h_1"]

        # Venue filtering: away -> h2h_3, h2h_2
        res_away = await ac.get("/api/v1/matches/h2h?club_id=arsenal&opponent_id=chelsea&venue=away")
        assert res_away.status_code == 200
        away_data = res_away.json()
        assert away_data["matches_played"] == 2
        assert away_data["draws"] == 1
        assert away_data["losses"] == 1
        assert away_data["goals_for"] == 2
        assert away_data["goals_against"] == 3
        assert away_data["goal_difference"] == -1
        assert away_data["win_rate"] == 0.0
        assert [m["id"] for m in away_data["recent_matches"]] == ["h2h_3", "h2h_2"]

        # Unseen opponent safe zero-state
        res_none = await ac.get("/api/v1/matches/h2h?club_id=arsenal&opponent_id=barcelona")
        assert res_none.status_code == 200
        none_data = res_none.json()
        assert none_data["matches_played"] == 0
        assert none_data["win_rate"] == 0.0
        assert none_data["recent_matches"] == []
        assert len(none_data["available_opponents"]) == 2

        bad_venue = await ac.get("/api/v1/matches/h2h?club_id=arsenal&opponent_id=chelsea&venue=neutral")
        assert bad_venue.status_code == 422


@pytest.mark.asyncio
async def test_terrace_patch_ownership_validation_no_duplicate_notifs_and_dynamic_tags(session_factory):
    async with session_factory() as session:
        session.add(
            Insight(
                id="ins_p4_edit",
                user_id="usr_p4_owner",
                author_name="OwnerGooner",
                author_club_id="arsenal",
                title="Arsenal Clean Sheet Edge",
                metric="clean_sheet_rate",
                team_ids="arsenal",
                venue="all",
                snapshot='{"metric":"clean_sheet_rate","formula":"(clean_sheets / matches_played) * 100","venue_filter":"all","series":[]}',
            )
        )
        await session.commit()

    owner_headers = auth_headers("usr_p4_owner", display_name="OwnerGooner")
    other_headers = auth_headers("usr_p4_other", display_name="ReplyGooner")
    intruder_headers = auth_headers("usr_p4_intruder", display_name="Intruder")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create post with #OldTag and image_url + insight
        create_res = await ac.post(
            "/api/v1/terrace/posts",
            json={
                "content": "Initial tactical breakdown on our right-side triangle. #OldTag #Tactics",
                "image_url": "https://example.com/initial.jpg",
                "insight_id": "ins_p4_edit",
                "club_id": "arsenal",
            },
            headers=owner_headers,
        )
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]

        # Create a second post and cheer/comment from other user so relationships & notifications exist
        cheer_res = await ac.post(f"/api/v1/terrace/posts/{post_id}/cheer", headers=other_headers)
        assert cheer_res.status_code == 200

        cmt_res = await ac.post(
            f"/api/v1/terrace/posts/{post_id}/comments",
            json={"content": "Original comment on Timber inverting."},
            headers=other_headers,
        )
        assert cmt_res.status_code == 201
        cmt_id = cmt_res.json()["id"]

        # Baseline notifications for post owner == 2 (1 cheer + 1 reply)
        notifs_before = (await ac.get("/api/v1/notifications", headers=owner_headers)).json()
        assert len(notifs_before) == 2

        # Tags after create
        tags_after_create = {t["tag"]: t["count"] for t in (await ac.get("/api/v1/terrace/tags")).json()}
        assert tags_after_create == {"OldTag": 1, "Tactics": 1}

        # Unauthenticated PATCH -> 401
        assert (
            await ac.patch(f"/api/v1/terrace/posts/{post_id}", json={"content": "Unauth edit"})
        ).status_code == 401
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/{post_id}/comments/{cmt_id}",
                json={"content": "Unauth comment edit"},
            )
        ).status_code == 401

        # Non-owner PATCH -> 403
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/{post_id}",
                json={"content": "Hijacked"},
                headers=intruder_headers,
            )
        ).status_code == 403
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/{post_id}/comments/{cmt_id}",
                json={"content": "Hijacked comment"},
                headers=owner_headers,
            )
        ).status_code == 403

        # Missing post / missing comment / mismatched post_id -> 404
        assert (
            await ac.patch(
                "/api/v1/terrace/posts/post_missing_404",
                json={"content": "Missing"},
                headers=owner_headers,
            )
        ).status_code == 404
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/{post_id}/comments/cmt_missing_404",
                json={"content": "Missing comment"},
                headers=other_headers,
            )
        ).status_code == 404
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/wrong_post_id/comments/{cmt_id}",
                json={"content": "Wrong parent"},
                headers=other_headers,
            )
        ).status_code == 404

        # Blank / whitespace content -> 422
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/{post_id}",
                json={"content": ""},
                headers=owner_headers,
            )
        ).status_code == 422
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/{post_id}",
                json={"content": "    "},
                headers=owner_headers,
            )
        ).status_code == 422
        assert (
            await ac.patch(
                f"/api/v1/terrace/posts/{post_id}/comments/{cmt_id}",
                json={"content": "   "},
                headers=other_headers,
            )
        ).status_code == 422

        # Owner PATCH post omitting image_url preserves image_url, sets updated_at, reloads counts/insight
        patch_post_1 = await ac.patch(
            f"/api/v1/terrace/posts/{post_id}",
            json={"content": "Updated breakdown with Rice & Zubimendi pivot. #NewTag #Tactics"},
            headers=owner_headers,
        )
        assert patch_post_1.status_code == 200
        edited_post = patch_post_1.json()
        assert edited_post["content"] == "Updated breakdown with Rice & Zubimendi pivot. #NewTag #Tactics"
        assert edited_post["image_url"] == "https://example.com/initial.jpg"
        assert edited_post["updated_at"] is not None
        assert edited_post["reactions_count"] == 1
        assert edited_post["comments_count"] == 1
        assert edited_post["insight"]["id"] == "ins_p4_edit"
        assert edited_post["user_reacted"] is False

        # Other user sees user_reacted == True on reloaded post
        list_other = (await ac.get("/api/v1/terrace/posts", headers=other_headers)).json()
        assert list_other[0]["user_reacted"] is True

        # Owner PATCH post explicitly clearing image_url
        patch_post_2 = await ac.patch(
            f"/api/v1/terrace/posts/{post_id}",
            json={"content": "Updated breakdown without photo. #NewTag #Tactics", "image_url": None},
            headers=owner_headers,
        )
        assert patch_post_2.status_code == 200
        assert patch_post_2.json()["image_url"] is None

        # Owner PATCH comment
        patch_cmt = await ac.patch(
            f"/api/v1/terrace/posts/{post_id}/comments/{cmt_id}",
            json={"content": "  Edited comment: Calafiori & Timber both invert cleanly.  "},
            headers=other_headers,
        )
        assert patch_cmt.status_code == 200
        assert patch_cmt.json()["content"] == "Edited comment: Calafiori & Timber both invert cleanly."

        # Zero duplicate notifications emitted on post or comment edit
        notifs_after_owner = (await ac.get("/api/v1/notifications", headers=owner_headers)).json()
        notifs_after_other = (await ac.get("/api/v1/notifications", headers=other_headers)).json()
        assert len(notifs_after_owner) == 2
        assert len(notifs_after_other) == 0

        # Dynamic tags updated immediately after edit (#OldTag gone, #NewTag present)
        tags_after_edit = {t["tag"]: t["count"] for t in (await ac.get("/api/v1/terrace/tags")).json()}
        assert tags_after_edit == {"NewTag": 1, "Tactics": 1}
        assert "OldTag" not in tags_after_edit

        # Dynamic tags return [] after delete
        del_res = await ac.delete(f"/api/v1/terrace/posts/{post_id}", headers=owner_headers)
        assert del_res.status_code == 200
        tags_after_delete = (await ac.get("/api/v1/terrace/tags")).json()
        assert tags_after_delete == []


@pytest.mark.asyncio
async def test_ingestion_run_sync_auto_grades_predictions_idempotently(session_factory):
    now = datetime.datetime.now(datetime.timezone.utc)
    # Seed ungraded predictions targeting fallback matches:
    # - fd-ars-1 is FINISHED: Arsenal FC 2 - 0 Wolverhampton Wanderers FC
    # - fd-ars-40 is SCHEDULED: Arsenal FC vs Nottingham Forest FC
    async with session_factory() as session:
        session.add_all(
            [
                Prediction(
                    id="pred_sync_exact",
                    user_id="usr_sync_exact",
                    user_name="ExactSyncFan",
                    user_club_id="arsenal",
                    match_id="fd-ars-1",
                    predicted_home_score=2,
                    predicted_away_score=0,
                    created_at=now - datetime.timedelta(days=5),
                ),
                Prediction(
                    id="pred_sync_outcome",
                    user_id="usr_sync_outcome",
                    user_name="OutcomeSyncFan",
                    user_club_id="arsenal",
                    match_id="fd-ars-1",
                    predicted_home_score=3,
                    predicted_away_score=1,
                    created_at=now - datetime.timedelta(days=5),
                ),
                Prediction(
                    id="pred_sync_miss",
                    user_id="usr_sync_miss",
                    user_name="MissSyncFan",
                    user_club_id="arsenal",
                    match_id="fd-ars-1",
                    predicted_home_score=0,
                    predicted_away_score=2,
                    created_at=now - datetime.timedelta(days=5),
                ),
                Prediction(
                    id="pred_sync_sched",
                    user_id="usr_sync_exact",
                    user_name="ExactSyncFan",
                    user_club_id="arsenal",
                    match_id="fd-ars-40",
                    predicted_home_score=2,
                    predicted_away_score=0,
                    created_at=now - datetime.timedelta(hours=1),
                ),
            ]
        )
        await session.commit()

    # First sync -> grades fd-ars-1 predictions automatically and emits 1 notification each
    async with session_factory() as session:
        res1 = await FootballIngestionService.run_sync(db=session, force_mock=True)
        assert res1["status"] == "SUCCESS"
        assert res1["matches_synced"] >= 40

    async with session_factory() as session:
        preds = {
            p.id: p
            for p in (await session.execute(select(Prediction))).scalars().all()
        }
        assert preds["pred_sync_exact"].points_awarded == 3
        assert preds["pred_sync_outcome"].points_awarded == 1
        assert preds["pred_sync_miss"].points_awarded == 0
        assert preds["pred_sync_sched"].points_awarded is None

        notifs_1 = (await session.execute(select(Notification))).scalars().all()
        assert len(notifs_1) == 3
        by_user = {n.user_id: n for n in notifs_1}
        assert by_user["usr_sync_exact"].type == "prediction_result"
        assert by_user["usr_sync_exact"].link == "/predictions"
        assert "3 pts" in by_user["usr_sync_exact"].message
        assert "1 pt" in by_user["usr_sync_outcome"].message
        assert "0 pts" in by_user["usr_sync_miss"].message

    # Second sync -> completely idempotent (no duplicate notifications, points unchanged)
    async with session_factory() as session:
        res2 = await FootballIngestionService.run_sync(db=session, force_mock=True)
        assert res2["status"] == "SUCCESS"

    async with session_factory() as session:
        notifs_2 = (await session.execute(select(Notification))).scalars().all()
        assert len(notifs_2) == 3
        preds_2 = {
            p.id: p
            for p in (await session.execute(select(Prediction))).scalars().all()
        }
        assert preds_2["pred_sync_exact"].points_awarded == 3
        assert preds_2["pred_sync_outcome"].points_awarded == 1
        assert preds_2["pred_sync_miss"].points_awarded == 0
        assert preds_2["pred_sync_sched"].points_awarded is None


@pytest.mark.asyncio
async def test_predictions_leaderboard_seasonal_campaign_exact_and_all_time(session_factory):
    now = datetime.datetime.now(datetime.timezone.utc)
    async with session_factory() as session:
        session.add_all(
            [
                Competition(id="PL", code="PL", name="Premier League", country="England"),
                Competition(id="CL", code="CL", name="UEFA Champions League", country="Europe"),
                Season(id="2025-2026-PL", competition_id="PL", start_year=2025, end_year=2026, is_current=False),
                Season(id="2025-2026-CL", competition_id="CL", start_year=2025, end_year=2026, is_current=False),
                Season(id="2026-2027-PL", competition_id="PL", start_year=2026, end_year=2027, is_current=True),
                Season(id="2026-2027-CL", competition_id="CL", start_year=2026, end_year=2027, is_current=True),
                # 2025-2026 PL (2-0)
                Match(
                    id="lb_2526_pl",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2025-2026-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="chelsea",
                    away_team_name="Chelsea FC",
                    utc_date=now - datetime.timedelta(days=200),
                    status="FINISHED",
                    home_score=2,
                    away_score=0,
                    winner="HOME_TEAM",
                ),
                # 2025-2026 CL (1-1)
                Match(
                    id="lb_2526_cl",
                    competition_id="CL",
                    competition_name="UEFA Champions League",
                    season_id="2025-2026-CL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="real-madrid",
                    away_team_name="Real Madrid CF",
                    utc_date=now - datetime.timedelta(days=180),
                    status="FINISHED",
                    home_score=1,
                    away_score=1,
                    winner="DRAW",
                ),
                # 2026-2027 PL (3-1)
                Match(
                    id="lb_2627_pl",
                    competition_id="PL",
                    competition_name="Premier League",
                    season_id="2026-2027-PL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="tottenham",
                    away_team_name="Tottenham Hotspur FC",
                    utc_date=now - datetime.timedelta(days=10),
                    status="FINISHED",
                    home_score=3,
                    away_score=1,
                    winner="HOME_TEAM",
                ),
                # 2026-2027 CL (2-0)
                Match(
                    id="lb_2627_cl",
                    competition_id="CL",
                    competition_name="UEFA Champions League",
                    season_id="2026-2027-CL",
                    home_team_id="arsenal",
                    home_team_name="Arsenal FC",
                    away_team_id="barcelona",
                    away_team_name="FC Barcelona",
                    utc_date=now - datetime.timedelta(days=5),
                    status="FINISHED",
                    home_score=2,
                    away_score=0,
                    winner="HOME_TEAM",
                ),
                # User A: strong in 2025-2026-PL (3 exact) + 2025-2026-CL (1 outcome) = 4; 2026-2027 miss (0)
                Prediction(
                    id="lb_p_a1",
                    user_id="usr_lb_a",
                    user_name="VeteranGooner",
                    user_club_id="arsenal",
                    match_id="lb_2526_pl",
                    predicted_home_score=2,
                    predicted_away_score=0,
                ),
                Prediction(
                    id="lb_p_a2",
                    user_id="usr_lb_a",
                    user_name="VeteranGooner",
                    user_club_id="arsenal",
                    match_id="lb_2526_cl",
                    predicted_home_score=0,
                    predicted_away_score=0,
                ),
                Prediction(
                    id="lb_p_a3",
                    user_id="usr_lb_a",
                    user_name="VeteranGooner",
                    user_club_id="arsenal",
                    match_id="lb_2627_pl",
                    predicted_home_score=0,
                    predicted_away_score=2,
                ),
                # User B: leads 2026-2027 campaign (3 exact PL + 3 exact CL = 6 pts), 0 in 2025-2026
                Prediction(
                    id="lb_p_b1",
                    user_id="usr_lb_b",
                    user_name="CurrentSeasonPro",
                    user_club_id="arsenal",
                    match_id="lb_2627_pl",
                    predicted_home_score=3,
                    predicted_away_score=1,
                ),
                Prediction(
                    id="lb_p_b2",
                    user_id="usr_lb_b",
                    user_name="CurrentSeasonPro",
                    user_club_id="arsenal",
                    match_id="lb_2627_cl",
                    predicted_home_score=2,
                    predicted_away_score=0,
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Campaign rollup "2026-2027" aggregates PL + CL
        res_2627 = await ac.get("/api/v1/predictions/leaderboard?season_id=2026-2027")
        assert res_2627.status_code == 200
        rows_2627 = res_2627.json()
        assert [r["user_name"] for r in rows_2627] == ["CurrentSeasonPro", "VeteranGooner"]
        assert rows_2627[0]["total_points"] == 6
        assert rows_2627[0]["exact_scores"] == 2
        assert rows_2627[0]["predictions_count"] == 2
        assert rows_2627[1]["total_points"] == 0
        assert rows_2627[1]["predictions_count"] == 1

        # 2. Exact season "2025-2026-PL" excludes 2025-2026-CL and 2026-2027-*
        res_2526_pl = await ac.get("/api/v1/predictions/leaderboard?season_id=2025-2026-PL")
        assert res_2526_pl.status_code == 200
        rows_2526_pl = res_2526_pl.json()
        assert len(rows_2526_pl) == 1
        assert rows_2526_pl[0]["user_name"] == "VeteranGooner"
        assert rows_2526_pl[0]["total_points"] == 3
        assert rows_2526_pl[0]["exact_scores"] == 1
        assert rows_2526_pl[0]["predictions_count"] == 1

        # 3. All-time aggregation (season_id=all and omitted match)
        res_all = await ac.get("/api/v1/predictions/leaderboard?season_id=all")
        res_default = await ac.get("/api/v1/predictions/leaderboard")
        assert res_all.status_code == 200
        assert res_default.status_code == 200
        assert res_all.json() == res_default.json()
        rows_all = res_all.json()
        assert [r["user_name"] for r in rows_all] == ["CurrentSeasonPro", "VeteranGooner"]
        assert rows_all[0]["total_points"] == 6
        assert rows_all[1]["total_points"] == 4
        assert rows_all[1]["predictions_count"] == 3

        # 4. Season with no predictions -> empty list
        res_empty = await ac.get("/api/v1/predictions/leaderboard?season_id=2019-2020-PL")
        assert res_empty.status_code == 200
        assert res_empty.json() == []


@pytest.mark.asyncio
async def test_messaging_blank_recipient_id_rejected():
    headers = auth_headers("usr_msg_guard", display_name="GuardGooner")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_blank = await ac.post(
            "/api/v1/messages/conversations",
            json={"recipient_id": "   "},
            headers=headers,
        )
        assert res_blank.status_code == 400
        assert res_blank.json()["detail"] == "Recipient ID is required"

