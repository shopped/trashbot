from gpiozero import LED
from time import sleep

pins = [5, 13, 11, 6]

leds = []
for p in pins:
    leds.append(LED(p))

for l in leds:
    l.on()
    sleep(1)
    l.off()
