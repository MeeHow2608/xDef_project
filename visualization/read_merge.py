import json
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from animation_v2 import match_animation

#########
# Pomocnicze funkcje do wizualizacji zdarzeń boiskowych
########

from data_processing.path import DATA_PATH
def location_draw(data, event):
    event = event-1 #ze względu na rodzaj zapisu danych
    pitch = Pitch(pitch_type='statsbomb',
                  axis=True, label=True)

    fig, ax = plt.subplots()
    x1, y1 = data[event]["location"]
    print(x1,y1)
    ax.scatter(x1, y1, c='red')

    pitch.draw(ax=ax)

    ax.set_title(data[event]["player"]["name"])
    plt.show()

def find_key_by_index(data, target_index):
    for key, value in data.items():
        if value.get('index') == target_index:
            return key
    return None

def animate(tracab_id, statsbomb_id, file_name, frame_index, pace = 3):

    with open(DATA_PATH + '/Tracab/' + tracab_id + '_tf10.json', 'r') as f:
        data_tracab = json.load(f)

    with open(DATA_PATH + '/statsbomb/'+ statsbomb_id + '_events.json', 'r', encoding="utf8") as f:
        data_statsbomb = json.load(f)

    with open(DATA_PATH + '/tackles/' + file_name + '.json', 'r', encoding="utf8") as f:
        data_merge = json.load(f)


    event_index = int(find_key_by_index(data_merge,frame_index))
    #print(data_tracab["FrameData"][frame_index])

    #location_draw(data_statsbomb,event_index)
    #print(data_statsbomb[event_index-1]["type"]["name"])
    #print(data_statsbomb[event_index-1]["player"]["name"])
    match_animation(data_tracab,data_merge[str(event_index)]["start"],data_merge[str(event_index)]["end"],pace = pace)

# Przykładowe wywołanie funkcji obrazującej przebieg akcji
# Wymagane id meczu tracab, id meczu statsbomb, nazwa pliku bez rozszerzenia
# i numer klatki zdarzenia ("index" w wygenerowanym pliku json)
animate('13251', '3836404', 'cracovia_widzew_tackles', 8935)