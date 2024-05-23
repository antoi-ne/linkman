import glfw
from OpenGL.GL import *
from time import sleep

from window import Window

win = Window()

i = True
while not win.should_close():
    win.set_color("magenta" if (i := not i) else "white")
    sleep(0.5)


win.terminate()
exit()
