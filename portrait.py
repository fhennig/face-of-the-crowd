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
    pt1 = tuple(triangle[0])
    pt2 = tuple(triangle[1])
    pt3 = tuple(triangle[2])
    cv2.line(frame, pt1, pt2, (0, 255, 0), 4, 8, 0)
    cv2.line(frame, pt2, pt3, (0, 255, 0), 4, 8, 0)
    cv2.line(frame, pt3, pt1, (0, 255, 0), 4, 8, 0)


def _enlargen_triangle(triangle, delta):
    p_new = []
    for i in range(len(triangle)):
        vx, vy = triangle[i]
        rest = np.vstack((triangle[:i], triangle[i:]))
        rest_x = [v[0] for v in rest]
        rest_y = [v[1] for v in rest]
        # no x that is bigger
        if not [x for x in rest_x
                if x > vx]:
            vx += delta
        if not [x for x in rest_x
                if x < vx]:
            vx -= delta
        if not [y for y in rest_y
                if y > vy]:
            vy += delta
        if not [y for y in rest_y
                if y < vy]:
            vy -= delta
        p_new.append((vx, vy))
    return np.array(p_new)


def _mask_triangle_only(frame, triangle):
    # taken from: https://stackoverflow.com/questions/15341538/
    mask = np.zeros(frame.shape, dtype=np.uint8)
    # fill the triangle so it doesn't get wiped out when the mask is applied
    channel_count = frame.shape[2]  # i.e. 3 or 4 depending on image
    ignore_mask_color = (255,)*channel_count
    triangle = _enlargen_triangle(triangle, -1)
    cv2.fillConvexPoly(mask, triangle, ignore_mask_color)
    # apply the mask
    masked_image = cv2.bitwise_and(frame, mask)
    return masked_image


def align_face(frame, face_landmarks, lm_targets):
    """Takes a frame and face_landmarks and centers the image and warps
    it.  Returns a frame again, same size as input.
    """
    assert isinstance(face_landmarks, list)
#    for landmark in face_landmarks:
#        cv2.circle(frame, landmark, 2, (0, 0, 255), 4)

    # mapping a point to its target point
    point_map = dict(zip(face_landmarks, lm_targets))

    # prep delaunay
    f_h, f_w, _ = frame.shape
    rect = (0, 0, f_w, f_h)
    edge_points = generate_edge_points(f_w, f_h)
    for ep in edge_points:
        point_map[ep] = ep
    subdiv = cv2.Subdiv2D(rect)
    for lm in face_landmarks:
        subdiv.insert(lm)
    for p in edge_points:
        subdiv.insert(p)
    # triangles
    triangle_list = subdiv.getTriangleList()
    triangle_list = [np.reshape(triangle, (3, 2))
                     for triangle in triangle_list]
#    for t in triangle_list:
#        draw_triangle(frame, t)

    new_frame = np.zeros(frame.shape, dtype=frame.dtype)

    for triangle in triangle_list:
        target = np.array([point_map[tuple(p.astype(np.int32))] for p in triangle]).astype(np.int32)
        M = cv2.getAffineTransform(triangle, target.astype(np.float32))
        f = cv2.warpAffine(frame, M, (f_w, f_h))
        mask = np.zeros((f_h, f_w), dtype=np.uint8)
        cv2.fillConvexPoly(mask, target, 255)
        cv2.fillConvexPoly(new_frame, target, 0)
        cv2.add(new_frame, f, dst=new_frame, mask=mask)
        #f = _mask_triangle_only(f, target.astype(np.int32))
        #new_frame = cv2.addWeighted(new_frame, f)

    return new_frame


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
        self.target_landmarks = mean  # TODO continue implementing and test

    def update(self, recognized_frames):
        """Updates the generated image, the merge of all the faces."""
        if len(recognized_frames) == 0:
            return False
        self.recognized_frames += recognized_frames
        self._update_target_landmarks()
        self._update_frame()
        return True
