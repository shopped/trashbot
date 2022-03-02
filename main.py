from gpiozero import Button, LED
from collections import deque
from adafruit_motor import motor
import time
import os
import subprocess
import asyncio
import websockets
import signal
import sys
import board
import pwmio

import tflite

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

state = "WAITING"
# BottomMode - SEARCHING <-> FOLLOWING <-> PAUSED
# TopMode - WAITING -> BUSY -> PROMPT -> BUSY -> WAITING
current_index = ""
print("Starting main loop...")

mr = motor.DCMotor(pwmio.PWMOut(board.D2), pwmio.PWMOut(board.D3))
ml = motor.DCMotor(pwmio.PWMOut(board.D22), pwmio.PWMOut(board.D27))
speed = 0.5
unspeed = -1 * speed

def stop():
    mr.throttle = 0
    ml.throttle = 0

def forward():
    mr.throttle = speed
    ml.throttle = speed
    time.sleep(.3)
    stop()
    

def left():
    mr.throttle = speed
    ml.throttle = unspeed
    time.sleep(.3)
    stop()

def right():
    mr.throttle = unspeed
    ml.throttle = speed
    time.sleep(.3)
    stop()

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
    os.system("ffmpeg -f video4linux2 -s 320x240 -ss 0:0:1 -i /dev/video1 -frames 20 -filter_complex \"crop=224:224:48:16,fps=4\" /home/pi/trashbot/data/{}/%02d.jpg".format(index))
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

last_front_cam_message = None
front_cam_messenger = None
front_button_lights = False

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
            if (front_cam_messenger is not None):
                front_cam_messenger.close()
                front_cam_messenger = None
            detect_trash = subprocess.Popen("/home/pi/trashbot/v4l2cxx/build/exitondiff")
            state = "WAITING"
        elif input_state[0]:
            asyncio.get_event_loop().run_until_complete(update_leds("paused"))
            state = "PAUSED"
            last_front_cam_message = None
        else:
            msg = front_cam_messenger.get_message()
            if (last_front_cam_message == msg):
                last_front_cam_message = None
                if (msg == "LEFT"):
                    left()
                elif (msg == "RIGHT"):
                    right()
                elif (msg == "FAR"):
                    forward()
                if (msg == "CLOSE"):
                    if (front_button_lights == False):
                        front_button_lights = True
                        button_lights[0].on()
                else:
                    if (front_button_lights == True):
                        front_button_lights = False
                        button_lights[0].off()
            else:
                last_front_cam_message = msg
    elif (state == "PAUSED"):
        if input_state[1]:
            asyncio.get_event_loop().run_until_complete(update_leds("following"))
            state = "FOLLOWING"
    elif (state == "WAITING"):
        if (input_claw.is_pressed):
            asyncio.get_event_loop().run_until_complete(update_leds("following"))
            detect_trash.terminate()
            front_cam_messenger = tflite.Messenger()
            last_front_cam_message = None
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
