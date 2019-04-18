import numpy as np


class FrameChecker:

    def __init__(self, margins=(0.35, 0.15, 0.2, 0.15)):
        self.margins = margins

    def check(self, recognized_frame):
        loc = recognized_frame.face_locations
        return True

    def filter_frames(self, recognized_frames):
        for rf in recognized_frames:
            if self.check(rf):
                yield rf


class CheckedFrame():

    def __init__(self, recognized_frame):
        # left eye, right eye
        self.left_eye = recognized_frame.left_eye
        self.right_eye = recognized_frame.right_eye

        # width
        l_a = np.array(self.left_eye)
        r_a = np.array(self.right_eye)
        d = np.linalg.norm(l_a - r_a)
        self.width_ok = np.abs(325 - d) < 55

        # centre
        c = ((l_a + r_a) / 2)
        self.centre = (int(c[0]), int(c[1]))
        self.centre_target = (540, self.centre[1])
        dist_to_centre = np.abs(c[0] - 540)
        self.centre_ok = dist_to_centre < 30

        # heigth
        h_min = int(np.min((l_a[1], r_a[1])))
        h_max = int(np.max((l_a[1], r_a[1])))
        x = int(c[0])
        self.h_min_point = (x, h_min)
        self.h_max_point = (x, h_max)
        self.height_ok = h_max - h_min < 50
