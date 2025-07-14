from ..data_models.match import Match
from ..database.mongo_football_client import MongoFootballClient
from ..config import Config as conf
from ..data_models.observation import Observation
from ..data_models.standing import Standing
from tqdm import tqdm
from typing import List
from ..data_models.h2h import H2H
from ..data_models.team import Team
import jaro


def engineer_all_features():
    mfc = MongoFootballClient(conf.MONGO_URL)
    matches = mfc.matches.get_matches()
    print("Calculating league.type values")
    processed_matches = list(map(league_type, matches))
    return processed_matches


def league_type(match: Match) -> Match:
    try:
        int(match.game_week)
        league_type = "league"
    except ValueError:
        league_type = "cup"

    match.league["type"] = league_type
    return match


def calculate_form(form):
    form_to_return = {}
    if form is None:
        return {}
    for week in range(1, len(form) + 1):
        if week < 6:
            partial_form = "N" * (6 - week) + form[0:week - 1]
            form_to_return[str(week)] = partial_form
        else:
            form_to_return[str(week)] = form[week - 6:week - 1]
    return form_to_return


def create_training_data(update=True):
    mfc = MongoFootballClient(conf.MONGO_URL)
    matches = mfc.matches.get_finished_matches()
    for match in tqdm(matches):
        observation = create_obs_from_match(match)
        if observation is not None:
            if update:
                mfc.observations.update_observation(observation)
            else:
                mfc.observations.add_observation(observation)


def process_raw_h2h(matches: List[Match]) -> List[H2H]:
    returned_h2h = []
    for match in matches:
        home_goals = match.score["fulltime"]["home"]
        away_goals = match.score["fulltime"]["away"]
        home_team = match.home_team
        away_team = match.away_team
        if home_goals > away_goals:
            result = "Home Win"
        elif away_goals > home_goals:
            result = "Away Win"
        else:
            result = "Draw"
        returned_h2h.append(H2H(result, home_team, home_goals, away_team, away_goals))
    return returned_h2h


def calc_h2h(home_team, away_team, league_id, season, date):
    mfc = MongoFootballClient(conf.MONGO_URL)
    h2h_matches = mfc.matches.get_h2h(home_team, away_team, league_id, season, date)
    try:
        h2h_stats = process_raw_h2h(h2h_matches)
    except Exception as e:
        print(e)
        raise RuntimeError("Couldn't process raw h2h info")

    home_wins = 0
    home_draws = 0
    home_losses = 0
    home_goals_scored = 0
    home_conceded = 0
    for h2h in h2h_stats:
        if home_team == h2h.home_team:
            home_goals_scored += h2h.home_goals
            home_conceded += h2h.away_goals
            if h2h.result == "Home Win":
                home_wins += 1
            elif h2h.result == "Draw":
                home_draws += 1
            else:
                home_losses += 1
        elif home_team == h2h.away_team:
            home_goals_scored += h2h.away_goals
            home_conceded += h2h.home_goals
            if h2h.result == "Away Win":
                home_wins += 1
            elif h2h.result == "Draw":
                home_draws += 1
            else:
                home_losses += 1

    if len(h2h_stats) == 0:
        home_ppg = 0
        away_ppg = 0
        h2h_diff = 0
        home_gd = 0
    else:
        home_ppg = ((home_wins * 3) + home_draws) / (len(h2h_stats))
        away_ppg = ((home_losses * 3) + home_draws) / (len(h2h_stats))
        h2h_diff = home_ppg - away_ppg
        home_gd = home_goals_scored - home_conceded

    return h2h_diff, home_gd, len(h2h_stats)


