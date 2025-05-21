from dataclasses import dataclass


@dataclass
class Standing:
    league_id: int
    season: int
    date: str
    standings: dict

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "Standing":
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return Standing(**mongo_doc)
