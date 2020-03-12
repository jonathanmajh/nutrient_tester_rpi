import json
from queue import Queue
from typing import List

import cv2 as cv
import matplotlib
import numpy as np
from matplotlib import pyplot as plt

from misc import QueueMessage

matplotlib.use('TkAgg')


def detect_lines():
    # load photo
    image = cv.imread('samples/white.jpg')
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # cv.imshow("gray", image_gray)
    # cv.waitKey(0)
    edges = cv.Canny(image_gray, 50, 150, apertureSize=3)
    # 100 min line and 80 max line length is ok for the inner square
    lines = cv.HoughLinesP(edges, 1, np.pi/180, 100,
                           minLineLength=100, maxLineGap=80)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv.namedWindow('lines', cv.WINDOW_NORMAL)
    cv.imshow('lines', image)
    cv.resizeWindow('lines', 800, 800)
    cv.waitKey(0)


def detect_all_circle():
    img = cv.imread('samples/focus.jpg')
    img = cv.medianBlur(img, 5)
    cimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    circles = cv.HoughCircles(cimg, cv.HOUGH_GRADIENT, 1, minDist=20,
                              param1=50, param2=30, minRadius=0, maxRadius=100)
    # it is important to get the right min (80) / max radius (100)
    # though minDist btw circles is important too
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        # draw the outer circle
        cv.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
    cv.namedWindow('circles', cv.WINDOW_NORMAL)
    cv.resizeWindow('circles', 800, 800)
    cv.imshow('circles', cimg)
    cv.waitKey(0)
    cv.destroyAllWindows()


def detect_one_circle():
    # also masked area outside circle
    img = cv.imread('samples/focus.jpg')
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img = cv.medianBlur(img, 5)
    cimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    circles = cv.HoughCircles(cimg, cv.HOUGH_GRADIENT, 1, 20,
                              param1=50, param2=30, minRadius=0, maxRadius=0)
    circles = np.uint16(np.around(circles))

    # multiple circles were detected but we only want the first circle
    # since it always detects the outer circle it might be good to reduce the radius so that only the inner circle is shown TODO
    i = circles[0][0]
    x, y, r = circles[0][0]
    print(circles[0][0])
    # draw the outer circle
    radius_offset = 60
    cv.circle(cimg, (i[0], i[1]), i[2]-radius_offset, (0, 255, 0), 2)
    # draw the center of the circle
    cv.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
    # cv.namedWindow('circles',cv.WINDOW_NORMAL)
    # cv.resizeWindow('circles', 800, 800)
    # cv.imshow('circles',cimg)
    # cv.waitKey(0)

    # create a mask of just the circle in white
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv.circle(mask, (i[0], i[1]), i[2]-radius_offset, 255, -1)
    # cv.imshow('mask',mask)
    # cv.waitKey(0)

    masked = cv.bitwise_and(img, img, mask=mask)
    # cv.namedWindow('masked',cv.WINDOW_NORMAL)
    # cv.resizeWindow('masked', 800, 800)
    # cv.imshow('masked',masked)
    # cv.waitKey(0)

    # dont really need an extra mask...
    hsv_mask = cv.bitwise_and(hsv, hsv, mask=mask)
    cv.namedWindow('masked', cv.WINDOW_NORMAL)
    cv.resizeWindow('masked', 800, 800)
    cv.imshow('masked', hsv_mask)
    cv.waitKey(0)

    for i, col in enumerate(['r', 'g', 'b']):
        hist = cv.calcHist([hsv], [i], mask, [256], [0, 256])
        plt.plot(hist, color=col)
        plt.xlim([0, 256])

    plt.show()

    hist_2d = cv.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
    plt.imshow(hist_2d,interpolation='nearest')
    plt.show()
    # Perhaps write the array to csv for easier reading
    # https://stackoverflow.com/questions/44691524/write-a-2d-array-to-a-csv-file-with-delimiter
    # there must be a faster way
    # rows, cols, temp = img.shape
    # for i in range(cols):
    #     for j in range(rows):
    #         if hypot(i-x, j-y) > r:
    #             img[j,i] = 0

    # cv.namedWindow('masked',cv.WINDOW_NORMAL)
    # cv.resizeWindow('masked', 800, 800)
    # cv.imshow('masked',img)
    # cv.waitKey(0)
    cv.destroyAllWindows()


def detect_circle(queue: Queue, filename: str):
    queue.put(QueueMessage('Starting', task_name='Detect Circle'))
    img = cv.imread(filename)
    img = cv.medianBlur(img, 5)
    # 256 shades of gray
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # detect circles
    circles = cv.HoughCircles(gray_img, cv.HOUGH_GRADIENT, 1, 20,
                              param1=50, param2=30, minRadius=0, maxRadius=0)
    circles = np.uint16(np.around(circles))
    queue.put(QueueMessage('Circle detected at: {}'.format(
        str(circles[0][0])), task_name='Detect Circle'))
    queue.put(QueueMessage('Finished', task_name='Detect Circle'))
    return circles[0][0]  # return first circle detected


def detect_color(queue: Queue, filename: str, location: List[int]):
    queue.put(QueueMessage('Starting', task_name='Detect Color'))
    radius_offset = 60
    img = cv.imread(filename)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    x, y, z = location
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv.circle(mask, (x, y), z-radius_offset, 255, -1)
    result = {}
    plot_color = ['r', 'g', 'b']
    hsv_var = ['h', 's', 'v']
    for i, col in enumerate(plot_color):
        hist = cv.calcHist([hsv], [i], mask, [256], [0, 256])
        result[hsv_var[i]] = hist
        plt.plot(hist, color=col)
        plt.xlim([0, 256])
    queue.put(QueueMessage('Saving Files', task_name='Detect Circle'))
    hist_file = '{}_hist.png'.format(filename[:-3])
    plt.savefig(hist_file, bbox_inches='tight')

    json_file = '{}_hist.json'.format(filename[:-3])
    with open(json_file, 'w') as jf:
        json.dump(result, jf, indent=4)
    queue.put(QueueMessage('Finished', task_name='Detect Circle'))
    return (hist_file, json_file, result)

def process_histogram(hist):
    """
    """

detect_all_circle()