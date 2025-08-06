from .collection import MongoCollection
from ..data_models.player_stats import PlayerStats
from pymongo import DESCENDING
from typing import List, Optional


class PlayerStatsCollection(MongoCollection):
    def get_player_stats(self, player_id: int, team_id: int, season: int, date: str) -> PlayerStats:
        stats = self.col.find({"player_id": player_id,
                               "team": team_id,
                               "season": season,
                               "date": {"$lt": date}}).sort("date", DESCENDING).limit(1)

        stat_to_return = next(stats, None)
        if stat_to_return is not None:
            try:
                return PlayerStats.from_mongo_doc(stat_to_return)
            except:
                print(stat_to_return)
        return None

    def add_player_stats(self, stats):
        self.col.insert_one(stats.__dict__)

    def get_non_played_players(self, played_players, team_id, season):
        players = self.col.distinct("player_id", {"team": team_id, "season": season})
        didnt_play = set(played_players) ^ set(players)
        return didnt_play
    
    def check_exists(self, team_id: int, date: str):
        stats = self.col.find_one({"team": team_id,
                                   "date": date})
        
        if stats is None:
            return False
        return True

    def season_exists(self, league_id, season) -> bool:
        pass  
