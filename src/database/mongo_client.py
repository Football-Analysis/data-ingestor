from pymongo import MongoClient
from ..data_models.match import Match
from typing import List


class MongoFootballClient:
    def __init__(self, url: str):
        self.url = url
        self.mc = MongoClient(self.url)

    def add_matches(self, matches: List[Match]):
        """Takes a list of Match objects and inserts them into the correct collection in mongo

        Args:
            matches (List[Match]): A list of processed matches
        """
        football = self.mc["football"]
        collection = football["matches"]

        for match in matches:
            collection.insert_one(match.__dict__)
        print("Added all matches")
