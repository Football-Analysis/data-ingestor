from src.utils.feature_engineering import create_standings, update_table, create_obs_from_match, update_obs, calc_h2h
from src.database.mongo_football_client import MongoFootballClient
from src.config import Config as conf
from src.ingestors.betfair_ingestor import BetfairClient
from src.ingestors.match_ingestor import ApiFootball
from src.data_models.team import Team
from tqdm import tqdm
from src.data_models.match import Match
from time import sleep, time

mfc = MongoFootballClient(conf.MONGO_URL, test=True)
af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)


matches = mfc.matches.get_matches()

# observations = []

# for match in tqdm(matches):
#     match_id = match.date + "-" + str(match.home_team)
#     exists = mfc.observations.check_observation(match_id)
#     if exists is None:
#         exists = mfc.player_stats.check_exists(match.home_team, match.date)
#         if exists:
#             obs = create_obs_from_match(match, True)
#             if obs is not None:
#                 mfc.observations.add_observation(obs)
#all_leagues = af.get_all_leagues_lineups()


# for league in tqdm(all_leagues):
#     # mfc.player_stats.season_exists(league[0], league[1])
#     create_standings(league[0], league[1], test=True)

for single_match in tqdm(matches):
    # lineup_exists = mfc.lineups.check_exists(single_match.fixture_id)
    standing_exists = mfc.standings.standing_exists(single_match.league["id"], single_match.season, single_match.date)
    stats_exist = mfc.player_stats.check_exists(single_match.home_team, single_match.date)
    obs_exist = mfc.observations.check_observation(f"{single_match.date}-{single_match.home_team}")
    if obs_exist:
        continue
    if stats_exist and standing_exists:
        obs = create_obs_from_match(single_match, True)
        mfc.observations.add_observation(obs)

    

