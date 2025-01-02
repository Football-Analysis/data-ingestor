from requests import get
from typing import List
from .ingestor import Ingestor
from ..data_models.match import Match


class ApiFootball(Ingestor):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)
        self.base_headers = {'x-rapidapi-key': self.api_key, 'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'}

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
        processed_matches = []
        for match in fixtures.json()["response"]:
            game_week = match["league"]["round"].split()[-1]
            processed_matches.append(Match(date=match["fixture"]["date"],
                                           home_team=match["teams"]["home"]["name"],
                                           away_team=match["teams"]["away"]["name"],
                                           score=match["score"],
                                           game_week=game_week))
        return processed_matches
