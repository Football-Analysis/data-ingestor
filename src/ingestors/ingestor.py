from abc import ABC


class Ingestor(ABC):
    """An abstract base class for what each ingestor should look like
    """
    def __init__(self, base_url, api_key):
        if api_key == "NOT_SET":
            raise ValueError("""API KEY must be set. This is done via environment variables,
                             FOOTABLL_API_KEY for API-Football and ODDS_API_KEY for OddsAPI""")
        self.base_url = base_url
        self.api_key = api_key
