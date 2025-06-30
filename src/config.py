import os


class Config:
    FOOTBALL_API_URL: str = "https://v3.football.api-sports.io/"
    ODDS_API_URL: str = "https://api.the-odds-api.com/v4"

    FOOTBALL_API_KEY: str = os.environ.get("FOOTABLL_API_KEY", "NOT_SET")
    ODDS_API_KEY: str = os.environ.get("ODDS_API_KEY", "NOT_SET")

    BETFAIR_API_KEY = os.environ.get("BETFAIR_API_KEY")

    MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
    MONGO_URL = f"mongodb://{MONGO_HOST}:27017/"

    BETFAIR_DATA_DIR = os.environ.get("BETFAIR_CERT_DIR", "/home/ubuntu/betfair-cert/")

    DAY_LIMIT = 1
