import numpy as np

# finger name: (tip landmark, middle joint landmark)
FINGERS = {
    "index": (8, 6),
    "middle": (12, 10),
    "ring": (16, 14),
    "pinky": (20, 18),
}


def normalize(landmarks, w, h):
    """21x2 array relative to the wrist, scaled by hand size, plus hand size in px."""
    pts = np.array([(x * w, y * h) for x, y, _ in landmarks])
    pts = pts - pts[0]
    size = np.linalg.norm(pts[9])
    return pts / size, size


def fingers_up(norm):
    """Return {finger name: True/False} using normalized landmarks."""
    up = {}
    # thumb: tip farther from the pinky base than the joint below it
    up["thumb"] = bool(np.linalg.norm(norm[4] - norm[17]) > np.linalg.norm(norm[3] - norm[17]))
    # other fingers: wrist is (0, 0), so norm[i] length = distance from the wrist
    for name, (tip, mid) in FINGERS.items():
        up[name] = bool(np.linalg.norm(norm[tip]) > np.linalg.norm(norm[mid]))
    return up

UP_T = 1.2
DOWN_T = 1.0
FINGER_NAMES = ["thumb", "index", "middle", "ring", "pinky"]


def finger_ratios(norm):
    """How extended each finger is: bigger = straighter."""
    r = {"thumb": np.linalg.norm(norm[4] - norm[17]) / np.linalg.norm(norm[3] - norm[17])}
    for name, (tip, mid) in FINGERS.items():
        r[name] = np.linalg.norm(norm[tip]) / np.linalg.norm(norm[mid])
    return r


class FingerTracker:
    """Remembers each finger's state so it only flips after a clear change."""

    def __init__(self, up_t=UP_T, down_t=DOWN_T):
        self.up_t = up_t
        self.down_t = down_t
        self.state = {name: False for name in FINGER_NAMES}

    def update(self, ratios):
        for name, r in ratios.items():
            if r > self.up_t:
                self.state[name] = True
            elif r < self.down_t:
                self.state[name] = False
        return dict(self.state)

    def reset(self):
        self.state = {name: False for name in FINGER_NAMES}