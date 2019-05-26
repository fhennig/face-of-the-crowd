import numpy as np
import cv2
import logging
from multiprocessing import Pool
from artsci2019.lib.util import is_in_frame


logger = logging.getLogger(__name__)


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


def get_delaunay_mapping(face_landmarks, targets, frame_w, frame_h, stable_points=[]):
    """Takes a list of face landmarks and a corresponding list of targets.
    Returns a list of tuples of triangles [(src_triangle, target_triangle)].
    The frame width and heigth are used for edge points.
    Optionally a list of stable points can be given."""
    assert isinstance(face_landmarks, list)
    assert isinstance(targets, list)
    logger.debug("delaunay mapping: frame: {} {}".format(frame_w, frame_h))
    logger.debug("delaunay mapping: face_landmarks: {}".format(face_landmarks))
    logger.debug("delaunay mapping: targets: {}".format(targets))

    point_map = dict(zip(face_landmarks, targets))

    logger.debug("LALAL")

    # prep delaunay
    rect = (0, 0, frame_w, frame_h)
    edge_points = generate_edge_points(frame_w, frame_h)
    edge_points += stable_points
    for ep in edge_points:
        logger.debug("ep: {}".format(ep))
        point_map[ep] = ep
    subdiv = cv2.Subdiv2D(rect)
    for lm in face_landmarks:
        if is_in_frame(frame_w, frame_h, lm):
            subdiv.insert(lm)
    for p in edge_points:
        subdiv.insert(p)

    logger.debug(("delaunay mapping: CHECKPOINT"))

    triangle_mapping = []
    for triangle in subdiv.getTriangleList():
        triangle = np.reshape(triangle, (3, 2)).astype(np.int32)
        target = np.array([point_map[tuple(p)] for p in triangle], dtype=np.int32)
        triangle_mapping.append((triangle, target))

    return triangle_mapping


def align_face(frame, face_landmarks, lm_targets, stable_points):
    """Takes a frame and face_landmarks and centers the image and warps
    it.  Returns a frame again, same size as input.
    """
    logger.debug("Aligning face ...")
    f_h, f_w, _ = frame.shape
    triangle_mapping = get_delaunay_mapping(face_landmarks, lm_targets, f_w, f_h, stable_points)
    logger.debug(("Triangle mapping generated. "))

    new_frame = np.zeros(frame.shape, dtype=frame.dtype)

    for orig, target in triangle_mapping:
        M = cv2.getAffineTransform(orig.astype(np.float32),
                                   target.astype(np.float32))  # args need to be np.float32
        f = cv2.warpAffine(frame, M, (f_w, f_h))
        mask = np.zeros((f_h, f_w), dtype=np.uint8)
        cv2.fillConvexPoly(mask, target, 255)  # target needs to have dtype=np.int32
        cv2.fillConvexPoly(new_frame, target, 0)
        cv2.add(new_frame, f, dst=new_frame, mask=mask)

    logger.debug("Aligning face done.")
    return new_frame


def _align_face(args):
    """Helper function for parallelization"""
    logger.info("Aligning face {}".format(args[4]))
    return align_face(args[0], args[1], args[2], args[3])


def get_target_landmarks(recognized_frames):
    a = np.array([rf.face_landmarks for rf in recognized_frames])
    mean = a.mean(axis=0)
    mean = mean.astype(np.int32)
    mean = [tuple(p) for p in mean]
    return mean


def gen_portrait(recognized_frames, pool_size, stable_points):
    """Generates a merged portrait with the given images.
    pool_size is the amount of threads to use while processing."""
    logger.info("gen portrait: given frames count: {}".format(len(recognized_frames)))
    logger.debug("recognized_frames: {}".format(recognized_frames))
    assert len(recognized_frames) > 0
    target_landmarks = get_target_landmarks(recognized_frames)
    logger.debug("target_landmarks: {}".format(target_landmarks))
    # align the images to the target landmarks
    with Pool(pool_size) as p:
        l = []
        for i, rf in enumerate(recognized_frames):
            l.append((rf.frame, rf.face_landmarks, target_landmarks, stable_points, i))
        logger.debug("l: {}".format(l))
        collected_frames = p.map(_align_face, l)
    # overlay the aligned images
    f = np.zeros(shape=collected_frames[0].shape,
                 dtype=np.uint8)
    for pframe in collected_frames:
        cv2.addWeighted(f, 1, pframe, (1 / len(collected_frames)), 0, f)
    return f


class PortraitGen:

    def __init__(self, stack_size, pool_size, stable_points):
        self.stack_size = stack_size
        self.pool_size = pool_size
        self.stable_points = stable_points
        self.recognized_frames = []
        self.target_landmarks = None
        self.portrait_frame = None

    def update(self, recognized_frames):
        """Updates the generated image, the merge of all the faces."""
        if not recognized_frames:
            return False
        self.recognized_frames += recognized_frames
        self.recognized_frames = self.recognized_frames[- self.stack_size:]
        self.portrait_frame = gen_portrait(self.recognized_frames, self.pool_size, self.stable_points)
        return True

    def get_portrait(self):
        return self.portrait_frame
