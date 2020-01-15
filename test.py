import sys
import time
from queue import Queue

import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

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
