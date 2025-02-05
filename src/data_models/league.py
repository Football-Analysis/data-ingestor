from dataclasses import dataclass
from typing import List


@dataclass
class League:
    league_id: int
    season: int
    teams: dict
