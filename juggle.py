import maestro
import time
import signal
import sys

def signal_handler(sig, frame):
    print("Juggling over")
    servo.setTarget(5, 6000)
    servo.close()
    sys.exit()

def turn(s):
   for i in range(6000, 5550, -50):
        servo.setTarget(5, i)
        time.sleep(.02)
   for i in range(5550, 6050, 50):
        servo.setTarget(5, i)
        time.sleep(.01)
   time.sleep(.07)
   for i in range(6000, 6550, 50):
        servo.setTarget(5, i)
        time.sleep(.02)
   for i in range(6550, 5950, -50):
        servo.setTarget(5, i)
        time.sleep(.01)

servo = maestro.Controller(ttyStr="/dev/ttyACM0", device=0x0c)
servo.setSpeed(5, 0)
servo.setAccel(5, 0)
time.sleep(.5)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

while True:
    turn(servo)
    time.sleep(.05)
