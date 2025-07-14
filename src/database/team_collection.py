from .collection import MongoCollection
from ..data_models.team import Team
from typing import List, Optional


class TeamCollection(MongoCollection):
    def get_all_teams(self) -> List[Team]:
        """Gets all teams held within the database

        Returns:
            List[Team]: The returned list of teams in the database
        """
        cursor = self.col.find()
        all_teams = []
        for team in cursor:
            all_teams.append(Team.from_mongo_doc(team))
        return list(all_teams)

    def add_team(self, team: Team):
        "Adds a team to the database"
        self.col.insert_one(team.__dict__)

    def get_team_from_name(self, team_name: str, source=None) -> Optional[Team]:
        """Given a team name, find the matching team, if one exists, if it doesnt return None

        Args:
            team_name (str): The team name to find
            source (str, optional): Which site to fin from e.g. betfair. Defaults to None.

        Returns:
            Optional[Team]: The matched team, None if no match
        """
        if source is None:
            team = self.col.find_one({"name": team_name})
        else:
            team = self.col.find_one({"name": team_name, "source": source})
        if team is None:
            return None
        else:
            team = Team.from_mongo_doc(team)
            return team.id
