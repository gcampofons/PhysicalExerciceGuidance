"""
Unified keypoint format used by the pose pipeline.

MediaPipe detector returns a list[Keypoint] of exactly 33
slots using MediaPipe landmark indices.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Keypoint:
    """Normalised 2-D pose keypoint."""
    x: float
    y: float
    visibility: float  # 0.0 (invisible / missing) → 1.0 (fully visible)
