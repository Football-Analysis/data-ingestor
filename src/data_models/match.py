from dataclasses import dataclass
from typing import Optional


@dataclass
class Match:
    date: str
    fixture_id: int
    home_team: int
    away_team: int
    score: dict
    game_week: int
    season: int
    league: dict
    result: str
