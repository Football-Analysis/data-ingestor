import os


class Config:
    FOOTBALL_API_URL: str = "https://v3.football.api-sports.io/"
    ODDS_API_URL: str = "https://api.the-odds-api.com/v4"

    FOOTBALL_API_KEY: str = os.environ.get("FOOTABLL_API_KEY", "NOT_SET")
    ODDS_API_KEY: str = os.environ.get("ODDS_API_KEY", "NOT_SET")

    BETFAIR_API_KEY = os.environ.get("BETFAIR_API_KEY")

    MONGO_URL = "mongodb://localhost:27017/"

    CURRENT_SEASON = 2024

    BETFAIR_DATA_DIR = "/home/ubuntu/betfair-data"

    odds_seasons = [2020,2021,2022,2023,2024]
    odds_dates = {
        2020: {
            "start": "2020-09-11T14:00:00Z",
            "end": "2021-05-23T15:00:00Z"
            },
        2021: {
            "start": "2021-08-13T14:00:00Z",
            "end": "2022-05-22T15:00:00Z"
            },
        2022: {
            "start": "2022-08-05T14:00:00Z",
            "end": "2023-05-28T15:00:00Z"
            },
        2023: {
            "start": "2023-08-11T14:00:00Z",
            "end": "2024-05-19T15:00:00Z"
            },
        2024: {
            "start": "2024-09-11T14:00:00Z",
            "end": "2025-02-09T15:00:00Z"
            }
        }
