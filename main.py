import sdl2.ext
import sdl2
import link
import pymikro.src.pymikro as pymikro

m_colors = [
    "red",
    "orange",
    "orange_light",
    "yellow_warm",
    "yellow",
    "lime",
    "green",
    "mint",
    "cyan",
    "turquoise",
    "blue",
    "plum",
    "violet",
    "purple",
    "magenta",
    "white",
]


def color_to_sdl(color: str) -> sdl2.ext.Color:
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


black = sdl2.ext.Color(0, 0, 0)

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
        self.window = sdl2.ext.Window(window_name, size=(display_mode.w, display_mode.h), flags=sdl2.SDL_WINDOW_BORDERLESS)
        self.renderer = sdl2.ext.Renderer(self.window, flags=sdl2.SDL_RENDERER_ACCELERATED)

        # render the window
        self.set_color(black)
        self.window.show()

    # change the window color
    def set_color(self, color):
        print(color)
        self.renderer.color = color
        self.renderer.clear()
        self.renderer.present()


class Maschine:
    def __init__(self) -> None:
        self.m = pymikro.MaschineMikroMk3()
        self.m.setScreen("linkman", 28)
        self.m.setLight('button', 'pad_mode')
        self.m.setLight('button', 'step')
        self.selected_color = "white"
        self.shift_pressed = False
        self.mode = 'pattern'
        self.beats = [
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

    def set_color_mode(self):
        for i in range(16):
            lvl = 1
            if self.selected_color == m_colors[i]:
                lvl = 3
            self.m.setLight("pad", i, lvl, m_colors[i])
        self.m.updLights()

    def set_pattern_mode(self, phase):
        for i in range(16):
            lvl = 1
            if i == phase:
                lvl = 3
            self.m.setLight("pad", i, lvl, m.beats[i])
            if i == phase and m.beats[i] == 'off':
                self.m.setLight("pad", i, 4, 'white')
        self.m.updLights()

    def read(self):
        cmd = self.m.readCmd()
        if cmd:
            if self.mode == 'color':
                if cmd["cmd"] == "pad":
                    self.selected_color = m_colors[cmd["pad_nb"]]
                if cmd["cmd"] == "btn":
                    if 'step' in cmd["btn_pressed"]:
                        self.mode = 'pattern'
                    if 'shift' in cmd["btn_pressed"]:
                        self.shift_pressed = True
                    else:
                        self.shift_pressed = False
            elif self.mode == 'pattern':
                if cmd["cmd"] == "pad":
                    if self.shift_pressed == True:
                        self.beats[cmd["pad_nb"]] = 'off'
                    else:
                        self.beats[cmd["pad_nb"]] = self.selected_color
                if cmd["cmd"] == "btn":
                    if 'pad_mode' in cmd["btn_pressed"]:
                        self.mode = 'color'
                    if 'shift' in cmd["btn_pressed"]:
                        self.shift_pressed = True
                    else:
                        self.shift_pressed = False



l = link.Link(120.0)
l.enabled = True


quantized = False
last_pulse = 0

m = Maschine()

w = Window("LINKMAN")

while 1:

    s = l.captureSessionState()

    lt = l.clock()

    beat = s.beatAtTime(lt.micros(), 4)
    phase = s.phaseAtTime(lt.micros(), 4)

    beat_pulse = int(beat * 4)
    phase_pulse = int(phase * 4)

    m.read()
    if m.mode == 'pattern':
        m.set_pattern_mode(phase_pulse)
    elif m.mode == 'color':
        m.set_color_mode()

    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            exit(0)

    if quantized == False:
        if phase_pulse % 4 == 0:
            quantized = True
        else:
            continue

    if beat_pulse > last_pulse:
        print(phase_pulse)
        w.set_color(color_to_sdl(m.beats[phase_pulse]))

    last_pulse = beat_pulse
