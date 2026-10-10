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