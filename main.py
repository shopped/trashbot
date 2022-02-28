from gpiozero import Button, LED
from collections import deque
import time
import os
import subprocess
import asyncio
import websockets
import signal
import sys

# main loop listens for button input
# TODO implement following mode, top/bottom swap

def signal_handler(sig, frame):
    asyncio.get_event_loop().run_until_complete(update_leds("clear"))
    sys.exit()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

input_pins = [18, 24, 25, 23] # go, stop, recycling, trash
input_buttons = []
input_buffer = deque(list(map(lambda x: [False, False], range(5))))
for p in input_pins:
    input_buttons.append(Button(p))

button_light_pins = [5, 13, 11, 6]
button_lights = []
for p in button_light_pins:
    button_lights.append(LED(p))

claw_pin = 26
input_claw = Button(claw_pin)
detect_trash = None

state = "FOLLOWING"
# BottomMode - SEARCHING <-> FOLLOWING <-> PAUSED
# Swap between BottomMode and TopMode by removing claw
# TopMode - WAITING -> BUSY -> PROMPT -> BUSY -> WAITING
current_index = ""
print("Starting main loop...")

async def update_leds(msg):
    async with websockets.connect('ws://192.168.1.10:1337') as ws:
        await ws.send(msg) 

def back_buttons_on():
    button_lights[2].on()
    button_lights[3].on()

def back_buttons_off():
    button_lights[2].off()
    button_lights[3].off()

def make_img_dir():
    global current_index
    os.chdir("data")
    folder_names = filter(os.path.isdir, os.listdir(os.getcwd()))
    num_folders = [int(name) for name in folder_names if name.isnumeric()]
    if (len(num_folders) == 0):
        last_number = -1
    else:
        last_number = max(num_folders)
    new_name = str(last_number + 1)
    os.mkdir(new_name)
    os.chdir("..")
    current_index = new_name
    return new_name

def generate_images():
    index = make_img_dir()
    print("Created new directory {}".format(index))
    juggle = subprocess.Popen(["python3","juggle.py"])
    os.system("ffmpeg -f video4linux2 -s 320x240 -ss 0:0:1 -i /dev/video0 -frames 20 -filter_complex \"crop=224:224:48:16,fps=4\" /home/pi/trashbot/data/{}/%02d.jpg".format(index))
    juggle.terminate()

def label_images(type):
    time_string = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    new_entry = "{} {} {}".format(current_index, type, time_string) # later COCO, OCR, and GPS
    label_path = os.getcwd() + "/data/labels.txt"
    if (os.path.exists(label_path)):
        with open(label_path, 'a') as f:
            f.write(new_entry + '\n')
    else:
        print("ERROR: labels.txt cannot be found, creating {}".format(label_path))
        with open(label_path, 'w') as f:
            f.write(new_entry + '\n')

asyncio.get_event_loop().run_until_complete(update_leds("following"))
while True:
    input_state = []
    for i in range(len(input_buttons)):
        input_state.append(input_buttons[i].is_pressed)
    input_buffer.append([input_state[2], input_state[3]])
    elem = input_buffer.popleft()
    if (state == "FOLLOWING"):
        if (input_claw.is_pressed is False):
            asyncio.get_event_loop().run_until_complete(update_leds("waiting"))
            detect_trash = subprocess.Popen("/home/pi/trashbot/v4l2cxx/build/exitondiff")
            state = "WAITING"
    elif (state == "WAITING"):
        if (input_claw.is_pressed):
            asyncio.get_event_loop().run_until_complete(update_leds("following"))
            detect_trash.terminate()
            state = "FOLLOWING"
        elif (detect_trash.poll() == 0):
            asyncio.get_event_loop().run_until_complete(update_leds("rainbow"))
            generate_images()
            asyncio.get_event_loop().run_until_complete(update_leds("prompt"))
            state = "PROMPT"
            back_buttons_on()
    elif (state == "PROMPT"):
        unknown = False
        trash = False
        recycle = False
        if (elem[0] or elem[1]):# .5s to process input for simultaenous press
            b1 = True in list(map(lambda x: x[0], input_buffer))
            b2 = True in list(map(lambda x: x[1], input_buffer))
            if (b1 and b2):
                unknown = True
            elif(elem[0]):
                recycle = True
            elif(elem[1]):
                trash = True
            input_buffer = deque(list(map(lambda x: [False, False], range(5))))
        if (unknown):
            button_lights[2].on()
            button_lights[3].on()
            asyncio.get_event_loop().run_until_complete(update_leds("unknown"))
            os.system("python3 trash.py");
            label_images("unknown")
            button_lights[2].off()
            button_lights[3].off()
            state = "WAITING"
        elif(recycle):
            button_lights[2].on()
            asyncio.get_event_loop().run_until_complete(update_leds("recycle"))
            os.system("python3 recycle.py");
            label_images("recycle")
            button_lights[2].off()
            state = "WAITING"
        elif(trash):
            button_lights[3].on()
            asyncio.get_event_loop().run_until_complete(update_leds("trash"))
            os.system("python3 trash.py");
            label_images("trash")
            button_lights[3].off()
            state = "WAITING"
        if (state == "WAITING"):
            print("Buttons off immediately, temporarily")
            asyncio.get_event_loop().run_until_complete(update_leds("waiting"))
            back_buttons_off()
    time.sleep(.1)
