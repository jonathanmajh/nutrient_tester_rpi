import os
import sys
import time
from math import sqrt
from queue import Queue
from threading import Thread

import maestro
from image_processing import detect_circle, detect_color
from misc import QueueMessage
from motor_control import (move_reactant_linear, move_water_linear,
                           move_water_valve)
from picamera import PiCamera
import RPi.GPIO as GPIO

def test_main(queue: Queue, completed: int, test_time: str):
    try:
        queue.put(QueueMessage('Starting', task_name='Test Main'))
        timer = time.time()
        pre_test_clean(queue)
        just_add_water(queue, completed)
        # tube cleaning can run async at while we are waiting for heater
        clean = Thread(target=post_test_clean, args=(queue, ))
        clean.start()
        run_heater(queue)
        filename = '/home/pi/nutrient_tester_rpi/{}.jpg'.format(test_time)
        location = movement_feedback(queue, completed, test_time)
        result = detect_color(queue, filename, location)
        # TODO add files to be sent, analysis
        # it doesnt really matter when cleaning finishes as long as it does by the end
        clean.join()
        queue.put(QueueMessage('Finished in: ' +
                               str(time.time() - timer), task_name='Test Main', message_type=0, filename=test_time))
    except:
        queue.put(QueueMessage('Unexpected Exception', 4, sys.exc_info()))


def pre_test_clean(queue: Queue):
    """
    Flush the pipe with air before test begins
    Assume water actuator starts in extended position
    """
    # suck in air
    queue.put(QueueMessage('Starting', task_name='Pre-Test Cleaning'))
    queue.put(QueueMessage('Sucking in Air', task_name='Pre-Test Cleaning'))
    move_water_valve(1)
    move_water_linear([0])
    queue.put(QueueMessage('Pushing out air, then pulling in water',
                           task_name='Pre-Test Cleaning'))
    move_water_valve(2)
    # push out air, pull in water
    move_water_linear([5000, 1000])
    queue.put(QueueMessage('Finished', task_name='Pre-Test Cleaning'))


def move_paper(queue: Queue, completed: int, jog: bool = False):
    """
    Moves new paper into position
    Need to somehow track roll usage
    """
    queue.put(QueueMessage('Starting', task_name='Move Paper'))
    speed = 6.28318530718 / 5  # rad / second
    length = 20  # mm
    total_length = 20 * completed
    inner_radius = 11.5  # of the spool
    thickness = 0.1  # used paper thickness
    radius = sqrt(total_length * thickness / 3.14159 +
                  inner_radius * inner_radius)
    # https://math.stackexchange.com/questions/2145821/calculating-the-length-of-tape-when-it-is-wound-up
    theta = length / radius
    run_time = theta / speed / 2
    if (jog):
        queue.put(QueueMessage('Jog mode', task_name='Move Paper'))
        run_time = run_time / 50
    queue.put(QueueMessage('Turning Servo by {rad} rad, time required {time} s'.format(
        rad=theta, time=run_time), task_name='Move Paper'))
    servo = maestro.Controller()
    #servo.setAccel(0, 4)
    #servo.setSpeed(0, 10)
    servo.setTarget(4, 5690)  # turn continuous servo
    time.sleep(run_time)
    servo.setTarget(4, 0)  # stop servo
    queue.put(QueueMessage('Finished', task_name='Move Paper'))


def just_add_water(queue: Queue, completed: int):
    """
    put water sample and reactant onto paper
    """
    queue.put(QueueMessage('Starting', task_name='Sampling'))
    queue.put(QueueMessage('Adding Water', task_name='Sampling'))
    move_water_valve(1)
    # push out some water then sucking back in
    move_water_linear([2000, 0])
    # move valve to inlet so no liquid can go on paper
    queue.put(QueueMessage('Adding Reactant', task_name='Sampling'))
    move_water_valve(2)
    move_reactant_linear(completed)
    queue.put(QueueMessage('Finished', task_name='Sampling'))


def run_heater(queue: Queue):
    """
    """
    queue.put(QueueMessage('Starting', task_name='Heater'))
    queue.put(QueueMessage('Turning on heater for {time} seconds'.format(
        time=300), task_name='Heater'))
    # TODO set pin to high
    time.sleep(300)  # 5 minutes
    queue.put(QueueMessage('Finished', task_name='Heater'))


def take_photo(queue: Queue, test_time: str):
    """
    """
    queue.put(QueueMessage('Starting', task_name='Camera'))
    queue.put(QueueMessage('Turning on LEDs', task_name='Camera'))
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
    queue.put(QueueMessage('Taking photo', task_name='Camera'))
    filename = '/home/pi/nutrient_tester_rpi/{}.jpg'.format(test_time)
    camera.capture(filename)
    queue.put(QueueMessage('Photo saved as "{}"'.format(
        filename), task_name='Camera'))
    camera.close()
    GPIO.output(23,GPIO.LOW)
    GPIO.output(24,GPIO.LOW)
    GPIO.output(25,GPIO.LOW)
    queue.put(QueueMessage('Finished', task_name='Camera'))
    return filename


def post_test_clean(queue: Queue):
    """
    Empty tubes so that there is only air
    """
    # make doubly sure
    queue.put(QueueMessage('Starting', task_name='Post-test Clean'))
    queue.put(QueueMessage('Push out water', task_name='Post-test Clean'))
    move_water_valve(2)
    # push water out
    move_water_linear([5000])
    # take in more air
    queue.put(QueueMessage('Pulling in air', task_name='Post-test Clean'))
    move_water_valve(1)
    move_water_linear(0)
    queue.put(QueueMessage('Push out air', task_name='Post-test Clean'))
    move_water_valve(2)
    move_water_linear([5000])
    queue.put(QueueMessage('Finished', task_name='Post-test Clean'))


def movement_feedback(queue: Queue, completed: int, test_time: str):
    """
    Ensures the postition of the paper is correct for the next test
    """
    queue.put(QueueMessage('Starting', task_name='Movement Feedback'))
    x = 340
    i = 0
    queue.put(QueueMessage('Initial Paper movement',
                           task_name='Movement Feedback'))
    move_paper(queue, completed)
    filename = take_photo(queue, test_time)
    location = detect_circle(queue, filename)
    incorrect = abs(location[0] - x) > 20
    while(incorrect):
        i = i + 1
        queue.put(QueueMessage('Paper Jog: {}'.format(
            i), task_name='Movement Feedback'))
        os.remove(filename)
        move_paper(queue, completed, True)
        filename = take_photo(queue, test_time)
        location = detect_circle(queue, filename)
        incorrect = abs(location[0] - x) > 20
    queue.put(QueueMessage('Finished', task_name='Movement Feedback'))
    return location
