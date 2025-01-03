from requests import get
from typing import List, Optional
from .ingestor import Ingestor
from ..data_models.match import Match
from time import sleep


class ApiFootball(Ingestor):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)
        self.base_headers = {'x-rapidapi-key': self.api_key, 'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'}

    def get_leagues(self, league_id: Optional[int] = None):
        sleep(0.143)
        endpoint = f"{self.base_url}/leagues"
        if league_id:
            params = {"id": league_id}
            leagues = get(endpoint, headers=self.base_headers, params=params)
        else:
            leagues = get(endpoint, headers=self.base_headers)

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
            game_week = match["league"]["round"].split()[-1]
            league_data = {}
            league_data["name"] = match["league"]["name"]
            league_data["id"] = match["league"]["id"]
            processed_matches.append(Match(date=match["fixture"]["date"],
                                           home_team=match["teams"]["home"]["name"],
                                           away_team=match["teams"]["away"]["name"],
                                           score=match["score"],
                                           game_week=game_week,
                                           season=season,
                                           league=league_data))
        return processed_matches

    def get_teams(self, league_id: int = 39, season: int = 2014):
        sleep(0.143)
        endpoint = f"{self.base_url}/teams"
        params = {"league": league_id, "season": season}
        teams = get(endpoint, headers=self.base_headers, params=params)
        print(teams.json())
