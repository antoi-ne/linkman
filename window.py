import glfw
import sys
import subprocess
from OpenGL.GL import *

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

def convert_color(func):
    def wrapper(self, color):
        if type(color) == str:
            color = colors.get(color, colors['black'])
        color = [i / 255 for i in color]
        func(self, color)
    return wrapper

class Window:

    def __init__(self, title="Linkman", size=None):
        if not glfw.init():
            print("Failed to initialize gflw")
            exit(1)
        if not size:
            size = glfw.get_video_mode(glfw.get_primary_monitor()).size
        self.window = glfw.create_window(size.width, size.height, title, glfw.get_primary_monitor(), None)

        if not self.window:
            print("Failed to open window")
            self.terminate()
            return

        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self._exit_callback)
        glfw.swap_buffers(self.window)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_HIDDEN)

        if 'darwin' in sys.platform:
            subprocess.Popen('caffeinate')

        self.color = (0, 0, 0)

    def _exit_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)


    def render(self):
        glClearColor(*self.color, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glfw.swap_buffers(self.window)

    @convert_color
    def set_color(self, color):
        self.color = color
        self.render()

    def poll_events(self):
        glfw.poll_events()

    def should_close(self):
        self.poll_events()
        return glfw.window_should_close(self.window)

    def terminate(self):
        glfw.terminate()
