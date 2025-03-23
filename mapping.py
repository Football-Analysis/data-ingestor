from src.utils.feature_engineering import map_ids, map_odd_ids
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf
from src.ingestors.betfair_ingestor import BetfairClient
from src.ingestors.match_ingestor import ApiFootball
from src.data_models.team import Team
from tqdm import tqdm

mfc = MongoFootballClient(conf.MONGO_URL)
af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)
#map_ids()
map_odd_ids()