import httpx
import datetime
import re
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings

class FootballDataProvider:
    """
    Adapter for football-data.org Free Tier (10 calls/min, 12 competitions).
    Provides resilient parsing, canonical normalization, rate-limit awareness,
    and a rich fallback dataset for offline development and testing.
    """
    BASE_URL = "https://api.football-data.org/v4"

    # Known Foundation Club mappings in football-data.org
    FOUNDATION_IDS = {
        57: "arsenal",
        86: "real-madrid",
        81: "barcelona",
        98: "milan"
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.FOOTBALL_DATA_API_KEY
        self.headers = {"X-Auth-Token": self.api_key} if self.api_key else {}

    @classmethod
    def map_team_id(cls, ext_id: Optional[int], name: str, short_name: Optional[str] = None) -> str:
        """Map external provider ID / names to canonical internal slug."""
        if ext_id and ext_id in cls.FOUNDATION_IDS:
            return cls.FOUNDATION_IDS[ext_id]

        name_lower = name.lower()
        if "arsenal" in name_lower:
            return "arsenal"
        if "real madrid" in name_lower:
            return "real-madrid"
        if "barcelona" in name_lower or (short_name and "barça" in short_name.lower()):
            return "barcelona"
        if "milan" in name_lower and "inter" not in name_lower:
            return "milan"

        # General slugification for opponents
        clean = (short_name or name).lower()
        clean = re.sub(r"\b(fc|cf|ac|afc|ssc|rcd|club)\b", "", clean)
        clean = re.sub(r"[^\w\s-]", "", clean).strip()
        slug = re.sub(r"[\s_-]+", "-", clean)
        return slug or "opponent"

    async def fetch_team_matches(self, team_id: int, season: int = 2024) -> List[Dict[str, Any]]:
        """Fetch matches for a specific team with rate limiting and timeout handling."""
        if not self.api_key:
            return []

        url = f"{self.BASE_URL}/teams/{team_id}/matches"
        params = {"season": season}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("matches", [])
                elif response.status_code == 429:
                    print(f"[FootballDataProvider] Rate limit (429) hit fetching team {team_id}.")
                    return []
                else:
                    print(f"[FootballDataProvider] API HTTP {response.status_code} for team {team_id}")
                    return []
            except httpx.RequestError as exc:
                print(f"[FootballDataProvider] Network error fetching team {team_id}: {exc}")
                return []

    async def fetch_competition_matches(self, comp_code: str = "PL", season: int = 2024) -> List[Dict[str, Any]]:
        """Fetch matches for a competition."""
        if not self.api_key:
            return []

        url = f"{self.BASE_URL}/competitions/{comp_code}/matches"
        params = {"season": season}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("matches", [])
                elif response.status_code == 429:
                    print(f"[FootballDataProvider] Rate limit (429) hit fetching competition {comp_code}.")
                    return []
                else:
                    print(f"[FootballDataProvider] API HTTP {response.status_code} for competition {comp_code}")
                    return []
            except httpx.RequestError as exc:
                print(f"[FootballDataProvider] Network error fetching competition {comp_code}: {exc}")
                return []

    def normalize_match(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a raw football-data.org match payload into canonical schema."""
        raw_id = raw.get("id")
        comp = raw.get("competition", {})
        comp_code = comp.get("code") or "PL"
        comp_name = comp.get("name") or comp_code

        home_raw = raw.get("homeTeam", {})
        away_raw = raw.get("awayTeam", {})

        home_id = self.map_team_id(home_raw.get("id"), home_raw.get("name", ""), home_raw.get("shortName"))
        away_id = self.map_team_id(away_raw.get("id"), away_raw.get("name", ""), away_raw.get("shortName"))

        utc_str = raw.get("utcDate")
        if utc_str:
            utc_date = datetime.datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        else:
            utc_date = datetime.datetime.now(datetime.timezone.utc)

        score_data = raw.get("score", {})
        full_time = score_data.get("fullTime", {})
        home_score = full_time.get("home")
        away_score = full_time.get("away")
        winner = score_data.get("winner")

        status = raw.get("status", "SCHEDULED")
        if status in ("TIMED", "SCHEDULED"):
            status = "SCHEDULED"
        elif status in ("IN_PLAY", "PAUSED"):
            status = "IN_PLAY"
        elif status == "FINISHED":
            status = "FINISHED"

        return {
            "id": f"fd-{raw_id}",
            "competition_id": comp_code,
            "competition_name": comp_name,
            "season_id": f"2024-2025-{comp_code}",
            "home_team_id": home_id,
            "home_team_name": home_raw.get("name", "Home Team"),
            "home_team_crest": home_raw.get("crest"),
            "away_team_id": away_id,
            "away_team_name": away_raw.get("name", "Away Team"),
            "away_team_crest": away_raw.get("crest"),
            "matchday": raw.get("matchday"),
            "utc_date": utc_date,
            "status": status,
            "venue": raw.get("venue"),
            "home_score": home_score,
            "away_score": away_score,
            "winner": winner,
            "source": "football-data.org"
        }

    def get_fallback_matches(self) -> List[Dict[str, Any]]:
        """
        High-fidelity 2024-2025 match schedule and results for the 4 Foundation Clubs.
        Provides realistic fixtures and results with official crest URLs.
        """
        matches = []
        base_date = datetime.datetime(2024, 8, 17, 14, 0, tzinfo=datetime.timezone.utc)

        # Arsenal 2024-2025 matches
        arsenal_fixtures = [
            ("fd-ars-1", "PL", "Premier League", 1, base_date + datetime.timedelta(days=0), "FINISHED", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", "wolves", "Wolverhampton Wanderers FC", "https://crests.football-data.org/76.png", 2, 0, "HOME_TEAM", "Emirates Stadium"),
            ("fd-ars-2", "PL", "Premier League", 2, base_date + datetime.timedelta(days=7), "FINISHED", "aston-villa", "Aston Villa FC", "https://crests.football-data.org/58.png", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", 0, 2, "AWAY_TEAM", "Villa Park"),
            ("fd-ars-3", "PL", "Premier League", 3, base_date + datetime.timedelta(days=14), "FINISHED", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", "brighton", "Brighton & Hove Albion FC", "https://crests.football-data.org/397.png", 1, 1, "DRAW", "Emirates Stadium"),
            ("fd-ars-4", "PL", "Premier League", 4, base_date + datetime.timedelta(days=28), "FINISHED", "tottenham", "Tottenham Hotspur FC", "https://crests.football-data.org/73.png", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", 0, 1, "AWAY_TEAM", "Tottenham Hotspur Stadium"),
            ("fd-ars-5", "PL", "Premier League", 5, base_date + datetime.timedelta(days=35), "FINISHED", "manchester-city", "Manchester City FC", "https://crests.football-data.org/65.png", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", 2, 2, "DRAW", "Etihad Stadium"),
            ("fd-ars-6", "PL", "Premier League", 6, base_date + datetime.timedelta(days=42), "FINISHED", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", "leicester", "Leicester City FC", "https://crests.football-data.org/338.png", 4, 2, "HOME_TEAM", "Emirates Stadium"),
            ("fd-ars-7", "PL", "Premier League", 7, base_date + datetime.timedelta(days=49), "FINISHED", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", "southampton", "Southampton FC", "https://crests.football-data.org/340.png", 3, 1, "HOME_TEAM", "Emirates Stadium"),
            ("fd-ars-8", "PL", "Premier League", 8, base_date + datetime.timedelta(days=63), "FINISHED", "bournemouth", "AFC Bournemouth", "https://crests.football-data.org/1044.png", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", 2, 0, "HOME_TEAM", "Vitality Stadium"),
            ("fd-ars-9", "PL", "Premier League", 9, base_date + datetime.timedelta(days=70), "FINISHED", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", "liverpool", "Liverpool FC", "https://crests.football-data.org/64.png", 2, 2, "DRAW", "Emirates Stadium"),
            ("fd-ars-10", "PL", "Premier League", 10, base_date + datetime.timedelta(days=77), "FINISHED", "newcastle", "Newcastle United FC", "https://crests.football-data.org/67.png", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", 1, 0, "HOME_TEAM", "St. James' Park"),
            ("fd-ars-11", "PL", "Premier League", 11, base_date + datetime.timedelta(days=84), "FINISHED", "chelsea", "Chelsea FC", "https://crests.football-data.org/61.png", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", 1, 1, "DRAW", "Stamford Bridge"),
            ("fd-ars-12", "PL", "Premier League", 12, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3), "SCHEDULED", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", "nottingham-forest", "Nottingham Forest FC", "https://crests.football-data.org/351.png", None, None, None, "Emirates Stadium"),
            ("fd-ars-13", "PL", "Premier League", 13, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10), "SCHEDULED", "west-ham", "West Ham United FC", "https://crests.football-data.org/563.png", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", None, None, None, "London Stadium"),
            ("fd-ars-14", "PL", "Premier League", 14, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14), "SCHEDULED", "arsenal", "Arsenal FC", "https://crests.football-data.org/57.png", "manchester-united", "Manchester United FC", "https://crests.football-data.org/66.png", None, None, None, "Emirates Stadium")
        ]

        # Real Madrid 2024-2025 matches
        real_fixtures = [
            ("fd-rma-1", "PD", "La Liga", 1, base_date + datetime.timedelta(days=1), "FINISHED", "mallorca", "RCD Mallorca", "https://crests.football-data.org/89.png", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", 1, 1, "DRAW", "Son Moix"),
            ("fd-rma-2", "PD", "La Liga", 2, base_date + datetime.timedelta(days=8), "FINISHED", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", "valladolid", "Real Valladolid CF", "https://crests.football-data.org/250.png", 3, 0, "HOME_TEAM", "Santiago Bernabéu"),
            ("fd-rma-3", "PD", "La Liga", 3, base_date + datetime.timedelta(days=15), "FINISHED", "las-palmas", "UD Las Palmas", "https://crests.football-data.org/275.png", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", 1, 1, "DRAW", "Gran Canaria"),
            ("fd-rma-4", "PD", "La Liga", 4, base_date + datetime.timedelta(days=22), "FINISHED", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", "betis", "Real Betis", "https://crests.football-data.org/90.png", 2, 0, "HOME_TEAM", "Santiago Bernabéu"),
            ("fd-rma-5", "PD", "La Liga", 5, base_date + datetime.timedelta(days=29), "FINISHED", "real-sociedad", "Real Sociedad", "https://crests.football-data.org/92.png", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", 0, 2, "AWAY_TEAM", "Reale Arena"),
            ("fd-rma-6", "PD", "La Liga", 6, base_date + datetime.timedelta(days=36), "FINISHED", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", "espanyol", "RCD Espanyol", "https://crests.football-data.org/80.png", 4, 1, "HOME_TEAM", "Santiago Bernabéu"),
            ("fd-rma-7", "PD", "La Liga", 7, base_date + datetime.timedelta(days=43), "FINISHED", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", "alaves", "Deportivo Alavés", "https://crests.football-data.org/263.png", 3, 2, "HOME_TEAM", "Santiago Bernabéu"),
            ("fd-rma-8", "PD", "La Liga", 8, base_date + datetime.timedelta(days=50), "FINISHED", "atletico-madrid", "Atlético de Madrid", "https://crests.football-data.org/78.png", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", 1, 1, "DRAW", "Metropolitano"),
            ("fd-rma-9", "PD", "La Liga", 9, base_date + datetime.timedelta(days=57), "FINISHED", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", "villarreal", "Villarreal CF", "https://crests.football-data.org/94.png", 2, 0, "HOME_TEAM", "Santiago Bernabéu"),
            ("fd-rma-10", "PD", "La Liga", 10, base_date + datetime.timedelta(days=71), "FINISHED", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", 0, 4, "AWAY_TEAM", "Santiago Bernabéu"),
            ("fd-rma-11", "PD", "La Liga", 11, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=4), "SCHEDULED", "leganes", "CD Leganés", "https://crests.football-data.org/745.png", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", None, None, None, "Butarque"),
            ("fd-rma-12", "PD", "La Liga", 12, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=11), "SCHEDULED", "real-madrid", "Real Madrid CF", "https://crests.football-data.org/86.png", "getafe", "Getafe CF", "https://crests.football-data.org/82.png", None, None, None, "Santiago Bernabéu")
        ]

        # Barcelona 2024-2025 matches
        barca_fixtures = [
            ("fd-bar-1", "PD", "La Liga", 1, base_date + datetime.timedelta(days=0), "FINISHED", "valencia", "Valencia CF", "https://crests.football-data.org/95.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", 1, 2, "AWAY_TEAM", "Mestalla"),
            ("fd-bar-2", "PD", "La Liga", 2, base_date + datetime.timedelta(days=7), "FINISHED", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", "athletic-club", "Athletic Club", "https://crests.football-data.org/77.png", 2, 1, "HOME_TEAM", "Montjuïc"),
            ("fd-bar-3", "PD", "La Liga", 3, base_date + datetime.timedelta(days=14), "FINISHED", "rayo-vallecano", "Rayo Vallecano", "https://crests.football-data.org/87.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", 1, 2, "AWAY_TEAM", "Vallecas"),
            ("fd-bar-4", "PD", "La Liga", 4, base_date + datetime.timedelta(days=21), "FINISHED", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", "valladolid", "Real Valladolid CF", "https://crests.football-data.org/250.png", 7, 0, "HOME_TEAM", "Montjuïc"),
            ("fd-bar-5", "PD", "La Liga", 5, base_date + datetime.timedelta(days=28), "FINISHED", "girona", "Girona FC", "https://crests.football-data.org/298.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", 1, 4, "AWAY_TEAM", "Montilivi"),
            ("fd-bar-6", "PD", "La Liga", 6, base_date + datetime.timedelta(days=35), "FINISHED", "villarreal", "Villarreal CF", "https://crests.football-data.org/94.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", 1, 5, "AWAY_TEAM", "La Cerámica"),
            ("fd-bar-7", "PD", "La Liga", 7, base_date + datetime.timedelta(days=42), "FINISHED", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", "getafe", "Getafe CF", "https://crests.football-data.org/82.png", 1, 0, "HOME_TEAM", "Montjuïc"),
            ("fd-bar-8", "PD", "La Liga", 8, base_date + datetime.timedelta(days=49), "FINISHED", "osasuna", "CA Osasuna", "https://crests.football-data.org/79.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", 4, 2, "HOME_TEAM", "El Sadar"),
            ("fd-bar-9", "PD", "La Liga", 9, base_date + datetime.timedelta(days=56), "FINISHED", "alaves", "Deportivo Alavés", "https://crests.football-data.org/263.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", 0, 3, "AWAY_TEAM", "Mendizorrotza"),
            ("fd-bar-10", "PD", "La Liga", 10, base_date + datetime.timedelta(days=63), "FINISHED", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", "sevilla", "Sevilla FC", "https://crests.football-data.org/559.png", 5, 1, "HOME_TEAM", "Montjuïc"),
            ("fd-bar-11", "PD", "La Liga", 11, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5), "SCHEDULED", "celta-vigo", "RC Celta de Vigo", "https://crests.football-data.org/558.png", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", None, None, None, "Balaídos"),
            ("fd-bar-12", "PD", "La Liga", 12, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=12), "SCHEDULED", "barcelona", "FC Barcelona", "https://crests.football-data.org/81.png", "las-palmas", "UD Las Palmas", "https://crests.football-data.org/275.png", None, None, None, "Montjuïc")
        ]

        # AC Milan 2024-2025 matches
        milan_fixtures = [
            ("fd-mil-1", "SA", "Serie A", 1, base_date + datetime.timedelta(days=0), "FINISHED", "milan", "AC Milan", "https://crests.football-data.org/98.png", "torino", "Torino FC", "https://crests.football-data.org/586.png", 2, 2, "DRAW", "San Siro"),
            ("fd-mil-2", "SA", "Serie A", 2, base_date + datetime.timedelta(days=7), "FINISHED", "parma", "Parma Calcio 1913", "https://crests.football-data.org/112.png", "milan", "AC Milan", "https://crests.football-data.org/98.png", 2, 1, "HOME_TEAM", "Ennio Tardini"),
            ("fd-mil-3", "SA", "Serie A", 3, base_date + datetime.timedelta(days=14), "FINISHED", "lazio", "SS Lazio", "https://crests.football-data.org/110.png", "milan", "AC Milan", "https://crests.football-data.org/98.png", 2, 2, "DRAW", "Stadio Olimpico"),
            ("fd-mil-4", "SA", "Serie A", 4, base_date + datetime.timedelta(days=28), "FINISHED", "milan", "AC Milan", "https://crests.football-data.org/98.png", "venezia", "Venezia FC", "https://crests.football-data.org/454.png", 4, 0, "HOME_TEAM", "San Siro"),
            ("fd-mil-5", "SA", "Serie A", 5, base_date + datetime.timedelta(days=35), "FINISHED", "inter", "FC Internazionale Milano", "https://crests.football-data.org/108.png", "milan", "AC Milan", "https://crests.football-data.org/98.png", 1, 2, "AWAY_TEAM", "San Siro"),
            ("fd-mil-6", "SA", "Serie A", 6, base_date + datetime.timedelta(days=42), "FINISHED", "milan", "AC Milan", "https://crests.football-data.org/98.png", "lecce", "US Lecce", "https://crests.football-data.org/5890.png", 3, 0, "HOME_TEAM", "San Siro"),
            ("fd-mil-7", "SA", "Serie A", 7, base_date + datetime.timedelta(days=49), "FINISHED", "fiorentina", "ACF Fiorentina", "https://crests.football-data.org/99.png", "milan", "AC Milan", "https://crests.football-data.org/98.png", 2, 1, "HOME_TEAM", "Artemio Franchi"),
            ("fd-mil-8", "SA", "Serie A", 8, base_date + datetime.timedelta(days=63), "FINISHED", "milan", "AC Milan", "https://crests.football-data.org/98.png", "udinese", "Udinese Calcio", "https://crests.football-data.org/115.png", 1, 0, "HOME_TEAM", "San Siro"),
            ("fd-mil-9", "SA", "Serie A", 9, base_date + datetime.timedelta(days=70), "FINISHED", "milan", "AC Milan", "https://crests.football-data.org/98.png", "napoli", "SSC Napoli", "https://crests.football-data.org/113.png", 0, 2, "AWAY_TEAM", "San Siro"),
            ("fd-mil-10", "SA", "Serie A", 10, base_date + datetime.timedelta(days=77), "FINISHED", "monza", "AC Monza", "https://crests.football-data.org/5911.png", "milan", "AC Milan", "https://crests.football-data.org/98.png", 0, 1, "AWAY_TEAM", "U-Power Stadium"),
            ("fd-mil-11", "SA", "Serie A", 11, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=6), "SCHEDULED", "milan", "AC Milan", "https://crests.football-data.org/98.png", "juventus", "Juventus FC", "https://crests.football-data.org/109.png", None, None, None, "San Siro"),
            ("fd-mil-12", "SA", "Serie A", 12, datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=13), "SCHEDULED", "empoli", "Empoli FC", "https://crests.football-data.org/107.png", "milan", "AC Milan", "https://crests.football-data.org/98.png", None, None, None, "Carlo Castellani")
        ]

        all_fixtures = arsenal_fixtures + real_fixtures + barca_fixtures + milan_fixtures

        for f in all_fixtures:
            matches.append({
                "id": f[0],
                "competition_id": f[1],
                "competition_name": f[2],
                "season_id": f"2024-2025-{f[1]}",
                "matchday": f[3],
                "utc_date": f[4],
                "status": f[5],
                "home_team_id": f[6],
                "home_team_name": f[7],
                "home_team_crest": f[8],
                "away_team_id": f[9],
                "away_team_name": f[10],
                "away_team_crest": f[11],
                "home_score": f[12],
                "away_score": f[13],
                "winner": f[14],
                "venue": f[15],
                "source": "football-data.org"
            })

        return matches
