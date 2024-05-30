import json
import math
from datetime import datetime
import pandas as pd
from unidecode import unidecode

from merge_names import mergeTeams
from path import DATA_PATH

with open(DATA_PATH, 'r') as file:
    DATA_PATH = file.readline().strip()

def readMatchesId(csv_source):
    matches_df = pd.read_csv(csv_source, sep=';')
    result = []
    for index, row in matches_df.iterrows():
        team_home = unidecode(row['home_team.home_team_name']).lower().split()[0]
        team_away = unidecode(row['away_team.away_team_name']).lower().split()[0]


        result.append({
            'statsbomb_id': row['match_id'],
            'tracab_id': row['GameID'],
            'filename': team_home + "_" + team_away
        })

        # Utworzenie nowego DataFrame na podstawie listy wyników
    df = pd.DataFrame(result)

    return df


def getLengths(data):  # funkcja do znalezienia długości połów

    length1 = 0
    length2 = 0

    for i in range(len(data['FrameData'])):
        if data['FrameData'][i]['Phase'] == 2:
            length1 += 1

    for i in range(length1, len(data['FrameData'])):
        if data['FrameData'][i]['Phase'] == 3:  # druga połowa zawiera przerwę,
            if data['FrameData'][i]['BallPosition'][0][
                'BallStatus'] == "Alive":  # dlatego traktuję początek 2 połowy jako pierwszą klatkę, gdzie trwa akcja
                length2 = len(data['FrameData']) - i
                break
    return length1, length2

def checkDirection(data_merge, teamID):         # funkcja do sprawdzania jaki był kierunek akcji
    if data_merge[0]['team_id'] == teamID:
        team = data_merge[0]
    elif data_merge[1]['team_id'] == teamID:
        team = data_merge[1]
    else:
        return None

    return team["firsthalf_direction"], team["secondhalf_direction"]

def calculate_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def SBToTrackab(coords):
    y_sb = 3400 - coords[1] * 85
    x_sb = -5200 + coords[0] * 85
    return (x_sb, y_sb)


def normalizePoint(point, changeDirection):

    point_x = point[0]
    point_y = point[1]
    if changeDirection:             # zamiana współrzędnych na przeciwne względem środka boiska
        point_x = 60 + (60 - point[0])
        point_y = 40 + (40 - point[1])


    # Wymiary statsbomb
    x_min_from = 0
    y_min_from = 80
    x_max_from = 120
    y_max_from = 0

    #Wymiary tracab
    x_min_to = -5250
    y_min_to = -3400
    x_max_to = 5250
    y_max_to = 3400

    # Przekształcenie
    x = ((point_x - x_min_from) / (x_max_from - x_min_from)) * (x_max_to - x_min_to) + x_min_to + 60
    y = ((point_y - y_min_from) / (y_max_from - y_min_from)) * (y_max_to - y_min_to) + y_min_to + 40

    return x, y

def accepted_distance(X, pass_length): # funkcja pomocnicza do sprawdzania akceptowalnej odległości zawodnika od lini podania
    if pass_length == 0:
        return 0
    # Przesunięcie (intercept)
    b = 255

    if b > pass_length / 4:
        m = b/pass_length
    else:
        # Współczynnik nachylenia (slope)
        m = (pass_length / 4) / pass_length



    # Obliczanie wartości funkcji liniowej
    y = m * X + b
    return y

def slope(punkt1, punkt2):
    x1, y1 = punkt1
    x2, y2 = punkt2

    # Oblicz współczynniki prostej y = mx + b
    if (x2 == x1):
        m = (y2 - y1) / 0.000001
    else:
        m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    return m, b
def distanceToPass(player, points, receiver, passer):
    if len(points) < 2:
        return distanceToPassCalculate(player,passer,receiver)
    else:
        distances = [distanceToPassCalculate(player, points[i], points[i + 1]) for i in range(len(points) - 1)]
        return min(distances)
def distanceToPassCalculate(player, p1, p2):
    x0, y0 = player
    m, b = slope(p1, p2)

    # Oblicz odległość punktu od prostej
    dist = abs(m * x0 - y0 + b) / math.sqrt(m**2 + 1)

    return dist

def normalize_value(original_value, pass_dist):
    normalized_value = original_value / ((pass_dist))
    return normalized_value


def calculate_posession_changes(frames):
    changeCount = 0
    for ix, frame in enumerate(frames):
        if ix == 0:
            prev_frame = frames[ix]
        else:
            if prev_frame["BallPosition"][0]["BallOwningTeam"] != frame["BallPosition"][0]["BallOwningTeam"]:
                changeCount += 1
            prev_frame = frames[ix]
    return changeCount


def if_pass_to_cf(eventData, ic_event_ix):
    ic_event = eventData[ic_event_ix - 1]

    # znajdowanie eventu pass
    try:
        pass_event_id = ic_event["related_events"][0]
    except:
        return -1
    checked_ix = ic_event_ix - 2
    while True:
        pass_event = eventData[checked_ix]
        if pass_event["id"] == pass_event_id:
            break
        checked_ix -= 1

    # znajdowanie eventu ball receipt
    checked_ix += 1
    while True:
        receipt_event = eventData[checked_ix]
        if receipt_event["type"]["id"] == 42:  # 42 to id eventu ball receipt
            break
        checked_ix += 1
        if checked_ix >= ic_event_ix:
            receipt_event = None
            break

    # sprawdzanie na jakiej pozycji gra adresat podania
    cf_id = [22, 23, 24, 25]
    if receipt_event != None:
        if receipt_event["position"]["id"] in cf_id:
            return 1
    return 0

