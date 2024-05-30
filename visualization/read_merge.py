import json
from data_processing import generateTrainingData
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from animation_v2 import match_animation

#########
# Pomocnicza funkcja do wyświetlania animacji
########

PATH = generateTrainingData.PATH

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


with open(PATH + '/Tracab/' + '13251_tf10.json', 'r') as f:
    data_tracab = json.load(f)

with open(PATH + '/statsbomb/'+'3836404_events.json', 'r', encoding="utf8") as f:
    data_statsbomb = json.load(f)

with open(PATH + '/tackles/'+'cracovia_widzew_tackles.json', 'r', encoding="utf8") as f:
    data_merge = json.load(f)


event_index = int(find_key_by_index(data_merge,127240))
print(data_tracab["FrameData"][127240])

#location_draw(data_statsbomb,event_index)
print(data_statsbomb[event_index-1]["type"]["name"])
print(data_statsbomb[event_index-1]["player"]["name"])
match_animation(data_tracab,data_merge[str(event_index)]["start"],data_merge[str(event_index)]["end"],pace = 3)

