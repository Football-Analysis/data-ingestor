from dataclasses import dataclass
from typing import List


@dataclass
class H2H:
    result: str
    home_team: int
    home_goals: int
    away_team: int
    away_goals: int

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "H2H":
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return H2H(**mongo_doc)