from dataclasses import dataclass
from typing import List


@dataclass
class Lineup:
    fixture_id: int
    date: str
    home_team: int
    home_lineup: List[int]
    away_team: int
    away_lineup: List[int]

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "Lineup":
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return Lineup(**mongo_doc)
