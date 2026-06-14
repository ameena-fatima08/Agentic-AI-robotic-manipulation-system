import cv2
import numpy as np


class DepthEstimator:

    def __init__(self):
        print("Lightweight Depth Estimator Initialized")

    def estimate(self, frame, bbox):

        x1, y1, x2, y2 = bbox

        # Bounding box width and height
        width = x2 - x1
        height = y2 - y1

        # Approximate object size
        area = width * height

        # Avoid division by zero
        if area <= 0:
            return 9999

        """
        Simple depth approximation:
        Bigger object in frame = closer object
        Smaller object = farther away
        """

        depth = 100000 / area

        return float(round(depth, 2))