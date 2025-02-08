from pymongo import MongoClient, DESCENDING
from ..data_models.league import League
from ..data_models.match import Match
from ..data_models.observation import Observation
from ..data_models.prediction import Prediction
from typing import List
from tqdm import tqdm


class MongoFootballClient:
    def __init__(self, url: str):
        self.url = url
        self.mc = MongoClient(self.url)
        self.football = self.mc["football"]
        self.match_collection = self.football["matches"]
        self.league_collection = self.football["leagues"]
        self.observation_collection = self.football["observations"]
        self.api_predictions_collection = self.football["apiPredictions"]
        

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

    def add_predictions(self, predictions: List[Prediction]):
        for prediction in predictions:
            self.api_predictions_collection.insert_one(prediction.__dict__)

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
        print("Casting all results as matches")
        matches = list(map(self.cast_mongo_to_match, cursor))
        for match in cursor:
            del match["_id"]
            matches.append(Match(**match))
        return matches
    
    def get_finished_matches(self) -> List[Match]:
        print("Querying all finished matches")
        cursor = self.match_collection.find({
            "result": {"$ne": "N/A"}
        })
        matches = []
        print("Casting all results as matches")
        matches = list(map(self.cast_mongo_to_match, cursor))
        for match in cursor:
            del match["_id"]
            matches.append(Match(**match))
        return matches
    
    def cast_mongo_to_match(self, match):
        del match["_id"]
        return Match(**match)
    
    def get_league(self, league_id: int, season:int) -> League:
        league = self.league_collection.find_one({
            "league_id": league_id,
            "season": season
        })
        if league is None:
            return False
        del league["_id"]
        return League(**league)
    
    def check_observation(self, match_id):
        obs = self.observation_collection.find_one({
            "match_id": match_id
        })
        if obs is None:
            return False
        del obs["_id"]
        return Observation(**obs)

    def cast_to_league(self, league):
        del league["_id"]
        return League(**league)
    
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
            del match["_id"]
            matches_to_return.append(Match(**match))
        
        if len(matches_to_return) < 5:
            return matches_to_return
        return matches_to_return[:5]

    
        



