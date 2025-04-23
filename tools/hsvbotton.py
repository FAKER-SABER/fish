# -*- coding: utf-8 -*-
import cv2
import numpy as np


def nothing(x):
    pass


# Create a window for the trackbars
cv2.namedWindow('Trackbars')
cv2.namedWindow('Result')

# Initial values
# low_H, low_S, low_V = 33, 19, 26
# high_H, high_S, high_V = 179, 243, 163
low_H, low_S, low_V = 111, 16, 80
high_H, high_S, high_V = 160, 78, 121

# Create trackbars
cv2.createTrackbar('Low H', 'Trackbars', low_H, 179, nothing)
cv2.createTrackbar('Low S', 'Trackbars', low_S, 255, nothing)
cv2.createTrackbar('Low V', 'Trackbars', low_V, 255, nothing)
cv2.createTrackbar('High H', 'Trackbars', high_H, 179, nothing)
cv2.createTrackbar('High S', 'Trackbars', high_S, 255, nothing)
cv2.createTrackbar('High V', 'Trackbars', high_V, 255, nothing)

# Load image
image_path = '../images/image.jpg'
original_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
if original_image is None:
    print(f"Error: Could not read image from {image_path}")
    exit()

# Resize image if it's too large
max_width = 800
if original_image.shape[1] > max_width:
    scale_ratio = max_width / original_image.shape[1]
    original_image = cv2.resize(original_image,
                                (int(original_image.shape[1] * scale_ratio),
                                 int(original_image.shape[0] * scale_ratio)))

# Convert to HSV once
hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

while True:
    # Get current positions of trackbars
    low_H = cv2.getTrackbarPos('Low H', 'Trackbars')
    low_S = cv2.getTrackbarPos('Low S', 'Trackbars')
    low_V = cv2.getTrackbarPos('Low V', 'Trackbars')
    high_H = cv2.getTrackbarPos('High H', 'Trackbars')
    high_S = cv2.getTrackbarPos('High S', 'Trackbars')
    high_V = cv2.getTrackbarPos('High V', 'Trackbars')

    # Create a copy of the original image to draw on
    image = original_image.copy()

    # Set color thresholds
    lower_bound = np.array([low_H, low_S, low_V])
    upper_bound = np.array([high_H, high_S, high_V])

    # Apply color thresholding
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Apply Gaussian and median blur to reduce noise
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    blurred = cv2.medianBlur(blurred, 5)
    # cv2腐蚀膨胀
    blurred = cv2.erode(blurred, None, iterations=10)
    blurred = cv2.dilate(blurred, None, iterations=10)

    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Thresholding
    _, binary = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

    # Create a horizontal stack of images for visualization
    mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # Stack images horizontally
    top_row = np.hstack([image, mask_colored])
    bottom_row = np.hstack([edges_colored, cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)])
    result = np.vstack([top_row, bottom_row])

    # Resize result if it's too large
    max_display_width = 1200
    if result.shape[1] > max_display_width:
        scale_ratio = max_display_width / result.shape[1]
        result = cv2.resize(result,
                            (int(result.shape[1] * scale_ratio),
                             int(result.shape[0] * scale_ratio)))

    # Show the result
    cv2.imshow('Result', result)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()