from src.ingestors.match_ingestor import ApiFootball
from src.config import Config as conf
from tqdm import tqdm
from src.database.mongo_football_client import MongoFootballClient
from src.utils.feature_engineering import create_standings, create_obs_from_match
from src.utils.ingest_utils import update_bets
from src.database.match_collection import MatchCollection
from pymongo import MongoClient

#update_bets()
mfc = MongoFootballClient(conf.MONGO_URL)

#mfc.observations.check_observation("2011-08-05T18:00:00+00:00-1299")

mfc.standings.standing_exists(39, 2024, "2021-05-20T19:00:00+00:00")


# af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
# mfc = MongoFootballClient(conf.MONGO_URL)

# no_player_leagues = af.get_all_leagues()
# player_leagues = af.get_player_stats_leagues()
# injury_leagues = af.get_injury_leagues()
# everything_leagues = af.get_max_leagues()
# lineup_leagues = af.get_all_leagues_lineups()
# print(len(no_player_leagues))
# print(len(player_leagues))
# print(len(injury_leagues))
# print(len(everything_leagues))
# print(len(lineup_leagues))


# matches = mfc.get_finished_matches(True)

# for match in tqdm(matches):
#     obs = create_obs_from_match(match)
#     if obs is not None:
#         mfc.add_observation(obs, True)

# for league in tqdm(lineup_leagues):
#     create_standings(league[0], league[1], test=True)


# for league in tqdm(lineup_leagues):
#     seasons_matches = af.get_seasons_matches(league[0], league[1])
#     mfc.add_matches(seasons_matches, True)



# leagues = mfc.get_list_of_leagues()
# print(len(leagues))
# injuries = 0
# for league in tqdm(leagues):
#     injury = af.get_current_season_injury(league)
#     # if injury is not None:
#     #     if injury in (2024, 2025):
#     #         injuries += 1
#     if injury:
#         injuries += 1

# print(injuries)


# total_matches = 0
# for league in tqdm(everything_leagues):
#     matches = af.get_seasons_matches(league[0], league[1])
#     total_matches += len(matches)

# print(total_matches)