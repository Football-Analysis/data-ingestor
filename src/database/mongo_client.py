from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import DuplicateKeyError
from ..data_models.league import League
from ..data_models.match import Match
from ..data_models.observation import Observation
from ..data_models.odds import Odds
from ..data_models.standing import Standing
from typing import List
from tqdm import tqdm
from ..data_models.team import Team
from datetime import datetime, timedelta
from ..config import Config as conf


class MongoFootballClient:
    def __init__(self, url: str):
        self.url = url
        self.mc = MongoClient(self.url)
        self.football = self.mc["football"]
        self.match_collection = self.football["matches"]
        self.test_match_collection = self.football["test_matches"]
        self.league_collection = self.football["leagues"]
        self.observation_collection = self.football["observations"]
        self.test_observation_collection = self.football["test_observations"]
        self.api_predictions_collection = self.football["apiPredictions"]
        self.odds_collection = self.football["odds"]
        self.team_collection = self.football["teams"]
        self.next_match_collection = self.football["next_matches"]
        self.next_observations_collection = self.football["next_observations"]
        self.standing_collection = self.football["standings"]
        self.test_standing_collection = self.football["test_standings"]

    def add_league(self, league: League):
        """Saves a list of teams that belonged to a certain league into mongo

        Args:
            league (List[League])
        """
        self.league_collection.insert_one(league.__dict__)

    def update_league(self, league: League):
        """Saves a list of teams that belonged to a certain league into mongo

        Args:
            league (List[League])
        """
        query = {"league_id": league.league_id, "season": league.season}
        update_values = {"$set": league.__dict__}
        self.league_collection.update_one(query, update_values)

    def add_observation(self, observation: Observation, test: bool = False):
        if test:
            col = self.test_observation_collection
        else:
            col = self.observation_collection

        col.insert_one(observation.__dict__)

    def update_observation(self, observation: Observation):
        query = {"match_id": observation.match_id}
        update_values = {"$set": observation.__dict__}
        self.observation_collection.update_one(query, update_values)

    def add_matches(self, matches: List[Match], test=False):
        """Takes a list of Match objects and inserts them into the correct collection in mongo

        Args:
            matches (List[Match]): A list of processed matches
        """
        if test:
            col = self.test_match_collection
        else:
            col = self.match_collection

        for match in matches:
            col.insert_one(match.__dict__)

    def get_current_leagues(self, current_season):
        current_leagues = self.match_collection.distinct("league.id", {"season": current_season})
        return current_leagues

    def update_matches(self, matches: List[Match]):
        for match in matches:
            query = {
                "league.id": match.league["id"],
                "season": match.season,
                "game_week": match.game_week,
                "away_team": match.away_team,
                "home_team": match.home_team}
            update_values = {"$set": match.__dict__}
            self.match_collection.update_one(query, update_values)

    def get_matches(self) -> List[Match]:
        print("Querying all matches")
        cursor = self.match_collection.find({})
        matches = []
        for match in cursor:
            matches.append(Match.from_mongo_doc(match))
        return matches

    def get_finished_matches(self, test=False) -> List[Match]:
        print("Querying all finished matches")

        if test:
            col = self.test_match_collection
        else:
            col = self.match_collection

        cursor = col.find({
            "result": {"$ne": "N/A"}
        })
        matches = []
        for match in cursor:
            matches.append(Match.from_mongo_doc(match))
        return matches

    def get_league(self, league_id: int, season: int) -> League:
        league = self.league_collection.find_one({
            "league_id": league_id,
            "season": season
        })
        if league is None:
            return False
        return League.from_mongo_doc(league)

    def get_all_leagues(self) -> List[League]:
        leagues = self.league_collection.find()

        leagues_to_return = []
        for league in leagues:
            leagues_to_return.append(League.from_mongo_doc(league))

        return leagues_to_return

    def check_observation(self, match_id):
        obs = self.observation_collection.find_one({
            "match_id": match_id
        })
        if obs is None:
            return False
        return Observation.from_mongo_doc(obs)

    def get_last_5_games(self, league: int, season: int, team: int, date: str,
                         all=False, home: bool = True, test: bool = False) -> List[Match]:
        if test:
            col = self.test_match_collection
        else:
            col = self.test_match_collection

        gen_filter = {
            "league.id": league,
            "season": season,
            "date": {"$lte": date},
            "result": {"$ne": "N/A"}
        }
        if all:
            gen_filter["$or"] = [{"home_team": team}, {"away_team": team}]
        else:
            if home:
                gen_filter["home_team"] = team
            else:
                gen_filter["away_team"] = team

        matches = col.find(gen_filter).sort("date", DESCENDING)

        matches_to_return = []
        for match in matches:
            matches_to_return.append(Match.from_mongo_doc(match))

        if len(matches_to_return) < 5:
            return matches_to_return
        return matches_to_return[:5]

    def check_odd(self, date, home):
        result = self.odds_collection.find_one({
            "date": date,
            "home_team": home
        })
        if result is not None:
            return True
        return False

    def get_all_teams(self) -> List[Team]:
        cursor = self.team_collection.find()
        all_teams = []
        for team in cursor:
            all_teams.append(Team.from_mongo_doc(team))
        return list(all_teams)

    def get_all_teams_from_leagues(self) -> List[int]:
        cursor = self.league_collection.find()
        all_teams = set()
        for league in cursor:
            teams = list(league["teams"].keys())
            teams = [int(x) for x in teams]
            all_teams.update(teams)
        return list(all_teams)

    def get_af_teams(self) -> List[Team]:
        cursor = self.team_collection.find({"source": "af"})
        all_teams = []
        for team in cursor:
            del team["_id"]
            all_teams.append(Team(**team))
        return all_teams

    def check_oa_team(self, name) -> bool:
        team = self.team_collection.find_one({"source": "oa",
                                              "name": name})
        if team is not None:
            return True
        return False

    def get_oa_id(self, name):
        team = self.team_collection.find_one({"source": "oa",
                                              "name": name})
        return team["id"]

    def add_team(self, team):
        self.team_collection.insert_one(team.__dict__)

    def add_odd(self, odd: Odds):
        self.odds_collection.insert_one(odd.__dict__)

    def update_odd(self, odd: Odds, home_team=None):
        if home_team is None:
            query = {"date": odd.date, "home_team": odd.home_team}
        else:
            query = {"date": odd.date, "home_team": home_team}
        update_values = {"$set": odd.__dict__}
        self.odds_collection.update_one(query, update_values)

    def get_betfair_team_names(self):
        home_teams = self.odds_collection.distinct("home_team")
        away_team = self.odds_collection.distinct("away_team")
        return list(set(home_teams).union(away_team))

    def get_team_from_name(self, team_name, source=None):
        if source is None:
            team = self.team_collection.find_one({"name": team_name})
        else:
            team = self.team_collection.find_one({"name": team_name, "source": source})
        if team is None:
            return None
        else:
            team = Team.from_mongo_doc(team)
            return team.id

    def get_betfair_team(self, team_name):
        team = self.team_collection.find_one({"name": team_name, "source": "betfair"})
        if team is None:
            return False
        else:
            return True

    def get_odds(self, processed=False) -> List[Odds]:
        if processed:
            mongo_filter = {"$or": [
                {"home_team": {"$type": 2}},
                {"away_team": {"$type": 2}}]}
        else:
            mongo_filter = {}
        odds = self.odds_collection.find(mongo_filter)
        odds_to_return = []
        for odd in odds:
            odds_to_return.append(Odds.from_mongo_doc(odd))
        return odds_to_return

    def get_match(self, date, home_team=None, away_team=None):
        if home_team is None and away_team is None:
            raise RuntimeError("When filtering for a match both home and away teams cannot be None")

        if home_team is None:
            match = self.match_collection.find_one({"date": date, "away_team": away_team})
        else:
            match = self.match_collection.find_one({"date": date, "home_team": home_team})

        if match is None:
            return None
        return Match.from_mongo_doc(match)

    def match_exists(self, league_id, season, home_team, away_team):
        match = self.match_collection.find_one({
            "league.id": league_id,
            "season": season,
            "home_team": home_team,
            "away_team": away_team
        })

        if match is None:
            return False
        else:
            return True

    def del_odd(self, date, home_team):
        self.odds_collection.delete_one({"date": date, "home_team": home_team})

    def get_next_gameweek(self, league_id, season):
        now = datetime.now()
        time_now = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        next_match = self.match_collection.find({
            "league.id": league_id,
            "season": season,
            "date": {"$gt": time_now}}).sort("date", ASCENDING).limit(1)

        for match in next_match:
            match_details = Match.from_mongo_doc(match)
            return match_details.game_week
        return None

    def get_leagues_matches(self, league_id, season, test=False) -> List[Match]:
        if test:
            col = self.test_match_collection
        else:
            col = self.match_collection

        matches = col.find({"season": season, "league.id": league_id, "result": {"$ne": "N/A"}}).sort("date", ASCENDING)
        leagues_matches = []
        for match in matches:
            leagues_matches.append(Match.from_mongo_doc(match))
        return leagues_matches

    def get_next_matches(self):
        time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        until_date = datetime.now() + timedelta(days=conf.DAY_LIMIT)
        until_date = until_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        matches = self.match_collection.find({"date": {"$gte": time_now, "$lte": until_date}})
        next_matches = []
        for match in matches:
            next_matches.append(Match.from_mongo_doc(match))
        self.add_next_matches(next_matches)
        return next_matches

    def add_next_matches(self, matches: List[Match]):
        try:
            for match in matches:
                self.next_match_collection.insert_one(match.__dict__)
        except:
            print(match)

    def delete_next_matches(self):
        self.next_match_collection.delete_many({})

    def delete_next_observations(self):
        self.next_observations_collection.delete_many({})

    def delete_standings(self):
        self.standing_collection.delete_many({})

    def get_last_stansings(self, league_id, season, date, test=False):
        if test:
            col = self.test_standing_collection
        else:
            col = self.standing_collection

        gen_filter = {
            "league_id": league_id,
            "season": season,
            "date": {"$lte": date}
        }

        standings = col.find(gen_filter).sort("date", DESCENDING)

        standings_to_return = []
        for standing in standings:
            standings_to_return.append(Standing.from_mongo_doc(standing))

        return standings_to_return

    def add_observations(self, observations: List[Observation], next_games=True):
        if next_games:
            col = self.next_observations_collection
        else:
            col = self.observation_collection
        obs_to_add = list(map(lambda x: x.__dict__, observations))
        col.insert_many(obs_to_add)

    def get_list_of_leagues(self):
        leagues = self.league_collection.distinct("league_id")
        return leagues

    def get_observation(self, match_id):
        obs = self.observation_collection.find_one({"match_id": match_id})
        if obs is None:
            return None
        else:
            return Observation.from_mongo_doc(obs)

    def create_points_per_difficulty(self):
        plfg = self.observation_collection.aggregate([
            {
                "$addFields": {
                    "home_ppd": {"$divide": [
                        "$home_plfg",
                        "$home_general_difficulty"
                    ]}
                }
            }
        ])

        for obs in tqdm(plfg):
            self.observation_collection.update_one({"match_id": obs["match_id"]}, {"$set": {"home_ppd": obs["home_ppd"]}})

    def standing_exists(self, league_id, season, date=None, test=False):
        if test:
            col = self.test_standing_collection
        else:
            col = self.standing_collection

        query_filter = {"league_id": league_id, "season": season}

        if date is not None:
            query_filter["date"] = date

        standing = col.find_one(query_filter)
        if standing is None:
            return False
        else:
            return True

    def add_standing(self, standing: Standing, test=False):
        if test:
            col = self.test_standing_collection
        else:
            col = self.standing_collection

        try:
            col.insert_one(standing.__dict__)
        except DuplicateKeyError:
            print(standing.__dict__)
            raise RuntimeError("Uh oh")

    def get_standings(self, date, league_id, season, test=False):
        if test:
            col = self.test_standing_collection
        else:
            col = self.standing_collection

        standing = col.find_one({"date": date, "league_id": league_id, "season": season})
        if standing is None:
            return None
        else:
            return Standing.from_mongo_doc(standing)

    def get_standings_from_team_date(self, league_id, season, team, date) -> Standing:
        standings = self.standing_collection.find({
            "league_id": league_id,
            "season": season,
            "date": {"$lt": date}
        }).sort("date", DESCENDING)

        standing_to_return = None
        for standing in standings:
            if standing_to_return is None:
                standing_to_return = Standing.from_mongo_doc(standing)
            return standing_to_return

    def set_default_difficulty(self):
        obs = self.observation_collection.find()
        for ob in tqdm(obs):
            try:
                ppd_diff = ob["home_ppd"] - ob["away_ppd"]
                self.observation_collection.update_one({"match_id": ob["match_id"]}, {"$set": {"ppd_diff": ppd_diff}})
            except:
                print(f"Couldn't create full ob for {ob["match_id"]}")

    def get_h2h(self, home_team, away_team, league_id, season, date):
        h2h_matches = self.match_collection.find({
            "league.id": league_id,
            "season": {"$in": [season, season - 1]},
            "home_team": {"$in": [home_team, away_team]},
            "away_team": {"$in": [home_team, away_team]},
            "date": {"$lt": date}
        })

        matches_to_return = []
        for match in h2h_matches:
            matches_to_return.append(Match.from_mongo_doc(match))

        return matches_to_return
