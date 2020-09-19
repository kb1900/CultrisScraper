from flask import Flask
import database, tools
import json, pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "Nothing to see here m8"


@app.route("/daily_stats_by_id/<userid>")
def daily_stats_by_id(userid):
    user = database.select_daily_stats_by_id(
        userid, database.create_connection("playerDB.db")
    )
    return json.dumps(user)


@app.route("/current_stats_by_id/<userid>")
def stats_by_id(userid):
    stats = database.select_player_by_id(
        database.create_connection("playerDB.db"), userid
    )
    peak_rank = database.calculate_peak(stats)
    recent_mins = database.calculate_week_playtime(stats)
    net_score = database.calcualte_week_net_score(stats)
    month_win_rate = database.calculate_month_winrate(stats)

    response = stats[-1]
    response["peak"] = peak_rank
    response["recent_mins"] = recent_mins
    response["net_score"] = net_score
    response["month_win_rate"] = month_win_rate

    return json.dumps(response)


@app.route("/current_stats_by_name/<username>")
def stats_by_name(username):
    stats = database.select_player_by_name(
        database.create_connection("playerDB.db"), username
    )
    peak_rank = database.calculate_peak(stats)
    recent_mins = database.calculate_week_playtime(stats)
    net_score = database.calcualte_week_net_score(stats)
    month_win_rate = database.calculate_month_winrate(stats)

    response = stats[-1]
    response["peak"] = peak_rank
    response["recent_mins"] = recent_mins
    response["net_score"] = net_score
    response["month_win_rate"] = month_win_rate

    return json.dumps(response)


@app.route("/rankings/<int:page>")
def rankings(page=1):
    player_dict = tools.rankings_query(page)
    return json.dumps(player_dict)


@app.route("/full_rankings/")
def full_rankings():
    player_dict = tools.full_rankings_query()
    return json.dumps(player_dict)


@app.route("/active_rankings/<int:page>")
def active_rankings(page=1):
    start = 20 * (page - 1)
    end = start + 20
    player_dict = database.calculate_active(database.create_connection("playerDB.db"))[
        start:end
    ]
    return json.dumps(player_dict)


@app.route("/full_active_rankings/")
def full_active_rankings():
    player_dict = database.calculate_active(database.create_connection("playerDB.db"))
    return json.dumps(player_dict)


@app.route("/netscores_rankings/")
def netscores_rankings():
    player_dict = database.calculate_net_scores(
        database.create_connection("playerDB.db")
    )
    return json.dumps(player_dict)


@app.route("/player_by_name/<username>")
def userid_by_name(username):
    df = pd.read_pickle("Player_Dump")
    player_dict = tools.player_stats_by_name(username, df)

    if not player_dict:
        player_dict = tools.player_stats_by_name_fuzzy(username, df)
    return json.dumps(player_dict)


if __name__ == "__main__":
    context = (
        "/etc/letsencrypt/live/cultris.net/fullchain.pem",
        "/etc/letsencrypt/live/cultris.net/privkey.pem",
    )  # certificate and key files
    app.run(host="0.0.0.0", port="5000", debug=True, ssl_context=context)
