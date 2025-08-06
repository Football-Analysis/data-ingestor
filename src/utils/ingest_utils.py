from src.utils.feature_engineering import create_standings, create_obs_from_match
from src.database.mongo_football_client import MongoFootballClient
from src.config import Config as conf
from src.ingestors.match_ingestor import ApiFootball
from src.data_models.bet import Bet
from tqdm import tqdm
from datetime import datetime


def update_matches_and_create_next_obs():
    mfc = MongoFootballClient(conf.MONGO_URL)
    af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)

    leagues = mfc.leagues.get_list_of_leagues()
    all_leagues = af.get_all_leagues()

    # print("Getting new and updating all league info")
    # for league in tqdm(all_leagues):
    #     exists = mfc.leagues.get_league(league[0], league[1])
    #     if not exists:
    #         league_to_save = af.get_teams_per_league(league[0], league[1])
    #         mfc.leagues.add_league(league_to_save)
    #     elif exists and len(exists.teams) == 0:
    #         league_to_save = af.get_teams_per_league(league[0], league[1])
    #         mfc.leagues.update_league(league_to_save)

    # print("Adding new, and updating all matches in the current season")
    # for league in tqdm(leagues):
    #     season = af.get_current_season(league)
    #     matches = af.get_seasons_matches(league, season)
    #     for match in matches:
    #         if mfc.matches.match_exists(match.league["id"], match.season, match.home_team, match.away_team):
    #             mfc.matches.update_matches([match])
    #         else:
    #             mfc.matches.add_matches([match])

    # print("Updating the standings for all leagues")
    # for league in tqdm(leagues):
    #     season = af.get_current_season(league)
    #     create_standings(league, season)

    # print("Refreshing new matches and observations")
    # mfc.matches.delete_next_matches()
    # mfc.observations.delete_next_observations()
    next_matches = []
    next_matches_leagues = mfc.matches.get_next_matches()
    next_matches.extend(next_matches_leagues)
    mfc.matches.add_next_matches(next_matches)

    observations = []

    for match in tqdm(next_matches):
        obs = create_obs_from_match(match)
        if obs is not None:
            observations.append(obs)
        if len(observations) == 1000:
            print("Adding 1000 observations")
            mfc.observations.add_observations(observations, True)
            observations = []
    mfc.observations.add_observations(observations, True)

    print("Ingest of latest data completed, new observations succesfully created")


def update_bets():
    mfc = MongoFootballClient(conf.MONGO_URL)
    af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)

    bets_to_check = mfc.bets.get_bets_no_result()
    print(f"{len(bets_to_check)} amount of unsettled bets to check")

    for bet in bets_to_check:
        fixture_id = mfc.matches.get_fixture_id(bet.date, bet.home_team)
        match = af.get_game_from_id(fixture_id)
        if match.result != "N/A":
            if bet.back and bet.home_team == bet.bet_on and match.result == "Home Win":
                result = "won"
            elif bet.back and bet.home_team != bet.bet_on and match.result == "Away Win":
                result = "won"
            elif not bet.back and bet.home_team == bet.bet_on and match.result != "Home Win":
                result = "won"
            elif not bet.back and bet.home_team != bet.bet_on and match.result != "Away Win":
                result = "won"
            else:
                result = "lost"

            bet.result = result
            print(f"updating bet for game with date {bet.date} and home team {bet.home_team}")
            mfc.bets.update_bet(bet)
            update_bankroll(bet)

def update_bankroll(bet: Bet):
    mfc = MongoFootballClient(conf.MONGO_URL)

    current_bankroll = mfc.bankroll.check_bankroll()

    if bet.result == "won":
        current_bankroll.bankroll += (bet.amount*bet.odds)-1
    else:
        current_bankroll.bankroll -= 1

    current_bankroll.amount_in_play -= bet.amount
    current_bankroll.date = datetime.now()
    mfc.bankroll.update_bankroll(current_bankroll)
