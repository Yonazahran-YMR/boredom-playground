@'



\# Sign Language Translator



A webcam app that reads hand signs and turns them into text. Part of my boredom-playground repo.



I'm building this in stages on purpose. Recognizing a static hand pose (a letter, a number) is a much easier problem than translating real sign language, and I don't want to pretend otherwise. The plan goes from webcam basics, to hand landmarks, to simple gestures, to A to Z, to text, and only then to actual sign language.



\## Status



Phase 2 done: live hand landmarks work. Nothing recognizes any sign yet.



\## Setup



Python 3.11 in a venv inside this folder. MediaPipe doesn't support the newest Python versions yet, so I'm avoiding 3.14.



&#x20;   C:\\Python311\\python.exe -m venv .venv

&#x20;   .\\.venv\\Scripts\\Activate.ps1

&#x20;   pip install -r requirements.txt



The hand model isn't in the repo. Download hand\_landmarker.task from

https://storage.googleapis.com/mediapipe-models/hand\_landmarker/hand\_landmarker/float16/latest/hand\_landmarker.task

and put it in a `models` folder.



My webcam is camera index 1, set in the scripts. The camera code uses the MSMF backend, because DirectShow capped my camera at 10 FPS.



\## What it can't do (yet)



Everything beyond drawing a hand skeleton. I'll keep this section honest as it grows.



\## Notes



Experiment notes and things that tripped me up live in `notes/`.

'@ | Set-Content README.md -Encoding utf8



\# Phase 1: Webcam



Got the camera working with OpenCV. A frame is just a NumPy array of shape (height, width, 3), and the colors are BGR, not RGB. I need to remember that for MediaPipe.



\## What clicked for me



The `with` block thing: `\_\_exit\_\_` always runs, so the camera gets released even if my code crashes. Before that, a crash could leave the camera locked.



\## Things that tripped me up



Moving the folder into the repo failed with an IOException because something was locking it. I ended up working in the inner folder and ignoring the empty leftover.



My venv came out as Python 3.14 because plain `python` picks the first one on PATH. Rebuilt it with the full path to 3.11.



My real webcam is index 1, not 0.



The camera ran at 10 FPS no matter what I did to lighting or format. I wrote a probe script that measures each backend. DirectShow gave 10 FPS, MSMF gave 30. So the fix was a single word in camera.py, and I only found it by measuring, not guessing.



\## Not done yet



Camera selection (the dropdown in my UI mockup) is postponed to Phase 9. Right now the index is hardcoded.

'@ | Set-Content notes\\phase1-webcam.md -Encoding utf8



@'



\# Phase 2: Hand detection



MediaPipe finds 21 points on a hand. First a palm detector finds the palm, then a second model predicts the joints inside that crop. On my laptop it takes about 14 ms per frame, so the camera was the bottleneck, not the model.



\## What clicked for me



x and y are fractions of the image, y goes down, and z is only a rough hint. The indices are fixed (4 is the thumb tip, 8 the index tip, 12 middle, 16 ring, 20 pinky), and Phase 3 will lean on that.



Normalizing means subtracting the wrist and dividing by hand size. That should make the same pose give the same numbers no matter where my hand is or how close it is. Raw pixels don't do that.



\## Things that tripped me up



The handedness label was swapped because my feed is mirrored. I fixed it by swapping the label in HandDetector.



Ran a script from the repo root instead of the project folder and got a file not found error.



\## Not solved yet



Normalizing removes position and size but not rotation. I want to see in Phase 3 whether tilting my hand breaks things.

'@ | Set-Content notes\\phase2-hands.md -Encoding utf8



