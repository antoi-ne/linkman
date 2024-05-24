import glfw
from OpenGL.GL import *
from time import sleep
from dataclasses import dataclass
from window import Window

@dataclass
class Size:
    width: int
    height: int

win = Window(size=Size(600, 375), full_screen=False)

i = True
win.set_color('black')

def button_grid(x, y, size, padding, count):
    return [win.add_rect(
        x + ((size + padding) * (i % count)),
        y + ((size + padding) * int(i / count)),
        size,
        size,
        'white') 
        for i in range(count ** 2)]

rects = button_grid(275, 50, 50, 25, 4)
win.render()
while not win.should_close():
    sleep(1)
    win.render()


win.terminate()
exit()
