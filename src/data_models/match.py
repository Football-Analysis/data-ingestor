from dataclasses import dataclass
from typing import Optional


@dataclass
class Match:
    date: str
    home_team: int
    away_team: int
    score: dict
    game_week: int
    season: int
    league: dict
    result: str
