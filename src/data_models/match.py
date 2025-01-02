from dataclasses import dataclass


@dataclass
class Match:
    date: set
    home_team: str
    away_team: str
    score: dict
    game_week: str