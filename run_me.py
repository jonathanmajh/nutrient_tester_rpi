import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT)
GPIO.output(24,GPIO.HIGH)
time.sleep(10)
GPIO.output(24,GPIO.LOW)