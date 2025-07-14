from ..data_models.match import Match


def process_raw_match(match):

    try:
        game_week = match["league"]["round"].split()[-1]
    except AttributeError:
        print(f"Cannot create a match for game with date {match["fixture"]["date"]} \
              and home team {match["teams"]["home"]["id"]}")
        return False, None
    try:
        int(game_week)
        game_week = int(game_week)
        league_type = "league"
    except ValueError:
        return False, None

    try:
        if match["score"]["fulltime"]["home"] > match["score"]["fulltime"]["away"]:
            result = "Home Win"
        elif match["score"]["fulltime"]["home"] < match["score"]["fulltime"]["away"]:
            result = "Away Win"
        elif match["score"]["fulltime"]["home"] == match["score"]["fulltime"]["away"]:
            result = "Draw"
    except TypeError:
        result = "N/A"

    league_data = {}
    league_data["name"] = match["league"]["name"]
    league_data["id"] = match["league"]["id"]
    league_data["type"] = league_type

    return True, Match(date=match["fixture"]["date"],
                       fixture_id=match["fixture"]["id"],
                       home_team=match["teams"]["home"]["id"],
                       away_team=match["teams"]["away"]["id"],
                       score=match["score"],
                       game_week=game_week,
                       season=match["league"]["season"],
                       league=league_data,
                       result=result)
