from ..data_models.match import Match
from ..database.mongo_client import MongoFootballClient
from ..config import Config as conf
from ..data_models.observation import Observation
from tqdm import tqdm
from typing import List, Tuple
from ..data_models.odds import Odds
from ..data_models.team import Team


def engineer_all_features():
    mfc = MongoFootballClient(conf.MONGO_URL)
    matches = mfc.get_matches()
    print("Calculating league.type values")
    processed_matches = list(map(league_type, matches))
    return processed_matches

def process_raw_match(match):
    game_week = match["league"]["round"].split()[-1]
    try:
        int(game_week)
        game_week = int(game_week)
        league_type = "league"
    except ValueError:
        return False, None

    try:
        if match["score"]["fulltime"]["home"] > match["score"]["fulltime"]["away"]:
            result = "Home Win"
        elif match["score"]["fulltime"]["home"] < match["score"]["fulltime"]["away"]:
            result = "Away Win"
        elif match["score"]["fulltime"]["home"] == match["score"]["fulltime"]["away"]:
            result = "Draw"
    except TypeError:
        result = "N/A"

    league_data = {}
    league_data["name"] = match["league"]["name"]
    league_data["id"] = match["league"]["id"]
    league_data["type"] = league_type

    return True, Match(date=match["fixture"]["date"],
                       fixture_id=match["fixture"]["id"],
                       home_team=match["teams"]["home"]["id"],
                       away_team=match["teams"]["away"]["id"],
                       score=match["score"],
                       game_week=game_week,
                       season=match["league"]["season"],
                       league=league_data,
                       result=result)
    
def league_type(match: Match) -> Match:
    try:
        int(match.game_week)
        league_type="league"
    except ValueError:
        league_type="cup"

    match.league["type"] = league_type
    return match

def calculate_form(form):
    form_to_return = {}
    if form is None:
        return {}
    for week in range(1, len(form)+1):
        if week < 6:
            partial_form = "N"*(6-week) + form[0:week-1]
            form_to_return[str(week)] = partial_form
        else:
            form_to_return[str(week)] = form[week-6:week-1]
    return form_to_return

def create_training_data(update=True):
    mfc = MongoFootballClient(conf.MONGO_URL)
    matches = mfc.get_finished_matches()
    for match in tqdm(matches):
        match_id = f"{match.date}-{match.home_team}"
        #if  not mfc.check_observation(match_id):
        result = match.result
        home_general_form, home_form_aggregate, away_general_form, away_form_aggregate = create_general_form(match)
        home_local_form, home_home_aggreagate, away_local_form, away_away_aggregate = create_local_form(match)
        observation = Observation(match_id=match_id,
                                  away_general_wins = away_form_aggregate[0],
                                  away_general_draws = away_form_aggregate[1],
                                  away_general_losses = away_form_aggregate[2],
                                  away_general_unknown = away_form_aggregate[3],
                                away_general_5=away_general_form[0],
                                away_general_4=away_general_form[1],
                                away_general_3=away_general_form[2],
                                away_general_2=away_general_form[3],
                                away_general_1=away_general_form[4],
                                away_away_wins=away_away_aggregate[0],
                                away_away_draws=away_away_aggregate[1],
                                away_away_losses=away_away_aggregate[2],
                                away_away_unknown=away_away_aggregate[3],
                                away_away_5=away_local_form[4],
                                away_away_4=away_local_form[3],
                                away_away_3=away_local_form[2],
                                away_away_2=away_local_form[1],
                                away_away_1=away_local_form[0],
                                home_general_wins=home_form_aggregate[0],
                                home_general_draws=home_form_aggregate[1],
                                home_general_losses=home_form_aggregate[2],
                                home_general_unknown=home_form_aggregate[3],
                                home_general_5=home_general_form[0],
                                home_general_4=home_general_form[1],
                                home_general_3=home_general_form[2],
                                home_general_2=home_general_form[3],
                                home_general_1=home_general_form[4],
                                home_home_wins=home_home_aggreagate[0],
                                home_home_draws=home_home_aggreagate[1],
                                home_home_losses=home_home_aggreagate[2],
                                home_home_unknown=home_home_aggreagate[3],
                                home_home_5=home_local_form[4],
                                home_home_4=home_local_form[3],
                                home_home_3=home_local_form[2],
                                home_home_2=home_local_form[1],
                                home_home_1=home_local_form[0],
                                result=result)
        if update:
            mfc.update_observation(observation)
        else:
            mfc.add_observation(observation)

        
def create_general_form(match: Match):
    mfc = MongoFootballClient(conf.MONGO_URL)
    league = mfc.get_league(match.league["id"], match.season)
    try:
        home_form = league.teams[str(match.home_team)]["form"][str(match.game_week)]
        if not bool(home_form):
            home_form = "NNNNN"
    except:
        home_form = "NNNNN"

    try:
        away_form = league.teams[str(match.away_team)]["form"][str(match.game_week)]
        if not bool(away_form):
            away_form = "NNNNN"
    except:
        away_form = "NNNNN"
    
    home_form = list(home_form)
    away_form = list(away_form)

    home_wins = home_form.count("W")
    home_draws = home_form.count("D")
    home_losses = home_form.count("L")
    home_unknown = home_form.count("N")
    away_wins = away_form.count("W")
    away_draws = away_form.count("D")
    away_losses = away_form.count("L")
    away_unknown = away_form.count("N")

    return home_form, (home_wins, home_draws, home_losses, home_unknown), \
        away_form, (away_wins, away_draws, away_losses, away_unknown)

def create_local_form(match: Match):
    mfc = MongoFootballClient(conf.MONGO_URL)

    home_home_matches = mfc.get_last_5_games(match.league["id"], match.season, match.home_team, match.game_week, True)
    home_home_form = calculate_local_form(home_home_matches)
    away_away_matches = mfc.get_last_5_games(match.league["id"], match.season, match.away_team, match.game_week, False)
    away_away_form = calculate_local_form(away_away_matches, False)

    home_wins = home_home_form.count("W")
    home_draws = home_home_form.count("D")
    home_losses = home_home_form.count("L")
    home_unknown = home_home_form.count("N")
    away_wins = away_away_form.count("W")
    away_draws = away_away_form.count("D")
    away_losses = away_away_form.count("L")
    away_unknown = away_away_form.count("N")

    return home_home_form, (home_wins, home_draws, home_losses, home_unknown), \
        away_away_form, (away_wins, away_draws, away_losses, away_unknown)

def calculate_local_form(matches: List[Match], home: bool = True) -> List[str]:
    form = []
    for match in matches:
        if home:
            if match.result == "Home Win":
                form.append("W")
            elif match.result == "Draw":
                form.append("D")
            else:
                form.append("L")
        else:
            if match.result == "Away Win":
                form.append("W")
            elif match.result == "Draw":
                form.append("D")
            else:
                form.append("L")
    form = (form + ["N"] * 5)[:5]
    return form
