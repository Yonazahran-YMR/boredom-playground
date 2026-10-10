@'
# Sign Language Translator

A webcam app that reads hand signs and turns them into text. Part of my boredom-playground repo.

I'm building this in stages on purpose. Recognizing a static hand pose (a letter, a number) is a much easier problem than translating real sign language, and I don't want to pretend otherwise. The plan goes from webcam basics, to hand landmarks, to simple gestures, to A to Z, to text, and only then to actual sign language.

## Status

Phase 2 done: live hand landmarks work. Nothing recognizes any sign yet.

## Setup

Python 3.11 in a venv inside this folder. MediaPipe doesn't support the newest Python versions yet, so I'm avoiding 3.14.

    C:\Python311\python.exe -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

The hand model isn't in the repo. Download hand_landmarker.task from
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
and put it in a `models` folder.

My webcam is camera index 1, set in the scripts. The camera code uses the MSMF backend, because DirectShow capped my camera at 10 FPS.

## What it can't do (yet)

Everything beyond drawing a hand skeleton. I'll keep this section honest as it grows.

## Notes

Experiment notes and things that tripped me up live in `notes/`.
'@ | Set-Content README.md -Encoding utf8
