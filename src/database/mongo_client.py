from pymongo import MongoClient, DESCENDING
from ..data_models.league import League
from ..data_models.match import Match
from ..data_models.observation import Observation
from ..data_models.odds import Odds
from typing import List
from tqdm import tqdm
from ..data_models.team import Team


class MongoFootballClient:
    def __init__(self, url: str):
        self.url = url
        self.mc = MongoClient(self.url)
        self.football = self.mc["football"]
        self.match_collection = self.football["matches"]
        self.league_collection = self.football["leagues"]
        self.observation_collection = self.football["observations"]
        self.api_predictions_collection = self.football["apiPredictions"]
        self.odds_collection = self.football["odds"]
        self.team_collection = self.football["teams"]
        

    def add_team_list(self, league: League):
        """Saves a list of teams that belonged to a certain league into mongo

        Args:
            league (List[League])
        """
        self.league_collection.insert_one(league.__dict__)
        print("Added all leagues")

    def add_observation(self, observation: Observation):
        self.observation_collection.insert_one(observation.__dict__)

    def update_observation(self, observation: Observation):
        query = {"match_id": observation.match_id}
        update_values = {"$set": observation.__dict__}
        self.observation_collection.update_one(query , update_values)

    def add_matches(self, matches: List[Match]):
        """Takes a list of Match objects and inserts them into the correct collection in mongo

        Args:
            matches (List[Match]): A list of processed matches
        """

        for match in matches:
            self.match_collection.insert_one(match.__dict__)

    def get_current_leagues(self, current_season):
        current_leagues = self.match_collection.distinct("league.id",{"season": current_season})
        return current_leagues

    def update_matches(self, matches: List[Match]):
        for match in matches:
            query = {"date": match.date, "home_team": match.home_team}
            update_values = {"$set": match.__dict__}
            self.match_collection.update_one(query , update_values)
        print("Updated all matches")

    def get_matches(self) -> List[Match]:
        print("Querying all matches")
        cursor = self.match_collection.find({})
        matches = []
        for match in cursor:
            matches.append(Match(**match))
        return matches
    
    def get_finished_matches(self) -> List[Match]:
        print("Querying all finished matches")
        cursor = self.match_collection.find({
            "result": {"$ne": "N/A"}
        })
        matches = []
        for match in cursor:
            matches.append(Match.from_mongo_doc(match))
        return matches
    
    
    def get_league(self, league_id: int, season:int) -> League:
        league = self.league_collection.find_one({
            "league_id": league_id,
            "season": season
        })
        if league is None:
            return False
        return League.from_mongo_doc(league)
    
    def check_observation(self, match_id):
        obs = self.observation_collection.find_one({
            "match_id": match_id
        })
        if obs is None:
            return False
        return Observation.from_mongo_doc(obs)
    
    def get_last_5_games(self, league: int, season: int, team: int, game_week: int, home: bool = True) -> List[Match]:
        gen_filter = {
            "league.id": league,
            "season": season,
            "game_week": {"$lt": game_week}
        }
        if home:
            gen_filter["home_team"] = team
        else:
            gen_filter["away_team"] = team

        matches = self.match_collection.find(gen_filter).sort("game_week", DESCENDING)

        matches_to_return = []
        for match in matches:
            matches_to_return.append(Match.from_mongo_doc(match))
        
        if len(matches_to_return) < 5:
            return matches_to_return
        return matches_to_return[:5]
    
    def check_odd(self, date, home):
        result = self.odds_collection.find_one({
            "date": date,
            "home_team": home
        })
        if result is not None:
            return True
        return False
    
    def get_all_teams(self):
        cursor = self.team_collection.find()
        all_teams = []
        for team in cursor:
            all_teams.append(Team.from_mongo_doc(team))
        return list(all_teams)
    
    def get_af_teams(self) -> List[Team]:
        cursor = self.team_collection.find({"source": "af"})
        all_teams = []
        for team in cursor:
            del team["_id"]
            all_teams.append(Team(**team))
        return all_teams
    
    def check_oa_team(self, name) -> bool:
        team = self.team_collection.find_one({"source": "oa",
                                            "name": name})
        if team is not None:
            return True
        return False

    def get_oa_id(self, name):
        team = self.team_collection.find_one({"source": "oa",
                                              "name": name})
        return team["id"]

    def add_team(self, team):
        self.team_collection.insert_one(team.__dict__)

    def add_odd(self, odd: Odds):
        self.odds_collection.insert_one(odd.__dict__)

    def update_odd(self, odd: Odds):
        query = {"date": odd.date, "home_team": odd.home_team}
        update_values = {"$set": odd.__dict__}
        self.odds_collection.update_one(query , update_values)

    
        



