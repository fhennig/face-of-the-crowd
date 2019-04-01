#! /usr/bin/env python3
import face_recognition
import cv2
import argparse
import numpy as np


def scale_face_locations(face_locations, factor):
    face_locations = [(int(top * factor),
                       int(right * factor),
                       int(bottom * factor),
                       int(left * factor))
                      for top, right, bottom, left in face_locations]
    return face_locations


def scale_face_landmarks(face_landmarks, factor):
    face_landmarks_new = []
    for flms in face_landmarks:
        flms_new = dict()
        for area, lms in flms.items():
            lms = [(int(x * factor),
                    int(y * factor))
                   for x, y in lms]
            flms_new[area] = lms
        face_landmarks_new.append(flms_new)
    return face_landmarks_new


def scale_frame(frame, factor):
    height, width, _ = frame.shape
    new_h = int(height * factor)
    new_w = int(width * factor)
    frame = cv2.resize(frame, (new_w, new_h))
    return frame


def get_faces(frame, scaling_factor):
    # Resize frame of video for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=1/scaling_factor, fy=1/scaling_factor)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_landmarks = face_recognition.face_landmarks(rgb_small_frame)
    # Scale them back up
    face_locations = scale_face_locations(face_locations, scaling_factor)
    face_landmarks = scale_face_landmarks(face_landmarks, scaling_factor)

    return face_locations, face_landmarks


def draw_face_box(frame, face_location):
    # Display the results
    top, right, bottom, left = face_location
    # Draw a box around the face
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)


LEFT_EYE_EDGE = (378, 994)
RIGHT_EYE_EDGE = (674, 994)


def align_face(frame, face_location, face_landmarks):
    """Takes a frame, face_location and face_landmarks and centers the
    image and warps it.
    Returns a frame again, same size as input."""
    # TODO implement aligning
    assert isinstance(face_landmarks, dict)
    for area_name, landmarks in face_landmarks.items():
        for lm in landmarks:
            cv2.circle(frame, lm, 2, (0, 0, 255), 4)

    M = cv2.getAffineTransform(np.float32([face_landmarks['left_eye'][1],
                                           face_landmarks['right_eye'][1],
                                           face_landmarks['nose_bridge'][3]]),
                               np.float32([(404, 876), (644, 880), (532, 1036)]))
    h, w, _ = frame.shape
    frame = cv2.warpAffine(frame, M, (w, h))
    return frame


class Application:
    def __init__(self, camera_number):
        self.camera_number = camera_number
        self.scaling_factor = 4
        self.preview_window = "preview"
        self.genimage_window = "genimage"
        self.video_capture = None
        self.collected_frames = []

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

    def update_genimage(self, frame, face_locations, face_landmarks):
        for i in range(len(face_locations)):
            face_loc = face_locations[i]
            face_marks = face_landmarks[i]
            p_frame = align_face(frame, face_loc, face_marks)
            self.collected_frames.append(p_frame)

        if len(self.collected_frames) > 0:
            f = np.zeros(shape=self.collected_frames[0].shape,
                         dtype=np.float64)
            for pframe in self.collected_frames:
                transparent_image = (pframe / 255) * (1 / len(self.collected_frames))
                f = cv2.add(f, transparent_image)
            f = scale_frame(f, 1 / 2)
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
        face_locations = []
        face_landmarks = []
        process_this_frame = True

        rval = True
        while rval:
            # get a single frame
            rval, frame = self.video_capture.read()

            frame = cv2.transpose(frame)
            frame = cv2.flip(frame, flipCode=1)

            # get the faces
            if process_this_frame:
                face_locations, face_landmarks = get_faces(frame, self.scaling_factor)

            process_this_frame = not process_this_frame

            # exit on ESC
            key = cv2.waitKey(20)
            if key == 113:  # exit on q
                break
            if key == 112:  # take screenshot on p
                self.update_genimage(frame, face_locations, face_landmarks)

            self.update_preview(frame, face_locations)


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--camera_input",
        default=1,
        type=int,
        help="Which camera to use.")

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    a = Application(args.camera_input)
    init_successful = a.init()
    if not init_successful:
        print("Error in init.")
        return
    a.start()
    a.teardown()


if __name__ == "__main__":
    main()
