import glfw
from OpenGL.GL import *
from time import sleep
from dataclasses import dataclass
from window import Window

@dataclass
class Size:
    width: int
    height: int

win = Window(size=Size(600, 400))

i = True
while not win.should_close():
    sleep(1)


win.terminate()
exit()
