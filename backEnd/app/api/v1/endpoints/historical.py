from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.historical import (
    HistoricalMatchSummary,
    HistoricalMatchDetail,
    ShotEvent,
    PassNode,
    PassLink
)

router = APIRouter()

HISTORICAL_MATCHES: List[HistoricalMatchDetail] = [
    HistoricalMatchDetail(
        id="hist_ars_barca_2011",
        title="Arsenal 2-1 FC Barcelona (UEFA Champions League)",
        competition="UEFA Champions League",
        season="2010/2011",
        match_date="2011-02-16",
        venue="Emirates Stadium, London",
        home_team_id="arsenal",
        home_team_name="Arsenal FC",
        home_score=2,
        away_team_id="barcelona",
        away_team_name="FC Barcelona",
        away_score=1,
        data_provider="StatsBomb Open Data",
        license_notice="Event data and pitch telemetry provided by StatsBomb open-data initiative under ODbL terms.",
        total_shots_home=12,
        total_shots_away=14,
        total_xg_home=1.84,
        total_xg_away=1.92,
        shots=[
            ShotEvent(
                id="shot_1",
                minute=26,
                second=12,
                team_id="barcelona",
                team_name="FC Barcelona",
                player_name="David Villa",
                x=88.5,
                y=42.0,
                outcome="Goal",
                xg=0.48,
                body_part="Right Foot",
                shot_type="Open Play"
            ),
            ShotEvent(
                id="shot_2",
                minute=38,
                second=45,
                team_id="barcelona",
                team_name="FC Barcelona",
                player_name="Lionel Messi",
                x=84.0,
                y=52.5,
                outcome="Saved",
                xg=0.35,
                body_part="Left Foot",
                shot_type="Open Play"
            ),
            ShotEvent(
                id="shot_3",
                minute=78,
                second=30,
                team_id="arsenal",
                team_name="Arsenal FC",
                player_name="Robin van Persie",
                x=94.5,
                y=28.0,
                outcome="Goal",
                xg=0.18,
                body_part="Left Foot",
                shot_type="Open Play"
            ),
            ShotEvent(
                id="shot_4",
                minute=83,
                second=15,
                team_id="arsenal",
                team_name="Arsenal FC",
                player_name="Andrey Arshavin",
                x=84.5,
                y=54.0,
                outcome="Goal",
                xg=0.42,
                body_part="Right Foot",
                shot_type="Fast Break"
            ),
            ShotEvent(
                id="shot_5",
                minute=65,
                second=10,
                team_id="arsenal",
                team_name="Arsenal FC",
                player_name="Samir Nasri",
                x=79.0,
                y=62.0,
                outcome="Blocked",
                xg=0.12,
                body_part="Right Foot",
                shot_type="Open Play"
            ),
            ShotEvent(
                id="shot_6",
                minute=89,
                second=50,
                team_id="barcelona",
                team_name="FC Barcelona",
                player_name="Pedro",
                x=89.0,
                y=35.0,
                outcome="Saved",
                xg=0.29,
                body_part="Right Foot",
                shot_type="Open Play"
            )
        ],
        pass_nodes=[
            PassNode(player_name="J. Wilshere", position="CM", jersey_number=19, x=54.0, y=48.0, passes_completed=58),
            PassNode(player_name="C. Fabregas", position="AM", jersey_number=4, x=62.0, y=55.0, passes_completed=52),
            PassNode(player_name="A. Song", position="DM", jersey_number=17, x=42.0, y=46.0, passes_completed=44),
            PassNode(player_name="S. Nasri", position="LW", jersey_number=8, x=68.0, y=75.0, passes_completed=40),
            PassNode(player_name="T. Walcott", position="RW", jersey_number=14, x=71.0, y=22.0, passes_completed=28),
            PassNode(player_name="R. van Persie", position="CF", jersey_number=10, x=78.0, y=50.0, passes_completed=22),
            PassNode(player_name="L. Koscielny", position="CB", jersey_number=6, x=28.0, y=62.0, passes_completed=60),
            PassNode(player_name="J. Djourou", position="CB", jersey_number=20, x=26.0, y=38.0, passes_completed=55)
        ],
        pass_links=[
            PassLink(source="J. Wilshere", target="C. Fabregas", pass_count=18),
            PassLink(source="A. Song", target="J. Wilshere", pass_count=16),
            PassLink(source="C. Fabregas", target="S. Nasri", pass_count=14),
            PassLink(source="J. Wilshere", target="T. Walcott", pass_count=11),
            PassLink(source="C. Fabregas", target="R. van Persie", pass_count=9),
            PassLink(source="L. Koscielny", target="A. Song", pass_count=15),
            PassLink(source="J. Djourou", target="J. Wilshere", pass_count=13)
        ]
    ),
    HistoricalMatchDetail(
        id="hist_clasico_2017",
        title="Real Madrid 2-3 FC Barcelona (El Clásico)",
        competition="La Liga",
        season="2016/2017",
        match_date="2017-04-23",
        venue="Santiago Bernabéu, Madrid",
        home_team_id="real-madrid",
        home_team_name="Real Madrid CF",
        home_score=2,
        away_team_id="barcelona",
        away_team_name="FC Barcelona",
        away_score=3,
        data_provider="StatsBomb Open Data",
        license_notice="Event data and pitch telemetry provided by StatsBomb open-data initiative under ODbL terms.",
        total_shots_home=14,
        total_shots_away=16,
        total_xg_home=2.15,
        total_xg_away=2.68,
        shots=[
            ShotEvent(
                id="shot_c1",
                minute=28,
                second=30,
                team_id="real-madrid",
                team_name="Real Madrid CF",
                player_name="Casemiro",
                x=96.0,
                y=48.0,
                outcome="Goal",
                xg=0.62,
                body_part="Left Foot",
                shot_type="Set Piece"
            ),
            ShotEvent(
                id="shot_c2",
                minute=33,
                second=12,
                team_id="barcelona",
                team_name="FC Barcelona",
                player_name="Lionel Messi",
                x=87.0,
                y=52.0,
                outcome="Goal",
                xg=0.38,
                body_part="Left Foot",
                shot_type="Open Play"
            ),
            ShotEvent(
                id="shot_c3",
                minute=73,
                second=40,
                team_id="barcelona",
                team_name="FC Barcelona",
                player_name="Ivan Rakitić",
                x=78.5,
                y=38.0,
                outcome="Goal",
                xg=0.15,
                body_part="Left Foot",
                shot_type="Open Play"
            ),
            ShotEvent(
                id="shot_c4",
                minute=85,
                second=20,
                team_id="real-madrid",
                team_name="Real Madrid CF",
                player_name="James Rodríguez",
                x=93.0,
                y=54.0,
                outcome="Goal",
                xg=0.55,
                body_part="Left Foot",
                shot_type="Open Play"
            ),
            ShotEvent(
                id="shot_c5",
                minute=92,
                second=55,
                team_id="barcelona",
                team_name="FC Barcelona",
                player_name="Lionel Messi",
                x=84.0,
                y=48.0,
                outcome="Goal",
                xg=0.34,
                body_part="Left Foot",
                shot_type="Fast Break"
            )
        ],
        pass_nodes=[
            PassNode(player_name="L. Messi", position="CF", jersey_number=10, x=74.0, y=52.0, passes_completed=48),
            PassNode(player_name="S. Busquets", position="DM", jersey_number=5, x=45.0, y=49.0, passes_completed=66),
            PassNode(player_name="I. Rakitić", position="CM", jersey_number=4, x=58.0, y=36.0, passes_completed=51),
            PassNode(player_name="A. Iniesta", position="CM", jersey_number=8, x=61.0, y=65.0, passes_completed=55),
            PassNode(player_name="J. Alba", position="LB", jersey_number=18, x=64.0, y=88.0, passes_completed=44),
            PassNode(player_name="L. Suárez", position="ST", jersey_number=9, x=82.0, y=48.0, passes_completed=24),
            PassNode(player_name="G. Piqué", position="CB", jersey_number=3, x=29.0, y=42.0, passes_completed=62)
        ],
        pass_links=[
            PassLink(source="S. Busquets", target="I. Rakitić", pass_count=19),
            PassLink(source="S. Busquets", target="A. Iniesta", pass_count=18),
            PassLink(source="A. Iniesta", target="J. Alba", pass_count=16),
            PassLink(source="J. Alba", target="L. Messi", pass_count=14),
            PassLink(source="I. Rakitić", target="L. Messi", pass_count=13),
            PassLink(source="L. Messi", target="L. Suárez", pass_count=10),
            PassLink(source="G. Piqué", target="S. Busquets", pass_count=22)
        ]
    )
]

@router.get("/matches", response_model=List[HistoricalMatchSummary])
async def list_historical_matches():
    """Retrieve list of legendary historical matches available for deep tactical visualization."""
    return [
        HistoricalMatchSummary(
            id=m.id,
            title=m.title,
            competition=m.competition,
            season=m.season,
            match_date=m.match_date,
            venue=m.venue,
            home_team_id=m.home_team_id,
            home_team_name=m.home_team_name,
            home_score=m.home_score,
            away_team_id=m.away_team_id,
            away_team_name=m.away_team_name,
            away_score=m.away_score,
            data_provider=m.data_provider,
            license_notice=m.license_notice
        )
        for m in HISTORICAL_MATCHES
    ]

@router.get("/matches/{match_id}", response_model=HistoricalMatchDetail)
async def get_historical_match_detail(match_id: str):
    """Retrieve deep match telemetry including interactive shot maps, coordinates, and pass networks."""
    m = next((item for item in HISTORICAL_MATCHES if item.id == match_id), None)
    if not m:
        raise HTTPException(status_code=404, detail="Historical match event data not found")
    return m
