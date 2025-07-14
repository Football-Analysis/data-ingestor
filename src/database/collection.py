from abc import ABC
from pymongo.database import Database


class MongoCollection(ABC):
    def __init__(self, db: Database, collection):
        self.col = db[collection]
