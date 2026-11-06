import asyncio
import datetime
import json
import sys
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal, engine, Base
from app.services.ingestion import FootballIngestionService
from app.services.arteta_timeline import ArtetaTimelineService
from app.models.squad import Player
from app.models.tactics import TacticalBoard
from app.models.insight import Insight
from app.models.terrace import Post, PostComment, PostReaction
from app.models.predictions import Prediction
from app.models.notifications import Notification
from app.models.messaging import Conversation, ConversationMember, DirectMessage
from app.models.football import Match
from app.api.v1.endpoints.squad import DEFAULT_PLAYERS
from app.api.v1.endpoints.tactics import DEMO_BOARDS, PRESETS
from app.api.v1.endpoints.insights import DEFAULT_INSIGHTS

async def seed_all():
    print("==================================================")
    print("      GUNNERS Community Realistic Data Seeder     ")
    print("==================================================")

    # 1. Ensure all tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE posts ADD COLUMN image_url VARCHAR(500)"))
        except Exception:
            pass

    async with AsyncSessionLocal() as session:
        # 2. Foundation Competitions, Seasons, Clubs & Matches
        print("[1/8] Ingesting foundation clubs and baseline matches...")
        await FootballIngestionService.run_sync(session, force_mock=True)
        print("[1b/8] Ingesting complete Mikel Arteta Era timeline (2019 - Present)...")
        await ArtetaTimelineService.seed_arteta_timeline(session)

        # 3. Squad Players for 4 Foundation Clubs
        print("[2/8] Seeding squad players...")
        for p_data in DEFAULT_PLAYERS:
            existing = await session.get(Player, p_data["id"])
            if not existing:
                player = Player(
                    id=p_data["id"],
                    club_id=p_data["club_id"],
                    name=p_data["name"],
                    short_name=p_data["short_name"],
                    position=p_data["position"],
                    jersey_number=p_data["jersey_number"],
                    nationality=p_data["nationality"],
                    appearances=p_data.get("appearances", 0),
                    goals=p_data.get("goals", 0),
                    assists=p_data.get("assists", 0),
                    clean_sheets=p_data.get("clean_sheets", 0),
                    minutes_played=p_data.get("minutes_played", 0),
                    yellow_cards=p_data.get("yellow_cards", 0),
                    red_cards=p_data.get("red_cards", 0),
                    photo_url=p_data.get("photo_url")
                )
                session.add(player)
        await session.commit()

        # 4. Tactical Boards across all 4 clubs
        print("[3/8] Seeding tactical blueprints...")
        for b_data in DEMO_BOARDS:
            existing = await session.get(TacticalBoard, b_data.id)
            if not existing:
                lineup_dict = [p.model_dump() for p in b_data.lineup]
                annotations_dict = [a.model_dump() for a in b_data.annotations] if b_data.annotations else []
                tb = TacticalBoard(
                    id=b_data.id,
                    user_id=f"usr_seed_{b_data.author_name.lower()}",
                    author_name=b_data.author_name,
                    author_club_id=b_data.author_club_id,
                    title=b_data.title,
                    formation=b_data.formation,
                    lineup=lineup_dict,
                    annotations=annotations_dict,
                    tactical_notes=b_data.tactical_notes,
                    is_public=b_data.is_public,
                    created_at=b_data.created_at,
                    updated_at=b_data.updated_at
                )
                session.add(tb)
        await session.commit()

        # 5. Data Lab Insights
        print("[4/8] Seeding Data Lab reproducible insights...")
        for ins_data in DEFAULT_INSIGHTS:
            existing = await session.get(Insight, ins_data.id)
            if not existing:
                snap_str = ins_data.snapshot.model_dump_json() if hasattr(ins_data.snapshot, "model_dump_json") else json.dumps(ins_data.snapshot)
                ins = Insight(
                    id=ins_data.id,
                    user_id=ins_data.user_id,
                    author_name=ins_data.author_name,
                    author_club_id=ins_data.author_club_id,
                    title=ins_data.title,
                    description=ins_data.description,
                    metric=ins_data.metric,
                    team_ids=",".join(ins_data.team_ids),
                    venue=ins_data.venue,
                    competition_id=ins_data.competition_id,
                    chart_type=ins_data.chart_type,
                    snapshot=snap_str,
                    is_public=ins_data.is_public,
                    created_at=ins_data.created_at
                )
                session.add(ins)
        await session.commit()

        # 6. Terrace Debates (Posts, Comments, Reactions)
        print("[5/8] Seeding The Terrace debates and interactions...")
        posts_data = [
            {
                "id": "post_seed_1",
                "author_id": "usr_seed_alex",
                "author_name": "GoonerAlex",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
                "content": "Our defensive compactness and high press structure at the Emirates have been elite this season. Backed up with reproducible Data Lab numbers: 83.3% home win rate! Check the attached tactical blueprint for how we isolate Saka on the right wing. #NorthLondonDerby #Tactics",
                "image_url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=800&q=80",
                "insight_id": "ins_arsenal_winrate",
                "tactical_board_id": "tb_arsenal_highpress",
                "created_at": datetime.datetime.utcnow() - datetime.timedelta(hours=2),
                "comments": [
                    {
                        "id": "cmt_seed_1_1",
                        "author_id": "usr_seed_clock",
                        "author_name": "ClockEndTactician",
                        "author_club_id": "arsenal",
                        "content": "Emirates record is impenetrable right now. When teams try to sit in a low block, having Timber invert creates the 3-2 rest defense that suffocates counters."
                    },
                    {
                        "id": "cmt_seed_1_2",
                        "author_id": "usr_seed_alex",
                        "author_name": "GoonerAlex",
                        "author_club_id": "arsenal",
                        "content": "Exactly! And Merino arriving late gives us that extra physical presence in the box when crosses come from Saka and White."
                    }
                ],
                "reactions": ["usr_seed_clock", "usr_seed_nb", "usr_seed_ash", "usr_fan_1", "usr_fan_2"]
            },
            {
                "id": "post_seed_2",
                "author_id": "usr_seed_clock",
                "author_name": "ClockEndTactician",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
                "content": "Declan Rice's ground duel winning rate (68.4%) and ball retention make him indispensable in European ties. Look at the central stability he brings next to Partey in our double pivot. #DataLab #Arsenal #COYG",
                "image_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=800&q=80",
                "insight_id": "ins_arsenal_clean_sheet",
                "tactical_board_id": "tb_arsenal_lowblock_breaker",
                "created_at": datetime.datetime.utcnow() - datetime.timedelta(hours=4),
                "comments": [
                    {
                        "id": "cmt_seed_2_1",
                        "author_id": "usr_seed_nb",
                        "author_name": "NorthBankFan",
                        "author_club_id": "arsenal",
                        "content": "Declan's engine allows Ødegaard to roam freely without worrying about getting caught in transition. Pure world-class midfielder."
                    }
                ],
                "reactions": ["usr_seed_alex", "usr_seed_nb", "usr_seed_ash", "usr_fan_3", "usr_fan_4"]
            },
            {
                "id": "post_seed_3",
                "author_id": "usr_seed_nb",
                "author_name": "NorthBankFan",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
                "content": "The atmosphere under the floodlights this week was electric. Big three points secured! Check the Data Lab numbers on our 2.18 goals per match and corner conversion. Proud to be a Gooner. #Arsenal #PremierLeague #Gunners",
                "image_url": "https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=800&q=80",
                "insight_id": "ins_arsenal_goals_per_game",
                "tactical_board_id": "tb_arsenal_derby_lockdown",
                "created_at": datetime.datetime.utcnow() - datetime.timedelta(hours=6),
                "comments": [
                    {
                        "id": "cmt_seed_3_1",
                        "author_id": "usr_seed_alex",
                        "author_name": "GoonerAlex",
                        "author_club_id": "arsenal",
                        "content": "Nicolas Jover's set-piece routines are literally winning us matches. Saliba and Gabriel are unplayable in both boxes."
                    }
                ],
                "reactions": ["usr_seed_alex", "usr_seed_clock", "usr_fan_5", "usr_fan_6"]
            },
            {
                "id": "post_seed_4",
                "author_id": "usr_seed_ash",
                "author_name": "AshburtonAnalyst",
                "author_club_id": "arsenal",
                "club_id": "arsenal",
                "content": "Statistical deep dive: Arsenal's campaign consistency stands at 2.36 PPG. When Saliba and Gabriel start together, our expected goals against drops to an extraordinary 0.65 per 90. #Emirates #TitleRace #COYG",
                "insight_id": "ins_arsenal_ppg",
                "created_at": datetime.datetime.utcnow() - datetime.timedelta(hours=8),
                "comments": [
                    {
                        "id": "cmt_seed_4_1",
                        "author_id": "usr_seed_clock",
                        "author_name": "ClockEndTactician",
                        "author_club_id": "arsenal",
                        "content": "Best center-back partnership since Tony Adams and Martin Keown. Absolute rocks."
                    }
                ],
                "reactions": ["usr_seed_alex", "usr_seed_clock", "usr_seed_nb", "usr_fan_7"]
            }
        ]

        for p_info in posts_data:
            existing_post = await session.get(Post, p_info["id"])
            if not existing_post:
                new_p = Post(
                    id=p_info["id"],
                    author_id=p_info["author_id"],
                    author_name=p_info["author_name"],
                    author_club_id=p_info["author_club_id"],
                    club_id=p_info["club_id"],
                    content=p_info["content"],
                    image_url=p_info.get("image_url"),
                    insight_id=p_info.get("insight_id"),
                    tactical_board_id=p_info.get("tactical_board_id"),
                    created_at=p_info["created_at"]
                )
                session.add(new_p)
                await session.flush()

                # Add comments
                for c in p_info.get("comments", []):
                    cmt = PostComment(
                        id=c["id"],
                        post_id=new_p.id,
                        author_id=c["author_id"],
                        author_name=c["author_name"],
                        author_club_id=c["author_club_id"],
                        content=c["content"],
                        created_at=new_p.created_at + datetime.timedelta(minutes=15)
                    )
                    session.add(cmt)

                # Add reactions
                for rxn_user in p_info.get("reactions", []):
                    rxn = PostReaction(
                        id=f"rxn_{new_p.id}_{rxn_user}",
                        post_id=new_p.id,
                        user_id=rxn_user,
                        reaction_type="cheer",
                        created_at=new_p.created_at + datetime.timedelta(minutes=5)
                    )
                    session.add(rxn)

        await session.commit()

        # 7. Predictor Matchday & Leaderboard Records
        print("[6/8] Seeding match predictions and leaderboard standings...")
        matches_res = await session.execute(select(Match).limit(5))
        seeded_matches = matches_res.scalars().all()

        predictions_data = [
            ("usr_seed_alex", "GoonerAlex", "arsenal", 28, 6),
            ("usr_seed_clock", "ClockEndTactician", "arsenal", 25, 5),
            ("usr_seed_nb", "NorthBankFan", "arsenal", 22, 4),
            ("usr_seed_ash", "AshburtonAnalyst", "arsenal", 19, 3),
        ]

        if seeded_matches:
            for user_id, user_name, club_id, total_pts, exact_cnt in predictions_data:
                for idx, match in enumerate(seeded_matches):
                    pred_id = f"pred_{user_id}_{match.id}"
                    existing_pred = await session.get(Prediction, pred_id)
                    if not existing_pred:
                        pts = 3 if idx < exact_cnt else 1
                        pred = Prediction(
                            id=pred_id,
                            user_id=user_id,
                            user_name=user_name,
                            user_club_id=club_id,
                            match_id=match.id,
                            predicted_home_score=match.home_score if match.home_score is not None else 2,
                            predicted_away_score=match.away_score if match.away_score is not None else 1,
                            points_awarded=pts,
                            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=idx + 1)
                        )
                        session.add(pred)
            await session.commit()

        # 8. Direct Debates in The Dressing Room
        print("[7/8] Seeding direct messaging conversations...")
        conv_id = "conv_seed_alex_clock"
        existing_conv = await session.get(Conversation, conv_id)
        if not existing_conv:
            conv = Conversation(
                id=conv_id,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
            )
            session.add(conv)
            await session.flush()

            # Members
            session.add(ConversationMember(conversation_id=conv_id, user_id="usr_seed_alex"))
            session.add(ConversationMember(conversation_id=conv_id, user_id="usr_seed_clock"))

            # Messages
            session.add(DirectMessage(
                id="msg_seed_1",
                conversation_id=conv_id,
                sender_id="usr_seed_alex",
                sender_name="GoonerAlex",
                sender_club_id="arsenal",
                content="Hey ClockEnd, saw your tactical board on the 3-2-4-1 low-block breaker. Do you think Timber tucking in gives Rice enough cover against counter-attacks?",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3)
            ))
            session.add(DirectMessage(
                id="msg_seed_2",
                conversation_id=conv_id,
                sender_id="usr_seed_clock",
                sender_name="ClockEndTactician",
                sender_club_id="arsenal",
                content="100%. Timber's agility lets him step out to press instantly or drop back beside Saliba and Gabriel. It's the exact structure Man City used with Stones, but Timber is quicker.",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
            ))
            await session.commit()

        # 9. In-App Notifications
        print("[8/8] Seeding sample notifications...")
        sample_notifications = [
            {
                "id": "notif_seed_1",
                "user_id": "usr_seed_alex",
                "type": "cheer",
                "title": "New Cheer",
                "message": "ClockEndTactician cheered your debrief on Emirates high press structure.",
                "link": "/terrace"
            },
            {
                "id": "notif_seed_2",
                "user_id": "usr_seed_alex",
                "type": "comment",
                "title": "New Reply",
                "message": "NorthBankFan replied to your discussion on #NorthLondonDerby.",
                "link": "/terrace"
            },
            {
                "id": "notif_seed_3",
                "user_id": "usr_seed_alex",
                "type": "prediction_result",
                "title": "Prediction Scored (+3 Pts)",
                "message": "Exact match scoreline predicted for Arsenal vs Chelsea!",
                "link": "/predictions"
            }
        ]
        for n_data in sample_notifications:
            existing_notif = await session.get(Notification, n_data["id"])
            if not existing_notif:
                notif = Notification(
                    id=n_data["id"],
                    user_id=n_data["user_id"],
                    type=n_data["type"],
                    title=n_data["title"],
                    message=n_data["message"],
                    link=n_data["link"],
                    is_read=False,
                    created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
                )
                session.add(notif)
        await session.commit()

        print("==================================================")
        print("  Community seeding completed successfully!       ")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(seed_all())
