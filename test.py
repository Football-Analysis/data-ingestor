from src.utils.feature_engineering import map_ids, map_odd_ids
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf
from src.ingestors.betfair_ingestor import BetfairClient
from src.ingestors.match_ingestor import ApiFootball
from src.data_models.team import Team

mfc = MongoFootballClient(conf.MONGO_URL)
af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)
#map_ids()
#map_odd_ids()
#team = mfc.get_team_from_name("Everton")
#print(team)
# matches = mfc.get_finished_matches()
# print(matches[0])

#bfc = BetfairClient("" ,conf.BETFAIR_API_KEY)

#bfc.get_downloaded_data()

teams = mfc.get_all_teams_from_leagues()
for team_id in teams:
    team_name = af.get_team_name(team_id)
    team_to_save = Team(team_id, team_name, "af")
    mfc.add_team(team_to_save)