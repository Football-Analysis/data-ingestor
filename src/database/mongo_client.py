from pymongo import MongoClient
from ..data_models.match import Match
from typing import List
import pandas as pd
from tqdm import tqdm


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

        for match in tqdm(matches):
            collection.insert_one(match.__dict__)
        print("Added all matches")

    def update_matches(self, matches: List[Match]):
        football = self.mc["football"]
        collection = football["matches"]

        for match in tqdm(matches):
            query = {"date": match.date, "home_team": match.home_team}
            update_values = {"$set": match.__dict__}
            collection.update_one(query , update_values)
        print("Updated all matches")

    def get_matches(self):
        football = self.mc["football"]
        collection = football["matches"]
        print("Querying all matches")
        cursor = collection.find({})
        matches = []
        print("Casting all results as matches")
        matches = list(map(self.cast_mongo_to_match, cursor))
        for match in cursor:
            del match["_id"]
            matches.append(Match(**match))
        return matches
    
    def cast_mongo_to_match(self, match):
        del match["_id"]
        return Match(**match)