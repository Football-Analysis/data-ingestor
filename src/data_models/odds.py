from dataclasses import dataclass


@dataclass
class Odds:
    date: str
    home_team: str
    home_odds: float
    away_odds: float
    draw_odds: float
    