def create_obs_from_match(match: Match) -> Observation:
    mfc = MongoFootballClient(conf.MONGO_URL)
    match_id = f"{match.date}-{match.home_team}"

    if match.game_week == 1:
        return None

    try:
        standing: Standing = mfc.standings.get_standings_from_team_date(match.league["id"], match.season, match.date)
        home_ppg = standing.standings[str(match.home_team)]["ppg"]
        home_plfg = standing.standings[str(match.home_team)]["plfg"]
        away_ppg = standing.standings[str(match.away_team)]["ppg"]
        away_plfg = standing.standings[str(match.away_team)]["plfg"]
        home_general_difficulty = standing.standings[str(match.home_team)]["difficulty"]
        away_general_difficulty = standing.standings[str(match.away_team)]["difficulty"]
        home_ppd = standing.standings[str(match.home_team)]["ppd"]
        away_ppd = standing.standings[str(match.away_team)]["ppd"]
        home_trend = standing.standings[str(match.home_team)]["trend"]
        away_trend = standing.standings[str(match.away_team)]["trend"]
        home_trend_diff = standing.standings[str(match.home_team)]["form_trend_diffs"]
        away_trend_diff = standing.standings[str(match.away_team)]["form_trend_diffs"]
    except Exception as e:
        print(e)
        print(f"Couldn't get standings for {match}")
        return None

    try:
        h2h_diff, home_gd, h2h_games = calc_h2h(match.home_team,
                                                match.away_team,
                                                match.league["id"],
                                                match.season,
                                                match.date)
    except Exception as e:
        print(e)
        print(f"Couldn't calculate h2h form for {match}")
        return None

    if match.game_week < 5:
        ten_gw = 1
        # five_gw = 1
    elif match.game_week < 10:
        ten_gw = 1
        # five_gw=0
    else:
        # five_gw=0
        ten_gw = 0

    observation = Observation(match_id=match_id,
                              home_ppg=home_ppg,
                              home_plfg=home_plfg,
                              away_ppg=away_ppg,
                              away_plfg=away_plfg,
                              home_general_difficulty=home_general_difficulty,
                              away_general_difficulty=away_general_difficulty,
                              result=match.result,
                              home_relative_form=home_ppg - home_plfg,
                              away_relative_form=away_ppg - away_plfg,
                              points_diff=home_ppg - away_ppg,
                              plfg_diff=home_plfg - away_plfg,
                              home_ppd=home_ppd,
                              away_ppd=away_ppd,
                              ppd_diff=home_ppd - away_ppd,
                              h2h_games=h2h_games,
                              h2h_diff=h2h_diff,
                              h2h_gd_diff=home_gd,
                              home_trend=home_trend,
                              home_trend_diff=home_trend_diff,
                              away_trend=away_trend,
                              away_trend_diff=away_trend_diff,
                              before_gw_ten=ten_gw)
    return observation


def calculate_difficulty(team, standings: Standing, last_games: List[Match]):
    difficulties = []
    for match in last_games:
        if match.home_team != team:
            difficulties.append(standings.standings[str(match.home_team)]["ppg"])
        else:
            difficulties.append(standings.standings[str(match.away_team)]["ppg"])

    return sum(difficulties) / len(last_games)


def calulate_last_five_ppg(form: List[str]):
    wins = form.count("W")
    draws = form.count("D")
    not_played = form.count("N")

    return (((wins * 3) + draws) / (5 - not_played))


def get_ppg(standing: Standing, team):
    return standing.standings[str(team)]["ppg"]


def create_general_form(match: Match, home_last_games, away_last_games):
    home_form = calculate_general_form(home_last_games, match.home_team)
    away_form = calculate_general_form(away_last_games, match.away_team)

    return home_form, away_form


def calculate_general_form(matches: List[Match], team: int):
    form = []
    for game in matches:
        if game.home_team == team:
            if game.result == "Home Win":
                form.append("W")
            elif game.result == "Away Win":
                form.append("L")
            else:
                form.append("D")
        else:
            if game.result == "Home Win":
                form.append("L")
            elif game.result == "Away Win":
                form.append("W")
            else:
                form.append("D")
    form = (form + ["N"] * 5)[:5]
    return form


