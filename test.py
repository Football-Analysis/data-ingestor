from src.utils.feature_engineering import map_ids, map_odd_ids
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf
from src.ingestors.betfair_ingestor import BetfairClient

mfc = MongoFootballClient(conf.MONGO_URL)
#map_ids()
map_odd_ids()
#team = mfc.get_team_from_name("Everton")
#print(team)
# matches = mfc.get_finished_matches()
# print(matches[0])


#bfc = BetfairClient("" ,conf.BETFAIR_API_KEY)

#bfc.get_downloaded_data()