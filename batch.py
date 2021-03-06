import os, json, csv
from typing import List

import cv2 as cv
import matplotlib
import numpy as np
from matplotlib import pyplot as plt

def detect_circle(filename: str):
    img = cv.imread(filename)
    img = cv.medianBlur(img, 5)
    # 256 shades of gray
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # detect circles
    circles = cv.HoughCircles(gray_img, cv.HOUGH_GRADIENT, 1, 20,
                              param1=50, param2=30, minRadius=0, maxRadius=0)
    circles = np.uint16(np.around(circles))
    i = circles[0][0]
    cv.circle(img, (i[0], i[1]), 60, (0, 255, 0), 2)
    # draw the center of the circle
    cv.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
    # cv.namedWindow('circles',cv.WINDOW_NORMAL)
    # cv.resizeWindow('circles', 800, 800)
    # cv.imshow('circles',img)
    # cv.waitKey(0)
    # cv.destroyWindow('circles')

    print('Circle detected at: {}'.format(
        str(circles[0][0])))
    return circles[0][0]  # return first circle detected


def detect_color(filename: str, location: List[int]):
    """
    using rgb
    """
    matplotlib.use('TkAgg')
    radius_offset = 60
    img = cv.imread(filename)
    # hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    x, y, z = location
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv.circle(mask, (x, y), 60, 255, -1)
    result = [0,0,0]
    plot_color = ['b', 'g', 'r']
    hsv_var = ['h', 's', 'v']
    for i, col in enumerate(plot_color):
        hist = cv.calcHist([img], [i], mask, [256], [0, 256])
        # plt.plot(hist, color=col)
        # plt.xlim([0, 256])
        for j, arr in enumerate(hist):
            result[i] = result[i] + (j * arr[0])
        # result[hsv_var[i]] = hist.tolist()

    # hist_file = '{}_hist_rgb.png'.format(filename[:-4])
    # plt.savefig(hist_file, bbox_inches='tight')
    plt.close('all')
    # json_file = '{}_hist.json'.format(filename[:-4])
    # with open(json_file, 'w') as jf:
    #     json.dump(result, jf, indent=4)

    return result

def detect_hsv(filename: str, location: List[int]):
    """
    using hsv
    """
    matplotlib.use('TkAgg')
    radius_offset = 60
    img = cv.imread(filename)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    x, y, z = location
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv.circle(mask, (x, y), z-radius_offset, 255, -1)
    result = {}
    plot_color = ['r', 'g', 'b']
    hsv_var = ['h', 's', 'v']
    result = [0, 0, 0]
    for i, col in enumerate(plot_color):
        hist = cv.calcHist([hsv], [i], mask, [256], [0, 256])
        # plt.plot(hist, color=col)
        # plt.xlim([0, 256])
        for j, arr in enumerate(hist):
            result[i] = result[i] + (j * arr[0])
        # result[hsv_var[i]] = hist.tolist()

    # hist_file = '{}_hist_sat.png'.format(filename[:-4])
    # plt.savefig(hist_file, bbox_inches='tight')
    plt.close('all')

    return result
    # json_file = '{}_hist.json'.format(filename[:-4])
    # with open(json_file, 'w') as jf:
    #     json.dump(result, jf, indent=4)

def batch_photo():
    """
    Batch function for processing photos in a directory
    """
    directory = os.fsencode('/home/jon/nutrient_tester_rpi/Calibration/')
    with open('/home/jon/nutrient_tester_rpi/Calibration/result_hsv.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'h', 's', 'v'])
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith('.jpg'):
                print('Processing: {}'.format(filename))
                filename = '/home/jon/nutrient_tester_rpi/Calibration/' + filename
                circle = detect_circle(filename)
                result = detect_hsv(filename, circle)
                writer.writerow([filename, result[0], result[1], result[2]])
            else:
                print('{} was skipped '.format(filename))


batch_photo()