def create_local_form(match: Match):
    mfc = MongoFootballClient(conf.MONGO_URL)

    home_home_matches = mfc.matches.get_last_5_games(match.league["id"], match.season, match.home_team, match.date, False, True)
    home_home_form = calculate_local_form(home_home_matches)
    away_away_matches = mfc.matches.get_last_5_games(match.league["id"], match.season, match.away_team, match.date, False, False)
    away_away_form = calculate_local_form(away_away_matches, False)

    home_wins = home_home_form.count("W")
    home_draws = home_home_form.count("D")
    home_losses = home_home_form.count("L")
    home_unknown = home_home_form.count("N")
    away_wins = away_away_form.count("W")
    away_draws = away_away_form.count("D")
    away_losses = away_away_form.count("L")
    away_unknown = away_away_form.count("N")

    return home_home_form, (home_wins, home_draws, home_losses, home_unknown), \
        away_away_form, (away_wins, away_draws, away_losses, away_unknown)


def calculate_local_form(matches: List[Match], home: bool = True) -> List[str]:
    form = []
    for match in matches:
        if home:
            if match.result == "Home Win":
                form.append("W")
            elif match.result == "Draw":
                form.append("D")
            else:
                form.append("L")
        else:
            if match.result == "Away Win":
                form.append("W")
            elif match.result == "Draw":
                form.append("D")
            else:
                form.append("L")
    form = (form + ["N"] * 5)[:5]
    return form


def map_ids():
    mfc = MongoFootballClient(conf.MONGO_URL)
    af_teams = mfc.teams.get_all_teams()
    betfair_teams = mfc.odds.get_betfair_team_names()
    complete_matches = 0
    for betfair_team in tqdm(betfair_teams):
        if isinstance(betfair_team, str):
            closest_match = None
            closest_score = 0
            for af_team in af_teams:
                if af_team.name == betfair_team and closest_score < 1:
                    closest_match = af_team
                    closest_score = 1
                    complete_matches += 1
                else:
                    match = jaro.jaro_winkler_metric(af_team.name, betfair_team)
                    if match > closest_score:
                        closest_match = af_team
                        closest_score = match

            if closest_score >= 0.95:
                team = Team(id=closest_match.id,
                            name=betfair_team,
                            source="betfair")
                mfc.teams.add_team(team)
    print(complete_matches / len(betfair_teams))


def map_odd_ids():
    mfc = MongoFootballClient(conf.MONGO_URL)
    odds = mfc.odds.get_odds(True)
    for odd in tqdm(odds):
        changed = False
        original_home_team = odd.home_team
        if isinstance(original_home_team, str):
            home_team = mfc.teams.get_team_from_name(odd.home_team)
            if home_team is not None:
                odd.home_team = home_team
                changed = True

        original_away_team = odd.away_team
        if isinstance(original_away_team, str):
            away_team = mfc.teams.get_team_from_name(odd.away_team)
            if away_team is not None:
                odd.away_team = away_team
                changed = True

        if isinstance(odd.away_team, str) ^ isinstance(odd.home_team, str):
            if isinstance(odd.home_team, str):
                match = mfc.matches.get_match(odd.date, away_team=odd.away_team)
                if match is not None:
                    home_team = match.home_team
                    odd.home_team = home_team
                    mfc.teams.add_team(Team(home_team, original_home_team, "betfair"))
                    changed = True
                else:
                    print("Deleting Cup game")
                    mfc.odds.del_odd(odd.date, original_home_team)

            elif isinstance(odd.away_team, str):
                match = mfc.matches.get_match(odd.date, home_team=odd.home_team)
                if match is not None:
                    away_team = match.away_team
                    odd.away_team = away_team
                    mfc.teams.add_team(Team(away_team, original_away_team, "betfair"))
                    changed = True
                else:
                    print(f"Deleting Cup game, {odd.date} with home team {odd.home_team}")
                    mfc.odds.del_odd(odd.date, original_home_team)

        if changed:
            print("Updating odds")
            mfc.odds.update_odd(odd, original_home_team)


