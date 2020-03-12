from picamera import PiCamera
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23,GPIO.OUT)
GPIO.output(23,GPIO.HIGH)
camera = PiCamera()
filename = '/home/pi/nutrient_tester_rpi/focus.jpg'
camera.capture(filename)
camera.close()
GPIO.output(23,GPIO.LOW)