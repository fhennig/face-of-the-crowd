import datetime
import cv2
import numpy as np

from artsci2019.frame_checker import FrameChecker
from artsci2019.util import scale_frame, scale_point, is_in_frame
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


def draw_triangles(frame, checked_frame, factor):
    f_h, f_w, _ = checked_frame.recognized_frame.frame.shape
    # prep delaunay
    rect = (0, 0, f_w, f_h)
    subdiv = cv2.Subdiv2D(rect)
    for lm in checked_frame.recognized_frame.face_landmarks:
        if is_in_frame(f_w, f_h, lm):
            subdiv.insert(lm)
    print("triangles: {}".format(len(subdiv.getTriangleList())))
    for t in subdiv.getTriangleList():
        t = np.reshape(t, (3, 2)).astype(np.int32)
        pt1 = scale_point(tuple(t[0]), factor)
        pt2 = scale_point(tuple(t[1]), factor)
        pt3 = scale_point(tuple(t[2]), factor)
        cv2.line(frame, pt1, pt2, (255, 255, 255), 1, 8, 0)
        cv2.line(frame, pt2, pt3, (255, 255, 255), 1, 8, 0)
        cv2.line(frame, pt3, pt1, (255, 255, 255), 1, 8, 0)


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
            cv2.imshow(self.genimage_window, self.genimage)
            self.checkpoint_time = current_time + datetime.timedelta(seconds=10)
        return changed

    def loop_update(self, frame):
        frame = scale_frame(frame, self.debug_scaling)
        new_preview = frame
        new_genimage = self.genimage

        current_time = datetime.datetime.now()
        if current_time > self.checkpoint_time and self.current_checked_frames:
            # draw face lines
            score = max([cf.total_score for cf in self.current_checked_frames])
            for cf in self.current_checked_frames:
                print("Score: {}".format(cf.total_score))
            new_genimage = cv2.addWeighted(self.genimage, 1 - score, frame, score, 0)
            draw_triangles(new_genimage, self.current_checked_frames[0], self.debug_scaling)
            draw_triangles(new_preview, self.current_checked_frames[0], self.debug_scaling)
            if score > 0.8:
                print("YO")
                draw_triangles(new_genimage, self.current_checked_frames[0], self.debug_scaling)

        # Display the resulting image
        cv2.imshow(self.preview_window, new_preview)
        cv2.imshow(self.genimage_window, new_genimage)
        cv2.waitKey(50)

        changed = self.portrait_update(self.current_checked_frames)

    def start(self):
        process_this_frame = True

        rval = True
        while rval:
            # get a single frame
            rval, frame = my_get_frame(self.video_capture, self.rotate)
            # TODO drop frames while processing

            # get the faces
            if process_this_frame:
                rfs = get_faces(frame, self.scaling_factor)
                self.current_checked_frames = [self.frame_checker.check(rf) for rf in rfs]

            process_this_frame = not process_this_frame

            self.loop_update(frame)

            # exit on ESC
            key = cv2.waitKey(20)
            if key == 113:  # exit on q
                break

