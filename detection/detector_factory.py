"""
Detector factory — returns the right backend by name.

Usage:
    with create_detector("mediapipe") as det:
        kpts = det.detect(frame, ts_ms)

    with create_detector("yolo") as det:
        kpts = det.detect(frame, ts_ms)

    with create_detector("movenet_lightning") as det:
        kpts = det.detect(frame, ts_ms)

    with create_detector("movenet_thunder") as det:
        kpts = det.detect(frame, ts_ms)

    with create_detector("rtmpose_s") as det:
        kpts = det.detect(frame, ts_ms)

    with create_detector("rtmpose_m") as det:
        kpts = det.detect(frame, ts_ms)
"""
from __future__ import annotations
from detection.base_detector import BaseDetector


def create_detector(backend: str) -> BaseDetector:
    """
    Instantiate a pose detector for the requested backend.

    Args:
        backend: One of
                 ``"mediapipe"``,
                 ``"yolo"``,
                 ``"movenet_lightning"``,
                 ``"movenet_thunder"``,
                 ``"rtmpose_s"``,
                 ``"rtmpose_m"``.

    Raises:
        ValueError: Unknown backend name.
        ImportError: Required package not installed.
    """
    if backend == "mediapipe":
        from detection.pose_detector import PoseDetector
        return PoseDetector()

    if backend == "yolo":
        from detection.yolo_detector import YOLODetector
        return YOLODetector()

    if backend in ("movenet_lightning", "movenet_thunder"):
        from detection.movenet_detector import MoveNetDetector
        return MoveNetDetector(variant=backend)

    if backend in ("rtmpose_s", "rtmpose_m", "rtmpose_x"):
        from detection.rtmpose_detector import RTMPoseDetector
        return RTMPoseDetector(variant=backend)

    raise ValueError(
        f"Unknown pose backend: {backend!r}. "
        "Valid options: 'mediapipe', 'yolo', "
        "'movenet_lightning', 'movenet_thunder', "
        "'rtmpose_s', 'rtmpose_m', 'rtmpose_x'."
    )
