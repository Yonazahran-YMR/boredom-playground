from pathlib import Path

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

model_path = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

options = vision.HandLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
    num_hands=2,
)

with vision.HandLandmarker.create_from_options(options) as landmarker:
    print("MediaPipe", mp.__version__, "loaded the hand model OK")