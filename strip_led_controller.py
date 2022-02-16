import time
import random
import math
import board
import neopixel
import asyncio
import websockets
import threading

pixel_pin = board.D21
num_pixels = 16
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

def wheel(pos):
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        b = int(pos * 3)
        r = int(255 - pos * 3)
        g = 0
    else:
        pos -= 170
        g = int(pos * 3)
        b = int(255 - pos * 3)
        r = 0
    return (r, g, b)

rainbow_active = False
prompt_active = False
following_active = False
searching_active = False
paused_active = False
waiting_active = False

async def rainbow_cycle(wait):
    for j in range(255):
        if (rainbow_active == False):
            return
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        await asyncio.sleep(wait)

def clear():
    pixels.fill((0,0,0))
    pixels.show()

async def rainbow():
    while rainbow_active:
        await rainbow_cycle(0.007)
    print("done rainbow")

async def following():
    while following_active:
        random_wait = random.randint(500, 9000)
        random_dur = random.randint(50, 300)
        random_pause = random.randint(50, 150)
        for i in range(8):
            if (following_active == False):
                return
            pixels[i] = (0,0,0)
            pixels[15-i] = (0,0,0)
            pixels.show()
            await asyncio.sleep(random_dur / 1000 / 16)
        if (following_active == False):
            return
        time.sleep(random_pause / 1000)
        for i in range(8):
            if (following_active == False):
                return
            pixels[8+i] = (0,255,0)
            pixels[7-i] = (0,255,0)
            pixels.show()
            await asyncio.sleep(random_dur / 1000 / 16)
        await asyncio.sleep(random_wait / 1000)
    print("done following")

# prompt, rainbow, following, searching, paused, waiting, trash, recycle, unknown
async def searching():
    g = (0,0,255)
    x = (0,0,0)
    while searching_active:
        pixels[0] = g
        pixels.show()
        await asyncio.sleep(1 / 32)
        for i in range(29):
            if i < 15:
                pixels[i] = g
                pixels[i - 1] = x
            else:
                pixels[30 - i] = x
                pixels[29 - i] = g
            pixels.show()
            await asyncio.sleep(1 / 32)
            if (searching_active == False):
                return
        pixels[0] = x
        pixels.show()
        await asyncio.sleep(1 / 32)

async def paused():
    while paused_active:
        for t in range(200):
            v = (math.sin(2*math.pi*t/200)+1)*50
            if (paused_active == False):
                return
            for i in range(16):
                pixels[i] = (int(v),0,0)
            pixels.show()
            await asyncio.sleep(.02)

async def waiting():
    while waiting_active:
        for t in range(200):
            v = (math.sin(2*math.pi*t/200)+1)*80
            if (waiting_active == False):
                return
            for i in range(16):
                pixels[i] = (int(v),int(v),int(v))
            pixels.show()
            await asyncio.sleep(.02)

async def prompt():
    b = True
    count = 0
    while prompt_active:
        count = count + 1
        if (count == 5):
            b = not b
            count = 0
        for i in range(16):
            if (i % 2 == 0):
                    pixels[i] = (255,0,0) if b else (0,255,0)
            else:
                    pixels[i] = (0,255,0) if b else (255,0,0)
        pixels.show()
        await asyncio.sleep(.1)
    print("prompt done")

def trash():
    for i in range(8,16):
        pixels[i] = (255,0,0)
        pixels.show()
        time.sleep(.05)
    time.sleep(1)
    for i in range(8,16):
        pixels[i] = (0,0,0)
        pixels.show()
        time.sleep(.05)

def recycle():
    for i in range(7,-1,-1):
        pixels[i] = (0,255,0)
        pixels.show()
        time.sleep(.05)
    time.sleep(1)
    for i in range(7,-1,-1):
        pixels[i] = (0,0,0)
        pixels.show()
        time.sleep(.05)

def unknown():
    for n in range(3):
        for i in range(8):
            pixels[8+i] = (0,0,255)
            pixels[7-i] = (0,0,255)
            pixels.show()
            time.sleep(.05)
        for i in range(8):
            pixels[i] = (0,0,0)
            pixels[15-i] = (0,0,0)
            pixels.show()
            time.sleep(.05)

# prompt, rainbow, following, searching, paused, waiting, trash, recycle, unknown
async def handler(websocket):
    global rainbow_active 
    global prompt_active 
    global following_active
    global searching_active
    global paused_active
    global waiting_active
    async for message in websocket:
        print(message)
        rainbow_active = False
        prompt_active = False
        following_active = False
        searching_active = False
        paused_active = False
        waiting_active = False
        clear()
        if (message == "prompt"):
            prompt_active = True
            asyncio.ensure_future(prompt())
        elif (message == "rainbow"): #processing
            rainbow_active = True
            asyncio.ensure_future(rainbow())
        elif (message == "following"):
            following_active = True
            asyncio.ensure_future(following())
        elif (message == "searching"):
            searching_active = True
            asyncio.ensure_future(searching())
        elif (message == "paused"): #in move mode
            paused_active = True
            asyncio.ensure_future(paused())
        elif (message == "waiting"): #for trash
            waiting_active = True
            asyncio.ensure_future(waiting())
        elif (message == "trash"):
            trash()
        elif (message == "recycle"):
            recycle()
        elif (message == "unknown"):
            unknown()
        else:
            print("Unknown message")
        # await asyncio.sleep(0)
        print("Done handling")

async def main():
    clear()
    async with websockets.serve(handler, "192.168.1.10", 1337):
        await asyncio.Future()  # run forever

print("Starting websockets")
asyncio.run(main())
