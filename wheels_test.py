import board
import pwmio
from time import sleep
from adafruit_motor import motor

mr = motor.DCMotor(pwmio.PWMOut(board.D2), pwmio.PWMOut(board.D3))
ml = motor.DCMotor(pwmio.PWMOut(board.D22), pwmio.PWMOut(board.D27))
speed = 0.5
unspeed = -1 * speed

def forward():
	mr.throttle = speed
	ml.throttle = speed

def left():
	mr.throttle = speed
	ml.throttle = unspeed

def right():
	mr.throttle = unspeed
	ml.throttle = speed

def backwards():
	mr.throttle = unspeed
	ml.throttle = unspeed

def stop():
	mr.throttle = 0
	ml.throttle = 0

forward()
sleep(.5)
stop()
sleep(.5)

left()
sleep(.5)
stop()
sleep(.5)

right()
sleep(.5)
stop()
sleep(.5)

backwards()
sleep(.5)
stop()
sleep(.5)

stop()
