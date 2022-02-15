import time
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

async def handler(websocket):
    global rainbow_active 
    global prompt_active 
    async for message in websocket:
        print(message)
        rainbow_active = False
        prompt_active= False
        clear()
        if (message == "prompt"):
            prompt_active = True
            asyncio.ensure_future(prompt())
        elif (message == "rainbow"):
            rainbow_active = True
            asyncio.ensure_future(rainbow())
        #elif (message == "paused"):
        #elif (message == "waiting"):
        elif (message == "trash"):
            trash()
        elif (message == "recycle"):
            recycle()
        elif (message == "unknown"):
            unknown()
        else:
            print("Unknown message")
        await asyncio.sleep(0)
        print("Done handling")

async def main():
    clear()
    async with websockets.serve(handler, "192.168.1.10", 1337):
        await asyncio.Future()  # run forever

print("Starting websockets")
asyncio.run(main())
