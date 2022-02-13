from gpiozero import LED
from time import sleep

pins = [5, 6, 13, 26]

l = LED(26)


l.on()
sleep(1)
l.off()