def create_standings(league_id, season, test=False):
    mfc = MongoFootballClient(conf.MONGO_URL, test)

    seasons_matches = mfc.matches.get_leagues_matches(league_id, season)

    if not mfc.standings.standing_exists(league_id, season):
        print(f"Creating standings for league {league_id}, season {season}, test collection - {test}")
        initialise_table(league_id, season, test)

    update_batches: List[List[Match]] = []
    date = ""
    match_batch: List[Match] = []
    for ind_match in seasons_matches:
        if len(update_batches) == 0 and len(match_batch) == 0:
            date = ind_match.date
            match_batch.append(ind_match)
        else:
            match_date = ind_match.date
            if match_date == date:
                match_batch.append(ind_match)
            else:
                date = match_date
                update_batches.append(match_batch)
                match_batch = [ind_match]
    if len(match_batch) > 0:
        update_batches.append(match_batch)

    last_date = "1970-01-01T00:00:00+00:00"
    for batch in update_batches:
        update_table(batch, last_date, test)
        last_date = batch[0].date


def update_table(match_batch: List[Match], last_date, test=False):
    mfc = MongoFootballClient(conf.MONGO_URL, test)
    standing = mfc.standings.get_standings(last_date, match_batch[0].league["id"], match_batch[0].season)

    standing_exists = mfc.standings.get_standings(match_batch[0].date, match_batch[0].league["id"], match_batch[0].season)
    if standing_exists is None:
        try:
            for match in match_batch:
                home_last_games = mfc.matches.get_last_5_games(match.league["id"],
                                                       match.season,
                                                       match.home_team,
                                                       match.date,
                                                       True)
                away_last_games = mfc.matches.get_last_5_games(match.league["id"],
                                                       match.season,
                                                       match.away_team,
                                                       match.date,
                                                       True)
                home_general_form, away_general_form = create_general_form(match, home_last_games, away_last_games)
                home_form_ppg = calulate_last_five_ppg(home_general_form)
                away_form_ppg = calulate_last_five_ppg(away_general_form)

                home_team_new_played = standing.standings[str(match.home_team)]["played"] + 1
                away_team_new_played = standing.standings[str(match.away_team)]["played"] + 1

                if match.result == "Home Win":
                    home_team_new_won = standing.standings[str(match.home_team)]["won"] + 1
                    home_team_new_lost = standing.standings[str(match.home_team)]["lost"]
                    home_team_new_draw = standing.standings[str(match.home_team)]["draw"]
                    home_team_new_points = standing.standings[str(match.home_team)]["points"] + 3
                    away_team_new_won = standing.standings[str(match.away_team)]["won"]
                    away_team_new_lost = standing.standings[str(match.away_team)]["lost"] + 1
                    away_team_new_draw = standing.standings[str(match.away_team)]["draw"]
                    away_team_new_points = standing.standings[str(match.away_team)]["points"]
                elif match.result == "Away Win":
                    home_team_new_won = standing.standings[str(match.home_team)]["won"]
                    home_team_new_lost = standing.standings[str(match.home_team)]["lost"] + 1
                    home_team_new_draw = standing.standings[str(match.home_team)]["draw"]
                    home_team_new_points = standing.standings[str(match.home_team)]["points"]
                    away_team_new_won = standing.standings[str(match.away_team)]["won"] + 1
                    away_team_new_lost = standing.standings[str(match.away_team)]["lost"]
                    away_team_new_draw = standing.standings[str(match.away_team)]["draw"]
                    away_team_new_points = standing.standings[str(match.away_team)]["points"] + 3
                elif match.result == "Draw":
                    home_team_new_won = standing.standings[str(match.home_team)]["won"]
                    home_team_new_lost = standing.standings[str(match.home_team)]["lost"]
                    home_team_new_draw = standing.standings[str(match.home_team)]["draw"] + 1
                    home_team_new_points = standing.standings[str(match.home_team)]["points"] + 1
                    away_team_new_won = standing.standings[str(match.away_team)]["won"]
                    away_team_new_lost = standing.standings[str(match.away_team)]["lost"]
                    away_team_new_draw = standing.standings[str(match.away_team)]["draw"] + 1
                    away_team_new_points = standing.standings[str(match.away_team)]["points"] + 1
                else:
                    raise RuntimeError(f"Result for finished match cannot be {match.result}")

                home_new_ppg = home_team_new_points / home_team_new_played
                away_new_ppg = away_team_new_points / away_team_new_played

                standing.standings[str(match.home_team)] = {
                "played": home_team_new_played,
                "won": home_team_new_won,
                "lost": home_team_new_lost,
                "draw": home_team_new_draw,
                "points": home_team_new_points,
                "ppg": home_new_ppg
            }
                standing.standings[str(match.away_team)] = {
                "played": away_team_new_played,
                "won": away_team_new_won,
                "lost": away_team_new_lost,
                "draw": away_team_new_draw,
                "points": away_team_new_points,
                "ppg": away_new_ppg
            }

                home_general_difficulty = calculate_difficulty(match.home_team, standing, home_last_games)
                away_general_difficulty = calculate_difficulty(match.away_team, standing, away_last_games)
                if home_general_difficulty == 0:
                    home_ppd = home_form_ppg / 1
                else:
                    home_ppd = home_form_ppg * home_general_difficulty
                if away_general_difficulty == 0:
                    away_ppd = away_form_ppg / 1
                else:
                    away_ppd = away_form_ppg * away_general_difficulty

                standings_history = mfc.standings.get_last_standings(match.league["id"], match.season, match.date)
                home_trend, home_form_diffs = get_ppd_rolling_window(standings_history, match.home_team)
                away_trend, away_form_diffs = get_ppd_rolling_window(standings_history, match.away_team)

                standing.date = match.date

                standing.standings[str(match.home_team)]["plfg"] = home_form_ppg
                standing.standings[str(match.home_team)]["difficulty"] = home_general_difficulty
                standing.standings[str(match.home_team)]["ppd"] = home_ppd
                standing.standings[str(match.home_team)]["trend"] = home_trend
                standing.standings[str(match.home_team)]["form_trend_diffs"] = home_form_diffs

                standing.standings[str(match.away_team)]["plfg"] = away_form_ppg
                standing.standings[str(match.away_team)]["difficulty"] = away_general_difficulty
                standing.standings[str(match.away_team)]["ppd"] = away_ppd
                standing.standings[str(match.away_team)]["trend"] = away_trend
                standing.standings[str(match.away_team)]["form_trend_diffs"] = away_form_diffs

            mfc.standings.add_standing(standing)
        except Exception as e:
            print(f"Cannot ingest league {match.league["id"]}, season {match.season}")
            print(e)
    else:
        pass


