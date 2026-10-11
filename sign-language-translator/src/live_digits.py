from pathlib import Path

import cv2
import joblib
import numpy as np

from camera import Webcam
from features import normalize
from hands import HandDetector, draw_hand

CAMERA_INDEX = 1
MIN_CONF = 0.6
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "digits_rf.joblib"

bundle = joblib.load(MODEL_PATH)
model, names = bundle["model"], bundle["names"]

with HandDetector() as detector, Webcam(CAMERA_INDEX) as cam:
    while True:
        frame = cam.read()
        if frame is None:
            break
        h, w = frame.shape[:2]

        found = detector.detect(frame)
        if found:
            landmarks, hand, score = found
            draw_hand(frame, landmarks)
            norm, _ = normalize(landmarks, w, h)
            probs = model.predict_proba(norm.flatten().reshape(1, -1))[0]
            best = int(np.argmax(probs))
            conf = probs[best]
            shown = names[best] if conf >= MIN_CONF else "?"

            cv2.putText(frame, f"{shown}  {conf:.0%}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0) if shown != "?" else (0, 165, 255), 4)
            cv2.putText(frame, f"{hand} hand", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            for i, (n, p) in enumerate(zip(names, probs)):
                cv2.putText(frame, f"{n}: {p:.2f}", (10, 125 + i * 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "No hand", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        cv2.putText(frame, "q = quit", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Live digits", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break