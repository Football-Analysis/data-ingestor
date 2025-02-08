from dataclasses import dataclass


@dataclass
class Prediction:
    home_chance: float
    away_chance: float
    draw_chance: float
    result: str