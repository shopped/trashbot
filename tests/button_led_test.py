from gpiozero import LED
from time import sleep

pins = [5, 6, 13, 26]

leds = []
for p in pins:
    leds.append(LED(p))

for l in leds:
    l.on()
    sleep(1)
    l.off()
