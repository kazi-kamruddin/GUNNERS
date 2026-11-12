from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.football import Match
from app.models.predictions import Prediction
from app.services.notifications import create_notification


def _outcome_sign(home: int, away: int) -> int:
    if home > away:
        return 1
    if home < away:
        return -1
    return 0


async def grade_match_predictions(db: AsyncSession, match: Match) -> int:
    """Grade all ungraded predictions for a finished match and emit notifications."""
    if match.status != "FINISHED" or match.home_score is None or match.away_score is None:
        return 0

    stmt = select(Prediction).where(
        and_(
            Prediction.match_id == match.id,
            Prediction.points_awarded.is_(None),
        )
    )
    predictions = (await db.execute(stmt)).scalars().all()
    if not predictions:
        return 0

    home_label = (
        match.home_team_name
        if match.home_team_name and match.home_team_name != "Home Team"
        else match.home_team_id
    )
    away_label = (
        match.away_team_name
        if match.away_team_name and match.away_team_name != "Away Team"
        else match.away_team_id
    )

    for pred in predictions:
        if (
            pred.predicted_home_score == match.home_score
            and pred.predicted_away_score == match.away_score
        ):
            pts = 3
        elif _outcome_sign(pred.predicted_home_score, pred.predicted_away_score) == _outcome_sign(
            match.home_score, match.away_score
        ):
            pts = 1
        else:
            pts = 0

        pred.points_awarded = pts
        pt_word = "pt" if pts == 1 else "pts"
        await create_notification(
            db,
            user_id=pred.user_id,
            notif_type="prediction_result",
            title="Prediction Graded",
            message=(
                f"{home_label} {match.home_score}-{match.away_score} {away_label}: "
                f"you earned {pts} {pt_word} "
                f"(predicted {pred.predicted_home_score}-{pred.predicted_away_score})."
            ),
            link="/predictions",
        )

    return len(predictions)
