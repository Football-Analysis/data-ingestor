from src.ingestors.odds_ingestor import OddsIngestor
from src.ingestors.match_ingestor import ApiFootball
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf

if __name__ == "__main__":
    af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
    mfc = MongoFootballClient(conf.MONGO_URL)

    for season in range(2014,2025):
        print(f"Getting matches for season {season}")
        matches = af.get_seasons_matches(season=season)
        mfc.add_matches(matches)

