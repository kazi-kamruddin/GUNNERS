import datetime
from typing import Dict, List
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.football import Match, Club
from app.schemas.analytics import (
    AnalyticsQueryRequest,
    AnalyticsResponse,
    AnalyticsSeriesItem,
    MatchResponse,
    MultiSeasonTrendsResponse,
    OpponentH2HOption,
    OpponentH2HResponse,
    SeasonTrendItem,
)
from app.services.arteta_timeline import ArtetaTimelineService

class AnalyticsEngine:
    @staticmethod
    async def compute_analytics(session: AsyncSession, query: AnalyticsQueryRequest) -> AnalyticsResponse:
        results = []

        for team_id in query.team_ids:
            # Fetch club info
            club_res = await session.execute(select(Club).where(Club.id == team_id))
            club = club_res.scalar_one_or_none()
            team_name = club.name if club else team_id

            # Filter conditions for completed matches
            filters = [
                Match.status == "FINISHED",
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
            ]

            if query.competition_id:
                filters.append(Match.competition_id == query.competition_id)
            if query.season_id:
                filters.append(Match.season_id == query.season_id)

            if query.venue == "home":
                filters.append(Match.home_team_id == team_id)
            elif query.venue == "away":
                filters.append(Match.away_team_id == team_id)

            stmt = select(Match).where(and_(*filters))
            res = await session.execute(stmt)
            matches = res.scalars().all()

            matches_played = len(matches)
            wins = 0
            draws = 0
            losses = 0
            clean_sheets = 0
            goals_for = 0
            goals_against = 0

            for m in matches:
                is_home = m.home_team_id == team_id
                t_score = m.home_score if is_home else m.away_score
                opp_score = m.away_score if is_home else m.home_score

                if t_score is None or opp_score is None:
                    continue

                goals_for += t_score
                goals_against += opp_score

                if opp_score == 0:
                    clean_sheets += 1

                if t_score > opp_score:
                    wins += 1
                elif t_score < opp_score:
                    losses += 1
                else:
                    draws += 1

            goal_diff = goals_for - goals_against

            # Compute specific metric according to specification in Gunners_PROJECT_DIRECTION.md
            metric_val = 0.0
            unit = ""
            formula_desc = ""

            if query.metric == "win_rate":
                unit = "%"
                formula_desc = "(wins / matches_played) * 100"
                if matches_played > 0:
                    metric_val = round((wins / matches_played) * 100, 1)
            elif query.metric == "loss_rate":
                unit = "%"
                formula_desc = "(losses / matches_played) * 100"
                if matches_played > 0:
                    metric_val = round((losses / matches_played) * 100, 1)
            elif query.metric == "clean_sheet_rate":
                unit = "%"
                formula_desc = "(clean_sheets / matches_played) * 100"
                if matches_played > 0:
                    metric_val = round((clean_sheets / matches_played) * 100, 1)
            elif query.metric == "goals_per_match":
                unit = "goals/match"
                formula_desc = "goals_for / matches_played"
                if matches_played > 0:
                    metric_val = round(goals_for / matches_played, 2)
            elif query.metric == "points_per_game":
                unit = "ppg"
                formula_desc = "((wins * 3) + draws) / matches_played"
                if matches_played > 0:
                    points = (wins * 3) + draws
                    metric_val = round(points / matches_played, 2)
            elif query.metric == "goal_difference":
                unit = "diff"
                formula_desc = "goals_for - goals_against"
                metric_val = float(goal_diff)

            results.append(
                AnalyticsSeriesItem(
                    team_id=team_id,
                    team_name=team_name,
                    matches_played=matches_played,
                    wins=wins,
                    draws=draws,
                    losses=losses,
                    clean_sheets=clean_sheets,
                    goals_for=goals_for,
                    goals_against=goals_against,
                    goal_difference=goal_diff,
                    metric_value=metric_val,
                    unit=unit
                )
            )

        return AnalyticsResponse(
            metric=query.metric,
            formula=formula_desc,
            venue_filter=query.venue,
            series=results,
            computed_at=datetime.datetime.utcnow()
        )

    @staticmethod
    async def compute_multi_season_trends(
        session: AsyncSession,
        club_id: str = "arsenal",
        venue: str = "all",
    ) -> MultiSeasonTrendsResponse:
        club_res = await session.execute(select(Club).where(Club.id == club_id))
        club = club_res.scalar_one_or_none()
        club_name = club.name if club else club_id

        ordered_seasons = sorted(
            ArtetaTimelineService.SEASONS_METADATA,
            key=lambda s: s["start_year"],
        )

        buckets: Dict[str, dict] = {}
        for s in ordered_seasons:
            prefix = f"{s['start_year']}-{s['end_year']}"
            buckets[prefix] = {
                "meta": s,
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "clean_sheets": 0,
                "goals_for": 0,
                "goals_against": 0,
            }

        filters = [Match.status == "FINISHED"]
        if venue == "home":
            filters.append(Match.home_team_id == club_id)
        elif venue == "away":
            filters.append(Match.away_team_id == club_id)
        else:
            filters.append(or_(Match.home_team_id == club_id, Match.away_team_id == club_id))

        stmt = select(Match).where(and_(*filters))
        matches = (await session.execute(stmt)).scalars().all()

        for m in matches:
            if m.home_score is None or m.away_score is None:
                continue

            parts = (m.season_id or "").split("-")
            if len(parts) < 2:
                continue
            prefix = f"{parts[0]}-{parts[1]}"
            bucket = buckets.get(prefix)
            if bucket is None:
                continue

            is_home = m.home_team_id == club_id
            t_score = m.home_score if is_home else m.away_score
            opp_score = m.away_score if is_home else m.home_score

            bucket["matches_played"] += 1
            bucket["goals_for"] += t_score
            bucket["goals_against"] += opp_score

            if opp_score == 0:
                bucket["clean_sheets"] += 1

            if t_score > opp_score:
                bucket["wins"] += 1
            elif t_score < opp_score:
                bucket["losses"] += 1
            else:
                bucket["draws"] += 1

        trends: List[SeasonTrendItem] = []
        for s in ordered_seasons:
            prefix = f"{s['start_year']}-{s['end_year']}"
            b = buckets[prefix]
            mp = b["matches_played"]
            wins = b["wins"]
            draws = b["draws"]
            losses = b["losses"]
            clean_sheets = b["clean_sheets"]
            gf = b["goals_for"]
            ga = b["goals_against"]
            gd = gf - ga

            win_rate = round((wins / mp) * 100, 1) if mp > 0 else 0.0
            loss_rate = round((losses / mp) * 100, 1) if mp > 0 else 0.0
            clean_sheet_rate = round((clean_sheets / mp) * 100, 1) if mp > 0 else 0.0
            goals_per_match = round(gf / mp, 2) if mp > 0 else 0.0
            points_per_game = round(((wins * 3) + draws) / mp, 2) if mp > 0 else 0.0

            trends.append(
                SeasonTrendItem(
                    season_id=s["id"],
                    label=s["label"],
                    start_year=s["start_year"],
                    end_year=s["end_year"],
                    matches_played=mp,
                    wins=wins,
                    draws=draws,
                    losses=losses,
                    clean_sheets=clean_sheets,
                    goals_for=gf,
                    goals_against=ga,
                    goal_difference=gd,
                    win_rate=win_rate,
                    points_per_game=points_per_game,
                    goals_per_match=goals_per_match,
                    clean_sheet_rate=clean_sheet_rate,
                    loss_rate=loss_rate,
                    arteta_milestone=s["arteta_milestone"],
                )
            )

        return MultiSeasonTrendsResponse(
            club_id=club_id,
            club_name=club_name,
            venue_filter=venue,
            trends=trends,
            computed_at=datetime.datetime.now(datetime.timezone.utc),
        )

    @staticmethod
    async def compute_opponent_h2h(
        session: AsyncSession,
        club_id: str = "arsenal",
        opponent_id: str = "chelsea",
        venue: str = "all",
    ) -> OpponentH2HResponse:
        stmt = (
            select(Match)
            .where(
                and_(
                    Match.status == "FINISHED",
                    or_(Match.home_team_id == club_id, Match.away_team_id == club_id),
                )
            )
            .order_by(Match.utc_date.desc())
        )
        all_matches = (await session.execute(stmt)).scalars().all()

        team_ids = {club_id, opponent_id}
        for m in all_matches:
            team_ids.add(m.home_team_id)
            team_ids.add(m.away_team_id)

        club_map: Dict[str, str] = {}
        if team_ids:
            clubs_res = await session.execute(select(Club).where(Club.id.in_(team_ids)))
            club_map = {c.id: c.name for c in clubs_res.scalars().all()}

        opponent_counts: Dict[str, dict] = {}
        h2h_matches: List[Match] = []

        for m in all_matches:
            if m.home_score is None or m.away_score is None:
                continue

            is_home = m.home_team_id == club_id
            opp_id = m.away_team_id if is_home else m.home_team_id
            if opp_id == club_id:
                continue

            raw_opp_name = m.away_team_name if is_home else m.home_team_name
            resolved_name = club_map.get(opp_id) or (
                raw_opp_name
                if raw_opp_name and raw_opp_name not in ("Home Team", "Away Team")
                else opp_id
            )

            if opp_id not in opponent_counts:
                opponent_counts[opp_id] = {"name": resolved_name, "count": 0}
            opponent_counts[opp_id]["count"] += 1

            if opp_id != opponent_id:
                continue
            if venue == "home" and not is_home:
                continue
            if venue == "away" and is_home:
                continue

            h2h_matches.append(m)

        matches_played = len(h2h_matches)
        wins = 0
        draws = 0
        losses = 0
        clean_sheets = 0
        goals_for = 0
        goals_against = 0
        recent_matches: List[MatchResponse] = []

        for m in h2h_matches:
            is_home = m.home_team_id == club_id
            t_score = m.home_score if is_home else m.away_score
            opp_score = m.away_score if is_home else m.home_score

            goals_for += t_score
            goals_against += opp_score
            if opp_score == 0:
                clean_sheets += 1
            if t_score > opp_score:
                wins += 1
            elif t_score < opp_score:
                losses += 1
            else:
                draws += 1

            resp = MatchResponse.model_validate(m)
            if (not resp.home_team_name or resp.home_team_name == "Home Team") and m.home_team_id in club_map:
                resp.home_team_name = club_map[m.home_team_id]
            if (not resp.away_team_name or resp.away_team_name == "Away Team") and m.away_team_id in club_map:
                resp.away_team_name = club_map[m.away_team_id]
            recent_matches.append(resp)

        goal_difference = goals_for - goals_against
        win_rate = round((wins / matches_played) * 100, 1) if matches_played > 0 else 0.0

        available_opponents = [
            OpponentH2HOption(
                opponent_id=opp_id,
                opponent_name=info["name"],
                matches_played=info["count"],
            )
            for opp_id, info in sorted(
                opponent_counts.items(),
                key=lambda item: (-item[1]["count"], item[1]["name"].lower()),
            )
        ]

        resolved_opponent_name = (
            club_map.get(opponent_id)
            or opponent_counts.get(opponent_id, {}).get("name")
            or opponent_id
        )

        return OpponentH2HResponse(
            club_id=club_id,
            opponent_id=opponent_id,
            opponent_name=resolved_opponent_name,
            venue_filter=venue,
            matches_played=matches_played,
            wins=wins,
            draws=draws,
            losses=losses,
            clean_sheets=clean_sheets,
            goals_for=goals_for,
            goals_against=goals_against,
            goal_difference=goal_difference,
            win_rate=win_rate,
            recent_matches=recent_matches,
            available_opponents=available_opponents,
            computed_at=datetime.datetime.now(datetime.timezone.utc),
        )
