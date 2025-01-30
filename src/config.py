import os


class Config:
    FOOTBALL_API_URL: str = "https://api-football-v1.p.rapidapi.com/v3"
    ODDS_API_URL: str = "https://api.the-odds-api.com/v4"

    FOOTBALL_API_KEY: str = os.environ.get("FOOTABLL_API_KEY", "NOT_SET")
    ODDS_API_KEY: str = os.environ.get("ODDS_API_KEY", "NOT_SET")

    MONGO_URL = "mongodb://localhost:27017/"

    CURRENT_SEASON = 2024
