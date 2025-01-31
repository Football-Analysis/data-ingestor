from src.ingestors.match_ingestor import ApiFootball
from src.database.mongo_client import MongoFootballClient
from src.data_models.league import League
from src.config import Config as conf
from src.utils.feature_engineering import engineer_all_features, create_standings
from tqdm import tqdm

if __name__ == "__main__":
    af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
    mfc = MongoFootballClient(conf.MONGO_URL)

    create_standings(39, 2014)
    #af.get_standings()
    # current_leagues = mfc.get_current_leagues(conf.CURRENT_SEASON)
    # for league in tqdm(current_leagues):
    #     games_to_update = af.get_seasons_matches(league, conf.CURRENT_SEASON)
    #     mfc.update_matches(games_to_update)

    #matches = mfc.get_matches()



    # leagues_to_get = af.get_leagues()
    # leagues = []
    # #print(leagues_to_get)
    # for league in tqdm(leagues_to_get):
    #     for season in leagues_to_get[league]:
    #          processed_league = af.get_teams_per_league(league_id=league, season=season)
    #          mfc.add_team_list(processed_league)

    #          processed_matches = af.get_seasons_matches(league_id=league, season=season)
    #          mfc.add_matches(processed_matches)

    # leagues_to_get = af.get_leagues()
    # leagues = []
    # for league in tqdm(leagues_to_get):
    #     for season in leagues_to_get[league]:
    #          processed_matches = af.get_seasons_matches(league_id=league, season=season)
    #          mfc.add_matches(processed_matches)


    # processed_matches = engineer_all_features()
    # print("Updating all matches")
    # mfc.update_matches(processed_matches)

    #league_name, teams = af.get_teams_per_league(39, 2024)
