from __future__ import division
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import logging
import hbp_nrp_cle.tf_framework as nrp
from hbp_nrp_excontrol.logs import clientLogger


class Coordinates: 

    def __init__(self, x, y, z):
        self.x = x 
        self.y = y
        self.z = z

class Results(object):
    """
    An intermediate helper class for the results of detect_red
    """

    def __init__(self, left, right, go_on):
        self.left = left
        self.right = right
        self.go_on = go_on


def detect_white(image):
    bridge = CvBridge()
    tf = nrp.tf_lib
    left_image  = 0
    right_image = 0 
    if not isinstance(image, type(None)):
        lower_threshold = np.array([0, 0, 252])
        upper_threshold = np.array([45, 13, 255])
        cv_image = bridge.imgmsg_to_cv2(image, "rgb8")
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv_image, lower_threshold, upper_threshold)
        image_size = (cv_image.shape[0] * cv_image.shape[1])
        if (image_size > 0): 
            half = cv_image.shape[1] // 2 
            left_image  = cv2.countNonZero(mask[:, :half])
            right_image = cv2.countNonZero(mask[:, half:])
            left_image = 2 * (left_image / image_size)
            right_image = 2 * (right_image / image_size)
        return Results(left_image, right_image, 0)