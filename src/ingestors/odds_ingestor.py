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

    def get_odds(self, sport_key: str, region: str = "uk"):
        """Given a sport, returns the current list of odds for that sports market

        Args:
            sport_key (str): The key of the sport to retrieve odds for (this can be got from the /sports endpoint)
            region (str) default = uk: The region to get bookmaker odds from
        """
        endpoint = f"{self.base_url}/sports/{sport_key}/odds"
        odds = get(endpoint, params={'api_key': self.api_key, 'regions': region})
        if 300 > odds.status_code >= 200:
            print(odds.json())
        else:
            raise RuntimeError(f"Unable to retrieve list of sports, status code {odds.status_code}, error message: {odds.text}")
