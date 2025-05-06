from src.ingestors.match_ingestor import ApiFootball
from ..config import Config as conf

def get_h2h(home_team, away_team, league_id, season):
    af = ApiFootball(conf.FOOTBALL_API_URL, conf.FOOTBALL_API_KEY)
    return af.get_h2h(home_team, away_team, league_id, season)