from gpiozero import Button
from time import sleep

b = Button(26)

while True:
	if b.is_pressed:
		print("Magnet Sensed")
	else:
		print("No magnet sensed")
	sleep(.1)
