import cv2
import numpy as np


def scale_face_location(face_location, factor):
    top, right, bottom, left = face_location
    return (int(top * factor),
            int(right * factor),
            int(bottom * factor),
            int(left * factor))


def scale_point(point, factor):
    x, y = point
    return (int(x * factor),
            int(y * factor))


def scale_face_locations(face_locations, factor):
    face_locations = [(int(top * factor),
                       int(right * factor),
                       int(bottom * factor),
                       int(left * factor))
                      for top, right, bottom, left in face_locations]
    return face_locations


def scale_face_landmarkss(face_landmarkss, factor):
    return [[(int(x * factor),
              int(y * factor))
             for x, y in flms]
            for flms in face_landmarkss]


def scale_frame(frame, factor):
    height, width, _ = frame.shape
    new_h = int(height * factor)
    new_w = int(width * factor)
    frame = cv2.resize(frame, (new_w, new_h))
    return frame