def if_player_cf(eventData, ic_event_ix):
    if eventData[ic_event_ix - 1]["type"]["name"] == "Dribbled Past":
        preTackle_event = eventData[ic_event_ix]
    else:
        preTackle_event = eventData[ic_event_ix - 2]

    # sprawdzanie na jakiej pozycji gra zawodnik
    cf_id = [22, 23, 24, 25]
    if preTackle_event != None:
        if preTackle_event["position"]["id"] in cf_id:
            return 1
    return 0


def get_interception_zone(interception_event):
    ic_x = interception_event["location"][0]
    ic_y = interception_event["location"][1]

    # w SB boisko ma wymiary 120/80, a rzeczywiste 105/68
    # pole karne ma wymiary 16.5/40.32,
    # w SB odpowiada to 18.86/46.08
    # pola karne zaczynają się na wysokości 101.14 oraz 18.86
    # a ich boczne granice to 16.96 oraz 63.03
    if ic_x <= 18.86 or ic_x >= 101.14:  # bliżej niż pole karne
        if ic_y <= 63.04 and ic_y >= 16.96:  # w polu karnym
            zone = 4
        else:  # obok pola karnego
            zone = 3
    else:  # przed linią pola karnego
        if ic_y <= 63.04 and ic_y >= 16.96:  # przed polem karnym
            zone = 2
        else:  # przy linii bocznej
            zone = 1
    return zone


# funkcja zliczająca piłkarzy atakujących oraz broniących na części od -10m od piłki do końca boiska
def get_attackers_to_defenders_ratio(frame):
    ball_pos_x = frame["BallPosition"][0]["X"]
    team0_count = 0
    team1_count = 0

    atk_team = None
    def_team = None

    if ball_pos_x < 0:  # analiza przechwytu na lewej stronie boiska
        for playerPos in frame["PlayerPositions"]:
            # zliczanie zawodników drużyn
            if playerPos["Team"] == 0 and playerPos["X"] < ball_pos_x + 1000:
                team0_count += 1
            elif playerPos["Team"] != 0 and playerPos["Team"] != 4 and playerPos["X"] < ball_pos_x + 1000:
                team1_count += 1

            # określanie która drużyna się broni na podstawie bramkarza
            if playerPos["JerseyNumber"] == 1:
                if playerPos["X"] < 0:
                    if playerPos["Team"] == 0:  # bramkarz teamu 0 jest na lewej stronie
                        def_team = 0
                        atk_team = 1
                    else:  # bramkarz teamu 1 jest na lewej stronie
                        def_team = 1
                        atk_team = 0
                else:
                    if playerPos["Team"] == 0:  # bramkarz teamu 0 jest na prawej stronie
                        def_team = 1
                        atk_team = 0
                    else:  # bramkarz teamu 1 jest na prawej stronie
                        def_team = 0
                        atk_team = 1
    else:  # analiza przechwytu na prawej stronie boiska
        for playerPos in frame["PlayerPositions"]:
            # zliczanie zawodników drużyn
            if playerPos["Team"] == 0 and playerPos["Team"] != 4 and playerPos["X"] > ball_pos_x - 1000:
                team0_count += 1
            elif playerPos["Team"] != 0 and playerPos["Team"] != 4 and playerPos["X"] > ball_pos_x - 1000:
                team1_count += 1

            # określanie która drużyna się broni na podstawie bramkarza
            if playerPos["JerseyNumber"] == 1:
                if playerPos["X"] < 0:
                    if playerPos["Team"] == 0:  # bramkarz teamu 0 jest na lewej stronie
                        def_team = 1
                        atk_team = 0
                    else:  # bramkarz teamu 1 jest na lewej stronie
                        def_team = 0
                        atk_team = 1
                else:
                    if playerPos["Team"] == 0:  # bramkarz teamu 0 jest na prawej stronie
                        def_team = 0
                        atk_team = 1
                    else:  # bramkarz teamu 1 jest na prawej stronie
                        def_team = 1
                        atk_team = 0

    # wyznaczanie liczby zawodników atakujących i broniących
    if atk_team == 0:  # team 0 jest drużyną atakującą
        def_players = team1_count - 1  # odejmuję bramkarza
        atk_players = team0_count
    else:  # team 1 jest drużyną atakującą
        def_players = team0_count - 1  # odejmuję bramkarza
        atk_players = team1_count

    if atk_players <= 0 or def_players <= 0:
        # print(frame["PlayerPositions"])
        # print(atk_players)
        # print(def_players)
        # print(ball_pos_x)
        return -2
    atk_def_ratio = atk_players / def_players
    return atk_def_ratio


