from .collection import MongoCollection
from ..data_models.bet import Bet
from typing import List


class BetCollection(MongoCollection):
    def get_bets_no_result(self) -> List[Bet]:
        """Returns a list of bets that have been placed that have no result for

        Returns:
            List[Bet]: List of no result bets
        """
        bets = self.col.find({"result": {"$exists": False}})

        bets_to_check = []
        for bet in bets:
            bets_to_check.append(Bet.from_mongo_doc(bet))

        return bets_to_check

    def update_bet(self, bet: Bet):
        """Update a bet in the databse

        Args:
            bet (Bet): The updaed bet to overwrite
        """
        query = {"date": bet.date, "home_team": bet.home_team}
        update_values = {"$set": bet.__dict__}
        self.col.update_one(query, update_values)
