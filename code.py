#! /usr/bin/env python3
import face_recognition
import cv2
import argparse




def get_faces(frame, scaling_factor):
    # Resize frame of video for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=1/scaling_factor, fy=1/scaling_factor)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_landmarks = face_recognition.face_landmarks(rgb_small_frame)
    return face_locations, face_landmarks


def draw_face_box(frame, face_location, scaling_factor):
    # Display the results
    top, right, bottom, left = face_location
    # Scale back up face locations since the frame we detected in was scaled down
    top *= scaling_factor
    right *= scaling_factor
    bottom *= scaling_factor
    left *= scaling_factor

    # change framesize to portrait crop
    left -= 80
    right += 80
    top -= 200
    bottom += 100

    # Draw a box around the face
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)


def align_face(frame, face_location, face_landmarks):
    """Takes a frame, face_location and face_landmarks and centers the
    image and warps it.
    Returns a frame again, same size as input."""
    # TODO implement aligning
    return frame


class Application:
    def __init__(self, camera_number):
        self.camera_number = camera_number
        self.scaling_factor = 4
        self.preview_window = "preview"
        self.genimage_window = "genimage"
        self.video_capture = None

    def init(self):
        # initialize window
        cv2.namedWindow(self.preview_window)
        cv2.namedWindow(self.genimage_window)

        # get webcam
        self.video_capture = cv2.VideoCapture(self.camera_number)
        self.video_capture.set(3, 1280)
        self.video_capture.set(4, 720)
        
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

    def start(self):
        face_locations = []
        face_landmarks = []
        process_this_frame = True

        rval = True
        while rval:
            # get a single frame
            rval, frame = self.video_capture.read()

            if process_this_frame:
                face_locations, face_landmarks = get_faces(frame, self.scaling_factor)

            process_this_frame = not process_this_frame

            for face_location in face_locations:
                draw_face_box(frame, face_location, self.scaling_factor)

            # Display the resulting image
            cv2.imshow(self.preview_window, frame)

            # exit on ESC
            key = cv2.waitKey(20)
            if key == 113:  # exit on q
                break
            if key == 102:
                print(face_landmarks)
                x = face_landmarks[0]['chin'][8]
                x = (x[0] * self.scaling_factor, x[1] * self.scaling_factor)
                cv2.circle(frame, x, 2, (0, 255,0), 2)
            if key == 112:  # take screenshot on p
                cv2.imshow(self.genimage_window, frame)


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
