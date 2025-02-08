from requests import get
from .ingestor import Ingestor


class OddsIngestor(Ingestor):
    """ A class to ingest sports odds from various bookmakers for a variety of sports, ready to be analysed at a later date
    """
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
        
    def get_odds_from_date(self, league, date):
        endpoint = f"{self.base_url}/sports/{league}/odds"
        params = {"api_key": self.api_key, "regions": "uk"}
        odds = get(endpoint, params=params)
        if 300 > odds.status_code >= 200:
            data = odds.json()
            print(data[1])
            print(len(data))
            print(odds.headers["x-requests-remaining"])
