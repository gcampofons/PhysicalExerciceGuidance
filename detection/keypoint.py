"""
Unified keypoint format shared by all detector backends.

Both MediaPipe and YOLOv8 detectors return a list[Keypoint] of exactly 33
slots using MediaPipe landmark indices so the rest of the codebase is
backend-agnostic.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Keypoint:
    """Normalised 2-D pose keypoint."""
    x: float
    y: float
    visibility: float  # 0.0 (invisible / missing) → 1.0 (fully visible)
