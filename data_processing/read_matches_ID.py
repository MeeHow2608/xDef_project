import pandas as pd
from unidecode import unidecode

############
# Funkcja służąca do łączenia nazw plików statsbomb i tracab z tych samych meczy
############

from path import DATA_PATH

with open(DATA_PATH, 'r') as file:
    DATA_PATH = file.readline().strip()

def readMatchesID():
    matches_df = pd.read_csv("data/match_list.csv", sep=';')
    for index, row in matches_df.iterrows():
        team_home = unidecode(row['home_team.home_team_name']).lower().split()[0]
        team_away = unidecode(row['away_team.away_team_name']).lower().split()[0]

        print(str(row['match_id']) + " " + str(row['GameID']) + " " + team_home + "_" + team_away + "_interceptions.json")

    # statsbomb_id                       tracab_id                              filename



