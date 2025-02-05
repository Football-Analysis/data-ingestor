from dataclasses import dataclass


@dataclass
class Observation:
    match_id: str
    away_five: str
    away_four: str
    away_three: str
    away_two: str
    away_one: str
    home_five: str
    home_four: str
    home_three: str
    home_two: str
    home_one: str
    result: str