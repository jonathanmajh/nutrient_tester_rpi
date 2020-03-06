import sys
import time
from queue import Queue
from math import sqrt

import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from motor_control import move_linear_water, move_valve
import maestro

from misc import QueueMessage
matplotlib.use('TkAgg')

def test_main(queue: Queue):
    try:
        queue.put(QueueMessage('Starting Tests'))
        detect_color(queue)
        queue.put(QueueMessage('Sleeping 5 seconds'))
        time.sleep(1)
        queue.put(QueueMessage('Raising Exception'))
        queue.put(QueueMessage('', 0))
    except:
        queue.put(QueueMessage('Unexpected Exception', 4, sys.exc_info()))


def detect_color(queue: Queue):
    # take a photo
    photo_path = '/home/jon/nutrient_tester_rpi/samples/real.png'
    # load photo
    image = cv2.imread(photo_path)
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

def pretest_clean(queue: Queue):
    """
    Flush the pipe with air before test begins
    Assume water actuator starts in extended position
    And Valve is 1
    """
    # suck in air
    move_linear_water([0])
    move_valve(2)
    # push out air, pull in water
    move_linear_water([5000, 1000])
    move_valve(1)


def move_paper(queue: Queue, completed: int):
    """
    Moves new paper into position
    Need to somehow track roll usage
    """
    speed = 2 # rad / second
    length = 20 # mm
    total_length = 20 * completed
    inner_radius = 123 #TODO
    thickness = 0.05 # used paper thickness.... TODO
    radius = sqrt(total_length * thickness / 3.14159 + inner_radius * inner_radius)
    # https://math.stackexchange.com/questions/2145821/calculating-the-length-of-tape-when-it-is-wound-up
    theta = length / radius
    run_time = theta / speed
    servo = maestro.Controller()
    servo.setAccel(0, 4)
    servo.setSpeed(0, 10)
    servo.setTarget(0, 6000) # turn continuous servo
    time.sleep(run_time)
    servo.setTarget(0, 1500) # stop servo
