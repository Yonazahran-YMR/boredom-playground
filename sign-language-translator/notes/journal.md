# Development journal

Notes on building this as I go: what worked, what broke, and what I learned.

## Phase 0: Setup

Project lives on D: because my C: drive is almost full, and pip's cache is moved to D: too. Moving the folder into the repo failed with an IOException (something was locking it), so I ended up working in the inner folder and ignoring the empty leftover.

My first venv came out as Python 3.14 because plain `python` picks the first one on PATH. MediaPipe doesn't support that yet, so I rebuilt it using the full path to 3.11.

## Phase 1: Webcam

A frame is just a NumPy array of shape (height, width, 3), and OpenCV stores colors as BGR, not RGB. I need to remember that for MediaPipe.

The `with` block thing clicked for me: `__exit__` always runs, so the camera gets released even if my code crashes.

My real webcam is index 1, not 0. It also ran at 10 FPS no matter what I tried with lighting or format. I wrote a probe script that measures each backend: DirectShow gave 10 FPS, MSMF gave 30. The fix was one word in camera.py, and I only found it by measuring, not guessing.

## Phase 2: Hand detection

MediaPipe finds 21 points on a hand. A palm detector finds the palm first, then a second model predicts the joints inside that crop. It takes about 14 ms per frame on my laptop, so the camera was the bottleneck, not the model.

x and y are fractions of the image, y goes down, and z is only a rough hint. The indices are fixed (4 is the thumb tip, 8 the index tip, 12 middle, 16 ring, 20 pinky), and Phase 3 will lean on that.

Normalizing means subtracting the wrist and dividing by hand size. That's supposed to make the same pose give the same numbers wherever my hand is and however close it is. Raw pixels don't.

Things that tripped me up: the handedness label was swapped because my feed is mirrored (fixed by swapping the label in HandDetector), and I ran a script from the repo root instead of the project folder.

Not solved yet: normalizing doesn't remove rotation. I want to see in Phase 3 whether tilting my hand breaks things.
