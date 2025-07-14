from .collection import MongoCollection
from ..data_models.observation import Observation
from typing import Optional, List


class ObservationCollection(MongoCollection):
    def __init__(self, db, collection):
        super().__init__(db, collection)
        self.next_observations = db["next_observations"]

    def add_observation(self, observation: Observation) -> bool:
        """Adds an observation the the database

        Args:
            observation (Observation): The observatio nto add to the databse
        """
        try:
            self.col.insert_one(observation.__dict__)
            return True
        except:
            return False
        
    def update_observation(self, observation: Observation):
        """Udates an existing observation in mongo

        Args:
            observation (Observation): The observation to update with
        """
        query = {"match_id": observation.match_id}
        update_values = {"$set": observation.__dict__}
        self.col.update_one(query, update_values)

    def check_observation(self, match_id: str) -> Optional[Observation]:
        """Given a match ID, checks if an observation for that match exists

        Args:
            match_id (str): The match ID (date + home team)

        Returns:
           Optional[Observataion] : The Observation matching the match ID, none if no match
        """
        obs = self.col.find_one({
            "match_id": match_id
        })
        if obs is None:
            return None

        return Observation.from_mongo_doc(obs)

    def delete_next_observations(self):
        """Wipes the next observation collection
        """
        self.next_observations.delete_many({})

    def add_observations(self, observations: List[Observation], next_games=True):
        """Add an observation to the database

        Args:
            observations (List[Observation]): The list of observations
            next_games (bool, optional): Which collction to add it to. Defaults to True.
        """
        if next_games:
            col = self.next_observations
        else:
            col = self.col
        obs_to_add = list(map(lambda x: x.__dict__, observations))
        col.insert_many(obs_to_add)