def trackingInformation(frame, event, data_merge): # zwraca dodatkowe informacje o przechwycie

    receiverPos = event['pass']['end_location']
    passPos = event['location']



    if data_merge[0]["team_id"] == event["team"]["id"]:
        team_id = 0
    else:
        team_id = 1

    if event["period"] == 1:
        direction = data_merge[team_id]["firsthalf_direction"]
    else:
        direction = data_merge[team_id]["secondhalf_direction"]

    if direction == "Left":
        changeDirection = True
    else:
        changeDirection = False

    players_in_area = [] # informacje o pilkarzach w wybranych obszarze
    min_dist = 10000000
    min_dist_pass = 10000000
    min_dist_rec = 10000000


    rec_pos = normalizePoint(receiverPos, changeDirection)

    # distanceReceiver = calculate_distance(p1, p2)

    pass_pos = normalizePoint(passPos, changeDirection)

    pass_length = calculate_distance(rec_pos, pass_pos)

    nearRec = []
    nearPass = []
    for playerPos in frame['PlayerPositions']:

        # drużyny tracabowe
        if (data_merge[team_id]["tf10_team"] == 1 and playerPos['Team'] == 0) or (
                data_merge[team_id]["tf10_team"] == 0 and playerPos['Team'] == 1):


            pl_pos = (playerPos['X'], playerPos['Y'])
            # p1 = SBToTrackab(receiverPos)


            # distancePass = calculate_distance(p1,p2)
            # if distanceReceiver < 255 or distancePass < 125:
            # return True

            # wyliczam odległość piłkarza od linii podania oraz sprawdzam jak blisko był piłki w momencie podania
            dist = distanceToPass(pl_pos, [pass_pos, rec_pos], rec_pos, pass_pos)
            if dist < min_dist:
                min_dist = dist
                min_pl = playerPos


            distPass = calculate_distance(pl_pos, pass_pos)
            if distPass < min_dist_pass:
                min_dist_pass = distPass


            distRec = calculate_distance(rec_pos, pl_pos)
            if distRec < min_dist_rec:
                min_dist_rec = distRec


            if distRec <= pass_length/4 or distRec<=5*85:
                nearRec.append(playerPos)

            if distPass <= 85:
                nearPass.append(playerPos)

            x = math.sqrt(distPass * distPass - dist * dist)
            pass_dist = calculate_distance(pass_pos, rec_pos)

            # wyliczam akceptowalną odległość od linii podania na podstawie odległości piłkarza od podania
            acc_length = accepted_distance(x, pass_dist)

            # distance = distanceToPass(p2, p3, normalizePoint(event["location"],changeDirection))
            if dist < acc_length and x <= pass_dist and x >= 0 and calculate_distance(pl_pos, rec_pos) <= pass_dist:
                players_in_area.append(playerPos)

    if min_dist == 10000000:
        return None
    return players_in_area,min_dist, min_dist_pass, min_dist_rec, pass_length, nearPass, nearRec, min_pl

def getTracabLocation(data_merge, event):
    point = event['location']

    if data_merge[0]["team_id"] == event["team"]["id"]:
        team_id = 0
    else:
        team_id = 1

    if event["period"] == 1:
        direction = data_merge[team_id]["firsthalf_direction"]
    else:
        direction = data_merge[team_id]["secondhalf_direction"]

    if direction == "Left":
        changeDirection = True
    else:
        changeDirection = False

    return normalizePoint(point, changeDirection)
def isPressed(frame, event, data_merge): # sprawdzanie obszaru, w którym może dojść do przechwytu

    receiverPos = event['pass']['end_location']
    passPos = event['location']

    if data_merge[0]["team_id"] == event["team"]["id"]:
        team_id = 0
    else:
        team_id = 1

    if event["period"] == 1:
        direction = data_merge[team_id]["firsthalf_direction"]
    else:
        direction = data_merge[team_id]["secondhalf_direction"]

    if direction == "Left":
        changeDirection = True
    else:
        changeDirection = False

    for playerPos in frame['PlayerPositions']:

        #drużyny tracabowe
        if (data_merge[team_id]["tf10_team"] == 1 and playerPos['Team'] == 0) or (data_merge[team_id]["tf10_team"] == 0 and playerPos['Team'] == 1):

            pl_pos = (playerPos['X'], playerPos['Y'])
            # p1 = SBToTrackab(receiverPos)
            rec_pos = normalizePoint(receiverPos, changeDirection)

            #distanceReceiver = calculate_distance(p1, p2)

            pass_pos = normalizePoint(passPos, changeDirection)

            #distancePass = calculate_distance(p1,p2)
            #if distanceReceiver < 255 or distancePass < 125:
                #return True



            # wyliczam odległość piłkarza od linii podania oraz sprawdzam jak blisko był piłki w momencie podania
            dist = distanceToPass(pl_pos, [pass_pos, rec_pos], rec_pos, pass_pos) # odleglosc od linii podania
            distPass = calculate_distance(pl_pos, pass_pos) # odleglosc sprawdzanego pilkarza od podajacego
            x = math.sqrt(distPass * distPass - dist * dist)
            pass_dist = calculate_distance(pass_pos, rec_pos)

            # wyliczam akceptowalną odległość od linii podania na podstawie odległości piłkarza od podania
            acc_length = accepted_distance(x, pass_dist)


            #distance = distanceToPass(p2, p3, normalizePoint(event["location"],changeDirection))

            if dist < acc_length and x <= pass_dist and x >=0 and calculate_distance(pl_pos, rec_pos) <= pass_dist:
                return True
    return False

