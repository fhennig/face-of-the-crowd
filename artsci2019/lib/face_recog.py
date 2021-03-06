import face_recognition
import cv2
from artsci2019.lib.util import scale_face_landmarkss, RecognizedFrame


def _face_landmarks_to_list(face_landmarks):
    """Takes a dict of the face landmarks and turns it into a single list
    of tuples."""
    res = []
    for area in ['chin', 'left_eyebrow', 'right_eyebrow', 'nose_bridge', 'nose_tip',
                 'left_eye', 'right_eye', 'top_lip', 'bottom_lip']:
        for lm in face_landmarks[area]:
            res.append(lm)
    return res


def get_faces(frame, scaling_factor):
    """Takes a frame, recognizes the faces and returns a list of
    RecognizedFrame, one for each face.  Can return an empty list."""
    # Resize frame of video for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=1/scaling_factor, fy=1/scaling_factor)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    # Find all the faces and face encodings in the current frame of video
    face_landmarkss = face_recognition.face_landmarks(rgb_small_frame)
    face_landmarkss = [_face_landmarks_to_list(flms) for flms in face_landmarkss]
    # Scale them back up
    face_landmarkss = scale_face_landmarkss(face_landmarkss, scaling_factor)

    r_frames = []

    for i in range(len(face_landmarkss)):
        r_frame = RecognizedFrame(frame,
                                  face_landmarkss[i])
        r_frames.append(r_frame)

    return r_frames



