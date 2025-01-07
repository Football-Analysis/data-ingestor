from ..data_models.match import Match
from ..database.mongo_client import MongoFootballClient
from ..config import Config as conf

def engineer_all_features():
    mfc = MongoFootballClient(conf.MONGO_URL)
    matches = mfc.get_matches()
    print("Calculating league.type values")
    print(matches[0])
    processed_matches = list(map(league_type, matches))
    print(processed_matches[0])
    return processed_matches

def league_type(match: Match) -> Match:
    if match.game_week in range(0,100):
        league_type="league"
    else:
        league_type="cup"

    match.league["type"] = league_type
    return match