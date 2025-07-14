from .collection import MongoCollection
from ..data_models.odds import Odds
from typing import List


class OddsCollection(MongoCollection):
    def check_odd(self, date: str, home: int) -> bool:
        """Checks if an odds exists for a givem match

        Args:
            date (str): The datetime the match happened on
            home (int): The home teams ID

        Returns:
            bool: If the odd exists
        """
        result = self.col.find_one({
            "date": date,
            "home_team": home
        })
        if result is not None:
            return True
        return False

    def add_odd(self, odd: Odds):
        """Adds an odd to the database

        Args:
            odd (Odds): The odds to add
        """
        # TODO: Checkif the odd already exists
        self.col.insert_one(odd.__dict__)

    def update_odd(self, odd: Odds, home_team=None):
        """Given an odd, update it in the database

        Args:
            odd (Odds): The odd to update
            home_team (int, optional): The home team to check against. Defaults to None.
        """
        if home_team is None:
            query = {"date": odd.date, "home_team": odd.home_team}
        else:
            query = {"date": odd.date, "home_team": home_team}
        update_values = {"$set": odd.__dict__}
        self.col.update_one(query, update_values)

    def get_betfair_team_names(self) -> List[int]:
        """Gets all names of the saved betfair names so they can later
           be mapped to api football IDs

        Returns:
            List[int]: A ist of team names
        """
        home_teams = self.col.distinct("home_team")
        away_team = self.col.distinct("away_team")
        return list(set(home_teams).union(away_team))

    def get_odds(self, processed=False) -> List[Odds]:
        """Gets the list of odds that exist

        Args:
            processed (bool, optional): Only return odds where both teams have
            been successfuly mapped to an ID. Defaults to False.

        Returns:
            List[Odds]: A list of returned odds
        """
        if processed:
            mongo_filter = {"$or": [
                {"home_team": {"$type": 2}},
                {"away_team": {"$type": 2}}]}
        else:
            mongo_filter = {}
        odds = self.col.find(mongo_filter)
        odds_to_return = []
        for odd in odds:
            odds_to_return.append(Odds.from_mongo_doc(odd))
        return odds_to_return

    def del_odd(self, date: str, home_team: int):
        """Deletes an odd

        Args:
            date (str): The date of the match
            home_team (int): The home teams id
        """
        self.col.delete_one({"date": date, "home_team": home_team})
