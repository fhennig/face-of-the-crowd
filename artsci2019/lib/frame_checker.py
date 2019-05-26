import numpy as np


class FrameChecker:

    def __init__(self, frame_width, frame_height):
        self.line_width = 220
        self.line_width_margin = 40
        self.centre = int(frame_width / 2)
        self.centre_margin = 60
        self.max_height = 100
        self.threshold = 0.5

    def check(self, recognized_frame):
        return CheckedFrame(self.line_width,
                            self.line_width_margin,
                            self.centre,
                            self.centre_margin,
                            self.max_height,
                            self.threshold,
                            recognized_frame)


class CheckedFrame:

    def __init__(self,
                 line_width,
                 line_width_margin,
                 centre,
                 centre_margin,
                 max_height,
                 threshold,
                 recognized_frame):
        """Takes a recognized frame and analyzes the position of the face to see
        if it is the proper size and in the right position to be used for the portrait."""
        # recognized frame
        self.recognized_frame = recognized_frame
        self.threshold = threshold
        # left eye, right eye
        self.left_eye = recognized_frame.left_eye
        self.right_eye = recognized_frame.right_eye

        # width
        l_a = np.array(self.left_eye)
        r_a = np.array(self.right_eye)
        d = np.linalg.norm(l_a - r_a)
        margin = np.abs(line_width - d)
        self.width_score = (1 - min(margin / line_width_margin, 1))
        self.width_ok = np.abs(line_width - d) < line_width_margin

        # centre
        c = ((l_a + r_a) / 2)
        self.centre = (int(c[0]), int(c[1]))
        self.centre_target = (centre, self.centre[1])
        dist_to_centre = np.abs(c[0] - centre)
        self.centre_score = (1 - min(dist_to_centre / centre_margin, 1))
        self.centre_ok = dist_to_centre < centre_margin

        # heigth
        h_min = int(np.min((l_a[1], r_a[1])))
        h_max = int(np.max((l_a[1], r_a[1])))
        x = int(c[0])
        self.h_min_point = (x, h_min)
        self.h_max_point = (x, h_max)
        self.height_score = (1 - min(float(h_max - h_min) / max_height, 1))
        self.height_ok = h_max - h_min < max_height

        # all
        self.total_score = (self.width_score * self.centre_score * self.height_score) ** 0.5
        self.all_ok = self.total_score > self.threshold
