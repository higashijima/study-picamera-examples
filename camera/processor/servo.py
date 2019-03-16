import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)

gpOut = 12

GPIO.setup(gpOut, GPIO.OUT)

servo = GPIO.PWM(gpOut, 50)

servo.start(0)

tern = 2.5 if sys.argv[1]=="open" else 7.25

servo.ChangeDutyCycle(tern)
time.sleep(0.5)

servo.stop()
GPIO.cleanup()


