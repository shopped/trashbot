from gpiozero import Button
from time import sleep

def one():
	iterations = 100

	b = Button(23)

	while (iterations > 0):
		iterations = iterations - 1
		if b.is_pressed:
			print("PRESSED")
		else:
			print("DEPRESSED")
		sleep(.1)

def all():
	print("Testing pins")
	pins = [23, 24, 25, 18]
	buttons = []

	for p in pins:
		buttons.append(Button(p))	

	iterations = 100

	while (iterations > 0):
		iterations = iterations - 1
		for i in range(4):
			if buttons[i].is_pressed:
				print(pins[i])
		sleep(.1)

all()
