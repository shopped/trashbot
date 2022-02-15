from gpiozero import Button
import time

# main loop listens for button input
# TODO start out in moving mode
# TODO go into waiting mode after claw removal with hall sensor
# Front button activates juggle.py and rainbow websocket

input_pins = [18, 24, 25, 23] # go, stop, recycling, trash
input_buttons = []
for p in input_pins:
    input_buttons.append(Button(p))

state = "WAITING" # WAITING -> BUSY -> PROMPT -> BUSY -> WAITING

print("Starting main loop...")

current_index = 0

while True:
    input_state = []
    for i in range(len(input_buttons)):
        input_state.append(input_buttons[i].is_pressed)
    sense_trash_simulation = input_state[0] or input_state[1]
    unknown = input_state[2] and input_state[3]
    recycle = input_state[2]
    trash = input_state[3]
    if (state == "WAITING"):
        if sense_trash_simulation:
            print("Rainbow LEDs Message")
            print("Make folder, update current index")
            print("Juggling Script and Video")
            state = "PROMPT"
            print("Setting state to PROMPT, Prompt Socket Message")
    elif (state == "PROMPT"):
        if (unknown):
            print("Unknown message, run trash")
            state = "WAITING"
        elif(trash):
            print("Trash message, run trash")
            state = "WAITING"
        elif(recycle):
            print("Recycle message, run recycle")
            state = "WAITING"
    time.sleep(.1)
