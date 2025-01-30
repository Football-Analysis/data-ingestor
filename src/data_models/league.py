from dataclasses import dataclass
from typing import List


@dataclass
class League:
    league_id: int
    league_name: str
    season: int
    teams: List[str]
