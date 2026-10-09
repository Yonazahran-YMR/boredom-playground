import cv2

class Webcam:
    def __init__(self, index=0, mirror=True):
        self.index = index
        self.mirror = mirror
        self.cap = None

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_MSMF)
        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(f"Could not open camera {self.index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return self

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return cv2.flip(frame, 1) if self.mirror else frame

    def __exit__(self, exc_type, exc, tb):
        self.cap.release()
        cv2.destroyAllWindows()