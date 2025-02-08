from src.ingestors.match_ingestor import ApiFootball
from src.database.mongo_client import MongoFootballClient
from src.data_models.league import League
from src.config import Config as conf
from src.utils.feature_engineering import engineer_all_features, create_training_data
from tqdm import tqdm

if __name__ == "__main__":
    af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
    mfc = MongoFootballClient(conf.MONGO_URL)
    