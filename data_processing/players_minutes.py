from generateTrainingData import PATH, readMatchesId
import json
from collections import Counter
import numpy as np
###################################
# Funkcja  zwracająca liczbę rozegranych minut dla każdego zawodnika występującego w danych
#############################

def read_minutes_matches():
    df = readMatchesId("data/match_list.csv")
    players_info = {}
    for index, row in df.iterrows(): # pomijam mecze z niepełnymi danymi
        if row['filename'] not in ['pogon_widzew', 'cracovia_legia', 'lech_wisla', 'rakow_jagiellonia',
                                   'pogon_zaglebie', 'cracovia_warta', 'pogon_lech', 'lech_rks',
                                   'cracovia_lech', 'lech_rakow', 'cracovia_gornik', 'lech_lechia',
                                   'cracovia_slask', 'lech_pogon', 'lech_gornik', 'cracovia_miedz',
                                   'pogon_legia', 'pogon_miedz', 'rakow_zaglebie', 'rakow_warta']:
            print(row['filename'])
            with open(PATH + "/statsbomb/" + str(row['statsbomb_id']) + '_lineups.json', 'r', encoding="utf8") as f:
                data_statsbomb = json.load(f)


            for i in range(2):
                for pl in data_statsbomb[i]["lineup"]:
                    if pl["player_name"] not in players_info:
                        if "player_nickname" in pl:
                            nickname = pl["player_nickname"]
                        else:
                            nickname = pl["player_name"]
                        players_info[pl["player_name"]] = {"nickname": nickname, "club": [data_statsbomb[i]["team_name"]],"minutes": 0,
                                                           "starts": 0, "matches": 0, "position": []}
                    if len(pl["positions"]) >= 1:

                        pos = pl["positions"][0]["position"]

                        hours, minutes, seconds = pl["positions"][0]["from"].split(":")
                        start_minute = int(hours) * 60 + int(minutes)
                        if "to" in pl["positions"][len(pl["positions"])-1]:
                            hours, minutes, seconds = pl["positions"][len(pl["positions"])-1]["to"].split(":")
                            end_minute = int(hours) * 60 + int(minutes)
                        else:
                            end_minute = 90
                        minutes_played = end_minute - start_minute

                        if start_minute == 0:
                            start = 1
                        else:
                            start = 0

                        match_played = 1

                        players_info[pl["player_name"]] = {
                            "nickname": players_info[pl["player_name"]]["nickname"],
                            "club": players_info[pl["player_name"]]["club"] + [data_statsbomb[i]["team_name"]],
                            "minutes": players_info[pl["player_name"]]["minutes"] + minutes_played,
                            "starts": players_info[pl["player_name"]]["starts"] + start,
                            "matches": players_info[pl["player_name"]]["matches"] + match_played,
                            "position": players_info[pl["player_name"]]["position"] + [pos]}
                    else:
                        pass

    for player_name, player_info in players_info.items():
        counter = Counter(player_info["position"])
        most_common_position = counter.most_common(1)
        if most_common_position:
            player_info["position"] = most_common_position[0][0]

        clubs = list(np.unique(player_info["club"]))
        if len(clubs) == 2:
            player_info["club"] = clubs[0] + ", " + clubs[1]
        elif len(clubs) == 3:
            player_info["club"] = clubs[0] + ", " + clubs[1] + ", " + clubs[2]
        elif len(clubs) == 1:
            player_info["club"] = clubs[0]

    with open("players_minutes_played.json", "w", encoding="utf-8") as json_file:
        json.dump(players_info, json_file, ensure_ascii=False)

#read_minutes_matches()
