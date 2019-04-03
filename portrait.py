import numpy as np
import cv2


def generate_edge_points(f_width, f_height):
    f_height -= 1
    f_width -= 1
    return [(0, 0),
            (0, int(f_height/2)),
            (0, f_height),
            (int(f_width/2), 0),
            (int(f_width/2), f_height),
            (f_width, 0),
            (f_width, int(f_height/2)),
            (f_width, f_height)]


def draw_triangle(frame, triangle):
    pt1 = (triangle[0], triangle[1])
    pt2 = (triangle[2], triangle[3])
    pt3 = (triangle[4], triangle[5])
    cv2.line(frame, pt1, pt2, (0, 255, 0), 4, 8, 0)
    cv2.line(frame, pt2, pt3, (0, 255, 0), 4, 8, 0)
    cv2.line(frame, pt3, pt1, (0, 255, 0), 4, 8, 0)


def align_face(frame, face_landmarks, lm_targets):
    """Takes a frame and face_landmarks and centers the image and warps
    it.  Returns a frame again, same size as input.
    """
    assert isinstance(face_landmarks, list)
    for landmark in face_landmarks:
        cv2.circle(frame, landmark, 2, (0, 0, 255), 4)

    # prep delaunay
    f_h, f_w, _ = frame.shape
    rect = (0, 0, f_w, f_h)
    edge_points = generate_edge_points(f_w, f_h)
    subdiv = cv2.Subdiv2D(rect)
    for lm in face_landmarks:
        subdiv.insert(lm)
    for p in edge_points:
        subdiv.insert(p)
    # triangles
    triangle_list = subdiv.getTriangleList()
    for t in triangle_list:
        draw_triangle(frame, t)
    # TODO for each triangle, get the affine transformation and transform it
    # then stitch the transformed triangles together
    M = cv2.getAffineTransform(np.float32([face_landmarks[37],
                                           face_landmarks[43],
                                           face_landmarks[30]]),
                               np.float32([(404, 876), (644, 880), (532, 1036)]))
    h, w, _ = frame.shape
    frame = cv2.warpAffine(frame, M, (w, h))
    return frame


class PortraitGen:

    def __init__(self):
        self.recognized_frames = []
        self.target_landmarks = None
        self.portrait_frame = None

    def _update_frame(self):
        """Updates the portrait_frame, the generated image."""
        assert len(self.recognized_frames) > 0
        collected_frames = []
        for r_frame in self.recognized_frames:
            p_frame = align_face(r_frame.frame, r_frame.face_landmarks, self.target_landmarks)
            collected_frames.append(p_frame)

        f = np.zeros(shape=collected_frames[0].shape,
                     dtype=np.float64)
        for pframe in collected_frames:
            transparent_image = (pframe / 255) * (1 / len(collected_frames))
            f = cv2.add(f, transparent_image)
        self.portrait_frame = f

    def _update_target_landmarks(self):
        """Updates the target location of the generated face by calculating
        the average position from the saved faces."""
        a = np.array([rf.face_landmarks for rf in self.recognized_frames])
        mean = a.mean(axis=0)
        mean = mean.astype(int)
        print(mean)
        self.target_landmarks = mean  # TODO continue implementing and test

    def update(self, recognized_frames):
        """Updates the generated image, the merge of all the faces."""
        if len(recognized_frames) == 0:
            return False
        self.recognized_frames += recognized_frames
        self._update_target_landmarks()
        self._update_frame()
        return True
