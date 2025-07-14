from .collection import MongoCollection
from ..data_models.league import League
from typing import List


class LeagueCollection(MongoCollection):
    def add_league(self, league: League):
        """Saves a list of teams that belonged to a certain league into mongo

        Args:
            league (List[League])
        """
        self.league_collection.insert_one(league.__dict__)

    def update_league(self, league: League):
        """Saves a list of teams that belonged to a certain league into mongo

        Args:
            league (List[League])
        """
        query = {"league_id": league.league_id, "season": league.season}
        update_values = {"$set": league.__dict__}
        self.league_collection.update_one(query, update_values)

    def get_league(self, league_id: int, season: int) -> League:
        """Given a season and league ID , return the league info,
           including which teams are in the league

        Args:
            league_id (int): The league ID wanted
            season (int): The season wanted

        Returns:
            League: The league info matching the filter
        """
        league = self.col.find_one({
            "league_id": league_id,
            "season": season
        })
        if league is None:
            return False
        return League.from_mongo_doc(league)
    
    def get_all_leagues(self) -> List[League]:
        """Returns all leagues that are held wthin the database

        Returns:
            List[League]: The list od returned leagues
        """
        leagues = self.col.find()

        leagues_to_return = []
        for league in leagues:
            leagues_to_return.append(League.from_mongo_doc(league))

        return leagues_to_return
    
    def get_list_of_leagues(self) -> List[int]:
        """GEt the full list of league IDs in the database

        Returns:
            List[int]: The full list of league ids
        """
        leagues = self.col.distinct("league_id")
        return leagues