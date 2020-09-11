import tools
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time
from progressbar import progressbar


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect("playerDB.db")
    except Error as e:
        print(e)

    return conn


def update_DB(conn):
    c = conn.cursor()
    # c.execute("CREATE TABLE stats (userID INTEGER, name TEXT, timestamp TEXT, rank INTEGER, AvgBPM FLOAT, MaxBPM FLOAT, MaxCombo INTEGER, PlayedRounds INTEGER, PlayedMin FLOAT, Score FLOAT, Wins INTEGER, WeekPlaytime FLOAT, NetScore FLOAT)")
    # c.execute("ALTER TABLE stats ADD COLUMN WeekPlaytime FLOAT")
    # c.execute("ALTER TABLE stats ADD COLUMN NetScore FLOAT")
    tools.scrape_leaderboard()
    player_list = []
    current_dump = pd.read_pickle("Player_Dump").to_dict("records")
    for player in current_dump:
        player_list.append(str(player["UserId"]))

    now = datetime.now()

    for userID in progressbar(player_list):
        player_data = next(
            item for item in current_dump if item["UserId"] == int(userID)
        )
        if player_data["Rank"] < 600:
            week = calculate_week_playtime(select_player_by_id(conn, int(userID)))
            netscore = calcualte_week_net_score(select_player_by_id(conn, int(userID)))
        else:
            week, netscore = 0.0, 0.0

        c.execute(
            "INSERT INTO stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                player_data["UserId"],
                player_data["Name"],
                now.strftime("%d/%m/%Y %H:%M"),
                player_data["Rank"],
                player_data["AVGRoundBpm"],
                player_data["MAXRoundBpm"],
                player_data["MaxCombo"],
                player_data["PlayedRounds"],
                player_data["Playedmin"],
                player_data["Score"],
                player_data["Wins"],
                week,
                netscore,
            ),
        )

    conn.commit()


def select_player_by_id(conn, userID):
    """
    Query SQL DB by userID and return a list of rows as dicts
    """
    player = None
    c = conn.cursor()
    c.execute("SELECT * FROM stats WHERE userID = ?", (str(userID),))

    rows = c.fetchall()  # list of tuples
    stats = to_dict(rows)

    return stats


def select_player_by_name(conn, username):
    """
    Query SQL DB by username and return a list of rows as dicts
    """
    player = None
    c = conn.cursor()
    c.execute("SELECT * FROM stats WHERE name = ?", (username,))

    rows = c.fetchall()  # list of tuples
    stats = to_dict(rows)

    return stats


def to_dict(rows):
    """
    Convert a list of tuples to dicts
    """
    keys = [
        "userID",
        "name",
        "timestamp",
        "rank",
        "avgbpm",
        "maxbpm",
        "maxcombo",
        "playedrounds",
        "playedmin",
        "score",
        "wins",
        "WeekPlaytime",
        "netscore",
    ]
    stats = []
    for tuple in rows:
        stats.append(dict(zip(keys, tuple)))

    return stats


def calculate_peak(stats):
    """
    Returns peak rank given list of stats as dicts
    """
    return min([element["rank"] for element in stats])


def calculate_week_playtime(stats):
    today = datetime.today()
    week_ago = today - timedelta(days=7)

    week_times = [
        element["playedmin"]
        for element in stats
        if datetime.strptime(element["timestamp"], "%d/%m/%Y %H:%M") > week_ago
    ]

    if len(week_times) > 0:
        return round(max(week_times) - min(week_times), 1)
    else:
        return 0


def calcualte_week_net_score(stats):
    today = datetime.today()
    week_ago = today - timedelta(days=7)

    scores = [
        element["score"]
        for element in stats
        if datetime.strptime(element["timestamp"], "%d/%m/%Y %H:%M") > week_ago
    ]

    if len(scores) > 0:
        return round(scores[-1] - scores[0], 1)
    else:
        return 0


def calculate_month_winrate(stats):
    today = datetime.today()
    month_ago = today - timedelta(days=30)

    month_wins = [
        element["wins"]
        for element in stats
        if datetime.strptime(element["timestamp"], "%d/%m/%Y %H:%M") > month_ago
    ]

    month_rounds = [
        element["playedrounds"]
        for element in stats
        if datetime.strptime(element["timestamp"], "%d/%m/%Y %H:%M") > month_ago
    ]

    wins = max(month_wins) - min(month_wins)
    rounds = max(month_rounds) - min(month_rounds)
    if rounds != 0:
        return round(wins / rounds * 100, 1)
    else:
        return 0


def calculate_active(conn):
    c = conn.cursor()
    c.execute(
        "SELECT MAX(datetime(substr(timestamp, 7, 4) || '-' || substr(timestamp, 4, 2) || '-' || substr(timestamp, 1, 2) || substr(timestamp, 12, 5))), userID, name, WeekPlaytime FROM stats GROUP BY userID ORDER BY WeekPlaytime DESC",
    )
    rows = c.fetchall()

    keys = ["timestamp", "UserId", "Name", "WeekPlaytime"]
    active_dict = []
    for tuple in rows:
        active_dict.append(dict(zip(keys, tuple)))

    return active_dict


def calculate_net_scores(conn):
    c = conn.cursor()
    c.execute(
        "SELECT MAX(datetime(substr(timestamp, 7, 4) || '-' || substr(timestamp, 4, 2) || '-' || substr(timestamp, 1, 2) || substr(timestamp, 12, 5))), userID, name, NetScore FROM stats WHERE NetScore != ? GROUP BY userID ORDER BY NetScore DESC",
        (0.0,),
    )
    rows = c.fetchall()

    keys = ["timestamp", "UserId", "Name", "NetScore"]
    net_scores_dict = []
    for tuple in rows:
        net_scores_dict.append(dict(zip(keys, tuple)))

    return net_scores_dict


if __name__ == "__main__":
    update_DB(create_connection("playerDB.db"))
    # active = calculate_active(conn)[0:20]
    # for i in active:
    #     print(i)
    # print("\n")
    # net_scores = calculate_net_scores(conn)[0:20]
    # for i in net_scores:
    #     print(i)
    # calculate_peak(select_player_by_name(conn, "z2sam"))
    # print(calculate_week_playtime(select_player_by_name(conn, "Shay")))
    # print(calculate_month_winrate(select_player_by_name(conn, "Shay")))
    # print(calcualte_week_net_score(select_player_by_name(conn, "Azteca")))

    while True:
        now = datetime.now()
        print("It is:", now.strftime("%d/%m/%Y %H:%M"))
        if (
            now.minute % 10 == 0
        ):  # pulling q10 minutes, update_DB takes 8-10 minutes now with filtering of rank < 1000
            print(
                "Updating Player_Dump and playerDB.db", now.strftime("%d/%m/%Y %H:%M")
            )
            try:
                update_DB(create_connection("playerDB.db"))
                print("Done with sucess!")
            except Exception as e:
                print(e)
                print("Done with failure!")

        time.sleep(60)
