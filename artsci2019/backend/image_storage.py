import cv2
import datetime
import os


class ImageStorage:

    def __init__(self, directory):
        self.dir = directory

    def update(self, recognized_frames):
        print("update")