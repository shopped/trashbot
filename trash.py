import maestro
import time

servo = maestro.Controller(ttyStr="/dev/ttyACM1", device=0x0c)
servo.setSpeed(5, 0)
servo.setAccel(5, 0)
servo.setTarget(5, 6000)
time.sleep(.5)
servo.setTarget(5, 4000)
time.sleep(1)
servo.setTarget(5, 6000)
servo.close()
