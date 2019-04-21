import numpy as np
import cv2
from multiprocessing import Pool


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
    pt1 = tuple(triangle[0])
    pt2 = tuple(triangle[1])
    pt3 = tuple(triangle[2])
    cv2.line(frame, pt1, pt2, (0, 255, 0), 4, 8, 0)
    cv2.line(frame, pt2, pt3, (0, 255, 0), 4, 8, 0)
    cv2.line(frame, pt3, pt1, (0, 255, 0), 4, 8, 0)


def get_delaunay_mapping(face_landmarks, targets, frame_w, frame_h):
    """Takes a list of face landmarks and a corresponding list of targets.
    Returns a list of tuples of triangles [(src_triangle, target_triangle)].
    The frame width and heigth are used for edge points."""
    assert isinstance(face_landmarks, list)
    assert isinstance(targets, list)

    point_map = dict(zip(face_landmarks, targets))

    # prep delaunay
    rect = (0, 0, frame_w, frame_h)
    edge_points = generate_edge_points(frame_w, frame_h)
    for ep in edge_points:
        point_map[ep] = ep
    subdiv = cv2.Subdiv2D(rect)
    print("rectangle: {}".format(rect))
    for lm in face_landmarks:
        print("Landmark: {}".format(lm))
        subdiv.insert(lm)
    for p in edge_points:
        subdiv.insert(p)

    triangle_mapping = []
    for triangle in subdiv.getTriangleList():
        triangle = np.reshape(triangle, (3, 2)).astype(np.int32)
        target = np.array([point_map[tuple(p)] for p in triangle], dtype=np.int32)
        triangle_mapping.append((triangle, target))

    return triangle_mapping


def align_face(frame, face_landmarks, lm_targets):
    """Takes a frame and face_landmarks and centers the image and warps
    it.  Returns a frame again, same size as input.
    """
    f_h, f_w, _ = frame.shape
    triangle_mapping = get_delaunay_mapping(face_landmarks, lm_targets, f_w, f_h)

    new_frame = np.zeros(frame.shape, dtype=frame.dtype)

    for orig, target in triangle_mapping:
        M = cv2.getAffineTransform(orig.astype(np.float32),
                                   target.astype(np.float32))  # args need to be np.float32
        f = cv2.warpAffine(frame, M, (f_w, f_h))
        mask = np.zeros((f_h, f_w), dtype=np.uint8)
        cv2.fillConvexPoly(mask, target, 255)  # target needs to have dtype=np.int32
        cv2.fillConvexPoly(new_frame, target, 0)
        cv2.add(new_frame, f, dst=new_frame, mask=mask)

    return new_frame


def _align_face(args):
    """Helper function for parallelization"""
    return align_face(*args)


class PortraitGen:

    def __init__(self, stack_size, pool_size):
        self.stack_size = stack_size
        self.pool_size = pool_size
        self.recognized_frames = []
        self.target_landmarks = None
        self.portrait_frame = None

    def _update_frame(self):
        """Updates the portrait_frame, the generated image."""
        assert len(self.recognized_frames) > 0
        # align the images to the target landmarks
        with Pool(self.pool_size) as p:
            l = [(r_f.frame, r_f.face_landmarks, self.target_landmarks) for r_f in self.recognized_frames]
            collected_frames = p.map(_align_face, l)
        # overlay the aligned images
        f = np.zeros(shape=collected_frames[0].shape,
                     dtype=np.uint8)
        for pframe in collected_frames:
            cv2.addWeighted(f, 1, pframe, (1 / len(collected_frames)), 0, f)
        self.portrait_frame = f

    def _update_target_landmarks(self):
        """Updates the target location of the generated face by calculating
        the average position from the saved faces."""
        a = np.array([rf.face_landmarks for rf in self.recognized_frames])
        mean = a.mean(axis=0)
        mean = mean.astype(np.int32)
        mean = [tuple(p) for p in mean]
        self.target_landmarks = mean

    def update(self, recognized_frames):
        """Updates the generated image, the merge of all the faces."""
        if not recognized_frames:
            return False
        self.recognized_frames += recognized_frames
        self.recognized_frames = self.recognized_frames[- self.stack_size:]
        self._update_target_landmarks()
        self._update_frame()
        return True

    def get_portrait(self):
        return self.portrait_frame
