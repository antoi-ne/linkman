import socket
import selectors
import link
import pymikro.src.pymikro as pymikro
import time
from network import Network


pattern_names = [
    "scene",
    "pattern",
    "events",
    "variation",
    "duplicate",
    "select",
    "solo",
    "mute",
]


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


class Maschine:
    def __init__(self) -> None:
        self.m = pymikro.MaschineMikroMk3()
        self.m.setScreen("linkman", 28)
        self.m.setLight("button", "pad_mode", 1)
        self.m.setLight("button", "keyboard", 1)
        self.selected_color = "white"
        self.pressed_color = "black"
        self.mode = "pattern"
        self.live = False
        self.beats = [
            [
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
            ],
            [
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
            ],
            [
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
            ],
            [
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
            ],
            [
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
            ],
            [
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
            ],
            [
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
            ],
            [
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
            ],
            [
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
            ],
        ]
        self.pattern = 0
        self.set_pattern_selected()

    def set_bpm(self, bpm):
        self.m.setScreen(f"bpm: {bpm:.2f}", 20)

    def set_pattern_selected(self):
        for idx, name in enumerate(pattern_names):
            lvl = 1
            if self.pattern == idx:
                lvl = 4
            self.m.setLight("button", name, lvl)
            self.m.updLights()

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
            self.m.setLight("pad", i, lvl, self.beats[self.pattern][i])
            if i == phase and self.beats[self.pattern][i] == "off":
                self.m.setLight("pad", i, 4, "white")
        self.m.updLights()

    def build_msg(self):
        msg = ""
        if self.live:
            msg += "l"
        else:
            msg += "p"
        msg += ":"
        msg += ",".join(m.beats[m.pattern])
        msg += ":"
        msg += self.pressed_color
        return msg

    def read(self):
        cmd = self.m.readCmd()
        if cmd:
            self.pressed_color = "black"

            if cmd["cmd"] == "btn":
                if "keyboard" in cmd["btn_pressed"]:
                    if self.live == False:
                        self.live = True
                        self.m.setLight("button", "keyboard", 4)
                    else:
                        self.live = False
                        self.m.setLight("button", "keyboard", 1)

            # live mode
            # pattern change
            if cmd["cmd"] == "btn":
                for pressed in cmd["btn_pressed"]:
                    try:
                        self.pattern = pattern_names.index(pressed)
                        self.set_pattern_selected()
                    except ValueError:
                        pass

            if self.mode == "color":  # color mode specifics
                if cmd["cmd"] == "pad":
                    self.selected_color = m_colors[cmd["pad_nb"]]
                    if cmd["pad_val"] > 0 and cmd["touched"] == True:
                        self.pressed_color = m_colors[cmd["pad_nb"]]
                if cmd["cmd"] == "btn":
                    if "pad_mode" in cmd["btn_pressed"]:
                        self.mode = "pattern"
                        self.m.setLight("button", "pad_mode", 1)

            elif self.mode == "pattern":  # pattern mode specific
                if (
                    cmd["cmd"] == "pad"
                    and cmd["pad_val"] == 0
                    and cmd["touched"] == False
                ):
                    if self.beats[self.pattern][cmd["pad_nb"]] != "off":
                        self.beats[self.pattern][cmd["pad_nb"]] = "off"
                    else:
                        self.beats[self.pattern][cmd["pad_nb"]] = self.selected_color
                if cmd["cmd"] == "btn":
                    if "pad_mode" in cmd["btn_pressed"]:
                        self.mode = "color"
                        self.m.setLight("button", "pad_mode", 4)


l = link.Link(120.0)
l.enabled = True


quantized = False
last_pulse = 0
last_msg = ""

m = Maschine()

nw = Network("udp", "master", "224.19.29.39", 4242)


def update_bpm(bpm):
    m.set_bpm(bpm)


l.setTempoCallback(update_bpm)

tick = 0

while 1:

    s = l.captureSessionState()

    lt = l.clock()

    beat = s.beatAtTime(lt.micros(), 4)
    phase = s.phaseAtTime(lt.micros(), 4)

    beat_pulse = int(beat * 4)
    phase_pulse = int(phase * 4)

    m.read()
    if m.mode == "pattern":
        m.set_pattern_mode(phase_pulse)
    elif m.mode == "color":
        m.set_color_mode()


    if quantized == False:
        if phase_pulse % 4 == 0:
            quantized = True
        else:
            continue

    msg = m.build_msg()

    if msg != last_msg:
        nw.send(bytes(msg, encoding="utf8"))
        last_msg = msg

    if tick == 1000:
        nw.send(bytes(msg, encoding="utf8"))
        tick = 0
    else:
        tick += 1

    last_pulse = beat_pulse



