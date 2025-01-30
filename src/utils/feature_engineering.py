from ..data_models.match import Match
from ..database.mongo_client import MongoFootballClient
from ..config import Config as conf

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
        league_type="league"
    except ValueError:
        league_type="cup"

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

    return Match(date=match["fixture"]["date"],
                 home_team=match["teams"]["home"]["name"],
                 away_team=match["teams"]["away"]["name"],
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
