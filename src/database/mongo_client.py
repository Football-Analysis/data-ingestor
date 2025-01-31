from pymongo import MongoClient
from ..data_models.league import League
from ..data_models.match import Match
from typing import List
from tqdm import tqdm


class MongoFootballClient:
    def __init__(self, url: str):
        self.url = url
        self.mc = MongoClient(self.url)
        self.football = self.mc["football"]
        self.match_collection = self.football["matches"]
        self.league_collection = self.football["leagues"]
        

    def add_team_list(self, league: League):
        """Saves a list of teams that belonged to a certain league into mongo

        Args:
            league (List[League])
        """
        self.league_collection.insert_one(league.__dict__)
        print("Added all leagues")


    def add_matches(self, matches: List[Match]):
        """Takes a list of Match objects and inserts them into the correct collection in mongo

        Args:
            matches (List[Match]): A list of processed matches
        """

        for match in matches:
            self.match_collection.insert_one(match.__dict__)
        print("Added all matches")

    def get_current_leagues(self, current_season):
        current_leagues = self.match_collection.distinct("league.id",{"season": current_season})
        return current_leagues

    def update_matches(self, matches: List[Match]):
        for match in matches:
            query = {"date": match.date, "home_team": match.home_team}
            update_values = {"$set": match.__dict__}
            self.match_collection.update_one(query , update_values)
        print("Updated all matches")

    def get_matches(self):
        football = self.mc["football"]
        collection = football["matches"]
        print("Querying all matches")
        cursor = collection.find({})
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
    
    def get_teams_in_season(self, league_id: int, season: int):
        league = self.league_collection.find_one({
            "league_id": league_id,
            "season": season
        })

        return league["teams"]
    
    def get_matches_in_gameweek(self, league_id: int, season: int, game_week: str) -> List[Match]:
        matches = self.match_collection.find({
            "league.id": league_id,
            "season": season,
            "game_week": game_week
        })

        weeks_matches = []
        for match in matches:
            del match["_id"]
            weeks_matches.append(Match(**match))

        return weeks_matches
    
    def get_gameweeks_for_season(self, league_id, season):
        gameweeks = self.match_collection.distinct("game_week",
                                                   {"league.id": league_id,
                                                    "season": season})
        return gameweeks

