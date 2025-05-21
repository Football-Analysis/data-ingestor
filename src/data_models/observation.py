from dataclasses import dataclass
from typing import Optional


@dataclass
class Observation:
    match_id: str
    home_ppg: float
    home_plfg: float
    away_ppg: float
    away_plfg: float
    home_general_difficulty: float
    away_general_difficulty: float
    home_relative_form: float
    away_relative_form: float
    points_diff: float
    plfg_diff: float
    home_ppd: float
    away_ppd: float
    ppd_diff: float
    h2h_games: int
    h2h_diff: float
    h2h_gd_diff: float
    before_gw_ten: int
    home_trend: int
    home_trend_diff: float
    away_trend: int
    away_trend_diff: float
    result: Optional[str]

    @staticmethod
    def from_mongo_doc(mongo_doc: dict) -> "Observation":
        if "_id" in mongo_doc:
            del mongo_doc["_id"]
            return Observation(**mongo_doc)
