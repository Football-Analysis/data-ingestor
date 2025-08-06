from src.ingestors.match_ingestor import ApiFootball
from src.config import Config as conf
from tqdm import tqdm
from src.database.mongo_football_client import MongoFootballClient
from src.utils.feature_engineering import create_standings, create_obs_from_match
from src.ingestors.betfair_ingestor import BetfairClient
from src.data_models.player_stats import PlayerStats
from time import time
from src.data_models.lineup import Lineup

af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
mfc = MongoFootballClient(conf.MONGO_URL, test=True)

matches = mfc.matches.get_matches()
total = 0
for match in tqdm(matches):
    exists = mfc.player_stats.check_exists(match.home_team, match.date)
    if not exists:
        continue
    total += 1
print(total)

# stats = af.get_player_stats(1208021)
# print(stats)

# all_leagues = af.get_all_leagues_lineups()
#stats_league = af.get_lineup_leagues()
# for league in tqdm(stats_league):
#     create_standings(league[0], league[1], test=True)


# bc = BetfairClient("",conf.BETFAIR_API_KEY)
# bc.get_downloaded_data(2024, 9, 27)

# no_player_leagues = af.get_all_leagues()
# player_leagues = af.get_player_stats_leagues()
# injury_leagues = af.get_injury_leagues()
# everything_leagues = af.get_max_leagues()
# lineup_leagues = af.get_all_leagues_lineups()
# print(len(no_player_leagues))
# print(len(player_leagues))
# print(len(injury_leagues))
# print(len(everything_leagues))
# print(len(lineup_leagues))


# print(len(stats_league))
# # current_min_league = af.get_all_leagues()
# # print(len(current_stats_league))
# # print(len(current_min_league))

# for league in tqdm(stats_league):
#     matches = af.get_seasons_matches(league[0], league[1])
#     for match in matches:
#         # if mfc.match_exists(match.league["id"], match.season, match.home_team, match.away_team):
#         #     #mfc.update_matches([match])
#         #     continue
#         # else:
#         mfc.add_matches([match], test=True)

# for league in tqdm(stats_league):
#     create_standings(league[0], league[1], test=True)

# matches = mfc.get_finished_matches(True)

# no_player_leagues = af.get_all_leagues()
# player_leagues = af.get_player_stats_leagues()
# injury_leagues = af.get_injury_leagues()
# everything_leagues = af.get_max_leagues()
# lineup_leagues = af.get_all_leagues_lineups()
# print(len(no_player_leagues))
# print(len(player_leagues))
# print(len(injury_leagues))
# print(len(everything_leagues))
# print(len(lineup_leagues))


# matches = mfc.get_finished_matches(True)

# for match in tqdm(matches):
#     obs = create_obs_from_match(match)
#     if obs is not None:
#         mfc.add_observation(obs, True)



