from src.ingestors.match_ingestor import ApiFootball
from src.database.mongo_client import MongoFootballClient
from src.data_models.league import League
from src.config import Config as conf
from src.utils.feature_engineering import engineer_all_features, create_training_data
from tqdm import tqdm

if __name__ == "__main__":
    af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
    mfc = MongoFootballClient(conf.MONGO_URL)
    #af.get_form()
    #create_training_data()
    # current_leagues = mfc.get_current_leagues(conf.CURRENT_SEASON)
    # for league in tqdm(current_leagues):
    #     games_to_update = af.get_seasons_matches(league, conf.CURRENT_SEASON)
    #     mfc.update_matches(games_to_update)

    #matches = mfc.get_matches()



    leagues_to_get = af.get_leagues()
    print(len(leagues_to_get))

#     matches = mfc.get_matches()
#     print(len(matches))
#     print(matches[0])
    for league in tqdm(leagues_to_get):
        matches = af.get_seasons_matches(league[0], league[1])
        mfc.update_matches(matches)

#     for league in leagues_to_get:
#         if league[0] == 39:
#             print(league)
#     for league in tqdm(leagues_to_get):
#         check_league = mfc.get_league(league[0], league[1])
#         if not check_league:
#             processed_league = af.get_teams_per_league(league_id=league[0], season=league[1])
#             mfc.add_team_list(processed_league)
#         else:
#             print(f"Skipping league {league[0]}, season {league[1]} - already in db")


        #processed_matches = af.get_seasons_matches(league_id=league, season=season)
        #mfc.add_matches(processed_matches)

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
