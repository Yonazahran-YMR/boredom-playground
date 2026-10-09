import cv2

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # 0 = first camera
if not cap.isOpened():
    raise SystemExit("Could not open webcam. Try index 1, or close other apps using the camera.")

first_frame = True
while True:
    ok, frame = cap.read()  # ok is False if the camera failed to deliver a frame
    if not ok:
        print("Failed to read frame")
        break

    if first_frame:
        print("Frame shape (height, width, channels):", frame.shape)
        first_frame = False

    cv2.imshow("Webcam (press q to quit)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()           # give the camera back to Windows
cv2.destroyAllWindows()