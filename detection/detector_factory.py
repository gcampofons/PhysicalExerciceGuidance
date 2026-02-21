"""
Detector factory — returns the right backend by name.

Usage:
    with create_detector("mediapipe") as det:
        kpts = det.detect(frame, ts_ms)

    with create_detector("yolo") as det:
        kpts = det.detect(frame, ts_ms)
"""
from __future__ import annotations
from detection.base_detector import BaseDetector


def create_detector(backend: str) -> BaseDetector:
    """
    Instantiate a pose detector for the requested backend.

    Args:
        backend: ``"mediapipe"`` or ``"yolo"``.

    Raises:
        ValueError: Unknown backend name.
        ImportError: Required package not installed (e.g. ultralytics for yolo).
    """
    if backend == "mediapipe":
        from detection.pose_detector import PoseDetector
        return PoseDetector()

    if backend == "yolo":
        from detection.yolo_detector import YOLODetector
        return YOLODetector()

    raise ValueError(
        f"Unknown pose backend: {backend!r}. Valid options: 'mediapipe', 'yolo'."
    )
