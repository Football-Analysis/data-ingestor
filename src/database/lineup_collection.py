from .collection import MongoCollection
from ..data_models.lineup import Lineup
from typing import List, Optional
from pymongo import DESCENDING, ASCENDING
from datetime import datetime, timedelta
from ..config import Config as conf


class LineupCollection(MongoCollection):
    def add_lineup(self, lineup: Lineup):
        self.col.insert_one(lineup.__dict__)

    def check_exists(self, fixture_id: int) -> bool:
        lineup = self.col.find_one({"fixture_id": fixture_id})
        if lineup is None:
            return False
        return True
    
    def get_lineups(self, fixture_id: int) -> Lineup:
        #print(f"Getting lineup for {fixture_id}")
        lineup = self.col.find_one({"fixture_id": fixture_id})
        #print(lineup)
        if lineup is None:
            return None
        return Lineup.from_mongo_doc(lineup)

    

