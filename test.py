from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf
from src.utils.feature_engineering import create_local_form
from src.data_models.match import Match
from src.ingestors.match_ingestor import ApiFootball
from src.ingestors.odds_ingestor import OddsIngestor
from datetime import datetime, timedelta
from src.data_models.odds import Odds
from src.data_models.team import Team

mfc = MongoFootballClient(conf.MONGO_URL)
af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)
oa = OddsIngestor(conf.ODDS_API_URL, conf.ODDS_API_KEY)

# request_total = 0
# for season in conf.odds_seasons:
#     query_date = datetime.strptime(conf.odds_dates[season]["start"], "%Y-%m-%dT%H:%M:%SZ")
#     end_date = datetime.strptime(conf.odds_dates[season]["end"], "%Y-%m-%dT%H:%M:%SZ")
#     total=0
#     while query_date < end_date:
#         query_date_string = query_date.strftime("%Y-%m-%dT%H:%M:%SZ")
#         odds = oa.get_odds_from_date("soccer_epl", query_date_string)

#         for odd in odds:
#             exists = mfc.check_odd(odd.date, odd.home_team)
#             if not exists:
#                 mfc.add_odd(odd)
#             else:
#                 mfc.update_odd(odd)
            
#         query_date = query_date + timedelta(days=7)
#         total+=1
#     request_total+=total

# print(request_total)


teams = mfc.get_all_teams()
for team_id in teams:
    team_name = af.get_team_name(team_id)
    team_to_save = Team(team_id, team_name)
    mfc.add_team(team_to_save)