from dataclasses import dataclass


@dataclass
class Observation:
    match_id: str
    away_general_wins: int
    away_general_draws: int
    away_general_losses: int
    away_general_unknown: int
    away_general_5: str
    away_general_4: str
    away_general_3: str
    away_general_2: str
    away_general_1: str
    home_general_wins: int
    home_general_draws: int
    home_general_losses: int
    home_general_unknown: int
    home_general_5: str
    home_general_4: str
    home_general_3: str
    home_general_2: str
    home_general_1: str
    home_home_wins: int
    home_home_draws: int
    home_home_losses: int
    home_home_unknown: int
    home_home_5: str
    home_home_4: str
    home_home_3: str
    home_home_2: str
    home_home_1: str
    away_away_wins: int
    away_away_draws: int
    away_away_losses: int
    away_away_unknown: int
    away_away_5: str
    away_away_4: str
    away_away_3: str
    away_away_2: str
    away_away_1: str
    home_api_pred: int
    draw_api_pred: int
    away_api_pred: int
    api_pred: int
    result: str