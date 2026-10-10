import time
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


class HandDetector:
    def __init__(self, num_hands=1):
        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.start = time.perf_counter()

    def detect(self, frame):
        """Return (landmarks, label, score) for the first hand, or None.
        landmarks is a list of 21 (x, y, z) tuples, x and y in 0..1."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.perf_counter() - self.start) * 1000)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.hand_landmarks:
            return None
        landmarks = [(lm.x, lm.y, lm.z) for lm in result.hand_landmarks[0]]
        category = result.handedness[0][0]
        # swapped because we feed a mirrored image
        label = "Right" if category.category_name == "Left" else "Left"
        return landmarks, label, category.score

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.landmarker.close()


def draw_hand(frame, landmarks, numbers=False):
    h, w = frame.shape[:2]
    points = [(int(x * w), int(y * h)) for x, y, _ in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, points[a], points[b], (255, 255, 255), 2)
    for i, p in enumerate(points):
        cv2.circle(frame, p, 4, (0, 255, 0), -1)
        if numbers:
            cv2.putText(frame, str(i), (p[0] + 5, p[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)