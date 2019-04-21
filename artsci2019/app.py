import datetime
import cv2
import numpy as np

from artsci2019.frame_checker import FrameChecker
from artsci2019.util import scale_frame, scale_point
from artsci2019.face_recog import get_faces


def draw_checked_frame(frame, checked_frame, factor):
    green = (100, 255, 100)
    red = (100, 100, 255)

    eye_line_color = green if checked_frame.width_ok else red
    cv2.line(frame,
             scale_point(checked_frame.left_eye, factor),
             scale_point(checked_frame.right_eye, factor),
             eye_line_color,
             thickness=2)

    centre_line_color = green if checked_frame.centre_ok else red
    cv2.line(frame,
             scale_point(checked_frame.centre, factor),
             scale_point(checked_frame.centre_target, factor),
             centre_line_color,
             thickness=4)

    height_line_color = green if checked_frame.height_ok else red
    cv2.line(frame,
             scale_point(checked_frame.h_min_point, factor),
             scale_point(checked_frame.h_max_point, factor),
             height_line_color,
             thickness=2)


def my_get_frame(video_capture, rotate):
    # get a single frame
    rval, frame = video_capture.read()

    if rotate:
        frame = cv2.transpose(frame)
        frame = cv2.flip(frame, flipCode=1)

    return rval, frame


class Application:
    def __init__(self, camera_number, rotate, fullscreen, processing_backend):
        self.camera_number = camera_number
        self.rotate = rotate
        self.fullscreen = fullscreen
        self.debug_scaling = 1/2
        if fullscreen:
            self.debug_scaling = 1
        self.scaling_factor = 4
        self.preview_window = "preview"
        self.genimage_window = "genimage"
        self.genimage = None
        self.video_capture = None
        self.collected_frames = []
        self.pb = processing_backend
        self.current_checked_frames = []
        self.checkpoint_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.frame_checker = None

    def init(self):
        # initialize window
        cv2.namedWindow(self.preview_window)
        cv2.namedWindow(self.genimage_window)
        if self.fullscreen:
            cv2.setWindowProperty(self.genimage_window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # get webcam
        self.video_capture = cv2.VideoCapture(self.camera_number)
        self.video_capture.set(3, 1920)
        self.video_capture.set(4, 1080)

        rval = False
        frame = None

        if self.video_capture.isOpened():  # try to get the first frame
            rval, frame = my_get_frame(self.video_capture, self.rotate)

        if frame is not None:
            self.genimage = scale_frame(frame, self.debug_scaling)
            cv2.imshow(self.genimage_window, self.genimage)

        if self.rotate:
            self.frame_checker = FrameChecker(1080, 1920)
        else:
            self.frame_checker = FrameChecker(1920, 1080)

        return rval

    def teardown(self):
        cv2.destroyWindow(self.preview_window)
        cv2.destroyWindow(self.genimage_window)

        self.video_capture.release()

    def portrait_update(self, checked_frames):
        current_time = datetime.datetime.now()
        if current_time < self.checkpoint_time:
            print("too early")
            return  # too early for an update
        # update portrait
        ok_frames = [cf.recognized_frame
                     for cf in checked_frames
                     if cf.all_ok]
        changed = False
        if ok_frames:
            changed = self.pb.update(ok_frames)
        if changed:
            print("Updated")
            portrait_frame = self.pb.get_portrait()
            f = scale_frame(portrait_frame, self.debug_scaling)
            self.genimage = f
            cv2.imshow(self.genimage_window, f)
            self.checkpoint_time = current_time + datetime.timedelta(seconds=10)
        return changed

    def loop_update(self, frame):
        frame = scale_frame(frame, self.debug_scaling)
        new_preview = frame
        new_genimage = np.copy(self.genimage)

        current_time = datetime.datetime.now()
        if current_time > self.checkpoint_time:
            # draw face lines
            for cf in self.current_checked_frames:
                draw_checked_frame(new_preview, cf, self.debug_scaling)
                draw_checked_frame(new_genimage, cf, self.debug_scaling)

        # Display the resulting image
        cv2.imshow(self.preview_window, new_preview)
        cv2.imshow(self.genimage_window, new_genimage)

        changed = self.portrait_update(self.current_checked_frames)

    def start(self):
        process_this_frame = True

        rval = True
        while rval:
            # get a single frame
            rval, frame = my_get_frame(self.video_capture, self.rotate)

            # get the faces
            if process_this_frame:
                rfs = get_faces(frame, self.scaling_factor)
                self.current_checked_frames = [self.frame_checker.check(rf) for rf in rfs]

            process_this_frame = not process_this_frame

            # exit on ESC
            key = cv2.waitKey(20)
            if key == 113:  # exit on q
                break

            self.loop_update(frame)
