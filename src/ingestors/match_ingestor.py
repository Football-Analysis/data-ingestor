from requests import get
from typing import List, Optional
from .ingestor import Ingestor
from ..data_models.match import Match
from ..data_models.league import League
from time import sleep
from ..utils.feature_engineering import process_raw_match


class ApiFootball(Ingestor):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)
        self.base_headers = {'x-rapidapi-key': self.api_key, 'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'}

    def get_teams_per_league(self, league_id: int, season:int) -> List[str]:
        sleep(0.143)
        endpoint = f'{self.base_url}/teams'
        params = {"league": league_id, "season": season}
        teams = get(endpoint, headers=self.base_headers, params=params)
        teams_data = teams.json()["response"]
        requests_left = teams.headers["x-ratelimit-requests-remaining"]
        print(f"Requests left on plan: {requests_left}")

        league_name = self.get_league_name(league_id)
        
        teams_to_save = []
        for team in teams_data:
            teams_to_save.append(team["team"]["name"])

        return League(league_id, league_name, season, teams_to_save)

    def get_leagues(self, league_id: Optional[int] = None):
        sleep(0.143)
        endpoint = f"{self.base_url}/leagues"
        if league_id:
            params = {"id": league_id, "type": "league"}
            leagues = get(endpoint, headers=self.base_headers, params=params)
        else:
            params = {"type": "league"}
            leagues = get(endpoint, headers=self.base_headers, params=params)

        league_data = leagues.json()
        leagues_to_get = {}
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["coverage"]["players"] == True:
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
        sleep(0.143)
        endpoint = f"{self.base_url}/fixtures"
        params = {"league": league_id, "season": season}
        fixtures = get(endpoint, headers=self.base_headers, params=params)
        requests_left = fixtures.headers["x-ratelimit-requests-remaining"]
        print(f"Requests left on plan: {requests_left}")
        processed_matches = []
        for match in fixtures.json()["response"]:
            processed_match = process_raw_match(match)
            processed_matches.append(processed_match)
        return processed_matches

    def get_league_name(self, league_id: int) -> str:
        sleep(0.143)
        endpoint = f"{self.base_url}/leagues"
        params = {"id": league_id}
        league = get(endpoint, headers=self.base_headers, params=params)
        league_name = league.json()["response"][0]["league"]["name"]
        return league_name
    
    def get_standings(self):
        sleep(0.143)
        endpoint = f"{self.base_url}/standings"
        params = {"league": 39, "season": 2024, "game_week":"10"}
        standings = get(endpoint, headers=self.base_headers, params=params)
        requests_left = standings.headers["x-ratelimit-requests-remaining"]
        print(f"Requests left on plan: {requests_left}")
        print(standings.json())
