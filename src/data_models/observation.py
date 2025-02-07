from dataclasses import dataclass


@dataclass
class Observation:
    match_id: str
    away_general_5: str
    away_general_4: str
    away_general_3: str
    away_general_2: str
    away_general_1: str
    home_general_5: str
    home_general_4: str
    home_general_3: str
    home_general_2: str
    home_general_1: str
    home_home_5: str
    home_home_4: str
    home_home_3: str
    home_home_2: str
    home_home_1: str
    away_away_5: str
    away_away_4: str
    away_away_3: str
    away_away_2: str
    away_away_1: str
    result: str