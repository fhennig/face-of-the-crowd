import cv2


def scale_point(point, factor):
    x, y = point
    return (int(x * factor),
            int(y * factor))


def scale_face_landmarkss(face_landmarkss, factor):
    return [[(int(x * factor),
              int(y * factor))
             for x, y in flms]
            for flms in face_landmarkss]


def crop_face_landmarks(face_landmarks, x_offset, y_offset):
    return [(x - x_offset,
             y - y_offset)
            for x, y in face_landmarks]


def scale_frame(frame, factor):
    height, width, _ = frame.shape
    new_h = int(height * factor)
    new_w = int(width * factor)
    frame = cv2.resize(frame, (new_w, new_h))
    return frame


def is_in_frame(frame_w, frame_h, lm):
    """Returns whether a given landmarks is within the frame boundaries or not."""
    return lm[0] < frame_w and lm[1] < frame_h and lm[0] >= 0 and lm[1] >= 0


class RecognizedFrame:
    def __init__(self, frame, face_landmarks):
        self.frame = frame
        self.face_landmarks = face_landmarks
        self.left_eye = self.face_landmarks[36]
        self.right_eye = self.face_landmarks[45]

    def cropped(self, new_width, new_height, x_offset, y_offset):
        return RecognizedFrame(
            self.frame[y_offset:y_offset + new_height, x_offset:x_offset + new_width],
            crop_face_landmarks(self.face_landmarks, x_offset, y_offset)
        )

    def __repr__(self):
        return str([self.frame,
                    self.face_landmarks,
                    self.left_eye,
                    self.right_eye])
