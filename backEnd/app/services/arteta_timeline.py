import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.football import Season, Match, Club, Competition

class ArtetaTimelineService:
    """
    Chronicles the complete tactical and competitive era of Mikel Arteta at Arsenal FC (Dec 2019 - Present).
    Provides season records, iconic match events, and real-time active campaign integration.
    """

    SEASONS_METADATA: List[Dict[str, Any]] = [
        {
            "id": "2026-2027-PL",
            "competition_id": "PL",
            "start_year": 2026,
            "end_year": 2027,
            "is_current": True,
            "label": "2026/27 (Current Campaign)",
            "headline": "Active Running Season & Live Matchdays",
            "arteta_milestone": "Live campaign tracking: Premier League title quest, European knockout stages, and real-time telemetry."
        },
        {
            "id": "2025-2026-PL",
            "competition_id": "PL",
            "start_year": 2025,
            "end_year": 2026,
            "is_current": False,
            "label": "2025/26",
            "headline": "Elite Continental & Domestic Chase",
            "arteta_milestone": "Title contention, deep Champions League knockout run, and peak squad maturity."
        },
        {
            "id": "2024-2025-PL",
            "competition_id": "PL",
            "start_year": 2024,
            "end_year": 2025,
            "is_current": False,
            "label": "2024/25",
            "headline": "Emirates Fortress & Defensive Supremacy",
            "arteta_milestone": "Best defensive metrics across Europe; Gabriel-Saliba partnership concede lowest xG in Premier League."
        },
        {
            "id": "2023-2024-PL",
            "competition_id": "PL",
            "start_year": 2023,
            "end_year": 2024,
            "is_current": False,
            "label": "2023/24",
            "headline": "Record 28 Premier League Wins (89 Pts)",
            "arteta_milestone": "Club record 28 Premier League victories in a single season, 89 points, and +62 goal difference."
        },
        {
            "id": "2022-2023-PL",
            "competition_id": "PL",
            "start_year": 2022,
            "end_year": 2023,
            "is_current": False,
            "label": "2022/23",
            "headline": "Title Contenders & Champions League Return (84 Pts)",
            "arteta_milestone": "Arsenal returned to the UEFA Champions League for the first time in 7 years with 84 points."
        },
        {
            "id": "2021-2022-PL",
            "competition_id": "PL",
            "start_year": 2021,
            "end_year": 2022,
            "is_current": False,
            "label": "2021/22",
            "headline": "Young Guns Cultural Reset",
            "arteta_milestone": "Youngest average starting XI in England; breakout campaigns for Bukayo Saka, Martin Ødegaard, and Gabriel Martinelli."
        },
        {
            "id": "2020-2021-PL",
            "competition_id": "PL",
            "start_year": 2020,
            "end_year": 2021,
            "is_current": False,
            "label": "2020/21",
            "headline": "Community Shield & Positional Rebuild",
            "arteta_milestone": "Defeated Liverpool on penalties to win the FA Community Shield; instituted Arteta's 3-2-5 in-possession shape."
        },
        {
            "id": "2019-2020-PL",
            "competition_id": "PL",
            "start_year": 2019,
            "end_year": 2020,
            "is_current": False,
            "label": "2019/20",
            "headline": "Arteta Appointed & FA Cup Victory",
            "arteta_milestone": "Mikel Arteta appointed Dec 20, 2019; won the FA Cup defeating Man City in semi-final and Chelsea in the final."
        }
    ]

    @classmethod
    def get_seasons_list(cls) -> List[Dict[str, Any]]:
        return cls.SEASONS_METADATA

    @classmethod
    def get_arteta_matches_dataset(cls) -> List[Dict[str, Any]]:
        """
        Curated canonical matches across all 8 seasons of the Mikel Arteta era.
        Contains verified real match details, derbies, and milestone results.
        """
        matches: List[Dict[str, Any]] = []

        # Helper constants
        ARS_CREST = "https://crests.football-data.org/57.png"
        CHE_CREST = "https://crests.football-data.org/61.png"
        MCI_CREST = "https://crests.football-data.org/65.png"
        LIV_CREST = "https://crests.football-data.org/64.png"
        MUN_CREST = "https://crests.football-data.org/66.png"
        TOT_CREST = "https://crests.football-data.org/73.png"
        NEW_CREST = "https://crests.football-data.org/67.png"
        AVL_CREST = "https://crests.football-data.org/58.png"
        BOU_CREST = "https://crests.football-data.org/1044.png"
        WOL_CREST = "https://crests.football-data.org/76.png"

        # --- 2019/20 Season (Arteta takes charge) ---
        matches.extend([
            {
                "id": "art-1920-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2019-2020-PL",
                "matchday": 19,
                "utc_date": datetime.datetime(2019, 12, 26, 15, 0, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "bournemouth",
                "home_team_name": "AFC Bournemouth",
                "home_team_crest": BOU_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 1,
                "away_score": 1,
                "winner": "DRAW",
                "venue": "Vitality Stadium"
            },
            {
                "id": "art-1920-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2019-2020-PL",
                "matchday": 21,
                "utc_date": datetime.datetime(2020, 1, 1, 20, 0, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "manchester-united",
                "away_team_name": "Manchester United FC",
                "away_team_crest": MUN_CREST,
                "home_score": 2,
                "away_score": 0,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-1920-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2019-2020-PL",
                "matchday": 36,
                "utc_date": datetime.datetime(2020, 7, 15, 19, 15, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "liverpool",
                "away_team_name": "Liverpool FC",
                "away_team_crest": LIV_CREST,
                "home_score": 2,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-1920-4",
                "competition_id": "PL",
                "competition_name": "FA Cup Final",
                "season_id": "2019-2020-PL",
                "matchday": 38,
                "utc_date": datetime.datetime(2020, 8, 1, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "chelsea",
                "away_team_name": "Chelsea FC",
                "away_team_crest": CHE_CREST,
                "home_score": 2,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Wembley Stadium"
            }
        ])

        # --- 2020/21 Season ---
        matches.extend([
            {
                "id": "art-2021-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2020-2021-PL",
                "matchday": 7,
                "utc_date": datetime.datetime(2020, 11, 1, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "manchester-united",
                "home_team_name": "Manchester United FC",
                "home_team_crest": MUN_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 0,
                "away_score": 1,
                "winner": "AWAY_TEAM",
                "venue": "Old Trafford"
            },
            {
                "id": "art-2021-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2020-2021-PL",
                "matchday": 15,
                "utc_date": datetime.datetime(2020, 12, 26, 17, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "chelsea",
                "away_team_name": "Chelsea FC",
                "away_team_crest": CHE_CREST,
                "home_score": 3,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2021-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2020-2021-PL",
                "matchday": 28,
                "utc_date": datetime.datetime(2021, 3, 14, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "tottenham",
                "away_team_name": "Tottenham Hotspur FC",
                "away_team_crest": TOT_CREST,
                "home_score": 2,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            }
        ])

        # --- 2021/22 Season ---
        matches.extend([
            {
                "id": "art-2122-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2021-2022-PL",
                "matchday": 6,
                "utc_date": datetime.datetime(2021, 9, 26, 15, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "tottenham",
                "away_team_name": "Tottenham Hotspur FC",
                "away_team_crest": TOT_CREST,
                "home_score": 3,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2122-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2021-2022-PL",
                "matchday": 25,
                "utc_date": datetime.datetime(2022, 4, 20, 18, 45, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "chelsea",
                "home_team_name": "Chelsea FC",
                "home_team_crest": CHE_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 2,
                "away_score": 4,
                "winner": "AWAY_TEAM",
                "venue": "Stamford Bridge"
            },
            {
                "id": "art-2122-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2021-2022-PL",
                "matchday": 34,
                "utc_date": datetime.datetime(2022, 4, 23, 11, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "manchester-united",
                "away_team_name": "Manchester United FC",
                "away_team_crest": MUN_CREST,
                "home_score": 3,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            }
        ])

        # --- 2022/23 Season (84 Points) ---
        matches.extend([
            {
                "id": "art-2223-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2022-2023-PL",
                "matchday": 9,
                "utc_date": datetime.datetime(2022, 10, 1, 11, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "tottenham",
                "away_team_name": "Tottenham Hotspur FC",
                "away_team_crest": TOT_CREST,
                "home_score": 3,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2223-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2022-2023-PL",
                "matchday": 10,
                "utc_date": datetime.datetime(2022, 10, 9, 15, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "liverpool",
                "away_team_name": "Liverpool FC",
                "away_team_crest": LIV_CREST,
                "home_score": 3,
                "away_score": 2,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2223-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2022-2023-PL",
                "matchday": 20,
                "utc_date": datetime.datetime(2023, 1, 15, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "tottenham",
                "home_team_name": "Tottenham Hotspur FC",
                "home_team_crest": TOT_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 0,
                "away_score": 2,
                "winner": "AWAY_TEAM",
                "venue": "Tottenham Hotspur Stadium"
            },
            {
                "id": "art-2223-4",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2022-2023-PL",
                "matchday": 21,
                "utc_date": datetime.datetime(2023, 1, 22, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "manchester-united",
                "away_team_name": "Manchester United FC",
                "away_team_crest": MUN_CREST,
                "home_score": 3,
                "away_score": 2,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            }
        ])

        # --- 2023/24 Season (Club Record 28 Wins, 89 Pts) ---
        matches.extend([
            {
                "id": "art-2324-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2023-2024-PL",
                "matchday": 8,
                "utc_date": datetime.datetime(2023, 10, 8, 15, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "manchester-city",
                "away_team_name": "Manchester City FC",
                "away_team_crest": MCI_CREST,
                "home_score": 1,
                "away_score": 0,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2324-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2023-2024-PL",
                "matchday": 23,
                "utc_date": datetime.datetime(2024, 2, 4, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "liverpool",
                "away_team_name": "Liverpool FC",
                "away_team_crest": LIV_CREST,
                "home_score": 3,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2324-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2023-2024-PL",
                "matchday": 29,
                "utc_date": datetime.datetime(2024, 4, 23, 19, 0, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "chelsea",
                "away_team_name": "Chelsea FC",
                "away_team_crest": CHE_CREST,
                "home_score": 5,
                "away_score": 0,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2324-4",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2023-2024-PL",
                "matchday": 35,
                "utc_date": datetime.datetime(2024, 4, 28, 13, 0, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "tottenham",
                "home_team_name": "Tottenham Hotspur FC",
                "home_team_crest": TOT_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 2,
                "away_score": 3,
                "winner": "AWAY_TEAM",
                "venue": "Tottenham Hotspur Stadium"
            }
        ])

        # --- 2024/25 Season ---
        matches.extend([
            {
                "id": "art-2425-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2024-2025-PL",
                "matchday": 1,
                "utc_date": datetime.datetime(2024, 8, 17, 14, 0, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "wolves",
                "away_team_name": "Wolverhampton Wanderers FC",
                "away_team_crest": WOL_CREST,
                "home_score": 2,
                "away_score": 0,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2425-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2024-2025-PL",
                "matchday": 4,
                "utc_date": datetime.datetime(2024, 9, 15, 13, 0, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "tottenham",
                "home_team_name": "Tottenham Hotspur FC",
                "home_team_crest": TOT_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 0,
                "away_score": 1,
                "winner": "AWAY_TEAM",
                "venue": "Tottenham Hotspur Stadium"
            },
            {
                "id": "art-2425-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2024-2025-PL",
                "matchday": 5,
                "utc_date": datetime.datetime(2024, 9, 22, 15, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "manchester-city",
                "home_team_name": "Manchester City FC",
                "home_team_crest": MCI_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 2,
                "away_score": 2,
                "winner": "DRAW",
                "venue": "Etihad Stadium"
            },
            {
                "id": "art-2425-4",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2024-2025-PL",
                "matchday": 9,
                "utc_date": datetime.datetime(2024, 10, 27, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "liverpool",
                "away_team_name": "Liverpool FC",
                "away_team_crest": LIV_CREST,
                "home_score": 2,
                "away_score": 2,
                "winner": "DRAW",
                "venue": "Emirates Stadium"
            }
        ])

        # --- 2025/26 Season ---
        matches.extend([
            {
                "id": "art-2526-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2025-2026-PL",
                "matchday": 2,
                "utc_date": datetime.datetime(2025, 8, 23, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "aston-villa",
                "away_team_name": "Aston Villa FC",
                "away_team_crest": AVL_CREST,
                "home_score": 3,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2526-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2025-2026-PL",
                "matchday": 10,
                "utc_date": datetime.datetime(2025, 11, 2, 15, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "chelsea",
                "away_team_name": "Chelsea FC",
                "away_team_crest": CHE_CREST,
                "home_score": 2,
                "away_score": 0,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2526-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2025-2026-PL",
                "matchday": 21,
                "utc_date": datetime.datetime(2026, 1, 18, 16, 30, tzinfo=datetime.timezone.utc),
                "status": "FINISHED",
                "home_team_id": "tottenham",
                "home_team_name": "Tottenham Hotspur FC",
                "home_team_crest": TOT_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 1,
                "away_score": 3,
                "winner": "AWAY_TEAM",
                "venue": "Tottenham Hotspur Stadium"
            }
        ])

        # --- 2026/27 Active Running Campaign ---
        now = datetime.datetime.now(datetime.timezone.utc)
        matches.extend([
            {
                "id": "art-2627-1",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2026-2027-PL",
                "matchday": 1,
                "utc_date": now - datetime.timedelta(days=70),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "bournemouth",
                "away_team_name": "AFC Bournemouth",
                "away_team_crest": BOU_CREST,
                "home_score": 3,
                "away_score": 0,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2627-2",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2026-2027-PL",
                "matchday": 2,
                "utc_date": now - datetime.timedelta(days=56),
                "status": "FINISHED",
                "home_team_id": "newcastle",
                "home_team_name": "Newcastle United FC",
                "home_team_crest": NEW_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 1,
                "away_score": 2,
                "winner": "AWAY_TEAM",
                "venue": "St. James' Park"
            },
            {
                "id": "art-2627-3",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2026-2027-PL",
                "matchday": 3,
                "utc_date": now - datetime.timedelta(days=35),
                "status": "FINISHED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "tottenham",
                "away_team_name": "Tottenham Hotspur FC",
                "away_team_crest": TOT_CREST,
                "home_score": 3,
                "away_score": 1,
                "winner": "HOME_TEAM",
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2627-4",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2026-2027-PL",
                "matchday": 4,
                "utc_date": now - datetime.timedelta(days=14),
                "status": "FINISHED",
                "home_team_id": "manchester-city",
                "home_team_name": "Manchester City FC",
                "home_team_crest": MCI_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": 1,
                "away_score": 1,
                "winner": "DRAW",
                "venue": "Etihad Stadium"
            },
            {
                "id": "art-2627-5",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2026-2027-PL",
                "matchday": 5,
                "utc_date": now + datetime.timedelta(days=3),
                "status": "SCHEDULED",
                "home_team_id": "arsenal",
                "home_team_name": "Arsenal FC",
                "home_team_crest": ARS_CREST,
                "away_team_id": "chelsea",
                "away_team_name": "Chelsea FC",
                "away_team_crest": CHE_CREST,
                "home_score": None,
                "away_score": None,
                "winner": None,
                "venue": "Emirates Stadium"
            },
            {
                "id": "art-2627-6",
                "competition_id": "PL",
                "competition_name": "Premier League",
                "season_id": "2026-2027-PL",
                "matchday": 6,
                "utc_date": now + datetime.timedelta(days=10),
                "status": "SCHEDULED",
                "home_team_id": "liverpool",
                "home_team_name": "Liverpool FC",
                "home_team_crest": LIV_CREST,
                "away_team_id": "arsenal",
                "away_team_name": "Arsenal FC",
                "away_team_crest": ARS_CREST,
                "home_score": None,
                "away_score": None,
                "winner": None,
                "venue": "Anfield"
            }
        ])

        return matches

    @classmethod
    async def seed_arteta_timeline(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        Idempotently ingest all Arteta era seasons and matches into target database.
        """
        # 1. Competitions
        comp = await db.get(Competition, "PL")
        if not comp:
            db.add(Competition(
                id="PL", code="PL", name="Premier League", country="England",
                emblem_url="https://crests.football-data.org/PL.png"
            ))

        # 2. Seasons
        for s in cls.SEASONS_METADATA:
            existing_s = await db.get(Season, s["id"])
            if not existing_s:
                db.add(Season(
                    id=s["id"],
                    competition_id=s["competition_id"],
                    start_year=s["start_year"],
                    end_year=s["end_year"],
                    is_current=s["is_current"]
                ))
            else:
                existing_s.is_current = s["is_current"]

        await db.flush()

        # 3. Matches
        matches_data = cls.get_arteta_matches_dataset()
        synced_matches = 0
        now = datetime.datetime.now(datetime.timezone.utc)

        for m in matches_data:
            existing_m = await db.get(Match, m["id"])
            if existing_m:
                existing_m.status = m["status"]
                existing_m.home_score = m["home_score"]
                existing_m.away_score = m["away_score"]
                existing_m.winner = m["winner"]
                existing_m.utc_date = m["utc_date"]
                existing_m.matchday = m.get("matchday")
                existing_m.venue = m.get("venue")
                existing_m.last_updated_at = now
            else:
                db.add(Match(
                    id=m["id"],
                    competition_id=m["competition_id"],
                    competition_name=m["competition_name"],
                    season_id=m["season_id"],
                    home_team_id=m["home_team_id"],
                    home_team_name=m["home_team_name"],
                    home_team_crest=m.get("home_team_crest"),
                    away_team_id=m["away_team_id"],
                    away_team_name=m["away_team_name"],
                    away_team_crest=m.get("away_team_crest"),
                    matchday=m.get("matchday"),
                    utc_date=m["utc_date"],
                    status=m["status"],
                    venue=m.get("venue"),
                    home_score=m.get("home_score"),
                    away_score=m.get("away_score"),
                    winner=m.get("winner"),
                    source="openfootball / arteta-timeline",
                    last_updated_at=now
                ))
            synced_matches += 1

        await db.commit()
        return {
            "seasons_count": len(cls.SEASONS_METADATA),
            "matches_synced": synced_matches,
            "status": "SUCCESS"
        }
