from dataclasses import dataclass
from typing import List


@dataclass
class League:
    league_id: int
    season: int
    teams: dict

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "League":
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return League(**mongo_doc)
