from src.ingestors.match_ingestor import ApiFootball
from src.config import Config as conf
from tqdm import tqdm
from src.database.mongo_football_client import MongoFootballClient
from src.utils.feature_engineering import create_standings, create_obs_from_match
from src.ingestors.betfair_ingestor import BetfairClient
from src.data_models.player_stats import PlayerStats

af = ApiFootball(base_url=conf.FOOTBALL_API_URL, api_key=conf.FOOTBALL_API_KEY)
mfc = MongoFootballClient(conf.MONGO_URL)

# stats = af.get_player_stats(1208021)
# print(stats)



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

stats_league = af.get_lineup_leagues()
# current_min_league = af.get_all_leagues()
# print(len(current_stats_league))
# print(len(current_min_league))

for league in tqdm(stats_league):
    matches = af.get_seasons_matches(league[0], league[1])
    for match in matches:
        # if mfc.match_exists(match.league["id"], match.season, match.home_team, match.away_team):
        #     #mfc.update_matches([match])
        #     continue
        # else:
        mfc.add_matches([match], test=True)

for league in tqdm(stats_league):
    create_standings(league[0], league[1], test=True)

matches = mfc.get_finished_matches(True)

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
#     seasons_matches = af.get_seasons_matches(league[0], league[1])
#     for match in seasons_matches:
#         stats = af.get_lineups(match.fixture_id)
#         if stats:
#             for player in stats:
#                 latest_stats  = mfc.get_player_stats(player.player_id, player.team, match.date, test=True)
#                 if latest_stats is None:
#                     result = match.result
#                     if (result == "Home Win" and player.team == match.home_team) or (result == "Away Win" and player.team == match.away_team):
#                         points = 3
#                     elif result == "Draw":
#                         points = 1
#                     else:
#                         points = 0
#                     if player.started:
#                         player_stat = PlayerStats(player_id=player.player_id,
#                                                 team=player.team,
#                                                 date=match.date,
#                                                 played=1,
#                                                 played_ppg=points,
#                                                 not_played=0,
#                                                 not_played_ppg=0)
#                     else:
#                         player_stat = PlayerStats(player_id=player.player_id,
#                                                 team=player.team,
#                                                 date=match.date,
#                                                 played=0,
#                                                 played_ppg=0,
#                                                 not_played=1,
#                                                 not_played_ppg=points)
#                         print(match.fixture_id)
#                     mfc.add_player_stats(player_stat, test=True)
#                 else:
#                     if (result == "Home Win" and player.team == match.home_team) or (result == "Away Win" and player.team == match.away_team):
#                         points = 3
#                     elif result == "Draw":
#                         points = 1
#                     else:
#                         points = 0
#                     if player.started:
#                         played = latest_stats.played + 1
#                         not_played = latest_stats.not_played
#                         played_ppg = ((latest_stats.played_ppg * latest_stats.played) + points) / played
#                         not_played_ppg = latest_stats.not_played_ppg
#                     else:
#                         not_played = latest_stats.not_played + 1
#                         played = latest_stats.played
#                         not_played_ppg = ((latest_stats.not_played_ppg * latest_stats.not_played) + points) / not_played
#                         played_ppg = latest_stats.played_ppg
#                     new_stats = PlayerStats(player_id=player.player_id,
#                                             team=player.team,
#                                             date=match.date,
#                                             played=played,
#                                             played_ppg=played_ppg,
#                                             not_played=not_played,
#                                             not_played_ppg=not_played_ppg)
#                     mfc.add_player_stats(new_stats, test=True)
#     if total > 0:
#         break
#     total += 1