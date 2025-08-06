from .collection import MongoCollection
from ..data_models.bankroll import Bankroll
from typing import List, Optional
from pymongo import DESCENDING, ASCENDING
from datetime import datetime, timedelta
from ..config import Config as conf


class BankrollCollection(MongoCollection):
    def __init__(self, db, collection):
        super().__init__(db, collection)

    def check_bankroll(self):
        current_bankroll = self.col.find().sort("date", DESCENDING).limit(1)
        bankroll_to_return = next(current_bankroll, None)
        if bankroll_to_return is not None:
            try:
                return Bankroll.from_mongo_doc(bankroll_to_return)
            except:
                raise RuntimeError(f"{bankroll_to_return} could not be cast to a bankroll type")
        return Bankroll(date=datetime.now(),
                        bankroll=1000.00,
                        amount_in_play=0,
                        liquid_funds=1000.00)
    
    def update_bankroll(self, bankroll: Bankroll) -> bool:
        self.col.insert_one(bankroll.__dict__)
        return True
