from src.utils.feature_engineering import create_standings, update_table, create_obs_from_match, update_obs
from src.database.mongo_client import MongoFootballClient
from src.config import Config as conf
from src.ingestors.betfair_ingestor import BetfairClient
from src.ingestors.match_ingestor import ApiFootball
from src.data_models.team import Team
from tqdm import tqdm
from src.data_models.match import Match
from time import sleep


def update_matches_and_create_next_obs():
    mfc = MongoFootballClient(conf.MONGO_URL)
    af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)

    leagues = mfc.get_list_of_leagues()
    all_leagues = af.get_all_leagues()

    print("Getting new and updating all league info")
    for league in tqdm(all_leagues):
        exists = mfc.get_league(league[0], league[1])
        if not exists:
            league_to_save = af.get_teams_per_league(league[0], league[1])
            mfc.add_league(league_to_save)
        elif exists and len(exists.teams) == 0:
            league_to_save = af.get_teams_per_league(league[0], league[1])
            mfc.update_league(league_to_save)

    print("Adding new, and updating all matches in the current season")
    for league in tqdm(leagues):
        season = af.get_current_season(league)
        matches = af.get_seasons_matches(league, season)
        for match in matches:
            if mfc.match_exists(match.league["id"], match.season, match.home_team, match.away_team):
                mfc.update_matches([match])
            else:
                mfc.add_matches([match])

    print("Updating the standings for all leagues")
    for league in tqdm(leagues):
        season = af.get_current_season(league)
        create_standings(league, season)

    print("Refreshing new matches and observations")
    mfc.delete_next_matches()
    mfc.delete_next_observations()
    next_matches = []
    for league in tqdm(leagues):
        season = af.get_current_season(league)
        gameweek = mfc.get_next_gameweek(league, season)
        if gameweek is not None:
            next_matches_leagues = mfc.get_next_matches(gameweek, season, league)
            next_matches.extend(next_matches_leagues)
    mfc.add_next_matches(next_matches)

    observations = []

    for match in tqdm(next_matches):
        obs = create_obs_from_match(match)
        if obs is not None:
            observations.append(obs)
        if len(observations) == 1000:
            print("Adding 1000 observations")
            mfc.add_observations(observations, True)
            observations = []
    mfc.add_observations(observations, True)

    print("Ingest of latest data completed, new observations succesfully created")
