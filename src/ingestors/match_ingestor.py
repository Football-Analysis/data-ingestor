from requests import get
from typing import List, Optional
from .ingestor import Ingestor
from ..data_models.match import Match
from ..data_models.league import League
from time import sleep, time
from ..utils.feature_engineering import process_raw_match, calculate_form


class ApiFootball(Ingestor):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)
        self.base_headers = {'x-apisports-key': self.api_key}
        self.start_minute = time()

    def get_teams_per_league(self, league_id: int, season:int) -> List[str]:
        endpoint = f'{self.base_url}/teams'
        params = {"league": league_id, "season": season}
        teams = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(teams.headers)
        teams_data = teams.json()["response"]
        requests_left = teams.headers["x-ratelimit-requests-remaining"]
        print(f"Requests left on plan: {requests_left}")
        
        teams_to_save = {}
        for team in teams_data:
            team_id = str(team["team"]["id"])
            teams_to_save[team_id] = {"form": {}}
            endpoint = f'{self.base_url}/teams/statistics'
            params = {"league": league_id, "season": season, "team": team_id}
            team_stats = get(endpoint, headers=self.base_headers, params=params)
            self.check_api_limits(team_stats.headers)
            form = team_stats.json()["response"]["form"]
            teams_form = calculate_form(form)
            teams_to_save[team_id]["form"] = teams_form

        return League(league_id, season, teams_to_save)

    def get_leagues(self, league_id: Optional[int] = None):
        endpoint = f"{self.base_url}/leagues"
        if league_id:
            params = {"id": league_id, "type": "league"}
            leagues = get(endpoint, headers=self.base_headers, params=params)
        else:
            params = {"type": "league"}
            leagues = get(endpoint, headers=self.base_headers, params=params)

        self.check_api_limits(leagues.headers)
        league_data = leagues.json()
        leagues_to_get = {}
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["coverage"]["fixtures"]["events"] == True and season["year"] > 2010:
                    if league_id in leagues_to_get:
                        leagues_to_get[league_id].append(season["year"])
                    else:
                        leagues_to_get[league_id] = [season["year"]]

        return leagues_to_get

    def get_seasons_matches(self, league_id: int = 39, season: int = 2014) -> List[Match]:
        """Takes a league and season, queries the fixtures API endpoint and returns all
        processed matches for that league and season

        Args:
            league_id (int, optional): The league id to get matches from. Defaults to 39 (Premier League).
            season (int, optional): The season to return matches from. Defaults to 2014.

        Returns:
            List[Match]: A list of processed match data
        """
        endpoint = f"{self.base_url}/fixtures"
        params = {"league": league_id, "season": season}
        fixtures = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(fixtures.headers)
        requests_left = fixtures.headers["x-ratelimit-requests-remaining"]
        print(f"Requests left on plan: {requests_left}")
        processed_matches = []
        for match in fixtures.json()["response"]:
            success, processed_match = process_raw_match(match)
            if success:
                processed_matches.append(processed_match)
        return processed_matches

    def get_league_name(self, league_id: int) -> str:
        endpoint = f"{self.base_url}/leagues"
        params = {"id": league_id}
        league = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(league.headers)
        league_name = league.json()["response"][0]["league"]["name"]
        return league_name
    
    def check_api_limits(self, headers):
        requests_left_day = int(headers["x-ratelimit-requests-remaining"])
        requests_left_min = int(headers["X-RateLimit-Remaining"])
        if requests_left_min == 449:
            self.start_minute = time()
        else:
            if requests_left_day % 5000 == 0:
                print(f"{requests_left_day} requests left on daily plan")
            if requests_left_min % 100 == 0:
                print(f"{requests_left_min} requests left on minute limit")
            if requests_left_day < 50:
                raise RuntimeError("Daily API limit reached for API-Football. Please come back tomorrow")
            if requests_left_min < 3:
                print(f"Hit API Rate limit, waiting until end of minute")
                time_left = 60 - (time() - self.start_minute)
                sleep(time_left+1)
        
            if time() - self.start_minute > 60:
                self.start_minute = time()

    def test(self):
        endpoint = f"{self.base_url}/status"
        league = get(endpoint, headers=self.base_headers)
        self.check_api_limits(league.headers)

