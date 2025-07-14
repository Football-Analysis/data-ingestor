from src.ingestors.match_ingestor import ApiFootball
from src.database.mongo_football_client import MongoFootballClient
from src.data_models.league import League
from src.config import Config as conf
from src.utils.feature_engineering import engineer_all_features, create_training_data
from time import sleep
import schedule
from src.utils.ingest_utils import update_matches_and_create_next_obs, update_bets
from pytz import timezone

if __name__ == "__main__":
    af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
    mfc = MongoFootballClient(conf.MONGO_URL)

    schedule.every().day.at("00:01", timezone("GMT")).do(update_matches_and_create_next_obs)
    schedule.every().hour.do(update_bets)

    print("Starting scheduled jobs")
    update_matches_and_create_next_obs()
    update_bets()
    while True:
        schedule.run_pending()
        sleep(1)