def get_ppd_rolling_window(standings: List[Standing], team):
    history = []
    form_now = standings[0].standings[str(team)]["ppd"]
    team_played = standings[0].standings[str(team)]["played"]
    for standing in standings:
        if standing.standings[str(team)]["played"] < team_played:
            history.append(standing.standings[str(team)]["ppd"])
            team_played = standing.standings[str(team)]["played"]
        if len(history) == 5:
            break

    form_diffs = []
    last_form = form_now
    improve = 0
    worse = 0
    for form in history:
        if form < last_form:
            improve += 1
        elif form > last_form:
            worse += 1
        form_diff = last_form - form
        form_diffs.append(form_diff)
        last_form = form

    trend = improve - worse
    diffs = sum(form_diffs)
    return trend, diffs


def initialise_table(league_id, season, test):
    mfc = MongoFootballClient(conf.MONGO_URL, test)

    league = mfc.leagues.get_league(league_id, season)
    try:
        teams_in_league = league.teams
    except:
        print(f"No teams can be found for league {league_id} and season {season}")
        teams_in_league = []

    initial_standings = {
        "played": 0,
        "won": 0,
        "lost": 0,
        "draw": 0,
        "points": 0,
        "ppg": 0,
        "plfg": 0,
        "difficulty": 0,
        "ppd": 0,
        "trend": 0,
        "form_trend_diffs": 0
    }

    standings = {}
    for team in teams_in_league:
        standings[str(team)] = initial_standings

    mfc.standings.add_standing(Standing(league_id=league_id,
                              season=season,
                              date="1970-01-01T00:00:00+00:00",
                              standings=standings))


def update_obs(obs: Observation):
    mfc = MongoFootballClient(conf.MONGO_URL)

    obs.home_plfg = obs.home_plfg / 5
    obs.away_plfg = obs.away_plfg / 5

    mfc.observations.update_observation(obs)
