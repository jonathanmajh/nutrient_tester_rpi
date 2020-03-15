import cv2 as cv
import numpy as np
import json
from matplotlib import pyplot as plt

filename = 'samples/focus.jpg'

img = cv.imread(filename)
img = cv.medianBlur(img, 5)
# 256 shades of gray
gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# detect circles
circles = cv.HoughCircles(gray_img, cv.HOUGH_GRADIENT, 1, 20,
                            param1=50, param2=30, minRadius=0, maxRadius=0)
circles = np.uint16(np.around(circles))

location = circles[0][0]  # return first circle detected

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
    result[hsv_var[i]] = hist.tolist()
    plt.plot(hist, color=col)
    plt.xlim([0, 256])

hist_file = '{}_hist.png'.format(filename[:-4])
plt.savefig(hist_file, bbox_inches='tight')

json_file = '{}_hist.json'.format(filename[:-4])
with open(json_file, 'w') as jf:
    json.dump(result, jf, indent=4)