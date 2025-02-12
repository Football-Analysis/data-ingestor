from requests import get
from .ingestor import Ingestor
from ..data_models.odds import Odds
from typing import List


class OddsIngestor(Ingestor):
    """ A class to ingest sports odds from various bookmakers for a variety of sports, ready to be analysed at a later date
    """
    def check_api(self, headers):
        requests_remaining = int(headers["x-requests-remaining"])
        if requests_remaining % 1000:
            print(f"{requests_remaining} credits remaining on monthly plan")
        if requests_remaining < 20:
            raise RuntimeError("API monthly creadit limit reached, please upgrade plan or wait until next month")

    def get_sports(self):
        """ Prints a list of sports that are in season and available to get odds for
        """
        endpoint = f'{self.base_url}/sports'
        sports = get(endpoint, params={'api_key': self.api_key})
        if 300 > sports.status_code >= 200:
            for sport in sports.json():
                print(sport["key"])
            print(sports.headers["x-requests-remaining"])
        else:
            raise RuntimeError(f"Unable to retrieve list of sports, status code {sports.status_code}, error message: {sports.text}")
        
    def get_odds_from_date(self, league, date) -> List[Odds]:
        endpoint = f"{self.base_url}/historical/sports/{league}/odds"
        params = {"api_key": self.api_key, "regions": "uk", "date": date}
        odds = get(endpoint, params=params)
        print(odds.headers["x-requests-remaining"])
        odds_list = []
        if 300 > odds.status_code >= 200:
            if len(odds.json()) > 0 and len(odds.json()["data"]) > 0:
                for match in odds.json()["data"]:
                    metadata = match
                    if len(match["bookmakers"]) > 0:
                        odds_to_use = metadata["bookmakers"][0]
                        home_team = metadata["home_team"]
                        away_team = metadata["away_team"]
                        for outcome in odds_to_use["markets"][0]["outcomes"]:
                            if outcome["name"] == home_team:
                                home_odds = outcome["price"]
                            elif outcome["name"] == away_team:
                                away_odds = outcome["price"]
                            else:
                                draw_odds = outcome["price"]

                        odds_list.append(Odds(date=metadata["commence_time"],
                                    home_team=home_team,
                                    home_odds=home_odds,
                                    away_odds=away_odds,
                                    draw_odds=draw_odds))
        else:
            raise RuntimeError(f"Got nothing back from API, status code {odds.status_code}")
        return(odds_list)
