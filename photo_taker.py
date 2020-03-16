from picamera import PiCamera
import RPi.GPIO as GPIO
import time

filename = input('Concentration-Test Number: ')
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
GPIO.output(23,GPIO.HIGH)
GPIO.output(24,GPIO.HIGH)
GPIO.output(25,GPIO.HIGH)
time.sleep(1)
camera = PiCamera()
filename = '/home/pi/nutrient_tester_rpi/samples/{}.jpg'.format(filename)
camera.capture(filename)
print('Photo saved as "{}"'.format(filename))
camera.close()
GPIO.output(23,GPIO.LOW)
GPIO.output(24,GPIO.LOW)
GPIO.output(25,GPIO.LOW)