def interceptionPlayerDistances(event,data_merge,frame_pass,frame_interception):
    player_name = event['player']['name']

    if data_merge[0]["team_id"] == event["team"]["id"]:
        team_id = 0
    else:
        team_id = 1

    if event["period"] == 1:
        direction = data_merge[team_id]["firsthalf_direction"]
    else:
        direction = data_merge[team_id]["secondhalf_direction"]

    if direction == "Left":
        changeDirection = True
    else:
        changeDirection = False


    # distanceReceiver = calculate_distance(p1, p2)


    jersey = None
    for player in data_merge[1 - team_id]["lineup"]:
        if player["player_name"] == player_name:
            jersey = player["jersey_number"]

    if jersey is None:
        for player in data_merge[team_id]["lineup"]:
            if player["player_name"] == player_name:
                jersey = player["jersey_number"]

    for p in frame_pass["PlayerPositions"]:
        if p["JerseyNumber"] == jersey and p["Team"] == data_merge[team_id]["tf10_team"]:
            player_pos = p


    for p in frame_interception["PlayerPositions"]:
        if p["JerseyNumber"] == jersey and p["Team"] == data_merge[team_id]["tf10_team"]:
            int_pos = p




    min_dist_passframe = 10000
    playersPassframe = []

    for playerPos in frame_pass['PlayerPositions']:
        if playerPos['Team'] == data_merge[team_id]["tf10_team"]:
            try:
                dist = calculate_distance([player_pos["X"],player_pos["Y"]],[playerPos["X"],playerPos["Y"]])
            except:
                return None
            if dist < min_dist_passframe and dist>0:
                min_dist_passframe = dist
            if dist < 255 and dist>0:
                playersPassframe.append(playerPos)

    min_dist_intframe = 10000
    playersIntframe = []

    try:
        for playerPos in frame_interception['PlayerPositions']:
            if playerPos['Team'] == data_merge[team_id]["tf10_team"]:
                dist = calculate_distance([int_pos["X"],int_pos["Y"]],[playerPos["X"],playerPos["Y"]])
                if dist < min_dist_intframe and dist > 0:
                    min_dist_intframe = dist
                if dist < 255 and dist > 0:
                    playersIntframe.append(playerPos)
    except:
        return None

    return min_dist_passframe, min_dist_intframe, playersPassframe, playersIntframe
# obliczanie odległości danego piłkarza od linii podania
def playerDistanceToPass(player_name, team_id, frame, receiver_position, pass_position, ballPositions, changeDirection, data_merge):

    try:
        jersey = None
        for player in data_merge[1-team_id]["lineup"]:
            if player["player_name"] == player_name:
                jersey = player["jersey_number"]

        if jersey is None:
            for player in data_merge[team_id]["lineup"]:
                if player["player_name"] == player_name:
                    jersey = player["jersey_number"]

        for p in frame["PlayerPositions"]:
            if p["JerseyNumber"] == jersey and p["Team"] == data_merge[1-team_id]["tf10_team"]:
                playerPos = p

            # drużyny tracabowe
        #if (data_merge[team_id]["tracab_index"] == 1 and playerPos['Team'] == 0) or (
                #data_merge[team_id]["tracab_index"] == 0 and playerPos['Team'] == 1):

        pl_pos = (playerPos['X'], playerPos['Y'])
    except:
        return None, None, None
    # p1 = SBToTrackab(receiverPos)
    rec_pos = normalizePoint(receiver_position, changeDirection)

    # distanceReceiver = calculate_distance(p1, p2)

    pass_pos = normalizePoint(pass_position, changeDirection)

    # distancePass = calculate_distance(p1,p2)
    # if distanceReceiver < 255 or distancePass < 125:
    # return True
    ballPositions.append(rec_pos)


    # wyliczam odległość piłkarza od linii podania oraz sprawdzam jak blisko był piłki w momencie podania

    dist = distanceToPass(pl_pos, ballPositions, rec_pos, pass_pos)  # odleglosc od linii podania

    dist_rec = calculate_distance(rec_pos,pl_pos)

    dist_pass = calculate_distance(pass_pos, pl_pos)

    return dist, dist_rec, dist_pass


# zwraca odległości piłkarza od linii podania w 3 momentach
def anticipationPlayer(player_name, event, data_tracab, startindex, endindex, startframe, midframe, endframe, data_merge):
    receiver_position = event['pass']['end_location']
    pass_position = event['location']



    if data_merge[0]["team_id"] == event["team"]["id"]:
        team_id = 0
    else:
        team_id = 1

    if event["period"] == 1:
        direction = data_merge[team_id]["firsthalf_direction"]
    else:
        direction = data_merge[team_id]["secondhalf_direction"]

    if direction == "Left":
        changeDirection = True
    else:
        changeDirection = False

    ballPositions = []
    for i in range(startindex,endindex):
        ballPositions.append([data_tracab['FrameData'][i]["BallPosition"][0]["X"],data_tracab['FrameData'][i]["BallPosition"][0]["Y"]])
    d1, d1_rec, d1_pass= playerDistanceToPass(player_name,team_id, startframe, receiver_position, pass_position, ballPositions, changeDirection, data_merge)
    if d1 is None:
        return None
    d2, d2_rec, d2_pass = playerDistanceToPass(player_name, team_id, midframe, receiver_position, pass_position, ballPositions, changeDirection,
                              data_merge)
    if d2 is None:
        return None
    d3, d3_rec, d3_pass= playerDistanceToPass(player_name, team_id, endframe, receiver_position, pass_position, ballPositions, changeDirection,
                              data_merge)

    if d3 is None:
        return None


    #diff1 = d2 - d1
    #diff2 = d3 - d2

    return d1, d2, d3, d1_rec, d2_rec, d3_rec, d1_pass, d2_pass, d3_pass

def checkInterceptionSuccess(index, data, frames_number):
    team = data['FrameData'][index]["BallPosition"][0]["BallOwningTeam"]
    i = index
    endframe = index + frames_number
    if endframe >= len(data["FrameData"]):
        endframe = len(data["FrameData"])-1
    while i<=endframe:
        if team != data['FrameData'][i]["BallPosition"][0]["BallOwningTeam"]:
            return False
        i=i+1
    return True


