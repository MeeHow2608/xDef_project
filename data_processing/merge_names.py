import json
import random
from statistics import mean
from difflib import SequenceMatcher
from unidecode import unidecode

##############
# Znajdowanie informacji o drużynach od obu dostawców danych
##############

PATH = 'D:/xDef_project/xDef/data_all'

def mergeTeams(statsbomb_id, tracab_id):
    with open(PATH +  "/Tracab/" + tracab_id+'_tf05.json', 'r') as f:
        data_tracab = json.load(f)
    with open(PATH + "/statsbomb/"+ statsbomb_id +'_lineups.json', 'r', encoding="utf8") as f:
        data_statsbomb = json.load(f)


    statsbomb_a = data_statsbomb[0]["team_name"]
    statsbomb_b = data_statsbomb[1]["team_name"]
    tracab_a = data_tracab["HomeTeam"]["TeamName"]
    tracab_b = data_tracab["AwayTeam"]["TeamName"]

    def find_prob(s, t):
        matcher = SequenceMatcher(None, s, t)
        return matcher.ratio()

    prob_a_home = find_prob(statsbomb_a,  tracab_a)
    prob_a_away = find_prob(statsbomb_a, tracab_b)

    prob_b_home = find_prob(statsbomb_b,  tracab_a)
    prob_b_away = find_prob(statsbomb_b, tracab_b)

    if prob_a_home > prob_a_away:
        team_home = statsbomb_a
    else:
        team_away = statsbomb_a

    if prob_b_home > prob_b_away:
        team_home = statsbomb_b
    else:
        team_away = statsbomb_b


    with open(PATH + '/Tracab/'+ tracab_id+'_tf10.json', 'r') as f:
        data_tf10 = json.load(f)
    print(len(data_tf10["FrameData"]))
    i = 0
    war = True
    while war == True:
        war = False
        for p in data_tf10["FrameData"][i]["PlayerPositions"]:
            if p['Team'] == -1:
                war = True
        i+=1
    team0 = [player for player in data_tf10["FrameData"][i]['PlayerPositions'] if player["Team"] == 1]

    team0_x = mean(player["X"] for player in team0)


    if team0_x < 0:
        team0_direction_firsthalf = "Right"
        team1_direction_firsthalf = "Left"

        team0_direction_secondhalf = "Left"
        team1_direction_secondhalf = "Right"
    else:
        team0_direction_firsthalf = "Left"
        team1_direction_firsthalf = "Right"

        team0_direction_secondhalf = "Right"
        team1_direction_secondhalf = "Left"


    for team in data_statsbomb:
        if team["team_name"] == team_home:
            team["tracab_name"] = tracab_a
            team["tracab_index"] = 0
            team["tracab_side"] = "HomeTeam"
        else:
            team["tracab_name"] = tracab_b
            team["tracab_index"] = 1
            team["tracab_side"] = "AwayTeam"



    data_statsbomb[0]["firsthalf_direction"] = team0_direction_firsthalf
    data_statsbomb[0]["secondhalf_direction"] = team0_direction_secondhalf

    data_statsbomb[1]["firsthalf_direction"] = team1_direction_firsthalf
    data_statsbomb[1]["secondhalf_direction"] = team1_direction_secondhalf




    data_statsbomb[0]["tracking_data"] = tracab_id + '_tf10.json'
    data_statsbomb[0]["events_data"] = statsbomb_id + '_events.json'

    data_statsbomb[1]["tracking_data"] = tracab_id + '_tf10.json'
    data_statsbomb[1]["events_data"] = statsbomb_id + '_events.json'


    team_home = unidecode(team_home).lower().split()[0]
    team_away = unidecode(team_away).lower().split()[0]

    tf10_home, tf10_away = checkTeamsTF10(tf05_file=data_tracab,tf10_file=data_tf10)

    if data_statsbomb[0]["tracab_side"] == "AwayTeam":
        data_statsbomb[0]["tf10_team"] = tf10_away
        data_statsbomb[1]["tf10_team"] = tf10_home
    else:
        data_statsbomb[0]["tf10_team"] = tf10_home
        data_statsbomb[1]["tf10_team"] = tf10_away

    with open(PATH + "/info/" + team_home + "_" + team_away +"_info.json", "w") as plik:
        json.dump(data_statsbomb, plik, indent=2)


def checkTeamsTF10(tf10_file, tf05_file): # w tf10 drużyny mają inne id, potrzeba dodatkowej funkcji do sprawdzania tego
    i = 0
    home_team = []
    for player in tf05_file["HomeTeam"]["Players"]:
        home_team.append(player["Jersey"])
    for player in tf05_file["AwayTeam"]["Players"]:
        if player["Jersey"] not in home_team:
            jersey = player["Jersey"]
            break

    while True:
        i = random.randint(0,len(tf10_file["FrameData"])-1)
        for player in tf10_file["FrameData"][i]["PlayerPositions"]:
            if player["JerseyNumber"] == jersey:
                away_team = player["Team"]
                home_team = 1 - player["Team"]
                return home_team, away_team

#mergeTeams("3836458","13305")
#mergeTeams("3836404", "13251")

