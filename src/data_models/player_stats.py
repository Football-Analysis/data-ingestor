from dataclasses import dataclass


@dataclass
class PlayerStats:
    player_id: str
    team: int
    date: str
    played: int
    played_ppg: int
    not_played: int
    not_played_ppg: int

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "PlayerStats":
        print("PRINTING MONGO DOC")
        print(mongo_doc)
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return PlayerStats(**mongo_doc)