# funkcja poprawiająca mergowanie danych
def findBestFrame(tracab_file, merge_data, index, event):

    player_id = event["player"]["id"]
    jersey = None

    #łączenie zawodników na podstawie jersey number
    for player in merge_data[0]["lineup"]:
        if player["player_id"] == player_id:
            jersey = player["jersey_number"]
            team = merge_data[0]["tf10_team"]
    if jersey is None:
        for player in merge_data[1]["lineup"]:
            if player["player_id"] == player_id:
                jersey = player["jersey_number"]
                team = merge_data[1]["tf10_team"]


    closest_dist = 10000
    result_index = index - 25
    X = None

    multipl = 1
    while multipl < 3 and closest_dist > 1000:      # zwiększenie zasięgu poszukiwań odpowiedniej klatki

        start_index = index - multipl*25
        end_index = index + multipl*25

        if start_index < 0:
            start_index = 0
        if end_index >= len(tracab_file["FrameData"]):
            end_index = len(tracab_file["FrameData"])-1

        for i in range(start_index, end_index):
            for player in tracab_file["FrameData"][i]["PlayerPositions"]:
                if player["Team"] == team and player["JerseyNumber"] == jersey:
                    X = player["X"]
                    Y = player["Y"]
            if X is not None:                       # pomijam klatki z błędami
                dist = calculate_distance((tracab_file["FrameData"][i]["BallPosition"][0]["X"],
                                       tracab_file["FrameData"][i]["BallPosition"][0]["Y"]),
                                      (X, Y))
                if dist < closest_dist:                 # sprawdzam, w której klatce piłkarz jest najbliżej piłki
                    closest_dist = dist
                    result_index = i
        multipl += 1
    return result_index

def findNameByTracabJersey(min_pl,merge_data):
    team = min_pl["Team"]
    jersey = min_pl["JerseyNumber"]
    if team == merge_data[0]["tf10_team"]:
        team_id = 0
    else:
        team_id = 1

    for player in merge_data[team_id]["lineup"]:
        if jersey == player["jersey_number"]:
            name = player["player_name"]

    return name


def findPlayersNear(data_tracab, index, data_merge, event, radius): # znajduje graczy w zadanym obszarze od lokalizacji eventu
    eventLocation = event["location"]
    if data_merge[0]["team_id"] == event["team"]["id"]:
        team_id = 0
    else:
        team_id = 1

    if event["period"] == 1:
        direction = data_merge[team_id]["firsthalf_direction"]
    else:
        direction = data_merge[team_id]["secondhalf_direction"]

    if direction == "Left":
        changeDirection = True
    else:
        changeDirection = False


    location = normalizePoint(eventLocation,changeDirection)
    players = []

    for player in data_merge[team_id]["lineup"]:
        if player["player_name"] == event["player"]["name"]:
            jersey = player["jersey_number"]

    for player in data_tracab["FrameData"][index]["PlayerPositions"]:
        dist = calculate_distance((player['X'],player['Y']),location)
        if dist < 85 * radius and player["Team"] == data_merge[team_id]["tf10_team"] and player["JerseyNumber"] != jersey:
            players.append(player)

    return players


