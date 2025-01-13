from src.ingestors.match_ingestor import ApiFootball
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf
from src.utils.feature_engineering import engineer_all_features

if __name__ == "__main__":
    af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
    mfc = MongoFootballClient(conf.MONGO_URL)

    # leagues_to_get = af.get_leagues()
    # for league in leagues_to_get:
    #     for season in leagues_to_get[league]:
    #         print(f"Getting matches for league {league}, season {season}")
    #         matches = af.get_seasons_matches(league_id=league, season=season)
    #         mfc.add_matches(matches)
    
    processed_matches = engineer_all_features()
    print("Updating all matches")
    mfc.update_matches(processed_matches)
