from dataclasses import dataclass
from typing import Any


@dataclass
class Player:
    player_id: str
    team: int
    minutes: int
    started: bool

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "Player":
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return Player(**mongo_doc)
