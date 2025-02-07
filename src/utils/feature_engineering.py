from ..data_models.match import Match
from ..database.mongo_client import MongoFootballClient
from ..config import Config as conf
from ..data_models.observation import Observation
from tqdm import tqdm
from typing import List, Tuple

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

def create_training_data():
    mfc = MongoFootballClient(conf.MONGO_URL)
    matches = mfc.get_finished_matches()
    for match in tqdm(matches):
        match_id = f"{match.date}-{match.home_team}"
        #if  not mfc.check_observation(match_id):
        result = match.result
        home_general_form, away_general_form = create_general_form(match)
        home_local_form, away_local_form = create_local_form(match)
        observation = Observation(match_id=match_id,
                                away_general_5=away_general_form[0],
                                away_general_4=away_general_form[1],
                                away_general_3=away_general_form[2],
                                away_general_2=away_general_form[3],
                                away_general_1=away_general_form[4],
                                away_away_5=away_local_form[4],
                                away_away_4=away_local_form[3],
                                away_away_3=away_local_form[2],
                                away_away_2=away_local_form[1],
                                away_away_1=away_local_form[0],
                                home_general_5=home_general_form[0],
                                home_general_4=home_general_form[1],
                                home_general_3=home_general_form[2],
                                home_general_2=home_general_form[3],
                                home_general_1=home_general_form[4],
                                home_home_5=home_local_form[4],
                                home_home_4=home_local_form[3],
                                home_home_3=home_local_form[2],
                                home_home_2=home_local_form[1],
                                home_home_1=home_local_form[0],
                                result=result)
        mfc.add_observation(observation)

        
def create_general_form(match: Match):
    mfc = MongoFootballClient(conf.MONGO_URL)
    league = mfc.get_league(match.league["id"], match.season)
    try:
        home_form = league.teams[str(match.home_team)]["form"][str(match.game_week)]
        if not bool(home_form):
            home_five = "N"
            home_four = "N"
            home_three = "N"
            home_two = "N"
            home_one = "N"
        else:
            home_five = home_form[0]
            home_four = home_form[1]
            home_three = home_form[2]
            home_two = home_form[3]
            home_one = home_form[4]
    except:
        home_five = "N"
        home_four = "N"
        home_three = "N"
        home_two = "N"
        home_one = "N"

    try:
        away_form = league.teams[str(match.away_team)]["form"][str(match.game_week)]
        if not bool(away_form):
            away_five = "N"
            away_four = "N"
            away_three = "N"
            away_two = "N"
            away_one = "N"
        else:
            away_five = away_form[0]
            away_four = away_form[1]
            away_three = away_form[2]
            away_two = away_form[3]
            away_one = away_form[4]
    except:
        away_five = "N"
        away_four = "N"
        away_three = "N"
        away_two = "N"
        away_one = "N"
    

    return (home_five, home_four, home_three, home_two, home_one), \
        (away_five, away_four, away_three, away_two, away_one)


def create_local_form(match: Match):
    mfc = MongoFootballClient(conf.MONGO_URL)

    home_home_matches = mfc.get_last_5_games(match.league["id"], match.season, match.home_team, match.game_week, True)
    home_home_form = calculate_local_form(home_home_matches)
    away_away_matches = mfc.get_last_5_games(match.league["id"], match.season, match.away_team, match.game_week, False)
    away_away_form = calculate_local_form(away_away_matches, False)

    return home_home_form, away_away_form

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

    
    

        


            



    



