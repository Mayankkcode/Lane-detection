# -*- coding: utf-8 -*-
"""lanedetection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kOEVhQdRRk5vob8DoLZQGb8il070cDmR
"""

# Model for the lane detection

import cv2
import numpy as np

def load_image(image_path):
    # Load the image
    return cv2.imread(image_path)

def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred

def detect_lanes(image):
    # Apply Canny Edge Detection
    edges = cv2.Canny(image, 50, 150)
    # Using Hough Transform to detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=50)
    return lines

def draw_lanes(image, lines):
    # Create a blank image to draw lanes
    lane_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Draw detected lane lines on the blank image
            cv2.line(lane_image, (x1, y1), (x2, y2), (255, 255, 255), 10)
    return lane_image

def generate_bitmap(lane_image, original_image):
    binary_output = np.where(lane_image > 0, 255, 0).astype('uint8')
    return binary_output

def background_isolation(image):
    # Optional: isolate background
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Define range for the lane color (white/yellow)
    lower_lane = np.array([0, 0, 200])
    upper_lane = np.array([180, 255, 255])
    # Mask the lanes
    mask = cv2.inRange(hsv, lower_lane, upper_lane)
    isolated = cv2.bitwise_and(image, image, mask=mask)
    return isolated

def process_pipeline(image_path):
    image = load_image(image_path)
    preprocessed = preprocess_image(image)
    lanes = detect_lanes(preprocessed)
    lane_image = draw_lanes(image, lanes)
    bitmap = generate_bitmap(lane_image, image)
    isolated_background = background_isolation(image)

    return bitmap, isolated_background

# Example :
bitmap, isolated_background = process_pipeline("img 1.jpg")

# Save outputs
cv2.imwrite("lane_bitmap.jpg", bitmap)
cv2.imwrite("isolated_background.jpg", isolated_background)

#Implementing the motion planning algorithm

import numpy as np
import matplotlib.pyplot as plt

class RRT:
    def __init__(self, start, goal, obstacle_list, map_size):
        self.start = start
        self.goal = goal
        self.obstacle_list = obstacle_list
        self.map_size = map_size
        self.step_size = 1.0
        self.max_iter = 1000
        self.node_list = [start]

    def plan(self):
        for i in range(self.max_iter):
            rand_point = self.random_point()
            nearest_node = self.get_nearest_node(rand_point)
            new_node = self.extend(nearest_node, rand_point)

            if self.is_collision(new_node):
                continue

            self.node_list.append(new_node)

            if self.is_goal_reached(new_node):
                print("Goal reached!")
                break

        return self.node_list

    def random_point(self):
        return np.random.uniform(0, self.map_size, 2)

    def get_nearest_node(self, rand_point):
        return min(self.node_list, key=lambda node: np.linalg.norm(np.array(node) - np.array(rand_point)))

    def extend(self, nearest_node, rand_point):
        direction = (rand_point - np.array(nearest_node)) / np.linalg.norm(rand_point - np.array(nearest_node))
        new_node = np.array(nearest_node) + self.step_size * direction
        return tuple(new_node)

    def is_collision(self, node):
        for obs in self.obstacle_list:
            if np.linalg.norm(np.array(node) - np.array(obs)) < 1.0:  # Simple distance-based collision check
                return True
        return False

    def is_goal_reached(self, node):
        return np.linalg.norm(np.array(node) - np.array(self.goal)) < 1.0

# Example
start = (0, 0)
goal = (10, 10)
obstacle_list = [(5, 5), (3, 7), (6, 9)]
map_size = 15

rrt = RRT(start, goal, obstacle_list, map_size)
path = rrt.plan()

# Plotting the result
for node in path:
    plt.scatter(node[0], node[1], c='blue')
plt.scatter(start[0], start[1], c='green', label='Start')
plt.scatter(goal[0], goal[1], c='red', label='Goal')
plt.show()