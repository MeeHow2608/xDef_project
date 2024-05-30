import math

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mplsoccer import Pitch
from PIL import Image

##########
# Tworzenie animacji na podstawie podanego fragmentu meczu
##########

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def update(frame,data,pitch, ax, startframe = 0, endframe = 0, pace = 3): #pace żeby spowolnić/przyśpieszyć animację; 4 najbardziej realistyczne
    ax.clear()
    pitch.draw(ax=ax)
    time = frame * pace + startframe # Każda klatka odpowiada kolejnej wartości time
    frames = endframe - startframe


    while time > endframe:
        time = time - frames
    for d in data['FrameData'][time]['PlayerPositions']:

        if d['Team'] == 1:
            color = 'red'
            ax.scatter(d['X'], d['Y'], s=100, color=color)
            ax.annotate(d['JerseyNumber'], (d['X'], d['Y']), fontsize=12, ha='center', va='center')


        elif d['Team'] == 0:
            color = 'blue'
            ax.scatter(d['X'], d['Y'], s=100, color=color)
            ax.annotate(d['JerseyNumber'], (d['X'], d['Y']), fontsize=12, ha='center', va='center')


    ax.scatter(data['FrameData'][time]['BallPosition'][0]['X'],data['FrameData'][time]['BallPosition'][0]['Y'], s=100, c='pink')

    ax.set_xlim(-5500, 5500)
    ax.set_ylim(-4400, 4400)


    # ax.set_title(str(time) + " "+ str(time/25) + " " + str(data['FrameData'][time]['Phase']) + " "+ data['FrameData'][time]['BallPosition'][0]['BallStatus'] + " " + str(closest_player))
    ax.set_title('Frame: ' + str(time) +' Time: ' + str(time / 25) + " Phase: " + str(data['FrameData'][time]['Phase']) + " Ballstatus: " + str(data['FrameData'][time]["GameRunning"]))

def match_animation(data, startframe, endframe, pace = 4):
    pitch = Pitch(pitch_type='tracab',  # example plotting a tracab pitch
                  pitch_length=105, pitch_width=68,
                  axis=True, label=True)  # showing axis labels is optional
    fig, ax = pitch.draw()
    ani = animation.FuncAnimation(fig, update, fargs=(data, pitch, ax, startframe, endframe, pace), frames=1000, interval=1)

    frames = []
    for frame in range((endframe - startframe) // pace):
        update(frame, data, pitch, ax, startframe, endframe, pace)
        fig.canvas.draw()
        image = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
        frames.append(image)

    frames[0].save("animation.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)


    plt.show()
