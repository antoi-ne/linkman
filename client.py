from link import Link
import socket
import selectors
from network import Network
import time
from window import Window


#
# CLIENT MAIN
#

# create the link
link = Link(120.0)
link.enabled = True
quantized = False
last_pulse = 0
beats = ["off"] * 16

window = Window("LINKMAN")
net = Network("udp", "client", "239.1.1.1", 4242)

live = False
pressed = "black"

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
    if window.should_close() == True:
        window.terminate()
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
        msg = str(b, encoding="utf8")
        split_msg = msg.split(":")
        if split_msg[0] == "l":
            live = True
        elif split_msg[0] == "p":
            live = False
        beats = split_msg[1].split(",")
        pressed = split_msg[2]

    if live:
        window.set_color(pressed)
    elif beat_pulse > last_pulse:
        window.set_color(beats[phase_pulse])
