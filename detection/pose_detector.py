"""
Thin wrapper around the MediaPipe Pose Landmarker Tasks API.

Responsibilities:
  - Download the model on first use (lazy, thread-safe via a lock).
  - Create a VIDEO-mode PoseLandmarker.
  - Expose a single `detect(frame_bgr, timestamp_ms)` method.
"""
from __future__ import annotations

import os
import threading
import urllib.request

import cv2
import mediapipe as mp
import numpy as np

from core.config import (
    MODEL_PATH, MODEL_URL, MODELS_DIR,
    MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE,
)

_download_lock = threading.Lock()


def ensure_model() -> None:
    """Download the pose landmarker model if it is not already present."""
    with _download_lock:
        if not os.path.exists(MODEL_PATH):
            os.makedirs(MODELS_DIR, exist_ok=True)
            print(f"[PoseDetector] Downloading model → {MODEL_PATH}")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("[PoseDetector] Model ready.")


class PoseDetector:
    """
    Wraps mediapipe.tasks.vision.PoseLandmarker in VIDEO running mode.

    Usage:
        with PoseDetector() as detector:
            landmarks = detector.detect(bgr_frame, timestamp_ms)
    """

    def __init__(self) -> None:
        ensure_model()
        BaseOptions        = mp.tasks.BaseOptions
        PoseLandmarker     = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOpts = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode  = mp.tasks.vision.RunningMode

        opts = PoseLandmarkerOpts(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            min_pose_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self._landmarker = PoseLandmarker.create_from_options(opts)

    # ── Context manager ───────────────────────────────────────────────────────
    def __enter__(self) -> "PoseDetector":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def close(self) -> None:
        self._landmarker.close()

    # ── Public API ────────────────────────────────────────────────────────────
    def detect(self, bgr_frame: np.ndarray, timestamp_ms: int) -> list | None:
        """
        Run pose detection on a single BGR frame.

        Args:
            bgr_frame:    OpenCV BGR frame (uint8, contiguous).
            timestamp_ms: Monotonically increasing timestamp in milliseconds.

        Returns:
            List of 33 NormalizedLandmark objects, or None if no pose found.
        """
        rgb = np.ascontiguousarray(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        return result.pose_landmarks[0] if result.pose_landmarks else None
