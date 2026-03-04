"""
Detector factory.

Usage:
    with create_detector() as det:
        kpts = det.detect(frame, ts_ms)
"""
from __future__ import annotations
from detection.base_detector import BaseDetector


def create_detector() -> BaseDetector:
    """
    Instantiate the MediaPipe pose detector.
    """
    from detection.pose_detector import PoseDetector
    return PoseDetector()
