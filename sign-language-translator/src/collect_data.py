import csv
from datetime import datetime
from pathlib import Path

import cv2

from camera import Webcam
from features import normalize
from hands import HandDetector, draw_hand

CAMERA_INDEX = 1
LABELS = ["0", "1", "2", "3", "4", "5"]  # press the same key to select a label
SAVE_EVERY = 3                            # while recording, save 1 of every 3 frames
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "landmarks.csv"
CSV_PATH.parent.mkdir(exist_ok=True)

session = datetime.now().strftime("%Y%m%d_%H%M%S")
header = ["label", "session", "hand"] + [f"{axis}{i}" for i in range(21) for axis in "xy"]

# count what's already in the file, so the on-screen totals are right
counts = {label: 0 for label in LABELS}
new_file = not CSV_PATH.exists()
if not new_file:
    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            if row["label"] in counts:
                counts[row["label"]] += 1

with open(CSV_PATH, "a", newline="") as f, \
        HandDetector() as detector, Webcam(CAMERA_INDEX) as cam:
    writer = csv.writer(f)
    if new_file:
        writer.writerow(header)

    current = LABELS[0]
    recording = False
    frame_n = 0

    while True:
        frame = cam.read()
        if frame is None:
            break
        h, w = frame.shape[:2]

        found = detector.detect(frame)
        if found:
            landmarks, hand, score = found
            draw_hand(frame, landmarks)
            if recording:
                frame_n += 1
                if frame_n % SAVE_EVERY == 0:
                    norm, _ = normalize(landmarks, w, h)
                    writer.writerow([current, session, hand] + [f"{v:.5f}" for v in norm.flatten()])
                    f.flush()  # so a crash doesn't lose data
                    counts[current] += 1

        color = (0, 0, 255) if recording else (200, 200, 200)
        status = "RECORDING" if recording else "paused"
        if recording and not found:
            status += " (no hand, not saving)"
        cv2.putText(frame, f"label: {current}   {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, "  ".join(f"{k}:{v}" for k, v in counts.items()), (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"keys {LABELS[0]}-{LABELS[-1]} = label   space = record/pause   q = quit",
                    (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Collect data", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord(" "):
            recording = not recording
        elif key != 255 and chr(key) in LABELS:
            current = chr(key)
            recording = False  # switching label always pauses, so poses don't get mislabeled