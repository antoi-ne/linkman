import sdl2.ext
import sdl2
import link
import pymikro.src.pymikro as pymikro

import socket
import selectors

class ClientManager():
    def __init__(self, addr=''):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

        if not addr:
            addr = ('0.0.0.0', 7777)
            print('listening on', addr)
            self.socket.bind(addr)
            self.socket.listen(32)
            self.selector = selectors.DefaultSelector()
            self.selector.register(self.socket, selectors.EVENT_READ)
        else:
            print('connecting to', addr)
            try:
                self.socket.connect((addr, 7777))
            except BlockingIOError:
                pass 

    def _accept_wrapper(self, sock):
        client_socket, client_address = sock.accept()
        print('connection from', client_address)
        client_socket.setblocking(False)
        self.selector.register(client_socket, selectors.EVENT_READ, data=client_address)

    def _close_wrapper(self, client_socket):
        self.selector.unregister(client_socket)
        client_socket.close()
    
    def _handle_client(self, client_socket, message):
        try:
            client_socket.sendall(message)
        except Exception as e:
            print('error occurred:', e) 
    
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

black = sdl2.ext.Color(0, 0, 0)


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

    return black


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
        self.set_color(black)
        self.window.show()

    # change the window color
    def set_color(self, color):
        print(color)
        self.renderer.color = color
        self.renderer.clear()
        self.renderer.present()


l = link.Link(120.0)
l.enabled = True


quantized = False
last_pulse = 0

w = Window("LINKMAN")

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

cm = ClientManager("172.20.10.2")

while 1:

    s = l.captureSessionState()

    lt = l.clock()

    beat = s.beatAtTime(lt.micros(), 4)
    phase = s.phaseAtTime(lt.micros(), 4)

    beat_pulse = int(beat * 4)
    phase_pulse = int(phase * 4)

    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            exit(0)

    if quantized == False:
        if phase_pulse % 4 == 0:
            quantized = True
        else:
            continue

    b = cm.recv()
    if b != None:
        beats = str(b, encoding='utf8').split(",")

    if beat_pulse > last_pulse:
        w.set_color(color_to_sdl(beats[phase_pulse]))

    last_pulse = beat_pulse
