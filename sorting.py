from gpiozero import Button, LED
import time

# main loop listens for button input
# TODO start out in moving mode
# TODO go into waiting mode after claw removal with hall sensor
# Front button activates juggle.py and rainbow websocket

input_pins = [18, 24, 25, 23] # go, stop, recycling, trash
input_buttons = []
for p in input_pins:
    input_buttons.append(Button(p))

button_light_pins = [5, 13, 11, 6]
button_lights = []
for p in button_light_pins:
    button_lights.append(LED(p))

state = "WAITING" # WAITING -> BUSY -> PROMPT -> BUSY -> WAITING
current_index = 0
print("Starting main loop...")

def back_buttons_on():
    button_lights[2].on()
    button_lights[3].on()

def back_buttons_off():
    button_lights[2].off()
    button_lights[3].off()

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
            back_buttons_on()
    elif (state == "PROMPT"):
        if (unknown):
            print("Unknown message, run trash")
            print("Will flash both to confirm")
            state = "WAITING"
        elif(trash):
            print("Trash message, run trash")
            print("Will flash trash to confirm")
            state = "WAITING"
        elif(recycle):
            print("Recycle message, run recycle")
            print("Will flash recycle to confirm")
            state = "WAITING"
        if (state == "WAITING"):
            print("Buttons off immediately, temporarily")
            back_buttons_off()
    time.sleep(.1)
