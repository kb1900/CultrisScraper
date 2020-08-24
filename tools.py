import json
import requests
import pandas as pd
from datetime import datetime
import pickle, dill  # TODO: switch to json for data out and in
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time
import re

PROFILE_URL = re.compile(
    "<?http:\/\/gewaltig\.net\/ProfileView\.aspx\?userid=([0-9]+).*"
)
PROFILE_ID = re.compile(".*?([0-9]+).*")


def get_online_players():
    """
    Returns list of players where each player is a dict
    """
    url = "http://gewaltig.net/liveinfo.aspx"
    response = requests.get(url)
    players = response.json()["players"]
    # rooms = response.json()['rooms']
    return players


def show_online_players():
    """
    Returns list of players where each player is a formatted string of "name (status)"
    """
    online = get_online_players()
    ffa_players = [
        x["name"]
        for x in online
        if not x["afk"] and not x["challenge"] and x["room"] == 0
    ]
    rookie_players = [
        x["name"]
        for x in online
        if not x["afk"] and not x["challenge"] and x["room"] == 1
    ]
    cheese_players = [
        x["name"]
        for x in online
        if not x["afk"] and not x["challenge"] and x["room"] == 2
    ]
    non_ffa_players = [
        x["name"]
        for x in online
        if not x["afk"] and not x["challenge"] and x["room"] not in [0, 1, 2]
    ]
    team_players = [
        x["name"] + " (" + x["team"] + ")" for x in online if not x["afk"] and x["team"]
    ]
    challenge_players = [
        x["name"] + " (" + x["challenge"] + ")" for x in online if x["challenge"]
    ]
    afk_players = [x["name"] for x in online if x["afk"]]

    players = (
        ffa_players
        + rookie_players
        + cheese_players
        + challenge_players
        + afk_players
        + team_players
    )
    for i in players:
        print(i)

    return [
        ffa_players,
        rookie_players,
        cheese_players,
        challenge_players,
        team_players,
        afk_players,
    ]


def get_player_data_by_id(player_id):
    url = "https://gewaltig.net/ProfileView.aspx?userid=" + str(player_id)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    player_name = text[text.find("Display Name") + 29 : text.find("Avatar") - 3]

    player_info = text[text.find("Rank") : text.find("%")]

    player_info_raw = player_info.splitlines()
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&() '
    player_info = []
    for i in player_info_raw:
        player_info.append("".join(c for c in i if c not in chars))

    player_stats = {}
    player_stats["id"] = player_id
    player_stats["Name"] = player_name
    player_stats["Score"] = player_info[0]
    player_stats["Rank"] = player_info[1]
    player_stats["Max Combo"] = player_info[2]
    player_stats["Max BPM"] = player_info[3]
    player_stats["AVG BPM"] = player_info[4]
    player_stats["Games Won"] = player_info[5]
    player_stats["Games Played"] = player_info[6]
    player_stats["Win %"] = player_info[7]

    # print(player_stats)
    return player_stats


def update_playerDB():
    """
    Goal is to have a player_DB with every userID (as this is static, unlike usernames)
    Then each time a new player_dump is created, we append that user's stats as a dict where the key is a time stamp
    Dump the dict as player_DB
    """

    # Get a fresh player_dump and userID list
    now = datetime.now()
    scrape_leaderboard()

    player_list = []
    current_dump = pd.read_pickle("Player_Dump").to_dict("records")
    for player in current_dump:
        player_list.append(player["UserId"])

    # Load the player_DB if it exists, otherwise create an empty dict
    # TODO: switch to json for data out and in
    try:
        with open("player_DB", "rb") as f:
            player_DB = dill.load(f)
    except FileNotFoundError:
        print(
            "player_DB pickle dump not found, initializing a new database as an empty dict"
        )
        player_DB = {}

    # Add {timestamp: stats} to the userid's value, so we end up with userid: {timestamp, stats}, {timestamp, stats}, {timestamp, stats}
    # Catch Keyerrors which are cases where the userID (new users) is not already in playerDB
    for userID in player_list:
        try:
            player_DB[userID].update(
                {
                    now.strftime("%d/%m/%Y %H:%M"): next(
                        item for item in current_dump if item["UserId"] == userID
                    )
                }
            )
        except KeyError:
            print(userID, "does not exist!, Creating a new entry")
            player_DB[userID] = {
                now.strftime("%d/%m/%Y %H:%M"): next(
                    item for item in current_dump if item["UserId"] == userID
                )
            }

    # Save the player_DB
    # TODO: switch to json for data out and in
    with open("player_DB", "wb") as f:
        dill.dump(player_DB, f)

    return player_DB


