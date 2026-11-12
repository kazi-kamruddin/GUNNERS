import datetime
import asyncio
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.football import Club, Competition, Season, Match, SyncRun
from app.providers.football_data import FootballDataProvider
from app.services.predictor_grading import grade_match_predictions


class FootballIngestionService:
    """
    Orchestrates extraction, transformation, normalization, and idempotent
    database loading of Arsenal FC matches, fixtures, and results.
    """

    @classmethod
    async def ensure_foundation_entities(cls, db: AsyncSession):
        """Ensure core competitions, seasons, Arsenal FC foundation club, and comparison opponent clubs exist."""
        # 1. Competitions
        comps = [
            Competition(id="PL", code="PL", name="Premier League", country="England", emblem_url="https://crests.football-data.org/PL.png"),
            Competition(id="PD", code="PD", name="La Liga", country="Spain", emblem_url="https://crests.football-data.org/PD.png"),
            Competition(id="SA", code="SA", name="Serie A", country="Italy", emblem_url="https://crests.football-data.org/SA.png"),
            Competition(id="CL", code="CL", name="UEFA Champions League", country="Europe", emblem_url="https://crests.football-data.org/CL.png"),
        ]
        for comp in comps:
            existing = await db.get(Competition, comp.id)
            if not existing:
                db.add(comp)

        # 2. Seasons
        seasons = [
            Season(id="2024-2025-PL", competition_id="PL", start_year=2024, end_year=2025, is_current=False),
            Season(id="2024-2025-PD", competition_id="PD", start_year=2024, end_year=2025, is_current=False),
            Season(id="2024-2025-SA", competition_id="SA", start_year=2024, end_year=2025, is_current=False),
            Season(id="2024-2025-CL", competition_id="CL", start_year=2024, end_year=2025, is_current=False),
            Season(id="2025-2026-PL", competition_id="PL", start_year=2025, end_year=2026, is_current=False),
            Season(id="2025-2026-CL", competition_id="CL", start_year=2025, end_year=2026, is_current=False),
            Season(id="2026-2027-PL", competition_id="PL", start_year=2026, end_year=2027, is_current=True),
            Season(id="2026-2027-CL", competition_id="CL", start_year=2026, end_year=2027, is_current=True),
        ]
        for season in seasons:
            existing = await db.get(Season, season.id)
            if not existing:
                db.add(season)

        # 3. Arsenal FC (sole foundation club) + Data Lab comparison opponents
        clubs = [
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
                crest_url="https://crests.football-data.org/57.png",
                is_foundation=True,
                is_active=True,
            ),
            Club(
                id="real-madrid",
                slug="real-madrid",
                name="Real Madrid CF",
                short_name="Real Madrid",
                primary_color="#00529F",
                secondary_color="#FFFFFF",
                accent_color="#EEB028",
                league="La Liga",
                country="Spain",
                crest_url="https://crests.football-data.org/86.png",
                is_foundation=False,
                is_active=True,
            ),
            Club(
                id="barcelona",
                slug="barcelona",
                name="FC Barcelona",
                short_name="Barcelona",
                primary_color="#A50044",
                secondary_color="#004D98",
                accent_color="#EDBB00",
                league="La Liga",
                country="Spain",
                crest_url="https://crests.football-data.org/81.png",
                is_foundation=False,
                is_active=True,
            ),
            Club(
                id="milan",
                slug="milan",
                name="AC Milan",
                short_name="AC Milan",
                primary_color="#FB090B",
                secondary_color="#000000",
                accent_color="#C0C0C0",
                league="Serie A",
                country="Italy",
                crest_url="https://crests.football-data.org/98.png",
                is_foundation=False,
                is_active=True,
            ),
        ]
        for club in clubs:
            existing = await db.get(Club, club.id)
            if not existing:
                db.add(club)
            else:
                existing.crest_url = club.crest_url
                existing.is_foundation = club.is_foundation
                existing.is_active = club.is_active

        await db.commit()

    @classmethod
    async def run_sync(
        cls,
        db: AsyncSession,
        api_key: Optional[str] = None,
        force_mock: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Arsenal FC football data ingestion run.
        Returns metrics summary.
        """
        started_at = datetime.datetime.now(datetime.timezone.utc)
        provider = FootballDataProvider(api_key=api_key)

        # Ensure foundation competitions, seasons, and clubs exist
        await cls.ensure_foundation_entities(db)

        normalized_matches: List[Dict[str, Any]] = []
        source_name = "football-data.org"

        if provider.api_key and not force_mock:
            print("[FootballIngestionService] Querying football-data.org live API for Arsenal FC (57)...")
            team_ids = [57]
            current_season_year = started_at.year if started_at.month >= 7 else started_at.year - 1
            for tid in team_ids:
                raw_matches = await provider.fetch_team_matches(tid, season=current_season_year)
                for raw in raw_matches:
                    normalized_matches.append(provider.normalize_match(raw))
                await asyncio.sleep(0.5)

        # Fallback if no API key or API call yielded no matches
        if not normalized_matches:
            print("[FootballIngestionService] Using curated Arsenal FC baseline match dataset...")
            normalized_matches = provider.get_fallback_matches()
            source_name = "football-data.org (curated baseline)"

        # Idempotent upsert of all matches
        synced_count = 0
        finished_matches: Dict[str, Match] = {}
        now = datetime.datetime.now(datetime.timezone.utc)

        for m_data in normalized_matches:
            m_id = m_data["id"]
            existing = await db.get(Match, m_id)

            if existing:
                existing.season_id = m_data.get("season_id", existing.season_id)
                existing.status = m_data["status"]
                existing.home_score = m_data["home_score"]
                existing.away_score = m_data["away_score"]
                existing.winner = m_data["winner"]
                existing.utc_date = m_data["utc_date"]
                existing.matchday = m_data.get("matchday")
                existing.venue = m_data.get("venue")
                existing.home_team_name = m_data.get("home_team_name", existing.home_team_name)
                existing.home_team_crest = m_data.get("home_team_crest", existing.home_team_crest)
                existing.away_team_name = m_data.get("away_team_name", existing.away_team_name)
                existing.away_team_crest = m_data.get("away_team_crest", existing.away_team_crest)
                if m_data.get("goalscorers") is not None:
                    existing.goalscorers = m_data.get("goalscorers", [])
                if m_data.get("lineups") is not None:
                    existing.lineups = m_data.get("lineups", {})
                if m_data.get("highlights") is not None:
                    existing.highlights = m_data.get("highlights", [])
                existing.last_updated_at = now
                match_obj = existing
            else:
                new_match = Match(
                    id=m_id,
                    competition_id=m_data.get("competition_id", "PL"),
                    competition_name=m_data.get("competition_name"),
                    season_id=m_data.get("season_id", "2026-2027-PL"),
                    home_team_id=m_data["home_team_id"],
                    home_team_name=m_data.get("home_team_name", "Home Team"),
                    home_team_crest=m_data.get("home_team_crest"),
                    away_team_id=m_data["away_team_id"],
                    away_team_name=m_data.get("away_team_name", "Away Team"),
                    away_team_crest=m_data.get("away_team_crest"),
                    matchday=m_data.get("matchday"),
                    utc_date=m_data["utc_date"],
                    status=m_data["status"],
                    venue=m_data.get("venue"),
                    home_score=m_data.get("home_score"),
                    away_score=m_data.get("away_score"),
                    winner=m_data.get("winner"),
                    goalscorers=m_data.get("goalscorers") or [],
                    lineups=m_data.get("lineups") or {},
                    highlights=m_data.get("highlights") or [],
                    source=source_name,
                    last_updated_at=now,
                )
                db.add(new_match)
                match_obj = new_match

            if (
                match_obj.status == "FINISHED"
                and match_obj.home_score is not None
                and match_obj.away_score is not None
            ):
                finished_matches[match_obj.id] = match_obj
            synced_count += 1

        # Record SyncRun
        completed_at = datetime.datetime.now(datetime.timezone.utc)
        sync_record = SyncRun(
            source=source_name,
            status="SUCCESS",
            matches_synced=synced_count,
            started_at=started_at,
            completed_at=completed_at,
        )
        db.add(sync_record)
        await db.flush()

        for finished_match in finished_matches.values():
            await grade_match_predictions(db, finished_match)

        await db.commit()

        duration = (completed_at - started_at).total_seconds()
        print(f"[FootballIngestionService] Sync finished: {synced_count} Arsenal matches upserted in {duration:.2f}s ({source_name})")

        return {
            "status": "SUCCESS",
            "matches_synced": synced_count,
            "duration_seconds": duration,
            "source": source_name,
            "completed_at": completed_at.isoformat(),
        }
