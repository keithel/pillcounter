import cv2
import numpy as np

# Load the image in grayscale
img = cv2.imread('pills1.jpg')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

pill_count = 0
for contour in contours:
    area = cv2.contourArea(contour)
    if area > 5000:
        pill_count += 1
        cv2.drawContours(img, [contour], 0, (0, 255, 0), 2)

cv2.imshow('gray', gray)
cv2.imshow('thresh', thresh)
cv2.imshow('contours', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

print('Number of pills:', pill_count)

