import maestro
import time

def turn(s):
   for i in range(6000, 5250, -50):
        servo.setTarget(5, i)
        time.sleep(.03)
   for i in range(5250, 6050, 50):
        servo.setTarget(5, i)
        time.sleep(.03)
   time.sleep(.07)
   for i in range(6000, 6750, 50):
        servo.setTarget(5, i)
        time.sleep(.03)
   for i in range(6750, 5950, -50):
        servo.setTarget(5, i)
        time.sleep(.03)

servo = maestro.Controller(ttyStr="/dev/ttyACM1", device=0x0c)
servo.setSpeed(5, 0)
servo.setAccel(5, 0)
turn(servo)
time.sleep(.07)
turn(servo)
servo.close()
