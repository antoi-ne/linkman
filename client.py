import sdl2.ext
import sdl2
from link import Link
from network import Network


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
            flags=sdl2.SDL_WINDOW_BORDERLESS,
        )
        self.renderer = sdl2.ext.Renderer(
            self.window, flags=sdl2.SDL_RENDERER_ACCELERATED
        )

        # render the window
        self.set_color("black")
        self.window.show()

    # convert the string to a sdl color
    def _convert_color_str(self, color: str) -> sdl2.ext.Color:
        match color:
            case "red":
                return sdl2.ext.Color(255, 0, 0)
            case "orange":
                return sdl2.ext.Color(255, 140, 0)
            case "orange_light":
                return sdl2.ext.Color(255, 140, 0)
            case "yellow_warm":
                return sdl2.ext.Color(253, 218, 13)
            case "yellow":
                return sdl2.ext.Color(255, 255, 0)
            case "lime":
                return sdl2.ext.Color(75, 100, 0)
            case "green":
                return sdl2.ext.Color(0, 255, 0)
            case "mint":
                return sdl2.ext.Color(62, 180, 137)
            case "cyan":
                return sdl2.ext.Color(0, 255, 255)
            case "turquoise":
                return sdl2.ext.Color(64, 224, 208)
            case "blue":
                return sdl2.ext.Color(0, 0, 255)
            case "plum":
                return sdl2.ext.Color(103, 49, 71)
            case "violet":
                return sdl2.ext.Color(255, 87, 51)
            case "purple":
                return sdl2.ext.Color(128, 0, 128)
            case "magenta":
                return sdl2.ext.Color(255, 0, 255)
            case "white":
                return sdl2.ext.Color(255, 255, 255)
        return sdl2.ext.Color(0, 0, 0)
    
    # change the window color
    def set_color(self, color):
        color = self._convert_color_str(color)
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

# create the window
window = Window("LINKMAN")

# connect the network
net = Network("172.20.10.2")

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
        beats = str(b, encoding='utf8').split(",")

    # draw the specified color
    if beat_pulse > last_pulse:
        window.set_color(beats[phase_pulse])
    last_pulse = beat_pulse
