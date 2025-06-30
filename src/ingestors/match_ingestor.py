from requests import get
from typing import List, Optional
from .ingestor import Ingestor
from ..data_models.match import Match
from ..data_models.league import League
from ..data_models.h2h import H2H
from ..data_models.player import Player
from time import sleep, time
from ..utils.api_response_processors import process_raw_match


class ApiFootball(Ingestor):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)
        self.base_headers = {'x-apisports-key': self.api_key}
        self.start_minute = time()

    def get_teams_per_league(self, league_id: int, season: int) -> League:
        endpoint = f'{self.base_url}/teams'
        params = {"league": league_id, "season": season}
        teams = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(teams.headers)
        teams_data = teams.json()["response"]

        teams_to_save = []
        for team in teams_data:
            team_id = team["team"]["id"]
            teams_to_save.append(team_id)

        return League(league_id, season, teams_to_save)

    def get_all_leagues(self):
        endpoint = f"{self.base_url}/leagues"
        params = {"type": "league"}
        leagues = get(endpoint, headers=self.base_headers, params=params)

        self.check_api_limits(leagues.headers)
        league_data = leagues.json()
        leagues_to_get = []
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["year"] > 2010:
                    leagues_to_get.append((league_id, season["year"]))
        return leagues_to_get

    def get_all_leagues_lineups(self):
        endpoint = f"{self.base_url}/leagues"
        params = {"type": "league"}
        leagues = get(endpoint, headers=self.base_headers, params=params)

        self.check_api_limits(leagues.headers)
        league_data = leagues.json()
        leagues_to_get = []
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["year"] > 2010 and season["coverage"]["fixtures"]["lineups"]:
                    leagues_to_get.append((league_id, season["year"]))
        return leagues_to_get

    def get_player_stats_leagues(self):
        endpoint = f"{self.base_url}/leagues"
        params = {"type": "league"}
        leagues = get(endpoint, headers=self.base_headers, params=params)

        self.check_api_limits(leagues.headers)
        league_data = leagues.json()
        leagues_to_get = []
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["year"] > 2010 and season["coverage"]["fixtures"]["statistics_players"]:
                    leagues_to_get.append((league_id, season["year"]))
        return leagues_to_get
    
    def get_all_leagues(self):
        endpoint = f"{self.base_url}/leagues"
        params = {"type": "league"}
        leagues = get(endpoint, headers=self.base_headers, params=params)

        self.check_api_limits(leagues.headers)
        league_data = leagues.json()
        leagues_to_get = []
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["current"] and season["coverage"]["fixtures"]["events"]:
                    leagues_to_get.append((league_id, season["year"]))
        return leagues_to_get

    def get_injury_leagues(self):
        endpoint = f"{self.base_url}/leagues"
        params = {"type": "league"}
        leagues = get(endpoint, headers=self.base_headers, params=params)

        self.check_api_limits(leagues.headers)
        league_data = leagues.json()
        leagues_to_get = []
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["year"] > 2010 and season["coverage"]["injuries"]:
                    leagues_to_get.append((league_id, season["year"]))
        return leagues_to_get

    def get_max_leagues(self):
        endpoint = f"{self.base_url}/leagues"
        params = {"type": "league"}
        leagues = get(endpoint, headers=self.base_headers, params=params)

        self.check_api_limits(leagues.headers)
        league_data = leagues.json()
        leagues_to_get = []
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["year"] > 2010 and season["coverage"]["injuries"] \
                   and season["coverage"]["fixtures"]["statistics_players"]:
                    leagues_to_get.append((league_id, season["year"]))
        return leagues_to_get

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
        leagues_to_get = []
        league_ids = []
        for league in league_data["response"]:
            league_id = league["league"]["id"]
            for season in league["seasons"]:
                if season["coverage"]["fixtures"]["events"] and season["year"] > 2010:
                    leagues_to_get.append((league_id, season["year"]))
                    if league_id not in league_ids:
                        print(league["league"]["name"])
                        league_ids.append(league_id)

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
        try:
            requests_left_day = int(headers["x-ratelimit-requests-remaining"])
            requests_left_min = int(headers["X-RateLimit-Remaining"])
        except Exception as e:
            requests_left_day = 1001
            requests_left_min = 101
            print(headers)
            print(e)

        if requests_left_min == 449:
            self.start_minute = time()
        else:
            if requests_left_day % 1000 == 0:
                print(f"{requests_left_day} requests left on daily plan")
            if requests_left_min % 50 == 0:
                print(f"{requests_left_min} requests left on minute limit")
            if requests_left_day < 50:
                raise RuntimeError("Daily API limit reached for API-Football. Please come back tomorrow")
            if requests_left_min < 3:
                print("Hit API Rate limit, waiting until end of minute")
                time_left = 60 - (time() - self.start_minute)
                sleep(time_left + 1)

            if time() - self.start_minute > 60:
                self.start_minute = time()

    def get_team_name(self, id):
        endpoint = f"{self.base_url}/teams"
        params = {"id": id}
        teams = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(teams.headers)
        return teams.json()["response"][0]["team"]["name"]

    def get_current_season(self, league_id):
        endpoint = f"{self.base_url}/leagues"
        params = {"id": league_id, "current": "true"}
        league = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(league.headers)
        try:
            return league.json()["response"][0]["seasons"][0]["year"]
        except:
            return None

    def get_current_season_injury(self, league_id):
        endpoint = f"{self.base_url}/leagues"
        params = {"id": league_id, "current": "true"}
        league = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(league.headers)
        try:
            season = league.json()["response"][0]["seasons"][0]
            if season["year"] > 2010 and season["coverage"]["fixtures"]["lineups"]:
                return True
        except:
            return False
        return False

    def get_h2h(self, team1_id, team2_id, league_id, season) -> List[H2H]:
        endpoint = f"{self.base_url}/fixtures/headtohead"
        params = {"h2h": f"{team1_id}-{team2_id}", "league": league_id, "season": season}
        h2h = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(h2h.headers)
        h2h = h2h.json()["response"]

        params = {"h2h": f"{team1_id}-{team2_id}", "league": league_id, "season": season - 1}
        h2h_last_season = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(h2h_last_season.headers)
        h2h_last_season = h2h_last_season.json()["response"]

        h2h_full = h2h + h2h_last_season
        returned_h2h = []
        for h2h in h2h_full:
            home_goals = h2h["score"]["fulltime"]["home"]
            away_goals = h2h["score"]["fulltime"]["away"]
            home_team = h2h["teams"]["home"]["id"]
            away_team = h2h["teams"]["away"]["id"]
            if home_goals > away_goals:
                result = "Home Win"
            elif away_goals > home_goals:
                result = "Away Win"
            else:
                result = "Draw"
            returned_h2h.append(H2H(result, home_team, home_goals, away_team, away_goals))
        return returned_h2h
    
    def get_player_stats(self, fixture_id: int) -> List[Player]:
        endpoint = f"{self.base_url}/fixtures/players"
        params = {"fixture": fixture_id}
        player_stats = get(endpoint, headers=self.base_headers, params=params)
        self.check_api_limits(player_stats.headers)
        try:
            if len(player_stats.json()["response"]) == 0:
                return False
        except:
            return False
        
        player_processed_stats = []
        for team in player_stats.json()["response"]:
            players = team["players"]
            team = team["team"]["id"]
            for player in players:
                player_id = player["player"]["id"]
                if player["statistics"][0]["games"]["minutes"] is None:
                    minutes = 0
                else:
                    minutes = player["statistics"][0]["games"]["minutes"]
                if minutes > 45:
                    started = True
                else:
                    started = False
                player_processed_stats.append(Player(player_id=player_id, team=team, minutes=minutes, started=started))
        return player_processed_stats
