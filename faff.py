from src.utils.feature_engineering import create_standings, update_table, create_obs_from_match, update_obs, calc_h2h
from src.database.mongo_football_client import MongoFootballClient
from src.config import Config as conf
from src.ingestors.betfair_ingestor import BetfairClient
from src.ingestors.match_ingestor import ApiFootball
from src.data_models.team import Team
from tqdm import tqdm
from src.data_models.match import Match
from time import sleep, time

mfc = MongoFootballClient(conf.MONGO_URL)
af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)


matches = mfc.get_finished_matches()

observations = []

for match in tqdm(matches):
    obs = create_obs_from_match(match)
    if obs is not None:
        mfc.observations.add_observation(obs)
