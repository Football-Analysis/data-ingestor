from .collection import MongoCollection
from ..data_models.standing import Standing
from pymongo import DESCENDING
from typing import List, Optional


class StandingCollection(MongoCollection):
    def standing_exists(self, league_id: int, season: int, date=None):
        """Checks if a standing exists

        Args:
            league_id (int): The league id to check against
            season (int): The seasons to chec kagainst
            date (_type_, optional): The date to check against. Defaults to None.
        """
        query_filter = {"league_id": league_id, "season": season}

        if date is not None:
            query_filter["date"] = date

        standing = self.col.find_one(query_filter)
        if standing is None:
            return False
        else:
            return True

    def delete_standings(self):
        """Wipes the standings database
        """
        self.col.delete_many({})

    def get_last_standings(self, league_id: int, season: int, date: str) -> List[Standing]:
        """Get the last standings of a given league

        Args:
            league_id (int): League ID to check against
            season (int): Season ID to check against
            date (str): The date to check against

        Returns:
            List[Standing]: The list of standings for the league
        """
        gen_filter = {
            "league_id": league_id,
            "season": season,
            "date": {"$lte": date}
        }

        standings = self.col.find(gen_filter).sort("date", DESCENDING)

        standings_to_return = []
        for standing in standings:
            standings_to_return.append(Standing.from_mongo_doc(standing))

        return standings_to_return

    def add_standing(self, standing: Standing):
        """Adds a standing to the database

        Args:
            standing (Standing): The standing to add
        """
        self.col.insert_one(standing.__dict__)

    def get_standings(self, date, league_id, season) -> Optional[Standing]:
        """Gets a specific standing from the database, returns None if no match

        Args:
            date (str): Tehd ate to match on 
            league_id (int): The league id to match on 
            season (int): The season to match on

        Returns:
            Optional[Standing]: The matched standing, None if no match
        """
        standing = self.col.find_one({"date": date, "league_id": league_id, "season": season})
        if standing is None:
            return None
        else:
            return Standing.from_mongo_doc(standing)
        
    def get_standings_from_team_date(self, league_id: int, season: int, date: str) -> Standing:
        """Get the standing from a specific point in time

        Args:
            league_id (int): League ID to check against
            season (int): Season ID to check against
            date (str): The date to check against

        Returns:
            Standing: The returned standing
        """
        standings = self.col.find({
            "league_id": league_id,
            "season": season,
            "date": {"$lt": date}
        }).sort("date", DESCENDING)

        standing_to_return = None
        for standing in standings:
            if standing_to_return is None:
                standing_to_return = Standing.from_mongo_doc(standing)
            return standing_to_return