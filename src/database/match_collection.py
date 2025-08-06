from .collection import MongoCollection
from ..data_models.match import Match
from typing import List, Optional
from pymongo import DESCENDING, ASCENDING
from datetime import datetime, timedelta
from ..config import Config as conf


class MatchCollection(MongoCollection):
    def __init__(self, db, collection):
        super().__init__(db, collection)
        self.next_match_collection = db["next_matches"]

    def add_matches(self, matches: List[Match]):
        """Takes a list of Match objects and inserts them into the correct collection in mongo

        Args:
            matches (List[Match]): A list of processed matches
        """
        for match in matches:
            self.col.insert_one(match.__dict__)

    def update_matches(self, matches: List[Match]):
        """Updates information for a list of matches

        Args:
            matches (List[Match]): The list of matches to update
        """
        for match in matches:
            query = {
                "league.id": match.league["id"],
                "season": match.season,
                "game_week": match.game_week,
                "away_team": match.away_team,
                "home_team": match.home_team}
            update_values = {"$set": match.__dict__}
            self.col.update_one(query, update_values)

    def get_matches(self) -> List[Match]:
        """Queries and returns all matches held within the database

        Returns:
            List[Match]: A list of all returned matches
        """
        print("Querying all matches")
        cursor = self.col.find({}).sort("date", ASCENDING)
        matches = []
        for match in cursor:
            matches.append(Match.from_mongo_doc(match))
        return matches

    def get_finished_matches(self) -> List[Match]:
        """Gets all finished matches within the database

        Returns:
            List[Match]: _description_
        """
        print("Querying all finished matches")
        cursor = self.col.find({"result": {"$ne": "N/A"}}).sort
        matches = []
        for match in cursor:
            matches.append(Match.from_mongo_doc(match))
        return matches

    def get_last_5_games(self, league: int, season: int, team: int, date: str,
                         all=False, home: bool = True) -> List[Match]:
        """Given a date, get the last 5 games for a specific team prior to that date

        Args:
            league (int): League id that the team belongs to
            season (int): Season in question
            team (int): The team to get the last matches of
            date (str): The date to get the games prior to
            all (bool, optional): If to return matches if they were home or away
            home (bool, optional): Return only home games

        Returns:
            List[Match]: The list of 5 (potential) matches
        """

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

        matches = self.col.find(gen_filter).sort("date", DESCENDING)

        matches_to_return = []
        for match in matches:
            matches_to_return.append(Match.from_mongo_doc(match))

        if len(matches_to_return) < 5:
            return matches_to_return
        return matches_to_return[:5]

    def get_match(self, date: str, home_team: Optional[int] = None, away_team: Optional[int] = None) -> Optional[Match]:
        """Given some match information, find the matching match in the databse,
           return None if no match exists

        Args:
            date (str): The datetime of the match
            home_team (_type_, optional): The id of the home team. Defaults to None.
            away_team (_type_, optional): The id of the away team. Defaults to None.

        Raises:
            RuntimeError: If both home team and away team are none there is not enough information to find a match

        Returns:
            _type_: _description_
        """
        if home_team is None and away_team is None:
            raise RuntimeError("When filtering for a match both home and away teams cannot be None")

        if home_team is None:
            match = self.col.find_one({"date": date, "away_team": away_team})
        else:
            match = self.col.find_one({"date": date, "home_team": home_team})

        if match is None:
            return None
        return Match.from_mongo_doc(match)

    def match_exists(self, league_id: int, season: int, home_team: int, away_team: int) -> bool:
        """Chec kto see if a given match exists in the database

        Args:
            league_id (int): The league id of the match
            season (int): The season which the match took place
            home_team (int): The home teams id
            away_team (int): The away teams id

        Returns:
            bool: True if exists, false otherwise
        """
        match = self.col.find_one({
            "league.id": league_id,
            "season": season,
            "home_team": home_team,
            "away_team": away_team
        })

        if match is None:
            return False
        else:
            return True

    def get_leagues_matches(self, league_id: int, season: int) -> List[Match]:
        """Returns a list of matches given a league ID and a season

        Args:
            league_id (int): The league ID to match on
            season (int): The season to match on

        Returns:
            List[Match]: The list of returned matches
        """
        matches = self.col.find({"season": season, "league.id": league_id, "result": {"$ne": "N/A"}}).sort("date", ASCENDING)
        leagues_matches = []
        for ind_match in matches:
            leagues_matches.append(Match.from_mongo_doc(ind_match))
        return leagues_matches

    def get_next_matches(self) -> List[Match]:
        """Gets the incoming matches in the next x amount of days (defined in the config.py file)

        Returns:
            List[Match]: The list of matches returned by the query
        """
        time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        until_date = datetime.now() + timedelta(days=conf.DAY_LIMIT)
        until_date = until_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        matches = self.col.find({"date": {"$gte": time_now, "$lte": until_date}})
        next_matches = []
        for match in matches:
            next_matches.append(Match.from_mongo_doc(match))
        self.add_next_matches(next_matches)
        return next_matches

    def add_next_matches(self, matches: List[Match]):
        """Adds the upcoming matches to the next matches collection

        Args:
            matches (List[Match]): The upcoming matches to save
        """
        try:
            for match in matches:
                self.next_match_collection.insert_one(match.__dict__)
        except:
            print(match)

    def delete_next_matches(self):
        """Wipe next matches collection
        """
        self.next_match_collection.delete_many({})

    def get_h2h(self, home_team: int, away_team: int, league_id: int,
                season: int, date: str) -> List[Match]:
        """Returns a list of head to head matches between the two given teams
           in this and last season

        Args:
            home_team (int): home team to check against
            away_team (int): away eam to check agaisnt
            league_id (int): What league you want the head to head matches from
            season (int): Which season to star te head to head search from
            date (str): The date of the match

        Returns:
            List[Match]: The list of recent head to head results
        """
        h2h_matches = self.col.find({
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

    def get_fixture_id(self, date: str, home_team: int) -> int:
        """Return te fixture ID of a match given the date and home team

        Args:
            date (str): Thed ate of the match
            home_team (int): The home team of the match

        Returns:
            int: The fixure ID
        """
        match = self.col.find_one({"date": date, "home_team": home_team})

        return match["fixture_id"]
