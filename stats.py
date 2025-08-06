from src.ingestors.match_ingestor import ApiFootball
from src.config import Config as conf
from tqdm import tqdm
from src.database.mongo_football_client import MongoFootballClient
from src.utils.feature_engineering import create_standings, create_obs_from_match, create_squad_strength
from src.ingestors.betfair_ingestor import BetfairClient
from src.data_models.player_stats import PlayerStats
from time import time
from src.data_models.match import Match
from src.data_models.player import Player
from src.data_models.lineup import Lineup
from typing import List

af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
mfc = MongoFootballClient(conf.MONGO_URL, test=True)

# create_squad_strength([Player(player_id=340151, team=742, started=True),
#                        Player(player_id=283252, team=742, started=True),
#                        Player(player_id=377009, team=742, started=True),
#                        Player(player_id=21098, team=742, started=True),
#                        Player(player_id=287790, team=742, started=True),
#                        Player(player_id=807, team=742, started=True),
#                        Player(player_id=404891, team=742, started=True),
#                        Player(player_id=411800, team=742, started=True),
#                        Player(player_id=110153, team=742, started=True),
#                        Player(player_id=203458, team=742, started=True),
#                        Player(player_id=1937, team=742, started=True)], match=Match(fixture_id=1, game_week=1, date="2025-02-28T19:45:00+00:00", season=2024, home_team=742, away_team=12, score={}, league={}, result="N/A"), test=True)

# mfc.observations.get_all()


#exists = mfc.player_stats.check_exists(match.home_team, match.date)
# stats_league = af.get_lineup_leagues()
# total = 0
# for league in tqdm(stats_league):    


def process_lineup(match: Match, lineup: List[int], team_id: int):
    skip=False
    if len(lineup) == 0:
        skip = True
    players_played = []
    for player in lineup:
        #print(lineup)
        start = time()
        team_id = team_id    
        players_played.append(player)
        latest_stats = mfc.player_stats.get_player_stats(player, team_id, match.season, match.date)
        try:
            standings = mfc.standings.get_last_standings(match.league["id"], match.season, match.date)[0]
        except:
            print(f"Skipping player stats for fixture {match.fixture_id}")
            skip=True
            break
        team_played = standings.standings[str(team_id)]["played"]
        team_ppg = standings.standings[str(team_id)]["ppg"]
        result = match.result
        if (result == "Home Win" and team_id == match.home_team) or (result == "Away Win" and team_id == match.away_team):
            points = 3
        elif result == "Draw":
            points = 1
        else:
            points = 0
        if latest_stats is None:
            player_stat = PlayerStats(player_id=player,
                                        team=team_id,
                                        season=match.season,
                                        date=match.date,
                                        played=1,
                                        played_ppg=points,
                                        not_played=team_played,
                                        not_played_ppg=team_ppg)
            mfc.player_stats.add_player_stats(player_stat)
        else:
            played = latest_stats.played + 1
            not_played = latest_stats.not_played
            played_ppg = ((latest_stats.played_ppg * latest_stats.played) + points) / played
            not_played_ppg = latest_stats.not_played_ppg
            new_stats = PlayerStats(player_id=player,
                                    team=team_id,
                                    season=match.season,
                                    date=match.date,
                                    played=played,
                                    played_ppg=played_ppg,
                                    not_played=not_played,
                                    not_played_ppg=not_played_ppg)
            mfc.player_stats.add_player_stats(new_stats)
        # end = time()
        # print(f"Time for each player {end-start}")
    if skip:
        return False
    before_start = time()
    not_played = mfc.player_stats.get_non_played_players(players_played, team_id, match.season)
    # if len(not_played) > 15:
    #     print(not_played)
    #     print(players_played)
    #     print(team_id)
    #     print(match.date)
    #     print(match.season)
    for player in not_played:
        start = time()
        try:
            standings = mfc.standings.get_last_standings(match.league["id"], match.season, match.date)[0]
        except:
            break
        player_stats = mfc.player_stats.get_player_stats(player, team_id, match.season, match.date)
        if player_stats is None:
            continue
        didnt_play = PlayerStats(player_id=player_stats.player_id,
                    team=player_stats.team,
                    date=match.date,
                    season=match.season,
                    played=player_stats.played,
                    played_ppg=player_stats.played_ppg,
                    not_played=player_stats.not_played + 1,
                    not_played_ppg=((player_stats.not_played_ppg * player_stats.not_played) + points) / (player_stats.not_played + 1))
        mfc.player_stats.add_player_stats(didnt_play)
        end = time()
    #     print(f"Time to process each non players {end-start}")
    # before_end = time()
    # print(f"Time to process all non players {before_end-before_start}")
    # print(f"League - {match.league["id"]}, season - {match.season}, date - {match.date}")
    # print(f"players not played {len(not_played)}, players played {players_played}")

matches = mfc.matches.get_matches()
for match in tqdm(matches):
    exists = mfc.player_stats.check_exists(match.home_team, match.date)
    if exists:
        #print("Skipping")
        continue
    lineup = mfc.lineups.get_lineups(match.fixture_id)
    if lineup is None:
        #no_lineup_total +=1
        continue
    try:
        #no_standing_total +=1
        standings = mfc.standings.get_last_standings(match.league["id"], match.season, match.date)[0]
    except:
        continue
        #print(f"Skipping player stats for fixture {match.fixture_id}")
    #print("PROCESSING FIXTURE")
    process_lineup(match, lineup.home_lineup, lineup.home_team)
    process_lineup(match, lineup.away_lineup, lineup.away_team)
