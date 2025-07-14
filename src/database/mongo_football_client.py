from pymongo import MongoClient
from .match_collection import MatchCollection
from .league_collection import LeagueCollection
from .observation_collection import ObservationCollection
from .standing_collection import StandingCollection
from .odd_collection import OddsCollection
from .team_collection import TeamCollection
from .bet_collection import BetCollection


class MongoFootballClient:
    def __init__(self, url: str, test: bool = False):
        self.url = url
        self.mc = MongoClient(self.url)
        self.db = self.mc["football"]
        if test:
            col_prefix = "test_"
        else:
            col_prefix = ""
        self.matches = MatchCollection(self.db, f"{col_prefix}matches")
        self.leagues = LeagueCollection(self.db, f"{col_prefix}leagues")
        self.observations = ObservationCollection(self.db, f"{col_prefix}observations")
        self.standings = StandingCollection(self.db, f"{col_prefix}standings")
        self.odds = OddsCollection(self.db, f"{col_prefix}odds")
        self.teams = TeamCollection(self.db, f"{col_prefix}teams")
        self.bets = BetCollection(self.db, f"{col_prefix}bets")