# total = 0
# for league in tqdm(stats_league):
#     start = time()
#     season = league[1]
#     seasons_matches = af.get_seasons_matches(league[0], league[1])
#     seasons_matches.sort(key=lambda x: x.date)
#     for match in seasons_matches:
#         exists = mfc.player_stats.check_exists(match.home_team, match.date)
#         if exists:
#             continue
#         stats = af.get_lineups(match.fixture_id)
#         if not stats:
#             continue
#         for team in stats:
#             team_id = team[0].team
#             players_played = []
#             for player in team:
#                 players_played.append(player.player_id)
#                 latest_stats = mfc.player_stats.get_player_stats(player.player_id, player.team, season, match.date)
#                 try:
#                     standings = mfc.standings.get_last_standings(league[0], league[1], match.date)[0]
#                 except:
#                     break
#                 team_played = standings.standings[str(player.team)]["played"]
#                 team_ppg = standings.standings[str(player.team)]["ppg"]
#                 result = match.result
#                 if (result == "Home Win" and player.team == match.home_team) or (result == "Away Win" and player.team == match.away_team):
#                     points = 3
#                 elif result == "Draw":
#                     points = 1
#                 else:
#                     points = 0
#                 if latest_stats is None:
#                     player_stat = PlayerStats(player_id=player.player_id,
#                                                 team=player.team,
#                                                 season=season,
#                                                 date=match.date,
#                                                 played=1,
#                                                 played_ppg=points,
#                                                 not_played=team_played,
#                                                 not_played_ppg=team_ppg)
#                     mfc.player_stats.add_player_stats(player_stat)
#                 else:
#                     played = latest_stats.played + 1
#                     not_played = latest_stats.not_played
#                     played_ppg = ((latest_stats.played_ppg * latest_stats.played) + points) / played
#                     not_played_ppg = latest_stats.not_played_ppg
#                     new_stats = PlayerStats(player_id=player.player_id,
#                                             team=player.team,
#                                             season=season,
#                                             date=match.date,
#                                             played=played,
#                                             played_ppg=played_ppg,
#                                             not_played=not_played,
#                                             not_played_ppg=not_played_ppg)
#                     mfc.player_stats.add_player_stats(new_stats)
#             not_played = mfc.player_stats.get_non_played_players(players_played, team_id, season)
#             for player in not_played:
#                 try:
#                     standings = mfc.standings.get_last_standings(league[0], league[1], match.date)[0]
#                 except:
#                     break
#                 player_stats = mfc.player_stats.get_player_stats(player, team_id, season, match.date)
#                 if player_stats is None:
#                     continue
#                 didnt_play = PlayerStats(player_id=player_stats.player_id,
#                             team=player_stats.team,
#                             date=match.date,
#                             season=season,
#                             played=player_stats.played,
#                             played_ppg=player_stats.played_ppg,
#                             not_played=player_stats.not_played + 1,
#                             not_played_ppg=((player_stats.not_played_ppg * player_stats.not_played) + points) / (player_stats.not_played + 1))
#                 mfc.player_stats.add_player_stats(didnt_play)
#     end = time()
#     print(f"Ingested a league {league[0]}, season {league[1]} in {end-start} seconds")
#     #break
#     # if total > 0:
#     #     break
#     # total += 1


# for league in tqdm(stats_league):
#     season = league[1]
#     start = time()
#     seasons_matches = af.get_seasons_matches(league[0], league[1])
#     end = time()
#     #print(f"Time to get the seasons matches: {end-start}")
#     seasons_matches.sort(key=lambda x: x.date)
#     start_matches = time()
#     if len(seasons_matches) == 0:
#         continue
#     exists = mfc.lineups.check_exists(seasons_matches[0].fixture_id)
#     if exists:
#         continue
#     for match in seasons_matches:
#         start_match = time()

#         start_check = time()
#         exists = mfc.lineups.check_exists(match.fixture_id)
#         if exists:
#             continue
#         lineup = af.get_lineups(match.fixture_id)
#         if not lineup:
#             end_check = time()
#             #print(f"Time to do all checks for a single match {end_check-start_check}")
#             continue
#         #print(f"Time to do all checks for a single match {end_check-start_check}")

#         home_team = []
#         away_team = []
#         start_process = time()
#         for team in lineup:
#             for player in team:
#                 if player.team == match.home_team:
#                     home_team.append(player.player_id)
#                 elif player.team == match.away_team:
#                     away_team.append(player.player_id)
#                 else:
#                     print(f"Cannot assign player {player.player_id} to home or away team, this should not be possible")
#                     #raise RuntimeError(f"Cannot assign player {player.player_id} to home or away team, this should not be possible")
        
#         lineup_to_save = Lineup(match.fixture_id, match.date, match.home_team, home_team, match.away_team, away_team)
#         mfc.lineups.add_lineup(lineup_to_save)
#         end_process = time()
#         end_match = time()
#         #print(f"Time to process one match: {end_match-start_match}")
#     end_matches = time()
#     #print(f"Time to process all matche sin a season {end_matches-start_matches}")
