import time
from pathlib import Path

import cv2

CAMERA_INDEX = 1
SAVE_DIR = Path(__file__).resolve().parent.parent / "recordings"
SAVE_DIR.mkdir(exist_ok=True)

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
if not cap.isOpened():
    raise SystemExit("Could not open webcam.")

prev_time = time.perf_counter()
fps = 0.0
saved_count = 0

while True:
    ok, frame = cap.read()
    if not ok:
        print("Failed to read frame")
        break

    frame = cv2.flip(frame, 1)   # mirror
    clean = frame.copy()         # untouched copy, for saving

    now = time.perf_counter()
    dt = now - prev_time
    prev_time = now
    if dt > 0:
        fps = 0.9 * fps + 0.1 * (1 / dt)

    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "s = save   q = quit", (10, frame.shape[0] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Webcam v2", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):
        path = SAVE_DIR / f"frame_{saved_count:04d}.png"
        if cv2.imwrite(str(path), clean):
            print("Saved", path)
            saved_count += 1
        else:
            print("Save failed:", path)

cap.release()
cv2.destroyAllWindows()