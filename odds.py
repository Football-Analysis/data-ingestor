from src.ingestors.betfair_ingestor import BetfairClient
from src.config import Config as conf

bc = BetfairClient("",conf.BETFAIR_API_KEY)
bc.get_downloaded_data(2017,5,5)