def generate_data(statsbomb_id,  tracab_id, filename): #podaje id i nazwy plików bez koncowek, bo tak łatwiej będzie to zautomatyzować
    with open(DATA_PATH + '/Tracab/' + tracab_id + "_tf10.json", 'r') as f:
        data_tracab = json.load(f)
    with open(DATA_PATH + '/statsbomb/' + statsbomb_id + "_events.json", 'r', encoding="utf8") as f:
        data_statsbomb = json.load(f)

    mergeTeams(statsbomb_id,tracab_id) #generowanie pliku statsbomb_lineups z dołączonymi informacjami tf05
                                        #potrzebne do sprawdzania drużyn
    with open(DATA_PATH + "/info/" + filename + "_info.json", 'r', encoding="utf8") as f:
        data_merge = json.load(f)
    print(len(data_tracab["FrameData"]))

    merge_dict = {}
    interceptions_dict = {}
    tackles_dict = {}
    x = getLengths(data_tracab)

    for i in range(len(data_statsbomb)):

        timestr = data_statsbomb[i]['timestamp']
        time_data = datetime.strptime(timestr, "%H:%M:%S.%f")
        seconds = time_data.hour * 3600 + time_data.minute * 60 + time_data.second + time_data.microsecond / 1e6

        tracab_index = round(seconds * 25)

        if data_statsbomb[i]['period'] == 2:
            tracab_index = tracab_index + (len(data_tracab['FrameData']) - x[1])

        if data_statsbomb[i]["type"]["name"] in ["Pass", "Interception", "Dribble", "Dribbled Past", "Duel", "Dispossessed"]:

            index = findBestFrame(data_tracab, data_merge, tracab_index, data_statsbomb[i])

            if index != None:
                tracab_index = index

        tracab_startindex = tracab_index - 125
        tracab_endindex = tracab_index + 125

        if tracab_startindex < 0:
            tracab_startindex = 0



        if tracab_endindex > len(data_tracab['FrameData']):
            tracab_endindex = len(data_tracab['FrameData'])

        merge_dict[i + 1] = {"index": tracab_index, "start": tracab_startindex, "end": tracab_endindex}
    for i in range(len(data_statsbomb)):
        if data_statsbomb[i]['type']['name'] == 'Interception' and (
                data_statsbomb[i]['location'][0] < 40):


            print(i)
            j = i
            while data_statsbomb[j]['type']['name'] != "Pass":
                j -= 1
            k = j - 1
            while len(data_statsbomb[k]['location']) < 2:
                print(data_statsbomb[k])
                k = k-1
            location = data_statsbomb[i]['location']
            prev_events = []
            while len(prev_events) < 2:
                ev_dist = calculate_distance(data_statsbomb[k]['location'], location)
                if ev_dist > 0:
                    prev_events.append(k)
                    location = data_statsbomb[k]['location']
                k -= 1



            # ilosc zawodników w sprawdzanym obszarze, odległość od linii podania, odległość od podającego, odległość od adresata podania, długość podania

            trackingInfo = trackingInformation(data_tracab['FrameData'][merge_dict[j + 1]["index"]],
                                                                         data_statsbomb[j], data_merge)
            if trackingInfo is not None:
                players, dist, pass_dist, rec_dist, pass_length, nearPass, nearRec, min_pl = trackingInfo



                anticipationResult = anticipationPlayer(
                    data_statsbomb[i]["player"]["name"], data_statsbomb[j], data_tracab,
                    merge_dict[j + 1]["index"],merge_dict[j + 2]["index"],
                    data_tracab['FrameData'][merge_dict[j + 1]["index"]-15],
                    data_tracab['FrameData'][merge_dict[j + 1]["index"]],
                    data_tracab['FrameData'][merge_dict[j + 1]["index"]+15],
                    data_merge)
                if anticipationResult is None:
                    pass
                else:
                    dist1, dist2, dist3, dist1_rec, dist2_rec, dist3_rec, dist1_pass, dist2_pass, dist3_pass = anticipationResult

                    interception_distances = interceptionPlayerDistances(
                        data_statsbomb[i],data_merge,data_tracab['FrameData'][merge_dict[j + 1]["index"]], data_tracab['FrameData'][merge_dict[i+1]["index"]])
                    if interception_distances is None:
                        pass
                    else:
                        min_dist_passframe, min_dist_intframe, playersPassframe, playersIntframe = interception_distances
                        pressure = False
                        try:
                            pressure = data_statsbomb[j]["under_pressure"]
                        except:
                            pass
                        if pressure == True:
                            pressure = 1
                        else:
                            pressure = 0
                        interceptionSuccess = checkInterceptionSuccess(merge_dict[i+1]["index"],data_tracab,75)

                        pos_changes = calculate_posession_changes(data_tracab['FrameData'][merge_dict[i+1]["start"]:merge_dict[i+1]["end"]])
                        pass_to_cf = if_pass_to_cf(data_statsbomb, data_statsbomb[i]['index'])
                        if pass_to_cf == -1:  # niekompletne dane np. brak eventu podania przed interception
                            # continue
                            pass_to_cf = 0
                        ic_zone = get_interception_zone(data_statsbomb[data_statsbomb[i]['index'] - 1])
                        try:
                            atk_def_ratio = get_attackers_to_defenders_ratio(data_tracab['FrameData'][merge_dict[i+1]["index"]])
                        except:
                            print('FAIL: ', i)
                        if atk_def_ratio == -2:  # niekompletne dane np. wszyscy zawodnicy są w 1 drużynie
                            continue


                        interceptions_dict[i + 1] = {"index": merge_dict[i+1]["index"],
                                                     "start": merge_dict[i+1]["start"],
                                                     "end": merge_dict[i+1]["end"],
                                                     "FrameCount": data_tracab['FrameData'][merge_dict[i + 1]['index']]['FrameCount'],
                                                     "statsbombID": statsbomb_id,
                                                     "tracabID": tracab_id,
                                                     "matchName": filename,
                                                     "playerID": data_statsbomb[i]["player"]["id"],
                                                     "playerName": data_statsbomb[i]["player"]["name"],
                                                     "location": getTracabLocation(data_merge, data_statsbomb[i]),
                                                     "possessionChanges": pos_changes,
                                                     "isPassToCF": pass_to_cf,
                                                     "interceptionZone": ic_zone,
                                                     "attackersDefendersRatio": atk_def_ratio,
                                                     "interceptionSuccess": interceptionSuccess,
                                                     "outcome": data_statsbomb[i]["interception"]["outcome"]["name"],
                                                     "passLength": pass_length,
                                                     "passLineDistance": dist,
                                                     "passDistance": pass_dist,
                                                     "receiverDistance": rec_dist,
                                                     "interceptionDistancePassMoment": min_dist_passframe,
                                                     "interceptionDistance": min_dist_intframe,
                                                     "passLineDistanceBeforePass": dist1,
                                                     "passLineDistanceMomentOfPass": dist2,
                                                     "passLineDistanceAfterPass": dist3,
                                                     "passDistanceBeforePass": dist1_pass,
                                                     "passDistanceMomentOfPass": dist2_pass,
                                                     "passDistanceAfterPass": dist3_pass,
                                                     "receiverDistanceBeforePass": dist1_rec,
                                                     "receiverDistanceMomentOfPass": dist2_rec,
                                                     "receiverDistanceAfterPass": dist3_rec,
                                                     "underPressure": pressure,
                                                     "playersNearPass": nearPass,
                                                     "playersNearReceiver": nearRec,
                                                     "playersInArea": players,
                                                     "playersNearInterceptionPassMoment": playersPassframe,
                                                     "playersNearInterception": playersIntframe,
                                                     "passEventTracabFrame": merge_dict[j + 1]["index"],
                                                     "passEvent": {
                                                         "id": j+1,
                                                         "type": data_statsbomb[j]["type"]["name"],
                                                         "location": getTracabLocation(data_merge, data_statsbomb[j]),
                                                         "player": data_statsbomb[j]["player"]
                                                     },
                                                     "previousEvent": {
                                                         "id": prev_events[0]+1,
                                                         "type": data_statsbomb[prev_events[0]]["type"]["name"],
                                                         "location": getTracabLocation(data_merge, data_statsbomb[prev_events[0]]),
                                                         "player": data_statsbomb[prev_events[0]]["player"]
                                                     },
                                                     "SecondPreviousEvent": {
                                                         "id": prev_events[1]+1,
                                                         "type": data_statsbomb[prev_events[1]]["type"]["name"],
                                                         "location": getTracabLocation(data_merge, data_statsbomb[prev_events[1]]),
                                                         "player": data_statsbomb[prev_events[1]]["player"]
                                                     },
                                                     "Y": 1}


        if data_statsbomb[i]['type']['name'] == "Duel" and data_statsbomb[i]['duel']['type']['name'] == "Tackle" and data_statsbomb[i]['location'][0] < 40:

            playersNear1 = findPlayersNear(data_tracab, merge_dict[i+1]["index"], data_merge, data_statsbomb[i], 3)
            playersNear2 = findPlayersNear(data_tracab, merge_dict[i+1]["index"], data_merge, data_statsbomb[i], 6)

            k = i-2
            location = data_statsbomb[i]['location']
            prev_events = []
            try:
                while len(prev_events) < 2:
                    ev_dist = calculate_distance(data_statsbomb[k]['location'], location)
                    if ev_dist > 0 and data_statsbomb[k]['type']["name"] != 'Pressure':
                        prev_events.append(k)
                        location = data_statsbomb[k]['location']
                    k -= 1


                pressure = False
                try:
                        pressure = data_statsbomb[prev_events[0]]["under_pressure"]
                except:
                    pass

                if pressure == True:
                    pressure = 1
                else:
                    pressure = 0

                if_cf = if_player_cf(data_statsbomb, data_statsbomb[i]['index'])
                if if_cf== -1:  # niekompletne dane
                    # continue
                    if_cf = 0

                pos_changes = calculate_posession_changes(
                    data_tracab['FrameData'][merge_dict[i + 1]["start"]:merge_dict[i + 1]["end"]])
                ic_zone = get_interception_zone(data_statsbomb[data_statsbomb[i]['index'] - 1])
                try:
                    atk_def_ratio = get_attackers_to_defenders_ratio(data_tracab['FrameData'][merge_dict[i + 1]["index"]])
                except:
                    print('FAIL: ', i)
                if atk_def_ratio == -2:  # niekompletne dane np. wszyscy zawodnicy są w 1 drużynie
                    continue





                tackles_dict[i + 1] = {"index": merge_dict[i + 1]["index"],
                                        "start": merge_dict[i + 1]["start"],
                                        "end": merge_dict[i + 1]["end"],
                                        "FrameCount": data_tracab['FrameData'][merge_dict[i + 1]['index']]['FrameCount'],
                                        "statsbombID": statsbomb_id,
                                        "tracabID": tracab_id,
                                        "matchName": filename,
                                        "playerID": data_statsbomb[i]["player"]["id"],
                                        "playerName": data_statsbomb[i]["player"]["name"],
                                        "location": getTracabLocation(data_merge,
                                                                     data_statsbomb[i]),
                                       "eventType": data_statsbomb[i]["type"]["name"],
                                       "prevEventType": data_statsbomb[i-1]["type"]["name"],
                                       "possessionChanges": pos_changes,
                                       "isCF": if_cf,
                                       "tackleZone": ic_zone,
                                       "attackersDefendersRatio": atk_def_ratio,
                                       "outcome": data_statsbomb[i]["duel"]["outcome"]["name"],
                                       "underPressure": pressure,
                                       "playersNear3m": playersNear1,
                                       "playersNear6m": playersNear2,
                                       "preTackleEvent": {
                                           "id": i,
                                           "type": data_statsbomb[i-1]["type"]["name"],
                                           "location": getTracabLocation(data_merge, data_statsbomb[i-1]),
                                           "player": data_statsbomb[i-1]["player"]
                                       },
                                       "previousEvent": {
                                           "id": prev_events[0] + 1,
                                           "type": data_statsbomb[prev_events[0]]["type"]["name"],
                                           "location": getTracabLocation(data_merge,
                                                                         data_statsbomb[prev_events[0]]),
                                           "player": data_statsbomb[prev_events[0]]["player"]
                                       },
                                       "SecondPreviousEvent": {
                                           "id": prev_events[1] + 1,
                                           "type": data_statsbomb[prev_events[1]]["type"]["name"],
                                           "location": getTracabLocation(data_merge,
                                                                         data_statsbomb[prev_events[1]]),
                                           "player": data_statsbomb[prev_events[1]]["player"]
                                       },
                                       "Y": 1}
            except:
                pass




        if data_statsbomb[i]['type']['name'] == "Dribble" and data_statsbomb[i]['dribble']['outcome']['name'] == "Complete" and data_statsbomb[i]['location'][0] > 80:
            # WAŻNE:
            # Dla odbiorów nieudanych, Dribbled Past ma informacje o obrońcy, ale występuje w danych eventowych PRZED Dribble
            # dlatego biorę poprawkę i odejmuję o 1 indeks zdarzenia, a jako prevEvent biorę event Dribble, który występuje po Dribbled Past
            # (te 2 zdarzenia realnie występują w tym samym czasie, więc nie ma to większego znaczenia)

            playersNear1 = findPlayersNear(data_tracab, merge_dict[i]["index"], data_merge, data_statsbomb[i], 3)
            playersNear2 = findPlayersNear(data_tracab, merge_dict[i]["index"], data_merge, data_statsbomb[i], 6)

            k = i - 1
            location = data_statsbomb[i]['location']
            prev_events = []


            try:
                while len(prev_events) < 2:
                    ev_dist = calculate_distance(data_statsbomb[k]['location'], location)
                    if ev_dist > 0 and data_statsbomb[k]["type"]["name"] != 'Pressure':
                        prev_events.append(k)
                        location = data_statsbomb[k]['location']
                    k -= 1

                pressure = False
                try:
                    pressure = data_statsbomb[prev_events[0]]["under_pressure"]
                except:
                    pass

                if pressure == True:
                    pressure = 1
                else:
                    pressure = 0

                if_cf = if_player_cf(data_statsbomb, data_statsbomb[i-1]['index'])
                if if_cf == -1:  # niekompletne dane
                    # continue
                    if_cf = 0

                pos_changes = calculate_posession_changes(
                    data_tracab['FrameData'][merge_dict[i]["start"]:merge_dict[i]["end"]])
                ic_zone = get_interception_zone(data_statsbomb[data_statsbomb[i-1]['index'] - 1])
                try:
                    atk_def_ratio = get_attackers_to_defenders_ratio(
                        data_tracab['FrameData'][merge_dict[i]["index"]])
                except:
                    print('FAIL: ', i)
                if atk_def_ratio == -2:  # niekompletne dane np. wszyscy zawodnicy są w 1 drużynie
                    continue

                tackles_dict[i] = {"index": merge_dict[i]["index"],
                                       "start": merge_dict[i]["start"],
                                       "end": merge_dict[i]["end"],
                                       "FrameCount": data_tracab['FrameData'][merge_dict[i]['index']]['FrameCount'],
                                       "statsbombID": statsbomb_id,
                                       "tracabID": tracab_id,
                                       "matchName": filename,
                                       "playerID": data_statsbomb[i-1]["player"]["id"],
                                       "playerName": data_statsbomb[i-1]["player"]["name"],
                                       "location": getTracabLocation(data_merge,
                                                                     data_statsbomb[i-1]),
                                       "eventType": data_statsbomb[i-1]["type"]["name"],
                                       "prevEventType": data_statsbomb[i]["type"]["name"],
                                       "possessionChanges": pos_changes,
                                       "isCF": if_cf,
                                       "tackleZone": ic_zone,
                                       "attackersDefendersRatio": atk_def_ratio,
                                       "outcome": checkInterceptionSuccess(merge_dict[i]["index"],data_tracab,75),
                                       "underPressure": pressure,
                                       "playersNear3m": playersNear1,
                                       "playersNear6m": playersNear2,
                                       "preTackleEvent": {
                                           "id": i,
                                           "type": data_statsbomb[i]["type"]["name"],
                                           "location": getTracabLocation(data_merge, data_statsbomb[i]),
                                           "player": data_statsbomb[i]["player"]
                                       },
                                       "previousEvent": {
                                           "id": prev_events[0] + 1,
                                           "type": data_statsbomb[prev_events[0]]["type"]["name"],
                                           "location": getTracabLocation(data_merge, data_statsbomb[prev_events[0]]),
                                           "player": data_statsbomb[prev_events[0]]["player"]
                                       },
                                       "secondPreviousEvent": {
                                           "id": prev_events[1] + 1,
                                           "type": data_statsbomb[prev_events[1]]["type"]["name"],
                                           "location": getTracabLocation(data_merge, data_statsbomb[prev_events[1]]),
                                           "player": data_statsbomb[prev_events[1]]["player"]
                                       },
                                       "Y": 0}
            except:
                pass

    with open(DATA_PATH + "/interceptions/"+ filename + "_interceptions.json", "w") as json_file:
        json.dump(interceptions_dict, json_file)

    with open(DATA_PATH + "/tackles/"+ filename + "_tackles.json", "w") as json_file:
        json.dump(tackles_dict, json_file)


