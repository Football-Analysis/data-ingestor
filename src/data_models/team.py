from dataclasses import dataclass


@dataclass
class Team:
    id: int
    name: str
    source: str

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "Team":
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return Team(**mongo_doc)

