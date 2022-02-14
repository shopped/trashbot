import maestro
import time

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
turn(servo)
time.sleep(.05)
turn(servo)
time.sleep(.05)
turn(servo)
time.sleep(.05)
turn(servo)
servo.close()
