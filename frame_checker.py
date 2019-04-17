


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