import time

import cv2

INDEX = 1  # change to 0 to test the other camera


def measure(backend, name, mjpg):
    cap = cv2.VideoCapture(INDEX, backend)
    label = "MJPG" if mjpg else "default"
    if not cap.isOpened():
        print(f"{name:6} {label:8} could not open")
        return
    if mjpg:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    for _ in range(5):  # warm up, first frames are slow
        cap.read()
    count = 0
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 3:
        ok, _ = cap.read()
        if ok:
            count += 1
    measured = count / (time.perf_counter() - t0)
    print(f"{name:6} {label:8} driver says {cap.get(cv2.CAP_PROP_FPS):.0f} fps, measured {measured:.1f} fps")
    cap.release()


for backend, name in [(cv2.CAP_DSHOW, "DSHOW"), (cv2.CAP_MSMF, "MSMF")]:
    for mjpg in (False, True):
        measure(backend, name, mjpg)