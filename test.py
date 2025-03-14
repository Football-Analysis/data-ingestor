from src.utils.feature_engineering import map_id
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf

mfc = MongoFootballClient(conf.MONGO_URL)
#map_id("Newcastle")

matches = mfc.get_finished_matches()
print(matches[0])