import datetime
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.football import Match, Club
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsResponse, AnalyticsSeriesItem

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
