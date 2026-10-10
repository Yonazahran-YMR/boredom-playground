import math

import cv2
import numpy as np

from camera import Webcam
from hands import HandDetector, draw_hand

CAMERA_INDEX = 1
np.set_printoptions(precision=2, suppress=True)


def normalize(landmarks, w, h):
    """Return (21x2 array relative to wrist and scaled by hand size, hand size in px)."""
    pts = np.array([(x * w, y * h) for x, y, _ in landmarks])  # pixels
    pts = pts - pts[0]                      # wrist becomes (0, 0)
    size = np.linalg.norm(pts[9])           # wrist to middle finger base
    return pts / size, size


def put(frame, text, y):
    cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


with HandDetector() as detector, Webcam(CAMERA_INDEX) as cam:
    while True:
        frame = cam.read()
        if frame is None:
            break
        h, w = frame.shape[:2]

        norm = None
        found = detector.detect(frame)
        if found:
            landmarks, label, score = found
            draw_hand(frame, landmarks)
            norm, size = normalize(landmarks, w, h)

            # pinch = distance between thumb tip (4) and index tip (8)
            raw_pinch = math.dist((landmarks[4][0] * w, landmarks[4][1] * h),
                                  (landmarks[8][0] * w, landmarks[8][1] * h))
            norm_pinch = np.linalg.norm(norm[4] - norm[8])

            put(frame, f"{label} hand", 30)
            put(frame, f"hand size:    {size:6.1f} px", 60)
            put(frame, f"pinch raw:    {raw_pinch:6.1f} px", 90)
            put(frame, f"pinch normed: {norm_pinch:6.2f}", 120)
        else:
            put(frame, "No hand", 30)

        cv2.putText(frame, "p = print normalized   q = quit", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Landmark data", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("p") and norm is not None:
            print(norm)
            print()