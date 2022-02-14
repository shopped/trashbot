import maestro
import time

servo = maestro.Controller(ttyStr="/dev/ttyACM0", device=0x0c)
servo.setSpeed(5, 0)
servo.setAccel(5, 0)
servo.setTarget(5, 6000)
time.sleep(1)
for i in range(3000,10100,100):
    servo.setTarget(5, i)
    time.sleep(.2)
    print(i)
servo.setTarget(5, 6000)
time.sleep(1)
servo.close()
