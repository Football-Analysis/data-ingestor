from src.ingestors.odds_ingestor import OddsIngestor
from src.ingestors.match_ingestor import ApiFootball
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf

if __name__ == "__main__":
    # oi = OddsIngestor(base_url=conf.ODDS_API_URL, api_key=conf.ODDS_API_KEY)
    # oi.get_sports()

    af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
    matches = af.get_seasons_matches()
    print(matches[0].__dict__)

    mfc = MongoFootballClient(conf.MONGO_URL)
    mfc.add_matches(matches)
