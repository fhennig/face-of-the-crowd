#! /usr/bin/env python3
import face_recog
import cv2
import argparse
from portrait import PortraitGen
from util import scale_face_locations, scale_frame


def draw_face_box(frame, face_location):
    # Display the results
    top, right, bottom, left = face_location
    # Draw a box around the face
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)


class Application:
    def __init__(self, camera_number, rotate):
        self.camera_number = camera_number
        self.rotate = rotate
        self.scaling_factor = 4
        self.preview_window = "preview"
        self.genimage_window = "genimage"
        self.video_capture = None
        self.collected_frames = []
        self.pg = PortraitGen()

    def init(self):
        # initialize window
        cv2.namedWindow(self.preview_window)
        cv2.namedWindow(self.genimage_window)

        # get webcam
        self.video_capture = cv2.VideoCapture(self.camera_number)
        self.video_capture.set(3, 1920)
        self.video_capture.set(4, 1080)

        if self.video_capture.isOpened():  # try to get the first frame
            rval, frame = self.video_capture.read()
        else:
            rval = False
        if not rval:
            return False
        return True

    def teardown(self):
        cv2.destroyWindow(self.preview_window)
        cv2.destroyWindow(self.genimage_window)

        self.video_capture.release()

    def update_genimage(self, recognized_frames):
        """Updates the generated image, the merge of all the faces."""
        changed = self.pg.update(recognized_frames)
        if not changed:
            return
        f = scale_frame(self.pg.portrait_frame, 1 / 2)
        cv2.imshow(self.genimage_window, f)

    def update_preview(self, frame, face_locations):
        factor = 1 / 2
        frame = scale_frame(frame, factor)
        if face_locations:
            face_locations = scale_face_locations(face_locations, factor)
            # draw boxes
            for face_location in face_locations:
                draw_face_box(frame, face_location)

        # Display the resulting image
        cv2.imshow(self.preview_window, frame)

    def start(self):
        recognized_frames = []
        process_this_frame = True

        rval = True
        while rval:
            # get a single frame
            rval, frame = self.video_capture.read()

            if self.rotate:
                frame = cv2.transpose(frame)
                frame = cv2.flip(frame, flipCode=1)

            # get the faces
            if process_this_frame:
                recognized_frames = face_recog.get_faces(frame, self.scaling_factor)

            process_this_frame = not process_this_frame

            # exit on ESC
            key = cv2.waitKey(20)
            if key == 113:  # exit on q
                break
            if key == 112:  # take screenshot on p
                self.update_genimage(recognized_frames)

            f_locs = [rf.face_loc for rf in recognized_frames]
            self.update_preview(frame, f_locs)


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

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    a = Application(args.camera_input,
                    args.rotate)
    init_successful = a.init()
    if not init_successful:
        print("Error in init.")
        return
    a.start()
    a.teardown()


if __name__ == "__main__":
    main()
