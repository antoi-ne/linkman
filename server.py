import socket
import selectors
import link
import pymikro.src.pymikro as pymikro


class ClientManager:
    def __init__(self, addr=""):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

        if not addr:
            addr = ("0.0.0.0", 7777)
            print("listening on", addr)
            self.socket.bind(addr)
            self.socket.listen(32)
            self.selector = selectors.DefaultSelector()
            self.selector.register(self.socket, selectors.EVENT_READ)
        else:
            print("connecting to", addr)
            try:
                self.socket.connect((addr, 7777))
            except BlockingIOError:
                pass

    def _accept_wrapper(self, sock):
        client_socket, client_address = sock.accept()
        print("connection from", client_address)
        client_socket.setblocking(False)
        self.selector.register(client_socket, selectors.EVENT_READ, data=client_address)

    def _close_wrapper(self, client_socket):
        self.selector.unregister(client_socket)
        client_socket.close()

    def _handle_client(self, client_socket, message):
        try:
            client_socket.sendall(message)
        except Exception as e:
            print("error occurred:", e)

    def send(self, msg):
        while len((events := self.selector.select(timeout=0))):
            for selector_key, _ in events:
                if selector_key.fileobj == self.socket:
                    self._accept_wrapper(selector_key.fileobj)
                else:
                    self._close_wrapper(selector_key.fileobj)

        for _, selector_key in self.selector.get_map().items():
            if selector_key.data is not None:
                client_socket = selector_key.fileobj
                self._handle_client(client_socket, msg)

    def recv(self):
        try:
            data = self.socket.recv(1024)
        except BlockingIOError:
            return None
        else:
            return data


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
        self.m.setLight("button", "pad_mode")
        self.m.setLight("button", "step")
        self.selected_color = "white"
        self.shift_pressed = False
        self.mode = "pattern"
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
            if i == phase and m.beats[i] == "off":
                self.m.setLight("pad", i, 4, "white")
        self.m.updLights()

    def read(self):
        cmd = self.m.readCmd()
        if cmd:
            if self.mode == "color":
                if cmd["cmd"] == "pad":
                    self.selected_color = m_colors[cmd["pad_nb"]]
                if cmd["cmd"] == "btn":
                    if "step" in cmd["btn_pressed"]:
                        self.mode = "pattern"
                    if "shift" in cmd["btn_pressed"]:
                        self.shift_pressed = True
                    else:
                        self.shift_pressed = False
            elif self.mode == "pattern":
                if cmd["cmd"] == "pad":
                    if self.shift_pressed == True:
                        self.beats[cmd["pad_nb"]] = "off"
                    else:
                        self.beats[cmd["pad_nb"]] = self.selected_color
                if cmd["cmd"] == "btn":
                    if "pad_mode" in cmd["btn_pressed"]:
                        self.mode = "color"
                    if "shift" in cmd["btn_pressed"]:
                        self.shift_pressed = True
                    else:
                        self.shift_pressed = False


l = link.Link(120.0)
l.enabled = True


quantized = False
last_pulse = 0
last_pattern = ""

m = Maschine()

cm = cm = ClientManager()

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

    pattern = ",".join(m.beats)

    if pattern != last_pattern:
        cm.send(bytes(pattern))
        last_pattern = pattern

    last_pulse = beat_pulse
