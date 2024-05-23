import sdl2.ext
import sdl2
from link import Link
import socket
import selectors
from network import Network
import time


# Window object
class Window:

    # create a window
    def __init__(self, window_name=""):

        # init the SDL2 library
        sdl2.ext.init()

        # set the window in fullscreen
        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
        display_mode = sdl2.SDL_DisplayMode()
        sdl2.SDL_GetCurrentDisplayMode(0, display_mode)

        # create the window and renderer
        self.window = sdl2.ext.Window(
            window_name,
            size=(display_mode.w, display_mode.h),
            flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP,
        )
        self.renderer = sdl2.ext.Renderer(
            self.window, flags=sdl2.SDL_RENDERER_ACCELERATED
        )

        # render the window
        self.set_color("black")
        self.window.show()

    # convert the string to a rgb color
    def _convert_color_str_to_rgb(self, color: str):
        colors = {
            "red": [255, 0, 0],
            "orange": [255, 140, 0],
            "yellow_warm": [253, 218, 13],
            "yellow": [255, 255, 0],
            "lime": [75, 100, 0],
            "green": [0, 255, 0],
            "mint": [62, 180, 137],
            "cyan": [0, 255, 255],
            "turquoise": [64, 224, 208],
            "blue": [0, 0, 255],
            "plum": [103, 49, 71],
            "violet": [255, 87, 51],
            "purple": [128, 0, 128],
            "magenta": [255, 0, 255],
            "white": [255, 255, 255],
            "black": [0, 0, 0],
        }
        if color in colors:
            return colors[color]
        return colors["black"]

    # convert the string to a sdl color
    def _convert_color_str_to_sdl(self, color: str) -> sdl2.ext.Color:
        rgb = self._convert_color_str_to_rgb(color)
        return sdl2.ext.Color(rgb[0], rgb[1], rgb[2])

    # change the window color
    def set_color(self, color):
        color = self._convert_color_str_to_sdl(color)
        self.renderer.color = color
        self.renderer.clear()
        self.renderer.present()

    # check if the window received an exit event
    def was_exited(self):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                return True
        return False

#
# CLIENT MAIN
#

# create the link
link = Link(120.0)
link.enabled = True
quantized = False
last_pulse = 0
beats = [
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
    "off",
]

window = Window("LINKMAN")
net = Network("udp", "client", "239.1.1.1", 4242)

live = False
pressed = "black"

# main script loop
while 1:

    # get the session state and clock
    session_state = link.captureSessionState()
    current_clock = link.clock()

    # calcul the beat and phase
    beat = session_state.beatAtTime(current_clock.micros(), 4)
    phase = session_state.phaseAtTime(current_clock.micros(), 4)
    beat_pulse = int(beat * 4)
    phase_pulse = int(phase * 4)

    # check for window exited
    if window.was_exited() == True:
        exit(0)

    # is this usefull ???
    if quantized == False:
        if phase_pulse % 4 == 0:
            quantized = True
        else:
            continue

    # receive message from the master
    b = net.recv()
    if b != None:
        msg = str(b, encoding="utf8")
        split_msg = msg.split(":")
        if split_msg[0] == "l":
            live = True
        elif split_msg[0] == "p":
            live = False
        beats = split_msg[1].split(",")
        pressed = split_msg[2]

    if live:
        window.set_color(pressed)
    elif beat_pulse > last_pulse:
        window.set_color(beats[phase_pulse])

    # draw the specified color
    if beat_pulse > last_pulse:
        window.set_color(beats[phase_pulse])
    last_pulse = beat_pulse

