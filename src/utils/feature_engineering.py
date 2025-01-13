from ..data_models.match import Match
from ..database.mongo_client import MongoFootballClient
from ..config import Config as conf

def engineer_all_features():
    mfc = MongoFootballClient(conf.MONGO_URL)
    matches = mfc.get_matches()
    print("Calculating league.type values")
    processed_matches = list(map(league_type, matches))
    return processed_matches

def league_type(match: Match) -> Match:
    try:
        int(match.game_week)
        league_type="league"
    except ValueError:
        league_type="cup"

    match.league["type"] = league_type
    return match