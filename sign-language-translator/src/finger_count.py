import cv2

from camera import Webcam
from features import fingers_up, normalize
from hands import HandDetector, draw_hand

CAMERA_INDEX = 1

with HandDetector() as detector, Webcam(CAMERA_INDEX) as cam:
    while True:
        frame = cam.read()
        if frame is None:
            break
        h, w = frame.shape[:2]

        found = detector.detect(frame)
        if found:
            landmarks, label, score = found
            draw_hand(frame, landmarks)
            norm, size = normalize(landmarks, w, h)
            up = fingers_up(norm)

            cv2.putText(frame, f"Fingers: {sum(up.values())}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            for i, (name, is_up) in enumerate(up.items()):
                color = (0, 255, 0) if is_up else (0, 0, 255)
                cv2.putText(frame, f"{name}: {'UP' if is_up else 'down'}", (10, 85 + i * 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        else:
            cv2.putText(frame, "No hand", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        cv2.putText(frame, "q = quit", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Finger counter", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break