"""
Application-wide configuration and paths.
"""
import os

# ── Root dir (project root, not this file's dir) ─────────────────────────────
ROOT_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
MODELS_DIR = os.path.join(ASSETS_DIR, "models")

# ── Pose landmarker model ──────────────────────────────────────────────────────
MODEL_FILENAME = "pose_landmarker_lite.task"
MODEL_PATH     = os.path.join(MODELS_DIR, MODEL_FILENAME)
MODEL_URL      = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)

# ── Camera ────────────────────────────────────────────────────────────────────
CAMERA_INDEX  = 0
CAMERA_WIDTH  = 640
CAMERA_HEIGHT = 480

# ── Detection thresholds ──────────────────────────────────────────────────────
MIN_DETECTION_CONFIDENCE = 0.55
MIN_TRACKING_CONFIDENCE  = 0.55

# Landmarks with visibility below this value are considered out-of-frame.
# Angle calculation and rep counting are skipped when any joint is occluded.
MIN_LANDMARK_VISIBILITY  = 0.6
