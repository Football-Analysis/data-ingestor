from pymongo import MongoClient
from .match_collection import MatchCollection
from .league_collection import LeagueCollection
from .observation_collection import ObservationCollection
from .standing_collection import StandingCollection
from .odd_collection import OddsCollection
from .team_collection import TeamCollection
from .bet_collection import BetCollection
from .player_stats_collection import PlayerStatsCollection
from .lineup_collection import LineupCollection
from .bankroll_collection import BankrollCollection


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
        self.leagues = LeagueCollection(self.db, f"leagues")
        self.observations = ObservationCollection(self.db, f"{col_prefix}observations")
        self.standings = StandingCollection(self.db, f"{col_prefix}standings")
        self.odds = OddsCollection(self.db, "odds")
        self.teams = TeamCollection(self.db, f"{col_prefix}teams")
        self.bets = BetCollection(self.db, "bets")
        self.player_stats = PlayerStatsCollection(self.db, f"{col_prefix}player_stats")
        self.lineups = LineupCollection(self.db, f"{col_prefix}lineups")
        self.bankroll = BankrollCollection(self.db, "bankroll")