def scrape_leaderboard():
    """
    Utilizes an endpoint to get all player data and returns as a dataframe
    """
    url = "http://gewaltig.net/WebStats.aspx?getall=true"
    response = requests.get(url)
    players = response.json()

    df = pd.DataFrame(players)
    df.to_pickle("Player_Dump")
    return df


def get_peak(player_id):
    # Using player_DB, calculate a userID's peak rank

    # Load the player_DB if it exists, otherwise return False
    try:
        with open("player_DB", "rb") as f:
            player_DB = dill.load(f)
    except FileNotFoundError:
        return False

    playerData = player_DB[player_id]
    ranks = []
    for timestamp, value in playerData.items():
        ranks.append(value["Rank"])
    print("All ranks for user id", player_id, ranks)
    return min(ranks)


def player_stats_by_name(player_name, df):
    for row in df.index:
        rowName = df.loc[row, "Name"]
        if fuzz.token_set_ratio(rowName, player_name.lower()) > 95:
            x = df.loc[df["Name"] == rowName]
            print(x.to_dict("records"))
            return x.to_dict("records")
    return False


def player_stats_by_id(player_id, df):
    x = df.loc[df["UserId"] == int(player_id)]
    print(x.to_dict("records"))
    return x.to_dict("records")


def player_query(arg):
    # load saved dataframe here
    df = pd.read_pickle("Player_Dump")

    # first check if we've got a profile url on our hands
    if "http://gewaltig.net/ProfileView.aspx" in arg:
        match = PROFILE_URL.match(arg)
        if match:
            userid = match.group(1)
            return player_stats_by_id(userid, df)
        else:
            return False
    # try looking up the user by name
    player = player_stats_by_name(arg, df)
    if player:
        return player
    # try seeing if the input argument has a number to look up by id again
    match = PROFILE_ID.match(arg)
    if match:
        userid = match.group(1)
        return player_stats_by_id(userid, df)
    return False


def rankings_query(page=1):
    # load saved dataframe here
    df = pd.read_pickle("Player_Dump")
    # get a truncated database, sorted by rank, converted to dict
    return (
        df.sort_values(by=["Rank"], ascending=True)
        .truncate(before=~-page * 20 - 1, after=page * 20 - 1)
        .to_dict("records")
    )


def player_url(player):
    return f"http://gewaltig.net/ProfileView.aspx?userid={player['UserId']}"


if __name__ == "__main__":

    starttime = time.time()
    while True:
        now = datetime.now()
        print("Updating Player_Dump and player_DB!", now.strftime("%d/%m/%Y %H:%M"))
        update_playerDB()
        print("Done!")
        time.sleep(
            600.0 - ((time.time() - starttime) % 600.0)
        )  # pulling q10 minutes, need to be weary of file sizes

    # SHOW ME THE DATA!
    # df = scrape_leaderboard()
    # pd.set_option('display.max_columns', None)
    # print(df.sort_values(by=['Playedmin'], ascending=False))

    # WHO IS ONLINE?
    # show_online_players()

    # TELL ME ABUOT PLAYER ____
    # df = pd.read_pickle("Player_Dump")
    # print(player_stats_by_name(player_name='null', df=df))
    # print(player_stats_by_id(8802, df))
