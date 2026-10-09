import time
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from camera import Webcam

CAMERA_INDEX = 1
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),         # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),         # index
    (5, 9), (9, 10), (10, 11), (11, 12),    # middle
    (9, 13), (13, 14), (14, 15), (15, 16),  # ring
    (13, 17), (17, 18), (18, 19), (19, 20), # pinky
    (0, 17),                                # palm edge
]

options = vision.HandLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH)),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
)

show_numbers = False
start = time.perf_counter()
prev = start
fps = 0.0

with vision.HandLandmarker.create_from_options(options) as landmarker, \
        Webcam(CAMERA_INDEX) as cam:
    while True:
        frame = cam.read()
        if frame is None:
            print("Failed to read frame")
            break
        h, w = frame.shape[:2]

        # BGR (OpenCV) -> RGB (MediaPipe), then wrap in MediaPipe's image type
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.perf_counter() - start) * 1000)
        t0 = time.perf_counter()
        result = landmarker.detect_for_video(mp_image, timestamp_ms)
        detect_ms = (time.perf_counter() - t0) * 1000

        if result.hand_landmarks:
            lms = result.hand_landmarks[0]  # 21 landmarks of the first hand
            # normalized (0..1) -> pixel coordinates
            points = [(int(lm.x * w), int(lm.y * h)) for lm in lms]

            for a, b in HAND_CONNECTIONS:
                cv2.line(frame, points[a], points[b], (255, 255, 255), 2)
            for i, p in enumerate(points):
                cv2.circle(frame, p, 4, (0, 255, 0), -1)
                if show_numbers:
                    cv2.putText(frame, str(i), (p[0] + 5, p[1] - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            hand = result.handedness[0][0]
            label = "Right" if hand.category_name == "Left" else "Left"  # swapped: we feed a mirrored image
            tip = lms[8]  # index fingertip
            cv2.putText(frame, f"{label} hand ({hand.score:.2f})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"index tip x={tip.x:.2f} y={tip.y:.2f} z={tip.z:.2f}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No hand", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        now = time.perf_counter()
        fps = 0.9 * fps + 0.1 * (1 / max(now - prev, 1e-6))
        prev = now
        cv2.putText(frame, f"FPS: {fps:.0f}  detect: {detect_ms:.0f} ms   n = numbers   q = quit",
                (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Hand detection", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("n"):
            show_numbers = not show_numbers