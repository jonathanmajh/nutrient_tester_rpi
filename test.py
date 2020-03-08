import sys
import time
from datetime import datetime
from queue import Queue
from math import sqrt
from picamera import PiCamera
from threading import Thread

import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from motor_control import move_water_linear, move_water_valve, move_reactant_linear
import maestro

from misc import QueueMessage
matplotlib.use('TkAgg')

def test_main(queue: Queue, completed: int, test_time: datetime, FORMAT: str):
    try:
        queue.put(QueueMessage('Starting', task_name='Test Main'))
        timer = time.time()
        pre_test_clean(queue)
        just_add_water(queue, completed)
        # tube cleaning can run async at while we are waiting for heater
        clean = Thread(target=post_test_clean, args=(queue, ))
        clean.start()
        run_heater(queue)
        move_paper(queue, completed)
        filename = take_photo(queue, test_time, FORMAT)
        detect_color(queue, filename)
        # it doesnt really matter when cleaning finishes as long as it does by the end
        clean.join()
        queue.put(QueueMessage('Finished in: ' + str(time.time() - timer), task_name='Test Main'))
    except:
        queue.put(QueueMessage('Unexpected Exception', 4, sys.exc_info()))


def detect_color(queue: Queue, filename: str):
    # load photo
    image = cv2.imread(filename)
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Range for lower red
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(image_hsv, lower_red, upper_red)
    # TODO color mask vs shape mask
    # Range for upper range
    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask = mask + cv2.inRange(image_hsv, lower_red, upper_red)
    queue.put(QueueMessage('Displaying Masked Image'))
    cv2.imshow('masks', mask)
    # waitKey is necessary for the image to appear in the windows -_-
    cv2.waitKey(0)
    hist = cv2.calcHist([image_hsv], [0, 1], None, [
                        180, 256], [0, 180, 0, 256])
    cv2.imshow('hist', hist)
    cv2.waitKey(0)
    plt.imshow(hist)
    plt.show()

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
    queue.put(QueueMessage('Pushing out air, then pulling in water', task_name='Pre-Test Cleaning'))
    move_water_valve(2)
    # push out air, pull in water
    move_water_linear([5000, 1000])
    queue.put(QueueMessage('Finished', task_name='Pre-Test Cleaning'))



def move_paper(queue: Queue, completed: int):
    """
    Moves new paper into position
    Need to somehow track roll usage
    """
    queue.put(QueueMessage('Starting', task_name='Move Paper'))
    speed = 2 # rad / second
    length = 20 # mm
    total_length = 20 * completed
    inner_radius = 123 #TODO
    thickness = 0.05 # used paper thickness.... TODO
    radius = sqrt(total_length * thickness / 3.14159 + inner_radius * inner_radius)
    # https://math.stackexchange.com/questions/2145821/calculating-the-length-of-tape-when-it-is-wound-up
    theta = length / radius
    run_time = theta / speed
    queue.put(QueueMessage('Turning Servo by {rad} rad, time required {time} s'.format(rad=theta, time=run_time), task_name='Move Paper'))
    servo = maestro.Controller()
    servo.setAccel(0, 4)
    servo.setSpeed(0, 10)
    servo.setTarget(0, 6000) # turn continuous servo
    time.sleep(run_time)
    servo.setTarget(0, 1500) # stop servo
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
    queue.put(QueueMessage('Turning on heater for {time} seconds'.format(time=300), task_name='Heater'))
    # TODO set pin to high
    time.sleep(300) # 5 minutes
    queue.put(QueueMessage('Finished', task_name='Heater'))

def take_photo(queue: Queue, test_time: datetime, FORMAT: str):
    """
    """
    queue.put(QueueMessage('Starting', task_name='Camera'))
    queue.put(QueueMessage('Turning on LEDs', task_name='Camera'))
    # TODO
    camera = PiCamera()
    queue.put(QueueMessage('Taking photo', task_name='Camera'))
    filename = '/home/pi/nutrient_tester_pi/{}.jpg'.format(test_time.strftime(FORMAT))
    camera.capture(filename)
    queue.put(QueueMessage('Photo saved as "{}"'.format(filename), task_name='Camera'))
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