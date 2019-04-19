#! /usr/bin/env python3
import datetime
import face_recog
import cv2
import argparse
import numpy as np

from frame_checker import CheckedFrame
from portrait import PortraitGen
from util import scale_frame, scale_point


def draw_checked_frame(frame, checked_frame, factor):
    green = (0, 255, 0)
    red = (0, 0, 255)

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
    def __init__(self, camera_number, rotate, fullscreen, pool_size):
        self.camera_number = camera_number
        self.rotate = rotate
        self.fullscreen = fullscreen
        self.scaling_factor = 4
        self.preview_window = "preview"
        self.genimage_window = "genimage"
        self.genimage = None
        self.video_capture = None
        self.collected_frames = []
        self.pg = PortraitGen(5, pool_size)
        self.debug_scaling = 1/2
        self.current_checked_frames = []
        self.checkpoint_time = datetime.datetime.now()

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
        changed = self.pg.update(ok_frames)
        if changed:
            print("Updated")
            f = scale_frame(self.pg.portrait_frame, self.debug_scaling)
            self.genimage = f
            cv2.imshow(self.genimage_window, f)
            self.checkpoint_time = current_time + datetime.timedelta(seconds=10)


    def loop_update(self, frame):
        frame = scale_frame(frame, self.debug_scaling)
        new_preview = frame
        new_genimage = np.copy(self.genimage)
        if self.current_checked_frames:
            # draw face lines
            for cf in self.current_checked_frames:
                draw_checked_frame(new_preview, cf, self.debug_scaling)
                draw_checked_frame(new_genimage, cf, self.debug_scaling)

            self.portrait_update(self.current_checked_frames)

        # Display the resulting image
        cv2.imshow(self.preview_window, new_preview)
        cv2.imshow(self.genimage_window, new_genimage)

    def start(self):
        process_this_frame = True

        rval = True
        while rval:
            # get a single frame
            rval, frame = my_get_frame(self.video_capture, self.rotate)

            # get the faces
            if process_this_frame:
                rfs = face_recog.get_faces(frame, self.scaling_factor)
                self.current_checked_frames = [CheckedFrame(rf) for rf in rfs]

            process_this_frame = not process_this_frame

            # exit on ESC
            key = cv2.waitKey(20)
            if key == 113:  # exit on q
                break

            self.loop_update(frame)


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--camera_input",
        default=1,
        type=int,
        help="Which camera to use."
    )
    parser.add_argument(
        "--rotate",
        action='store_true',
        default=False,
        help="Whether to rotate the image."
    )
    parser.add_argument(
        "--fullscreen",
        action='store_true',
        default=False,
        help="Whether to display the generated image fullscreen."
    )
    parser.add_argument(
        "--pool_size",
        default=4,
        type=int,
        help="The number of parallel processes to use."
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print(args)
    a = Application(args.camera_input,
                    args.rotate,
                    args.fullscreen,
                    args.pool_size)
    init_successful = a.init()
    if not init_successful:
        print("Error in init.")
        return
    a.start()
    a.teardown()


if __name__ == "__main__":
    main()
