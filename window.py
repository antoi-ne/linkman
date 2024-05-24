import glfw
from OpenGL.GL import *
from dataclasses import dataclass
from typing import List

colors = {
    "red": (255, 0, 0),
    "orange": (255, 140, 0),
    "yellow_warm": (253, 218, 13),
    "yellow": (255, 255, 0),
    "lime": (75, 100, 0),
    "green": (0, 255, 0),
    "mint": (62, 180, 137),
    "cyan": (0, 255, 255),
    "turquoise": (64, 224, 208),
    "blue": (0, 0, 255),
    "plum": (103, 49, 71),
    "violet": (255, 87, 51),
    "purple": (128, 0, 128),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}

def convert_color(color):
    if type(color) == str:
        color = colors.get(color, colors['black'])
    color = [i / 255 for i in color]
    return color

@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int
    color: List[float]

class Window:

    def __init__(self, title="Linkman", size=None, full_screen=True):
        if not glfw.init():
            print("Failed to initialize gflw")
            exit(1)
        if not size or full_screen:
            size = glfw.get_video_mode(glfw.get_primary_monitor()).size
        self.window = glfw.create_window(size.width, size.height, title, glfw.get_primary_monitor() if full_screen else None, None)

        if not self.window:
            print("Failed to open window")
            self.terminate()
            return

        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self._key_callback)
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glfw.swap_buffers(self.window)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_HIDDEN)

        #allow to draw in pixels and not percentages
        glMatrixMode(GL_PROJECTION)
        glOrtho(0, size.width, size.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        self.bg = (0, 0, 0)
        self.rects = []

    def _key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)

    def render(self):
        glClearColor(*self.bg, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        for r in self.rects:
            self.draw_rect(r)
        glfw.swap_buffers(self.window)

    def set_color(self, color):
        self.bg = convert_color(color)

    def draw_rect(self, r):
        glBegin(GL_QUADS)
        glColor(*r.color)
        glVertex(r.x, r.y)
        glVertex(r.x + r.width, r.y)
        glVertex(r.x + r.width, r.y + r.height)
        glVertex(r.x, r.y + r.height)
        glEnd()

    def add_rect(self, x, y, width, height, color):
        r = Rect(x, y, width, height, list(convert_color(color)))
        self.rects.append(r)
        return r

    def remove_rect(self, r):
        return self.rects.remove(r)

    def poll_events(self):
        glfw.poll_events()

    def should_close(self):
        self.poll_events()
        return glfw.window_should_close(self.window)

    def terminate(self):
        glfw.terminate()
