import os
from betfairlightweight import APIClient
from .ingestor import Ingestor
import bz2
import json
from datetime import datetime, timedelta
from ..data_models.odds import Odds
from ..database.mongo_client import MongoFootballClient
from ..config import Config as conf
from jaro import jaro_winkler_metric
from time import sleep


class BetfairClient(Ingestor):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, api_key)

        self.mfc = MongoFootballClient(conf.MONGO_URL)

        self.username = os.getenv("BETFAIR_USERNAME", None)
        if self.username is None:
            raise RuntimeError("BETFAIR_USERNAME environment variable must be set")

        self.password = os.getenv("BETFAIR_PASSWORD", None)
        if self.password is None:
            raise RuntimeError("BETFAIR_PASSWORD environment variable must be set")

        self.trading = APIClient(self.username,
                                 self.password,
                                 app_key=self.api_key,
                                 certs="/home/ubuntu/betfair-cert/")

        self.trading.login()

    def get_downloaded_data(self, year, month, day):
        market_ids = {}
        processed_mids = []
        saved_odds = 0
        file_date = datetime(year, month, day)
        while file_date.year < 2025:
            print(f"Downloading files for {file_date.year}, {file_date.month}, {file_date.day}")
            try:
                months_list = self.trading.historic.get_file_list("Soccer",
                                                                  "Basic Plan",
                                                                  from_day=file_date.day,
                                                                  from_month=file_date.month,
                                                                  from_year=file_date.year,
                                                                  to_day=file_date.day,
                                                                  to_month=file_date.month,
                                                                  to_year=file_date.year,
                                                                  market_types_collection=["MATCH_ODDS"])
            except:
                print("Probably an ssl error, will try again in 30 seconds")
                sleep(30)
                months_list = self.trading.historic.get_file_list("Soccer",
                                                                  "Basic Plan",
                                                                  from_day=file_date.day,
                                                                  from_month=file_date.month,
                                                                  from_year=file_date.year,
                                                                  to_day=file_date.day,
                                                                  to_month=file_date.month,
                                                                  to_year=file_date.year,
                                                                  market_types_collection=["MATCH_ODDS"])

            file_date += timedelta(1)
            for data_file in months_list:
                file_name = None
                while file_name is None:
                    try:
                        file_name = self.trading.historic.download_file(data_file, conf.BETFAIR_DATA_DIR)
                    except:
                        print("Probably a SSL error, try again in 30 seconds")
                        sleep(30)

                binary_file = bz2.BZ2File(file_name, 'rb')
                data_list = []
                try:
                    for line in binary_file:
                        my_json = line.decode('utf8').replace("'", '"')
                        try:
                            data = json.loads(my_json)
                            data_list.append(data)
                        except:
                            print(f"Failed to parse json line in file {file_name}, ignoring this line")
                except:
                    print(f"Failed to parse this file {file_name}, ignoring this file")

                for data_point in data_list:
                    mc = data_point["mc"]
                    for market in mc:
                        mid = market["id"]
                        if mid not in market_ids and mid not in processed_mids:
                            if "marketDefinition" in market:
                                skip = False
                                runners = market["marketDefinition"]["runners"]
                                runner_objects = {}
                                home_away = market["marketDefinition"]["eventName"].split()
                                home = home_away[0]
                                away = home_away[-1]
                                for runner in runners:
                                    runner_id = runner["id"]
                                    runner_name = runner["name"]

                                    if home.lower() in runner_name.lower() or \
                                       jaro_winkler_metric(home.lower(), runner_name.lower()) > 0.8:
                                        runner_objects[runner_id] = {"name": runner_name, "home": True, "odds": 0.0}
                                    elif away.lower() in runner_name.lower() or \
                                         jaro_winkler_metric(away.lower(), runner_name.lower()) > 0.8:
                                        runner_objects[runner_id] = {"name": runner_name, "home": False, "odds": 0.0}
                                    elif runner_name == "The Draw":
                                        runner_objects[runner_id] = {"name": runner_name, "draw": True, "odds": 0.0}
                                    else:
                                        print(f"Cannot assign {runner_name} to the home or away team")
                                        skip = True
                                        processed_mids.append(mid)

                                if not skip:
                                    market_ids[mid] = runner_objects
                                    market_ids[mid]["started"] = False
                                    market_ids[mid]["startTime"] = market["marketDefinition"]["marketTime"][:-5] + "+00:00"
                        elif mid not in processed_mids:
                            if not market_ids[mid]["started"]:
                                if "rc" in market:
                                    for runner in market["rc"]:
                                        if runner["ltp"] > market_ids[mid][runner["id"]]["odds"]:
                                            market_ids[mid][runner["id"]]["odds"] = runner["ltp"]
                                if "marketDefinition" in market:
                                    if market["marketDefinition"]["inPlay"]:
                                        market_ids[mid]["started"] = True
                                        for team_id in market_ids[mid]:
                                            if not isinstance(team_id, int):
                                                pass
                                            else:
                                                runner = market_ids[mid][team_id]
                                                if "draw" in runner:
                                                    draw_odds = runner["odds"]
                                                elif runner["home"]:
                                                    home_id = self.mfc.get_team_from_name(runner["name"], "betfair")
                                                    if home_id is not None:
                                                        home_team = home_id
                                                    else:
                                                        home_team = runner["name"]
                                                    home_odds = runner["odds"]
                                                elif not runner["home"]:
                                                    away_id = self.mfc.get_team_from_name(runner["name"], "betfair")
                                                    if away_id is not None:
                                                        away_team = away_id
                                                    else:
                                                        away_team = runner["name"]
                                                    away_odds = runner["odds"]
                                                else:
                                                    raise RuntimeError("Couldn't find home away and draw odds")
                                        odd_to_save = Odds(date=market_ids[mid]["startTime"],
                                                            home_team=home_team,
                                                            away_team=away_team,
                                                            home_odds=home_odds,
                                                            away_odds=away_odds,
                                                            draw_odds=draw_odds)
                                        self.mfc.add_odd(odd_to_save)
                                        processed_mids.append(mid)
                                        del market_ids[mid]
                                        saved_odds += 1
                                        if saved_odds % 50 == 0:
                                            print(f"Saved {saved_odds} amount of fixture odds")