def generateBigDataFile(names):
    data = []
    for filename in names:
        try:
            with open(DATA_PATH + "/interceptions/"+ filename + "_interceptions.json", 'r') as file:
                filedata = json.load(file)
                data.append(filedata)
        except:
            pass
    with open(DATA_PATH + "/interceptions/" + "complete_data_interceptions.json", 'w') as file:
        json.dump(data, file, indent=4)

    data = []
    for filename in names:
        try:
            with open(DATA_PATH + "/tackles/" + filename + "_tackles.json", 'r') as file:
                filedata = json.load(file)
                data.append(filedata)
        except:
            pass
    with open(DATA_PATH + "/tackles/" + "complete_data_tackles.json", 'w') as file:
        json.dump(data, file, indent=4)


# Wywołanie:

'''

df = readMatchesId("data/match_list.csv")


for index, row in df.iterrows():
    if os.path.exists(PATH + "/interceptions/" + row['filename']+ "_interceptions.json"):
        pass
    else:
        if row['filename'] not in ['pogon_widzew','cracovia_legia','lech_wisla','rakow_jagiellonia',
                                   'pogon_zaglebie', 'cracovia_warta', 'pogon_lech', 'lech_rks',
                                   'cracovia_lech', 'lech_rakow', 'cracovia_gornik', 'lech_lechia',
                                   'cracovia_slask', 'lech_pogon', 'lech_gornik', 'cracovia_miedz',
                                   'pogon_legia', 'pogon_miedz', 'rakow_zaglebie', 'rakow_warta']:
            print(row['filename'])
            generate_data(str(row['statsbomb_id']), str(row['tracab_id']), str(row['filename']))

generateBigDataFile(df["filename"].values)


'''
